from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime

# Database imports
from database import init_engine, get_db, Base
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
            await init_engine()
            logger.info("Database initialized successfully")
            
            # Run migrations
            from database import engine
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database migrations completed")
            
            # Insert sample data if needed
            await insert_sample_data()
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    else:
        logger.warning("No database URL provided - running without database")
    
    yield
    
    logger.info("Shutting down AI News Dashboard...")

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
    db = Depends(get_db)
):
    """Get paginated news items with filtering and search"""
    try:
        async for db in get_db():
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
            
            # Apply sorting
            if sort_by == 'date':
                query = query.order_by(NewsItem.published_at.desc())
            elif sort_by == 'relevance':
                query = query.order_by(NewsItem.relevance_score.desc())
            
            # Get total count
            count_query = select(func.count(NewsItem.id))
            if q:
                count_query = count_query.where(
                    or_(
                        NewsItem.title.ilike(f"%{q}%"),
                        NewsItem.summary.ilike(f"%{q}%")
                    )
                )
            if source_id:
                count_query = count_query.where(NewsItem.source_id == source_id)
            if category:
                count_query = count_query.where(NewsItem.category == category)
            
            total = await db.scalar(count_query)
            
            # Apply pagination
            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size)
            
            result = await db.execute(query)
            news_items = result.scalars().all()
            
            return {
                "items": [
                    {
                        "id": item.id,
                        "title": item.title,
                        "summary": item.summary,
                        "url": item.url,
                        "source": item.source.name if item.source else "Unknown",
                        "category": item.category,
                        "published_at": item.published_at.isoformat() if item.published_at else None,
                        "image_url": item.image_url,
                        "sentiment": item.sentiment,
                        "relevance_score": item.relevance_score,
                        "is_favorite": False  # TODO: Check user favorites
                    } for item in news_items
                ],
                "total": total,
                "page": page,
                "limit": page_size
            }
            
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch news")

@app.get("/api/news/{item_id}")
async def get_news_item(item_id: int, db = Depends(get_db)):
    """Get specific news item"""
    try:
        async for db in get_db():
            if db is None:
                raise HTTPException(status_code=404, detail="News item not found")
            
            result = await db.execute(
                select(NewsItem).options(selectinload(NewsItem.source)).where(NewsItem.id == item_id)
            )
            item = result.scalar_one_or_none()
            
            if not item:
                raise HTTPException(status_code=404, detail="News item not found")
            
            return {
                "id": item.id,
                "title": item.title,
                "summary": item.summary,
                "url": item.url,
                "source": item.source.name if item.source else "Unknown",
                "category": item.category,
                "published_at": item.published_at.isoformat() if item.published_at else None,
                "image_url": item.image_url,
                "sentiment": item.sentiment,
                "relevance_score": item.relevance_score,
                "is_favorite": False
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
async def get_favorites(db = Depends(get_db)):
    """Get user favorites"""
    try:
        async for db in get_db():
            if db is None:
                return {"items": []}
            
            result = await db.execute(
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
async def add_favorite(news_item_id: int, db = Depends(get_db)):
    """Add item to favorites"""
    try:
        async for db in get_db():
            if db is None:
                raise HTTPException(status_code=500, detail="Database not available")
            
            # Check if news item exists
            news_result = await db.execute(select(NewsItem).where(NewsItem.id == news_item_id))
            news_item = news_result.scalar_one_or_none()
            
            if not news_item:
                raise HTTPException(status_code=404, detail="News item not found")
            
            # Check if already favorited
            existing = await db.execute(
                select(Favorite).where(Favorite.news_item_id == news_item_id)
            )
            if existing.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Already favorited")
            
            # Add favorite
            favorite = Favorite(news_item_id=news_item_id)
            db.add(favorite)
            await db.commit()
            
            return {"id": favorite.id, "news_item_id": news_item_id, "created_at": favorite.created_at.isoformat()}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding favorite {news_item_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to add favorite")

@app.delete("/api/favorites/{news_item_id}")
async def remove_favorite(news_item_id: int, db = Depends(get_db)):
    """Remove item from favorites"""
    try:
        async for db in get_db():
            if db is None:
                raise HTTPException(status_code=500, detail="Database not available")
            
            result = await db.execute(
                select(Favorite).where(Favorite.news_item_id == news_item_id)
            )
            favorite = result.scalar_one_or_none()
            
            if not favorite:
                raise HTTPException(status_code=404, detail="Favorite not found")
            
            await db.delete(favorite)
            await db.commit()
            
            return {"message": "Favorite removed", "status": "success"}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing favorite {news_item_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to remove favorite")

# Sources endpoints
@app.get("/api/sources")
async def get_sources(db = Depends(get_db)):
    """Get news sources"""
    try:
        async for db in get_db():
            if db is None:
                return {"items": []}
            
            result = await db.execute(select(Source))
            sources = result.scalars().all()
            
            return {
                "items": [
                    {
                        "id": source.id,
                        "name": source.name,
                        "url": source.url,
                        "feed_url": source.feed_url,
                        "category": source.category,
                        "is_active": source.active,
                        "source_type": source.source_type
                    } for source in sources
                ]
            }
            
    except Exception as e:
        logger.error(f"Error fetching sources: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch sources")

@app.patch("/api/sources/{id}/toggle")
async def toggle_source(id: int, db = Depends(get_db)):
    """Toggle source active status"""
    try:
        async for db in get_db():
            if db is None:
                raise HTTPException(status_code=500, detail="Database not available")
            
            result = await db.execute(select(Source).where(Source.id == id))
            source = result.scalar_one_or_none()
            
            if not source:
                raise HTTPException(status_code=404, detail="Source not found")
            
            source.active = not source.active
            await db.commit()
            
            return {"id": id, "is_active": source.active, "message": "Source toggled"}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling source {id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to toggle source")

# Admin endpoints
@app.get("/api/admin/overview")
async def get_admin_overview(db = Depends(get_db)):
    """Get admin dashboard overview"""
    try:
        async for db in get_db():
            if db is None:
                return {"totalNews": 0, "totalFavorites": 0, "activeSources": 0}
            
            news_count = await db.scalar(select(func.count(NewsItem.id)))
            favorites_count = await db.scalar(select(func.count(Favorite.id)))
            sources_count = await db.scalar(select(func.count(Source.id)))
            active_sources_count = await db.scalar(select(func.count(Source.id)).where(Source.active == True))
            
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
async def broadcast_news(payload: Dict[str, Any], db = Depends(get_db)):
    """Broadcast news to platforms"""
    try:
        # TODO: Implement email broadcasting, LinkedIn posting, etc.
        logger.info(f"Broadcast payload: {payload}")
        
        # Log broadcast
        broadcast_log = BroadcastLog(
            platform=payload.get("platform", "email"),
            status="sent",
            recipient_count=len(payload.get("recipients", [])),
            message_id="broadcast_" + str(int(datetime.utcnow().timestamp()))
        )
        
        async for db in get_db():
            if db is not None:
                db.add(broadcast_log)
                await db.commit()
        
        return {"message": "Broadcast sent", "status": "success", "payload": payload}
        
    except Exception as e:
        logger.error(f"Error broadcasting news: {e}")
        raise HTTPException(status_code=500, detail="Failed to broadcast news")

@app.get("/feed")
async def get_feed(db = Depends(get_db)):
    """RSS feed endpoint"""
    try:
        async for db in get_db():
            if db is None:
                return {"items": [], "total": 0}
            
            result = await db.execute(
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
                        "source": item.source.name if item.source else "Unknown",
                        "published_at": item.published_at.isoformat() if item.published_at else None
                    } for item in items
                ],
                "total": len(items)
            }
            
    except Exception as e:
        logger.error(f"Error fetching feed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch feed")

async def insert_sample_data():
    """Insert sample data if database is empty"""
    try:
        async for db in get_db():
            if db is None:
                return
            
            # Check if sources exist
            sources_result = await db.execute(select(Source).limit(1))
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
                        name="The Verge", 
                        url="https://theverge.com", 
                        feed_url="https://www.theverge.com/rss/index.xml",
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
                await db.commit()
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
                        relevance_score=0.95
                    ),
                    NewsItem(
                        title="OpenAI Releases New Language Model",
                        summary="OpenAI announces the release of their latest language model with improved capabilities and better performance.",
                        url="https://example.com/openai-release",
                        source_id=2,
                        category="Company News",
                        published_at=datetime.utcnow(),
                        sentiment="neutral",
                        relevance_score=0.88
                    )
                ]
                
                db.add_all(news_items)
                await db.commit()
                logger.info("Sample news items inserted")
                
    except Exception as e:
        logger.error(f"Failed to insert sample data: {e}")

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
