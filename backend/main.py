from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging

from database import init_db
from routers import news, favorites, broadcast, sources, admin
from ingestion.scheduler import start_scheduler, stop_scheduler
from config import get_settings

# Configure logging - reduce logging for Railway
settings = get_settings()
if settings.is_production:
    logging.basicConfig(level=logging.WARNING)  # Only show warnings and errors in production
else:
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    if not settings.is_production:
        scheduler_task = asyncio.create_task(start_scheduler())
    yield
    if not settings.is_production:
        scheduler_task.cancel()

app = FastAPI(
    title="AI News Dashboard API",
    description="Aggregates, deduplicates, and broadcasts AI news from 20+ sources.",
    version="1.0.0",
    lifespan=lifespan,
    debug=settings.debug
)

# Configure CORS for production
if settings.is_production:
    allowed_origins = [
        "https://yourdomain.com",  # Replace with your actual domain
        "https://www.yourdomain.com",
    ]
else:
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(news.router, prefix="/api/news", tags=["News"])
app.include_router(favorites.router, prefix="/api/favorites", tags=["Favorites"])
app.include_router(broadcast.router, prefix="/api/broadcast", tags=["Broadcast"])
app.include_router(sources.router, prefix="/api/sources", tags=["Sources"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])

@app.get("/health")
@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "AI News Dashboard"}
