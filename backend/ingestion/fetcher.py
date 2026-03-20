"""
RSS and feed fetcher — parses feeds and normalises items into
a common NewsItemCreate schema ready for database insertion.
"""

import hashlib
import logging
from datetime import datetime, timezone
from typing import Optional

import feedparser
import httpx

from ingestion.sources_registry import SourceConfig
from schemas import NewsItemCreate

logger = logging.getLogger(__name__)


def _hash(text: str) -> str:
    return hashlib.sha256(text.lower().strip().encode()).hexdigest()


def _parse_date(entry) -> Optional[datetime]:
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        except Exception:
            pass
    return datetime.now(tz=timezone.utc)


async def fetch_rss(source: SourceConfig, source_id: int, max_items: int = 50) -> list[NewsItemCreate]:
    if not source.feed_url:
        return []

    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.get(source.feed_url, headers={"User-Agent": "AINewsDashboard/1.0"})
            resp.raise_for_status()
            feed = feedparser.parse(resp.text)
    except Exception as exc:
        logger.warning("Failed to fetch %s: %s", source.feed_url, exc)
        return []

    items: list[NewsItemCreate] = []
    for entry in feed.entries[:max_items]:
        title = getattr(entry, "title", "").strip()
        url = getattr(entry, "link", "").strip()
        if not title or not url:
            continue

        summary = getattr(entry, "summary", "") or getattr(entry, "description", "") or ""
        # Strip HTML tags crudely for summary
        import re
        summary = re.sub(r"<[^>]+>", " ", summary).strip()[:1000]

        author = getattr(entry, "author", "") or ""
        tags = [t.get("term", "") for t in getattr(entry, "tags", []) if t.get("term")]

        items.append(NewsItemCreate(
            source_id=source_id,
            title=title,
            summary=summary,
            url=url,
            author=author,
            published_at=_parse_date(entry),
            tags=tags,
            content_hash=_hash(title + url),
        ))

    return items


async def fetch_hacker_news(source_id: int, max_items: int = 30) -> list[NewsItemCreate]:
    """Fetch top HN stories matching AI keywords."""
    ai_keywords = {"ai", "llm", "gpt", "machine learning", "neural", "openai", "anthropic", "gemini", "mistral"}
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            top_ids_resp = await client.get("https://hacker-news.firebaseio.com/v0/topstories.json")
            top_ids = top_ids_resp.json()[:100]

            items: list[NewsItemCreate] = []
            for story_id in top_ids:
                if len(items) >= max_items:
                    break
                story_resp = await client.get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json")
                story = story_resp.json()
                if not story or story.get("type") != "story":
                    continue
                title = (story.get("title") or "").lower()
                if not any(kw in title for kw in ai_keywords):
                    continue
                url = story.get("url") or f"https://news.ycombinator.com/item?id={story_id}"
                items.append(NewsItemCreate(
                    source_id=source_id,
                    title=story.get("title", ""),
                    summary="",
                    url=url,
                    author=story.get("by", ""),
                    published_at=datetime.fromtimestamp(story.get("time", 0), tz=timezone.utc),
                    tags=["hacker-news"],
                    content_hash=_hash(story.get("title", "") + url),
                ))
            return items
    except Exception as exc:
        logger.warning("HN fetch failed: %s", exc)
        return []


async def fetch_arxiv(source_id: int, category: str = "cs.AI", max_items: int = 20) -> list[NewsItemCreate]:
    """Fetch latest arXiv papers for a given category."""
    feed_url = f"http://export.arxiv.org/rss/{category}"
    mock_source = type("S", (), {"feed_url": feed_url, "name": f"arXiv {category}"})()
    from ingestion.sources_registry import SourceConfig
    sc = SourceConfig(f"arXiv {category}", feed_url, feed_url, "rss", "research")
    return await fetch_rss(sc, source_id, max_items)
