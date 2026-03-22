from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

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
async def get_news(page: int = 1, page_size: int = 30, sort_by: str = 'date', q: str = '', source_id: int = None, category: str = None):
    """Return news items with proper structure frontend expects"""
    return {
        "items": [
            {
                "id": 1,
                "title": "AI Breakthrough: New Model Achieves Human-Level Performance",
                "summary": "Researchers announce a groundbreaking AI model that demonstrates human-level reasoning capabilities in multiple benchmarks.",
                "url": "https://example.com/ai-breakthrough",
                "source": "TechCrunch",
                "category": "AI Research",
                "published_at": "2024-01-15T10:00:00Z",
                "image_url": "https://example.com/image.jpg",
                "sentiment": "positive",
                "relevance_score": 0.95,
                "is_favorite": False
            },
            {
                "id": 2,
                "title": "OpenAI Releases New Language Model",
                "summary": "OpenAI announces the release of their latest language model with improved capabilities and better performance.",
                "url": "https://example.com/openai-release",
                "source": "The Verge",
                "category": "Company News",
                "published_at": "2024-01-14T15:30:00Z",
                "image_url": "https://example.com/image2.jpg",
                "sentiment": "neutral",
                "relevance_score": 0.88,
                "is_favorite": False
            }
        ],
        "total": 2,
        "page": page,
        "limit": page_size
    }

@app.post("/api/news/refresh")
async def refresh_news():
    """Refresh news sources"""
    return {"message": "News refresh started", "status": "success"}

@app.get("/api/news/{item_id}")
async def get_news_item(item_id: int):
    """Get specific news item"""
    return {
        "id": item_id,
        "title": "AI Breakthrough: New Model Achieves Human-Level Performance",
        "summary": "Researchers announce a groundbreaking AI model that demonstrates human-level reasoning capabilities.",
        "url": "https://example.com/ai-breakthrough",
        "source": "TechCrunch",
        "category": "AI Research",
        "published_at": "2024-01-15T10:00:00Z",
        "image_url": "https://example.com/image.jpg",
        "sentiment": "positive",
        "relevance_score": 0.95,
        "is_favorite": False
    }

@app.get("/api/favorites")
async def get_favorites():
    """Get user favorites"""
    return {"items": []}

@app.post("/api/favorites/{news_item_id}")
async def add_favorite(news_item_id: int):
    """Add item to favorites"""
    return {"id": 1, "news_item_id": news_item_id, "created_at": "2024-01-15T10:00:00Z"}

@app.delete("/api/favorites/{news_item_id}")
async def remove_favorite(news_item_id: int):
    """Remove item from favorites"""
    return {"message": "Favorite removed", "status": "success"}

@app.get("/api/sources")
async def get_sources():
    """Get news sources"""
    return {
        "items": [
            {"id": 1, "name": "TechCrunch", "url": "https://techcrunch.com", "category": "Technology", "is_active": True},
            {"id": 2, "name": "The Verge", "url": "https://theverge.com", "category": "Technology", "is_active": True},
            {"id": 3, "name": "AI News", "url": "https://ai-news.com", "category": "AI", "is_active": True}
        ]
    }

@app.patch("/api/sources/{id}/toggle")
async def toggle_source(id: int):
    """Toggle source active status"""
    return {"id": id, "is_active": False, "message": "Source toggled"}

@app.get("/api/admin/overview")
async def get_admin_overview():
    """Get admin dashboard overview"""
    return {"totalNews": 150, "totalFavorites": 25, "activeSources": 12}

@app.post("/api/broadcast")
async def broadcast_news(payload: Dict[str, Any]):
    """Broadcast news to platforms"""
    return {"message": "Broadcast sent", "status": "success", "payload": payload}

@app.get("/feed")
async def get_feed():
    """RSS feed endpoint"""
    return {"items": [], "total": 0}

logging.info("FastAPI app started successfully")
