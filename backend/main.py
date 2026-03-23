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
                    "source": item.source.name if item.source else "Unknown",
                    "published_at": item.published_at.isoformat() if item.published_at else None,
                    "impact_score": item.impact_score,
                    "category": item.category,
                    "sentiment": item.sentiment,
                    "relevance_score": item.relevance_score
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
            "source": item.source.name if item.source else "Unknown",
            "published_at": item.published_at.isoformat() if item.published_at else None,
            "impact_score": item.impact_score,
            "category": item.category,
            "sentiment": item.sentiment,
            "relevance_score": item.relevance_score,
            "raw_content": item.raw_content
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
        
        # Simple mock data for now
        return {
            "trend": [
                {"date": "2024-01-15", "count": 12},
                {"date": "2024-01-16", "count": 18},
                {"date": "2024-01-17", "count": 15},
                {"date": "2024-01-18", "count": 22},
                {"date": "2024-01-19", "count": 25},
                {"date": "2024-01-20", "count": 20},
                {"date": "2024-01-21", "count": 28}
            ]
        }
            
    except Exception as e:
        logger.error(f"Error fetching news trend: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch news trend")

@app.get("/api/admin/source-distribution")
async def get_source_distribution(db: Session = Depends(get_db)):
    """Get source distribution data for admin dashboard"""
    try:
        if db is None:
            return {"distribution": []}
        
        # Simple mock data for now
        return {
            "distribution": [
                {"source": "TechCrunch", "count": 45},
                {"source": "The Verge", "count": 32},
                {"source": "AI News", "count": 28},
                {"source": "Wired", "count": 15},
                {"source": "MIT Review", "count": 12}
            ]
        }
            
    except Exception as e:
        logger.error(f"Error fetching source distribution: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch source distribution")

@app.get("/api/admin/category-breakdown")
async def get_category_breakdown(db: Session = Depends(get_db)):
    """Get category breakdown data for admin dashboard"""
    try:
        if db is None:
            return {"categories": []}
        
        # Simple mock data for now
        return {
            "categories": [
                {"category": "AI Research", "count": 38},
                {"category": "Company News", "count": 25},
                {"category": "Technology", "count": 42},
                {"category": "Business", "count": 18},
                {"category": "Science", "count": 15}
            ]
        }
            
    except Exception as e:
        logger.error(f"Error fetching category breakdown: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch category breakdown")

@app.get("/api/admin/broadcast-analytics")
async def get_broadcast_analytics(db: Session = Depends(get_db)):
    """Get broadcast analytics data for admin dashboard"""
    try:
        if db is None:
            return {"analytics": {}}
        
        # Simple mock data for now
        return {
            "analytics": {
                "total_broadcasts": 156,
                "successful_broadcasts": 142,
                "failed_broadcasts": 14,
                "total_recipients": 2847,
                "average_open_rate": 0.68,
                "platforms": {
                    "email": 89,
                    "linkedin": 45,
                    "twitter": 22
                }
            }
        }
            
    except Exception as e:
        logger.error(f"Error fetching broadcast analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch broadcast analytics")

@app.get("/api/admin/system-health")
async def get_system_health(db: Session = Depends(get_db)):
    """Get system health data for admin dashboard"""
    try:
        # Health check data
        return {
            "health": {
                "database": "healthy" if db is not None else "unhealthy",
                "api": "healthy",
                "memory_usage": 0.65,
                "cpu_usage": 0.42,
                "disk_usage": 0.38,
                "uptime": "5 days, 12 hours",
                "last_restart": "2024-01-16T08:30:00Z"
            }
        }
            
    except Exception as e:
        logger.error(f"Error fetching system health: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch system health")

@app.get("/api/admin/recent-activity")
async def get_recent_activity(db: Session = Depends(get_db)):
    """Get recent activity data for admin dashboard"""
    try:
        if db is None:
            return {"activities": []}
        
        # Simple mock data for now
        return {
            "activities": [
                {"id": 1, "type": "news_added", "message": "New article: AI Breakthrough in Healthcare", "timestamp": "2024-01-21T14:30:00Z"},
                {"id": 2, "type": "broadcast_sent", "message": "Newsletter sent to 1,245 subscribers", "timestamp": "2024-01-21T12:15:00Z"},
                {"id": 3, "type": "source_added", "message": "New source added: MIT Technology Review", "timestamp": "2024-01-21T10:45:00Z"},
                {"id": 4, "type": "user_favorite", "message": "User favorited article about OpenAI", "timestamp": "2024-01-21T09:20:00Z"},
                {"id": 5, "type": "system_restart", "message": "System restarted successfully", "timestamp": "2024-01-21T08:30:00Z"}
            ]
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
                    "source": item.source.name if item.source else "Unknown",
                    "published_at": item.published_at.isoformat() if item.published_at else None
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
