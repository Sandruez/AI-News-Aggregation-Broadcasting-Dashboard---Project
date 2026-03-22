from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure logging - minimal
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Create minimal FastAPI app
app = FastAPI(
    title="AI News Dashboard API",
    description="Aggregates, deduplicates, and broadcasts AI news from 20+ sources.",
    version="1.0.0"
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
    return {"items": [], "total": 0, "page": 1, "limit": 20}

@app.get("/api/favorites")
async def get_favorites():
    return {"items": []}

@app.get("/api/sources")
async def get_sources():
    return {"items": []}

@app.get("/api/admin/overview")
async def get_admin_overview():
    return {"totalNews": 0, "totalFavorites": 0, "activeSources": 0}

# Log startup
logging.info("FastAPI app created successfully")
