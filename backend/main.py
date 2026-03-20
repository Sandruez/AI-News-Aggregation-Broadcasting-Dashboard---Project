from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

from database import init_db
from routers import news, favorites, broadcast, sources
from ingestion.scheduler import start_scheduler, stop_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    scheduler_task = asyncio.create_task(start_scheduler())
    yield
    scheduler_task.cancel()

app = FastAPI(
    title="AI News Dashboard API",
    description="Aggregates, deduplicates, and broadcasts AI news from 20+ sources.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(news.router, prefix="/api/news", tags=["News"])
app.include_router(favorites.router, prefix="/api/favorites", tags=["Favorites"])
app.include_router(broadcast.router, prefix="/api/broadcast", tags=["Broadcast"])
app.include_router(sources.router, prefix="/api/sources", tags=["Sources"])

@app.get("/health")
async def health():
    return {"status": "ok", "service": "AI News Dashboard"}
