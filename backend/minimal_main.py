from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
