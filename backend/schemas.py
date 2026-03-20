from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional


# ── News ────────────────────────────────────────────────

class NewsItemCreate(BaseModel):
    source_id: Optional[int] = None
    title: str
    summary: Optional[str] = ""
    url: str
    author: Optional[str] = ""
    published_at: Optional[datetime] = None
    tags: list[str] = []
    content_hash: Optional[str] = None


class SourceOut(BaseModel):
    id: int
    name: str
    url: str
    category: Optional[str]

    class Config:
        from_attributes = True


class NewsItemOut(BaseModel):
    id: int
    title: str
    summary: Optional[str]
    ai_summary: Optional[str]
    author: Optional[str]
    url: str
    published_at: Optional[datetime]
    ingested_at: Optional[datetime]
    tags: list[str]
    is_duplicate: bool
    impact_score: int
    is_favorited: bool = False
    source: Optional[SourceOut]

    class Config:
        from_attributes = True


class NewsListResponse(BaseModel):
    items: list[NewsItemOut]
    total: int
    page: int
    page_size: int


# ── Favorites ───────────────────────────────────────────

class FavoriteOut(BaseModel):
    id: int
    news_item_id: int
    created_at: datetime
    news_item: Optional[NewsItemOut]

    class Config:
        from_attributes = True


# ── Broadcast ───────────────────────────────────────────

class BroadcastRequest(BaseModel):
    favorite_id: int
    platform: str  # email | linkedin | whatsapp | blog | newsletter
    recipient: Optional[str] = None  # email address for email broadcasts


class BroadcastResult(BaseModel):
    platform: str
    status: str
    message: str
    generated_content: Optional[str] = None


# ── Sources ─────────────────────────────────────────────

class SourceCreateRequest(BaseModel):
    name: str
    url: str
    feed_url: Optional[str] = None
    source_type: str = "rss"
    category: Optional[str] = None
