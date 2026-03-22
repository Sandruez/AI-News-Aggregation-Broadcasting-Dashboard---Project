from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from contextlib import asynccontextmanager
import asyncio

# Configure logging - minimal
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Log if environment variables are set
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
            
            # Use existing database setup
            from database import init_engine, Base
            from models import Source, NewsItem, Favorite, BroadcastLog, User
            
            # Initialize engine
            init_engine()
            
            # Run migrations
            from database import engine
            if engine:
                async with engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
            
            logging.info("Database migrations completed successfully!")
        except Exception as e:
            logging.error(f"Database migration failed: {e}")
    else:
        logging.info("No database - running without migrations")
    
    yield

# Create minimal FastAPI app
app = FastAPI(
    title="AI News Dashboard API",
    description="Aggregates, deduplicates, and broadcasts AI news from 20+ sources.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

# Root endpoint
@app.get("/")
async def root():
    return {"message": "AI News Dashboard API", "version": "1.0.0"}

# Mock API endpoints to prevent frontend crashes
@app.get("/api/news")
async def get_news():
    return {
        "items": [
            {
                "id": 1,
                "title": "AI Breakthrough: New Model Achieves Human-Level Performance",
                "summary": "Researchers announce a groundbreaking AI model that demonstrates human-level reasoning capabilities.",
                "url": "https://example.com/ai-breakthrough",
                "source": "TechCrunch",
                "category": "AI Research",
                "published_at": "2024-01-15T10:00:00Z",
                "image_url": "https://example.com/image.jpg",
                "sentiment": "positive",
                "relevance_score": 0.95
            },
            {
                "id": 2,
                "title": "OpenAI Releases New Language Model",
                "summary": "OpenAI announces the release of their latest language model with improved capabilities.",
                "url": "https://example.com/openai-release",
                "source": "The Verge",
                "category": "Company News",
                "published_at": "2024-01-14T15:30:00Z",
                "image_url": "https://example.com/image2.jpg",
                "sentiment": "neutral",
                "relevance_score": 0.88
            }
        ],
        "total": 2,
        "page": 1,
        "limit": 20
    }

@app.get("/api/favorites")
async def get_favorites():
    return {"items": []}

@app.get("/api/sources")
async def get_sources():
    return {
        "items": [
            {"id": 1, "name": "TechCrunch", "url": "https://techcrunch.com", "category": "Technology", "is_active": True},
            {"id": 2, "name": "The Verge", "url": "https://theverge.com", "category": "Technology", "is_active": True},
            {"id": 3, "name": "AI News", "url": "https://ai-news.com", "category": "AI", "is_active": True}
        ]
    }

@app.get("/api/admin/overview")
async def get_admin_overview():
    return {"totalNews": 150, "totalFavorites": 25, "activeSources": 12}

@app.get("/feed")
async def get_feed():
    return {"items": [], "total": 0}

# Log startup
logging.info("FastAPI app created successfully")
