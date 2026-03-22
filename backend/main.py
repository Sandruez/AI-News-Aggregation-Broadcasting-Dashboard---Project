from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

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

@app.get("/feed")
async def get_feed():
    return {"items": [], "total": 0}

logging.info("FastAPI app started successfully")
