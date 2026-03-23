import feedparser
import httpx
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from urllib.parse import urljoin, urlparse
import asyncio
from sqlalchemy import select, and_
from database import get_db
from models import Source, NewsItem
from groq_service import groq_service

logger = logging.getLogger(__name__)

class NewsAggregator:
    """Service for aggregating news from RSS feeds"""
    
    def __init__(self):
        self.timeout = 30
        self.max_articles_per_source = 50
        self.deduplication_window_hours = 24
    
    async def fetch_rss_feed(self, feed_url: str) -> Optional[List[Dict]]:
        """Fetch and parse RSS feed"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(feed_url)
                response.raise_for_status()
                
                feed = feedparser.parse(response.content)
                
                if feed.bozo:
                    logger.warning(f"Feed parsing warning for {feed_url}: {feed.bozo_exception}")
                
                articles = []
                for entry in feed.entries[:self.max_articles_per_source]:
                    article = {
                        'title': entry.get('title', ''),
                        'summary': entry.get('summary', entry.get('description', '')),
                        'url': entry.get('link', ''),
                        'published_at': self._parse_date(entry),
                        'guid': entry.get('id', entry.get('link', '')),
                        'author': entry.get('author', ''),
                        'tags': [tag.term for tag in entry.get('tags', [])]
                    }
                    articles.append(article)
                
                logger.info(f"Fetched {len(articles)} articles from {feed_url}")
                return articles
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching {feed_url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching {feed_url}: {e}")
            return None
    
    def _parse_date(self, entry) -> Optional[datetime]:
        """Parse date from RSS entry"""
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            try:
                return datetime(*entry.published_parsed[:6])
            except (ValueError, TypeError):
                pass
        
        if hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            try:
                return datetime(*entry.updated_parsed[:6])
            except (ValueError, TypeError):
                pass
        
        return datetime.utcnow()
    
    async def process_article(self, article: Dict, source: Source, db) -> Optional[NewsItem]:
        """Process individual article with AI analysis"""
        try:
            # Check for duplicates
            existing = await db.execute(
                select(NewsItem).where(
                    and_(
                        NewsItem.url == article['url'],
                        NewsItem.source_id == source.id
                    )
                )
            )
            if existing.scalar_one_or_none():
                return None  # Skip duplicate
            
            # AI analysis
            sentiment_analysis = await groq_service.score_impact(
                article['title'], 
                article['summary']
            )
            
            # Generate summary if needed
            summary = article['summary']
            if len(summary) > 500:
                summary = await groq_service.summarize(article['title'], article['summary'])
            
            # Create news item
            news_item = NewsItem(
                title=article['title'],
                summary=summary,
                url=article['url'],
                source_id=source.id,
                category=source.category or "Technology",
                published_at=article['published_at'],
                sentiment="positive" if sentiment_analysis > 6 else "negative" if sentiment_analysis < 4 else "neutral",
                relevance_score=sentiment_analysis / 10.0,
                raw_content=article['summary'][:2000],  # Store raw content for future processing
                guid=article['guid']
            )
            
            return news_item
            
        except Exception as e:
            logger.error(f"Error processing article {article.get('title', 'Unknown')}: {e}")
            return None
    
    async def aggregate_from_source(self, source_id: int, db) -> int:
        """Aggregate news from a single source"""
        try:
            # Get source
            result = await db.execute(select(Source).where(Source.id == source_id))
            source = result.scalar_one_or_none()
            
            if not source or not source.active:
                return 0
            
            # Fetch RSS feed
            articles = await self.fetch_rss_feed(source.feed_url or source.url)
            if not articles:
                return 0
            
            # Process articles
            processed_count = 0
            for article in articles:
                news_item = await self.process_article(article, source, db)
                if news_item:
                    db.add(news_item)
                    processed_count += 1
            
            await db.commit()
            logger.info(f"Processed {processed_count} new articles from {source.name}")
            return processed_count
            
        except Exception as e:
            logger.error(f"Error aggregating from source {source_id}: {e}")
            return 0
    
    async def aggregate_all_sources(self) -> Dict[str, int]:
        """Aggregate news from all active sources"""
        results = {}
        
        try:
            async for db in get_db():
                if db is None:
                    continue
                
                # Get all active sources
                result = await db.execute(select(Source).where(Source.active == True))
                sources = result.scalars().all()
                
                # Process each source
                tasks = []
                for source in sources:
                    task = self.aggregate_from_source(source.id, db)
                    tasks.append(task)
                
                # Run concurrently
                counts = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Compile results
                for i, count in enumerate(counts):
                    source_name = sources[i].name if i < len(sources) else f"Source {i}"
                    if isinstance(count, Exception):
                        logger.error(f"Error processing {source_name}: {count}")
                        results[source_name] = 0
                    else:
                        results[source_name] = count
                
                break  # Only need one db session
                
        except Exception as e:
            logger.error(f"Error in aggregate_all_sources: {e}")
        
        return results
    
    async def cleanup_old_articles(self, days_to_keep: int = 30) -> int:
        """Clean up old articles to manage database size"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            async for db in get_db():
                if db is None:
                    continue
                
                # Count old articles
                count_result = await db.execute(
                    select(NewsItem).where(NewsItem.published_at < cutoff_date)
                )
                old_articles = count_result.scalars().all()
                
                # Delete old articles
                for article in old_articles:
                    await db.delete(article)
                
                await db.commit()
                logger.info(f"Cleaned up {len(old_articles)} old articles")
                return len(old_articles)
                
        except Exception as e:
            logger.error(f"Error cleaning up old articles: {e}")
            return 0
    
    async def get_feed_health(self) -> Dict[str, Any]:
        """Get health status of all RSS feeds"""
        try:
            async for db in get_db():
                if db is None:
                    continue
                
                # Get all sources
                result = await db.execute(select(Source))
                sources = result.scalars().all()
                
                health_status = {}
                
                for source in sources:
                    # Check last successful fetch
                    recent_articles = await db.execute(
                        select(NewsItem)
                        .where(and_(
                            NewsItem.source_id == source.id,
                            NewsItem.published_at >= datetime.utcnow() - timedelta(hours=24)
                        ))
                        .limit(1)
                    )
                    
                    has_recent = recent_articles.scalar_one_or_none() is not None
                    
                    health_status[source.name] = {
                        'active': source.active,
                        'feed_url': source.feed_url or source.url,
                        'has_recent_articles': has_recent,
                        'last_check': datetime.utcnow().isoformat()
                    }
                
                return health_status
                
        except Exception as e:
            logger.error(f"Error getting feed health: {e}")
            return {}

# Global instance
news_aggregator = NewsAggregator()
