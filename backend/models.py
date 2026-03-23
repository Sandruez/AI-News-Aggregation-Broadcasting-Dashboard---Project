from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime,
    ForeignKey, JSON, func
)
from sqlalchemy.orm import relationship
from database import Base


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    url = Column(String(512), nullable=False)
    feed_url = Column(String(512))
    source_type = Column(String(50), default="rss")  # rss | api | scrape
    active = Column(Boolean, default=True)
    category = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    news_items = relationship("NewsItem", back_populates="source")


class NewsItem(Base):
    __tablename__ = "news_items"

    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=True)
    title = Column(Text, nullable=False)
    summary = Column(Text)
    ai_summary = Column(Text)
    author = Column(String(255))
    url = Column(String(512), unique=True, nullable=False)
    published_at = Column(DateTime(timezone=True))
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())
    tags = Column(JSON, default=list)
    is_duplicate = Column(Boolean, default=False)
    duplicate_of = Column(Integer, ForeignKey("news_items.id"), nullable=True)
    content_hash = Column(String(64))
    impact_score = Column(Integer, default=0)
    category = Column(String(100))
    image_url = Column(String(512))
    sentiment = Column(String(50))
    relevance_score = Column(func.float(), default=0.0)
    raw_content = Column(Text)
    guid = Column(String(512), unique=True)

    source = relationship("Source", back_populates="news_items")
    favorites = relationship("Favorite", back_populates="news_item")


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    news_item_id = Column(Integer, ForeignKey("news_items.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    news_item = relationship("NewsItem", back_populates="favorites")
    user = relationship("User", back_populates="favorites")
    broadcast_logs = relationship("BroadcastLog", back_populates="favorite")


class BroadcastLog(Base):
    __tablename__ = "broadcast_logs"

    id = Column(Integer, primary_key=True)
    favorite_id = Column(Integer, ForeignKey("favorites.id"), nullable=True)
    platform = Column(String(50))  # email | linkedin | whatsapp | blog | newsletter
    status = Column(String(50), default="pending")  # pending | sent | failed
    payload = Column(JSON)
    response = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    favorite = relationship("Favorite", back_populates="broadcast_logs")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    email = Column(String(255), unique=True)
    role = Column(String(50), default="viewer")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    favorites = relationship("Favorite", back_populates="user")
