from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
async def get_news():
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
            }
        ],
        "total": 1,
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
            {"id": 1, "name": "TechCrunch", "url": "https://techcrunch.com", "category": "Technology", "is_active": True}
        ]
    }

@app.get("/api/admin/overview")
async def get_admin_overview():
    return {"totalNews": 1, "totalFavorites": 0, "activeSources": 1}

@app.get("/feed")
async def get_feed():
    return {"items": [], "total": 0}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
