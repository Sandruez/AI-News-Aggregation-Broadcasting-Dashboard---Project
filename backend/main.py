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

# Log startup
logging.info("FastAPI app created successfully")
