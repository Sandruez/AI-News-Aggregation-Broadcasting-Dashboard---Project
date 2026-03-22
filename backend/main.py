from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from contextlib import asynccontextmanager
import asyncio

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

DATABASE_URL = os.getenv("DATABASE_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if DATABASE_URL:
    logging.info("DATABASE_URL found")
else:
    logging.warning("DATABASE_URL not found")

if GROQ_API_KEY:
    logging.info("GROQ_API_KEY found")
else:
    logging.warning("GROQ_API_KEY not found")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database if DATABASE_URL is available
    if DATABASE_URL:
        try:
            logging.info("Running database migrations...")
            
            # Import database components
            from database import init_engine, Base
            from models import Source, NewsItem, Favorite, BroadcastLog, User
            
            # Initialize database
            init_engine()
            
            # Import engine for migrations
            from database import engine
            
            if engine:
                # Run migrations
                async with engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
                
                logging.info("Database migrations completed successfully!")
                
                # Insert sample data if tables are empty
                await insert_sample_data()
            else:
                logging.error("Failed to initialize database engine")
                
        except Exception as e:
            logging.error(f"Database migration failed: {e}")
    else:
        logging.info("No database - running without migrations")
    
    yield

async def insert_sample_data():
    """Insert sample data if database is empty"""
    try:
        from database import get_db
        from models import Source, NewsItem
        
        async for db in get_db():
            if db is None:
                return
                
            # Check if sources exist
            from sqlalchemy import select
            result = await db.execute(select(Source).limit(1))
            source_exists = result.first() is not None
            
            if not source_exists:
                # Insert sample sources
                sample_sources = [
                    Source(name="TechCrunch", url="https://techcrunch.com", category="Technology", active=True),
                    Source(name="The Verge", url="https://theverge.com", category="Technology", active=True),
                    Source(name="AI News", url="https://ai-news.com", category="AI", active=True)
                ]
                
                db.add_all(sample_sources)
                await db.commit()
                logging.info("Sample sources inserted")
                
    except Exception as e:
        logging.error(f"Failed to insert sample data: {e}")

app = FastAPI(title="AI News Dashboard API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

@app.get("/")
async def root():
    return {"message": "AI News Dashboard API", "version": "1.0.0"}

@app.get("/api/news")
async def get_news():
    try:
        from database import get_db
        from models import NewsItem
        from sqlalchemy import select
        
        async for db in get_db():
            if db is None:
                return {"items": [], "total": 0, "page": 1, "limit": 20}
            
            result = await db.execute(select(NewsItem).limit(10))
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
                        "relevance_score": item.relevance_score
                    } for item in news_items
                ],
                "total": len(news_items),
                "page": 1,
                "limit": 20
            }
    except Exception as e:
        logging.error(f"Error fetching news: {e}")
        return {"items": [], "total": 0, "page": 1, "limit": 20}

@app.get("/api/favorites")
async def get_favorites():
    try:
        from database import get_db
        from models import Favorite
        from sqlalchemy import select
        
        async for db in get_db():
            if db is None:
                return {"items": []}
            
            result = await db.execute(select(Favorite))
            favorites = result.scalars().all()
            
            return {
                "items": [
                    {
                        "id": fav.id,
                        "news_item_id": fav.news_item_id,
                        "created_at": fav.created_at.isoformat()
                    } for fav in favorites
                ]
            }
    except Exception as e:
        logging.error(f"Error fetching favorites: {e}")
        return {"items": []}

@app.get("/api/sources")
async def get_sources():
    try:
        from database import get_db
        from models import Source
        from sqlalchemy import select
        
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
                        "category": source.category,
                        "is_active": source.active
                    } for source in sources
                ]
            }
    except Exception as e:
        logging.error(f"Error fetching sources: {e}")
        return {"items": []}

@app.get("/api/admin/overview")
async def get_admin_overview():
    try:
        from database import get_db
        from models import NewsItem, Favorite, Source
        from sqlalchemy import select, func
        
        async for db in get_db():
            if db is None:
                return {"totalNews": 0, "totalFavorites": 0, "activeSources": 0}
            
            news_count = await db.scalar(select(func.count(NewsItem.id)))
            favorites_count = await db.scalar(select(func.count(Favorite.id)))
            sources_count = await db.scalar(select(func.count(Source.id)))
            
            return {
                "totalNews": news_count,
                "totalFavorites": favorites_count,
                "activeSources": sources_count
            }
    except Exception as e:
        logging.error(f"Error fetching admin overview: {e}")
        return {"totalNews": 0, "totalFavorites": 0, "activeSources": 0}

@app.get("/feed")
async def get_feed():
    return {"items": [], "total": 0}

logging.info("FastAPI app started successfully")
