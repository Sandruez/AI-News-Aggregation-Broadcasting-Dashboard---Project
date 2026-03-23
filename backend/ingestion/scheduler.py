"""
Scheduler: runs the full ingestion pipeline on a configurable interval.
Orchestrates: fetch → deduplicate → AI summarise → score → persist.
"""

import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import select, func

from config import get_settings
from database import SessionLocal
from models import Source, NewsItem
from schemas import NewsItemCreate
from ingestion.sources_registry import ALL_SOURCES
from ingestion.fetcher import fetch_rss, fetch_hacker_news, fetch_arxiv
from ingestion.deduplicator import is_duplicate
from groq_service import groq_service

logger = logging.getLogger(__name__)
settings = get_settings()


async def seed_sources():
    """Ensure all sources from registry exist in DB."""
    db = SessionLocal()
    try:
        for sc in ALL_SOURCES:
            existing = db.execute(select(Source).where(Source.url == sc.url))
            if not existing.scalar_one_or_none():
                db.add(Source(
                    name=sc.name,
                    url=sc.url,
                    feed_url=sc.feed_url,
                    source_type=sc.source_type,
                    category=sc.category,
                    active=sc.active,
                ))
        db.commit()
    except Exception as e:
        logger.error(f"Error seeding sources: {e}")
        db.rollback()
    finally:
        db.close()


async def run_ingestion():
    logger.info("Starting ingestion run at %s", datetime.now(tz=timezone.utc).isoformat())
    await seed_sources()

    db = SessionLocal()
    try:
        sources_result = db.execute(select(Source).where(Source.active == True))
        sources = sources_result.scalars().all()

        # Load recent hashes and titles for dedup
        recent_items = db.execute(
            select(NewsItem.content_hash, NewsItem.title)
            .order_by(NewsItem.ingested_at.desc())
            .limit(500)
        )
        rows = recent_items.all()
        existing_hashes = {r[0] for r in rows if r[0]}
        existing_titles = [r[1] for r in rows if r[1]]

        new_count = 0
        for source in sources:
            try:
                if source.source_type == "hn":
                    items = await fetch_hacker_news(source.id)
                elif source.source_type == "arxiv":
                    cat = "cs.AI" if "AI" in source.name else "cs.LG"
                    items = await fetch_arxiv(source.id, cat)
                else:
                    items = await fetch_rss(
                        next(s for s in ALL_SOURCES if s.url == source.url),
                        source.id,
                        settings.max_items_per_source,
                    )

                for item in items:
                    # Check URL uniqueness first
                    url_exists = db.execute(
                        select(NewsItem).where(NewsItem.url == item.url)
                    )
                    if url_exists.scalar_one_or_none():
                        continue

                    dup, reason = await is_duplicate(
                        item.title, item.content_hash or "",
                        existing_hashes, existing_titles
                    )

                    ai_summary = ""
                    impact = 5
                    if not dup and item.summary:
                        try:
                            ai_summary = await groq_service.summarize(item.title, item.summary)
                            impact = await groq_service.score_impact(item.title, item.summary)
                        except Exception as e:
                            logger.warning("AI enrichment failed for %s: %s", item.title[:50], e)

                    news = NewsItem(
                        source_id=item.source_id,
                        title=item.title,
                        summary=item.summary,
                        ai_summary=ai_summary,
                        author=item.author,
                        url=item.url,
                        published_at=item.published_at,
                        tags=item.tags,
                        is_duplicate=dup,
                        content_hash=item.content_hash,
                        impact_score=impact,
                    )
                    db.add(news)
                    existing_hashes.add(item.content_hash or "")
                    existing_titles.insert(0, item.title)
                    existing_titles = existing_titles[:500]
                    new_count += 1

                db.commit()

            except Exception as exc:
                logger.error("Ingestion error for source %s: %s", source.name, exc)
                db.rollback()

    finally:
        db.close()
        
    logger.info("Ingestion complete. Added %d new items.", new_count)


async def start_scheduler():
    """Runs ingestion on startup and then every N minutes."""
    await run_ingestion()
    while True:
        await asyncio.sleep(settings.fetch_interval_minutes * 60)
        await run_ingestion()


async def stop_scheduler():
    pass  # Cancellation handled by asyncio task cancel
