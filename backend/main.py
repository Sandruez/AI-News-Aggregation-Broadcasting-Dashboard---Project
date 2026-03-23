from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime

# Database imports
from database import init_engine, get_db, Base, Session
from models import Source, NewsItem, Favorite, User, BroadcastLog
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

# Configuration
from config import get_settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Starting AI News Dashboard...")
    
    # Initialize database
    if settings.database_url:
        try:
            from database import init_db
            init_db()
            logger.info("Database initialized successfully (create_all run)")
            
            # Start news ingestion in background using the correct scheduler
            from ingestion.scheduler import start_scheduler
            asyncio.create_task(start_scheduler())
            logger.info("News ingestion scheduler started in background via ingestion.scheduler")
            
            # Insert sample data if needed
            await insert_sample_data()
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
    else:
        logger.warning("No database URL provided - running without database")
    
    yield
    
    logger.info("Shutting down AI News Dashboard...")

async def run_ingestion_scheduler():
    """DEPRECATED: Use ingestion.scheduler.start_scheduler instead."""
    pass

app = FastAPI(
    title="AI News Dashboard API",
    version="2.0.0",
    description="Production-ready AI news aggregation and broadcasting platform",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health checks
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0"
    }

@app.get("/")
async def root():
    return {
        "message": "AI News Dashboard API", 
        "version": "2.0.0",
        "status": "running"
    }

# News endpoints
@app.get("/api/news")
async def get_news(
    page: int = 1, 
    page_size: int = 30, 
    sort_by: str = 'date', 
    q: Optional[str] = None, 
    source_id: Optional[int] = None, 
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get paginated news items with filtering and search"""
    try:
        # Debug logging
        logger.info(f"News API called with params: page={page}, page_size={page_size}, sort_by={sort_by}, q={q}, source_id={source_id}, category={category}")
        
        if db is None:
            return {"items": [], "total": 0, "page": page, "limit": page_size}
        
        # Build query
        query = select(NewsItem).options(selectinload(NewsItem.source))
        
        # Apply filters
        if q:
            query = query.where(
                or_(
                    NewsItem.title.ilike(f"%{q}%"),
                    NewsItem.summary.ilike(f"%{q}%")
                )
            )
        
        if source_id:
            query = query.where(NewsItem.source_id == source_id)
        
        if category:
            query = query.where(NewsItem.category == category)
        
        if sort_by == 'date':
            query = query.order_by(NewsItem.published_at.desc())
        elif sort_by == 'impact':
            query = query.order_by(NewsItem.impact_score.desc())
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = db.execute(count_query).scalar()
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        result = db.execute(query)
        items = result.scalars().all()
        
        return {
            "items": [
                {
                    "id": item.id,
                    "title": item.title,
                    "summary": item.summary,
                    "url": item.url,
                    "source": {
                        "name": item.source.name if item.source else "Unknown",
                        "category": item.source.category if item.source else "general"
                    },
                    "published_at": item.published_at.isoformat() if item.published_at else None,
                    "impact_score": item.impact_score,
                    "category": item.category,
                    "sentiment": item.sentiment,
                    "relevance_score": item.relevance_score,
                    "tags": item.tags or [],
                    "is_favorited": False  # TODO: Check if item is favorited
                } for item in items
            ],
            "total": total_result,
            "page": page,
            "page_size": page_size
        }
        
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch news")

@app.get("/api/news/{item_id}")
def get_news_item(item_id: int, db: Session = Depends(get_db)):
    """Get specific news item"""
    try:
        if db is None:
            raise HTTPException(status_code=404, detail="News item not found")
        
        result = db.execute(
            select(NewsItem).options(selectinload(NewsItem.source))
            .where(NewsItem.id == item_id)
        )
        item = result.scalar_one_or_none()
        
        if not item:
            raise HTTPException(status_code=404, detail="News item not found")
        
        return {
            "id": item.id,
            "title": item.title,
            "summary": item.summary,
            "url": item.url,
            "source": {
                "name": item.source.name if item.source else "Unknown",
                "category": item.source.category if item.source else "general"
            },
            "published_at": item.published_at.isoformat() if item.published_at else None,
            "impact_score": item.impact_score,
            "category": item.category,
            "sentiment": item.sentiment,
            "relevance_score": item.relevance_score,
            "raw_content": item.raw_content,
            "tags": item.tags or [],
            "is_favorited": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching news item {item_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch news item")

@app.post("/api/news/refresh")
async def refresh_news(db = Depends(get_db)):
    """Trigger news refresh from sources"""
    try:
        # TODO: Implement background task to refresh from RSS feeds
        logger.info("News refresh triggered")
        return {"message": "News refresh started", "status": "success"}
    except Exception as e:
        logger.error(f"Error refreshing news: {e}")
        raise HTTPException(status_code=500, detail="Failed to refresh news")

# Favorites endpoints
@app.get("/api/favorites")
async def get_favorites(db: Session = Depends(get_db)):
    """Get user favorites"""
    try:
        if db is None:
            return {"items": []}
        
        result = db.execute(
            select(Favorite).options(selectinload(Favorite.news_item).selectinload(NewsItem.source))
        )
        favorites = result.scalars().all()
        
        return {
            "items": [
                {
                    "id": fav.id,
                    "news_item_id": fav.news_item_id,
                    "created_at": fav.created_at.isoformat(),
                    "news_item": {
                        "id": fav.news_item.id,
                        "title": fav.news_item.title,
                        "summary": fav.news_item.summary,
                        "url": fav.news_item.url,
                        "source": fav.news_item.source.name if fav.news_item.source else "Unknown",
                        "category": fav.news_item.category,
                        "published_at": fav.news_item.published_at.isoformat() if fav.news_item.published_at else None,
                        "image_url": fav.news_item.image_url,
                        "sentiment": fav.news_item.sentiment,
                        "relevance_score": fav.news_item.relevance_score
                    } if fav.news_item else None
                } for fav in favorites
            ]
        }
            
    except Exception as e:
        logger.error(f"Error fetching favorites: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch favorites")

@app.post("/api/favorites/{news_item_id}")
async def add_favorite(news_item_id: int, db: Session = Depends(get_db)):
    """Add item to favorites"""
    try:
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
        
        # Check if news item exists
        news_result = db.execute(select(NewsItem).where(NewsItem.id == news_item_id))
        news_item = news_result.scalar_one_or_none()
        
        if not news_item:
            raise HTTPException(status_code=404, detail="News item not found")
        
        # Check if already favorited
        existing = db.execute(
            select(Favorite).where(Favorite.news_item_id == news_item_id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Already favorited")
        
        # Add favorite
        favorite = Favorite(news_item_id=news_item_id)
        db.add(favorite)
        db.commit()
        
        return {"id": favorite.id, "news_item_id": news_item_id, "created_at": favorite.created_at.isoformat()}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding favorite {news_item_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to add favorite")

@app.delete("/api/favorites/{news_item_id}")
async def remove_favorite(news_item_id: int, db: Session = Depends(get_db)):
    """Remove item from favorites"""
    try:
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
        
        result = db.execute(
            select(Favorite).where(Favorite.news_item_id == news_item_id)
        )
        favorite = result.scalar_one_or_none()
        
        if not favorite:
            raise HTTPException(status_code=404, detail="Favorite not found")
        
        db.delete(favorite)
        db.commit()
        
        return {"message": "Favorite removed", "status": "success"}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing favorite {news_item_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to remove favorite")

# Sources endpoints
@app.get("/api/sources")
def get_sources(db: Session = Depends(get_db)):
    """Get news sources"""
    try:
        if db is None:
            return {"items": [], "total": 0}
        
        result = db.execute(select(Source).order_by(Source.name))
        sources = result.scalars().all()
        
        return {
            "items": [
                {
                    "id": source.id,
                    "name": source.name,
                    "url": source.url,
                    "feed_url": source.feed_url,
                    "type": source.source_type,
                    "category": source.category,
                    "active": source.active,
                    "is_active": source.active
                } for source in sources
            ],
            "total": len(sources)
        }
        
    except Exception as e:
        logger.error(f"Error fetching sources: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch sources")

@app.patch("/api/sources/{id}/toggle")
async def toggle_source(id: int, db: Session = Depends(get_db)):
    """Toggle source active status"""
    try:
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
        
        result = db.execute(select(Source).where(Source.id == id))
        source = result.scalar_one_or_none()
        
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")
        
        source.active = not source.active
        db.commit()
        
        return {"id": id, "is_active": source.active, "active": source.active, "message": "Source toggled"}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling source {id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to toggle source")

# Admin endpoints
@app.get("/api/admin/overview")
async def get_admin_overview(db: Session = Depends(get_db)):
    """Get admin dashboard overview"""
    try:
        if db is None:
            return {"totalNews": 0, "totalFavorites": 0, "activeSources": 0}
        
        news_count = db.scalar(select(func.count(NewsItem.id)))
        favorites_count = db.scalar(select(func.count(Favorite.id)))
        sources_count = db.scalar(select(func.count(Source.id)))
        active_sources_count = db.scalar(select(func.count(Source.id)).where(Source.active == True))
        
        return {
            "totalNews": news_count,
            "totalFavorites": favorites_count,
            "totalSources": sources_count,
            "activeSources": active_sources_count
        }
            
    except Exception as e:
        logger.error(f"Error fetching admin overview: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch admin overview")

@app.post("/api/broadcast")
async def broadcast_news(payload: Dict[str, Any], db: Session = Depends(get_db)):
    """Broadcast news to platforms"""
    try:
        if db is None:
            raise HTTPException(status_code=500, detail="Database not available")
            
        # TODO: Implement email broadcasting, LinkedIn posting, etc.
        logger.info(f"Broadcast payload: {payload}")
        
        # Log broadcast
        broadcast_log = BroadcastLog(
            platform=payload.get("platform", "email"),
            status="sent",
            payload=payload,
            favorite_id=payload.get("favorite_id")
        )
        
        db.add(broadcast_log)
        db.commit()
        
        return {"message": "Broadcast sent", "status": "success", "payload": payload}
        
    except Exception as e:
        logger.error(f"Error broadcasting news: {e}")
        raise HTTPException(status_code=500, detail="Failed to broadcast news")

# Additional admin endpoints for frontend
@app.get("/api/admin/news-trend")
async def get_news_trend(days: int = 7, db: Session = Depends(get_db)):
    """Get news trend data for admin dashboard"""
    try:
        if db is None:
            return {"trend": []}
        
        from datetime import datetime, timedelta
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Query news items by date range
        result = db.execute(
            select(
                func.date(NewsItem.published_at).label('date'),
                func.count(NewsItem.id).label('count')
            )
            .where(NewsItem.published_at >= start_date)
            .where(NewsItem.published_at <= end_date)
            .group_by(func.date(NewsItem.published_at))
            .order_by(func.date(NewsItem.published_at))
        )
        
        # Format data for frontend
        trend_data = []
        for row in result:
            trend_data.append({
                "date": row.date.strftime("%Y-%m-%d"),
                "articles": row.count,
                "duplicates": 0  # TODO: Calculate actual duplicates
            })
        
        # If no data, return empty array
        if not trend_data:
            return {"trend": []}
        
        return {"trend": trend_data}
            
    except Exception as e:
        logger.error(f"Error fetching news trend: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch news trend")

@app.get("/api/admin/source-distribution")
async def get_source_distribution(db: Session = Depends(get_db)):
    """Get source distribution data for admin dashboard"""
    try:
        if db is None:
            return {"distribution": []}
        
        # Query real data from database
        result = db.execute(
            select(Source.name, func.count(NewsItem.id).label('count'))
            .join(NewsItem, Source.id == NewsItem.source_id, isouter=True)
            .group_by(Source.name)
            .order_by(func.count(NewsItem.id).desc())
        )
        
        distribution = []
        for row in result:
            distribution.append({
                "source": row.name,
                "count": row.count or 0
            })
        
        # If no data, return sample sources with 0 counts
        if not distribution:
            sources_result = db.execute(select(Source).order_by(Source.name))
            sources = sources_result.scalars().all()
            distribution = [{"source": source.name, "count": 0} for source in sources]
        
        return {"distribution": distribution}
            
    except Exception as e:
        logger.error(f"Error fetching source distribution: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch source distribution")

@app.get("/api/admin/category-breakdown")
async def get_category_breakdown(db: Session = Depends(get_db)):
    """Get category breakdown data for admin dashboard"""
    try:
        if db is None:
            return {"categories": []}
        
        # Query real data from database
        result = db.execute(
            select(NewsItem.category, func.count(NewsItem.id).label('count'))
            .where(NewsItem.category.isnot(None))
            .group_by(NewsItem.category)
            .order_by(func.count(NewsItem.id).desc())
        )
        
        categories = []
        for row in result:
            categories.append({
                "category": row.category,
                "count": row.count
            })
        
        # If no data, return empty array
        if not categories:
            categories = []
        
        return {"categories": categories}
            
    except Exception as e:
        logger.error(f"Error fetching category breakdown: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch category breakdown")

@app.get("/api/admin/broadcast-analytics")
async def get_broadcast_analytics(db: Session = Depends(get_db)):
    """Get broadcast analytics data for admin dashboard"""
    try:
        if db is None:
            return {"analytics": {}}
        
        # Query real data from database
        result = db.execute(
            select(
                func.count(BroadcastLog.id).label('total_broadcasts'),
                func.sum(
                    case(
                        (BroadcastLog.status == 'sent', 1),
                        else_ = 0
                    )
                ).label('successful_broadcasts'),
                func.sum(
                    case(
                        (BroadcastLog.status == 'sent', 1),
                        else_ = 0
                    )
                ).label('failed_broadcasts'),
                func.count(BroadcastLog.favorite_id).label('total_recipients')
            )
        )
        
        row = result.first()
        
        return {
            "analytics": {
                "total_broadcasts": row.total_broadcasts or 0,
                "successful_broadcasts": row.successful_broadcasts or 0,
                "failed_broadcasts": row.failed_broadcasts or 0,
                "total_recipients": row.total_recipients or 0,
                "average_open_rate": 0.68  # TODO: Calculate actual rate
            }
        }
            
    except Exception as e:
        logger.error(f"Error fetching broadcast analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch broadcast analytics")
            
    except Exception as e:
        logger.error(f"Error fetching broadcast analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch broadcast analytics")

@app.get("/api/admin/system-health")
async def get_system_health(db: Session = Depends(get_db)):
    """Get system health data for admin dashboard"""
    try:
        # Health check data
        health_data = {
            "uptime": "N/A",  # TODO: Calculate actual uptime
            "database_status": "connected" if db else "disconnected",
            "last_ingestion": "N/A",  # TODO: Get last ingestion time
            "memory_usage": "N/A",  # TODO: Get actual memory usage
            "disk_space": "N/A"  # TODO: Get actual disk space
        }
        
        return health_data
            
    except Exception as e:
        logger.error(f"Error fetching system health: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch system health")

@app.get("/api/admin/recent-activity")
async def get_recent_activity(db: Session = Depends(get_db)):
    """Get recent activity data for admin dashboard"""
    try:
        if db is None:
            return {"activity": []}
        
        # Query recent activity from database
        from datetime import datetime, timedelta
        
        # Get recent news items (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        
        recent_news = db.execute(
            select(NewsItem.title, NewsItem.published_at, NewsItem.source)
                .options(selectinload(NewsItem.source))
                .where(NewsItem.published_at >= week_ago)
                .order_by(NewsItem.published_at.desc())
                .limit(10)
        )
        
        # Get recent favorites (last 7 days)
        recent_favorites = db.execute(
            select(Favorite.created_at, Favorite.news_item)
                .options(selectinload(Favorite.news_item))
                .where(Favorite.created_at >= week_ago)
                .order_by(Favorite.created_at.desc())
                .limit(5)
        )
        
        # Get recent broadcasts (last 7 days)
        recent_broadcasts = db.execute(
            select(BroadcastLog.created_at, BroadcastLog.platform, BroadcastLog.status)
                .where(BroadcastLog.created_at >= week_ago)
                .order_by(BroadcastLog.created_at.desc())
                .limit(5)
        )
        
        # Combine activities
        activities = []
        
        # Add news items
        for item in recent_news.scalars().all():
            activities.append({
                "type": "news",
                "title": item.title[:50] + '...' if len(item.title) > 50 else item.title,
                "description": f'New article: {item.title}',
                "timestamp": item.published_at.isoformat() if item.published_at else None,
                "source": item.source.name if item.source else "Unknown"
            })
        
        # Add favorites
        for fav in recent_favorites.scalars().all():
            activities.append({
                "type": "favorite",
                "title": f'Favorited: {fav.news_item.title[:50] if len(fav.news_item.title) > 50 else fav.news_item.title}',
                "description": f'Added {fav.news_item.title} to favorites',
                "timestamp": fav.created_at.isoformat() if fav.created_at else None
            })
        
        # Add broadcasts
        for broadcast in recent_broadcasts.scalars().all():
            activities.append({
                "type": "broadcast",
                "title": f'Broadcast to {broadcast.platform}',
                "description": f'Sent broadcast to {broadcast.platform}',
                "timestamp": broadcast.created_at.isoformat() if broadcast.created_at else None
            })
        
        # Sort by timestamp
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return {"activity": activities}
        }
            
    except Exception as e:
        logger.error(f"Error fetching recent activity: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch recent activity")

@app.get("/api/feed")
async def get_feed(db: Session = Depends(get_db)):
    """RSS feed endpoint"""
    try:
        if db is None:
            return {"items": [], "total": 0}
        
        result = db.execute(
            select(NewsItem).options(selectinload(NewsItem.source))
            .order_by(NewsItem.published_at.desc())
            .limit(20)
        )
        items = result.scalars().all()
        
        # TODO: Convert to proper RSS XML format
        return {
            "items": [
                {
                    "id": item.id,
                    "title": item.title,
                    "summary": item.summary,
                    "url": item.url,
                    "source": {
                        "name": item.source.name if item.source else "Unknown",
                        "category": item.source.category if item.source else "general"
                    },
                    "published_at": item.published_at.isoformat() if item.published_at else None,
                    "tags": item.tags or [],
                    "is_favorited": False
                } for item in items
            ],
            "total": len(items)
        }
            
    except Exception as e:
        logger.error(f"Error fetching feed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch feed")

@app.post("/api/admin/test-fetch")
async def test_fetch():
    """Test RSS fetcher directly"""
    try:
        from ingestion.fetcher import fetch_rss
        from ingestion.sources_registry import ALL_SOURCES
        
        # Test with a simple source
        test_source = ALL_SOURCES[0]  # OpenAI Blog
        logger.info(f"Testing fetch for: {test_source.name}")
        
        items = await fetch_rss(test_source, 1, 5)  # source_id=1, max_items=5
        
        return {
            "source": test_source.name,
            "feed_url": test_source.feed_url,
            "items_fetched": len(items),
            "items": [
                {
                    "title": item.title,
                    "url": item.url,
                    "summary": item.summary[:100] + "..." if item.summary else ""
                } for item in items
            ]
        }
    except Exception as e:
        logger.error(f"Test fetch error: {e}")
        return {"error": str(e), "source": test_source.name}

@app.post("/api/admin/insert-sample-data")
async def manual_insert_sample_data():
    """Manually insert sample data"""
    try:
        await insert_sample_data()
        return {"message": "Sample data inserted successfully", "status": "success"}
    except Exception as e:
        logger.error(f"Error inserting sample data: {e}")
        raise HTTPException(status_code=500, detail="Failed to insert sample data")

@app.post("/api/admin/trigger-ingestion")
async def trigger_ingestion():
    """Manually trigger news ingestion for debugging"""
    try:
        from ingestion.scheduler import run_ingestion
        asyncio.create_task(run_ingestion())
        return {"message": "Ingestion triggered", "status": "success"}
    except Exception as e:
        logger.error(f"Error triggering ingestion: {e}")
        raise HTTPException(status_code=500, detail="Failed to trigger ingestion")

async def insert_sample_data():
    """Insert sample data if database is empty"""
    try:
        db = next(get_db())
        if db is None:
            return
        
        try:
            # Check if sources exist
            sources_result = db.execute(select(Source).limit(1))
            source_exists = sources_result.scalar_one_or_none() is not None
            
            if not source_exists:
                # Insert sample sources
                sample_sources = [
                    Source(
                        name="TechCrunch", 
                        url="https://techcrunch.com", 
                        feed_url="https://techcrunch.com/feed/",
                        category="Technology", 
                        active=True,
                        source_type="rss"
                    ),
                    Source(
                        name="AI News", 
                        url="https://ai-news.com", 
                        feed_url="https://ai-news.com/feed/",
                        category="AI", 
                        active=True,
                        source_type="rss"
                    )
                ]
                
                db.add_all(sample_sources)
                db.commit()
                logger.info("Sample sources inserted")
                
                # Insert sample news items
                news_items = [
                    NewsItem(
                        title="AI Breakthrough: New Model Achieves Human-Level Performance",
                        summary="Researchers announce a groundbreaking AI model that demonstrates human-level reasoning capabilities in multiple benchmarks.",
                        url="https://example.com/ai-breakthrough",
                        source_id=1,
                        category="AI Research",
                        published_at=datetime.utcnow(),
                        sentiment="positive",
                        relevance_score=0.92
                    ),
                    NewsItem(
                        title="OpenAI Announces Major Update to GPT Models",
                        summary="OpenAI releases significant improvements to their language models, offering better performance and reduced costs.",
                        url="https://example.com/openai-release",
                        source_id=2,
                        category="Company News",
                        published_at=datetime.utcnow(),
                        sentiment="neutral",
                        relevance_score=0.88
                    )
                ]
                
                db.add_all(news_items)
                db.commit()
                logger.info("Sample news items inserted")
                
        finally:
            db.close()
                
    except Exception as e:
        logger.error(f"Failed to insert sample data: {e}")

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
