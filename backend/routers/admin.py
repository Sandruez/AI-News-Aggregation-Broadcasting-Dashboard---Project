"""
Admin router for analytics and system monitoring.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc, case
from datetime import datetime, timedelta
from typing import Optional

from database import get_db
from models import NewsItem, Favorite, BroadcastLog, Source

router = APIRouter()


@router.get("/overview")
async def get_admin_overview(db: AsyncSession = Depends(get_db)):
    """Get system overview statistics."""
    now = datetime.utcnow()
    
    # Total counts
    total_news = await db.scalar(select(func.count(NewsItem.id)))
    total_favorites = await db.scalar(select(func.count(Favorite.id)))
    total_broadcasts = await db.scalar(select(func.count(BroadcastLog.id)))
    active_sources = await db.scalar(select(func.count(Source.id)).where(Source.active == True))
    
    # Recent activity (last 24 hours)
    yesterday = now - timedelta(days=1)
    recent_news = await db.scalar(
        select(func.count(NewsItem.id))
        .where(NewsItem.ingested_at >= yesterday)
    )
    
    return {
        "totalNews": total_news or 0,
        "totalFavorites": total_favorites or 0,
        "totalBroadcasts": total_broadcasts or 0,
        "activeSources": active_sources or 0,
        "recentNews": recent_news or 0,
        "uptime": "99.8%"  # Mock - would calculate from actual uptime
    }


@router.get("/news-trend")
async def get_news_trend(
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db)
):
    """Get news ingestion trend over time."""
    now = datetime.utcnow()
    trend_data = []
    
    for i in range(days):
        date = now - timedelta(days=i)
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        # Count articles and duplicates for this day
        total_articles = await db.scalar(
            select(func.count(NewsItem.id)).where(
                and_(NewsItem.ingested_at >= start_of_day, NewsItem.ingested_at < end_of_day)
            )
        )
        
        duplicate_articles = await db.scalar(
            select(func.count(NewsItem.id)).where(
                and_(
                    NewsItem.ingested_at >= start_of_day,
                    NewsItem.ingested_at < end_of_day,
                    NewsItem.is_duplicate == True
                )
            )
        )
        
        trend_data.append({
            "date": date.strftime("%a") if days <= 7 else date.strftime("%m/%d"),
            "articles": total_articles or 0,
            "duplicates": duplicate_articles or 0
        })
    
    return list(reversed(trend_data))


@router.get("/source-distribution")
async def get_source_distribution(db: AsyncSession = Depends(get_db)):
    """Get distribution of articles by source."""
    result = await db.execute(
        select(
            Source.name,
            func.count(NewsItem.id).label('count')
        )
        .join(NewsItem, Source.id == NewsItem.source_id)
        .group_by(Source.id, Source.name)
        .order_by(desc(func.count(NewsItem.id)))
        .limit(10)
    )
    
    sources = []
    for row in result:
        sources.append({
            "name": row.name,
            "value": row.count
        })
    
    return sources


@router.get("/category-breakdown")
async def get_category_breakdown(db: AsyncSession = Depends(get_db)):
    """Get category performance statistics."""
    result = await db.execute(
        select(
            Source.category,
            func.count(NewsItem.id).label('count'),
            func.avg(NewsItem.impact_score).label('avg_impact')
        )
        .join(NewsItem, Source.id == NewsItem.source_id)
        .where(NewsItem.is_duplicate == False)
        .group_by(Source.category)
        .order_by(desc(func.count(NewsItem.id)))
    )
    
    categories = []
    for row in result:
        categories.append({
            "category": row.category,
            "count": row.count,
            "impact": round(float(row.avg_impact), 1) if row.avg_impact else 0
        })
    
    return categories


@router.get("/broadcast-analytics")
async def get_broadcast_analytics(db: AsyncSession = Depends(get_db)):
    """Get broadcast platform analytics."""
    result = await db.execute(
        select(
            BroadcastLog.platform,
            func.count(BroadcastLog.id).label('sent'),
            func.sum(case((BroadcastLog.status == 'sent', 1), else_=0)).label('success'),
            func.sum(case((BroadcastLog.status == 'failed', 1), else_=0)).label('failed')
        )
        .group_by(BroadcastLog.platform)
        .order_by(desc(func.count(BroadcastLog.id)))
    )
    
    platforms = []
    for row in result:
        platforms.append({
            "platform": row.platform,
            "sent": row.sent,
            "success": row.success or 0,
            "failed": row.failed or 0
        })
    
    return platforms


@router.get("/system-health")
async def get_system_health():
    """Get system health metrics."""
    # Mock data - in production, these would be real metrics
    return {
        "database": {
            "status": "healthy",
            "responseTime": "45ms",
            "connections": 12
        },
        "api": {
            "status": "healthy", 
            "responseTime": "120ms",
            "requests": 1234
        },
        "ingestion": {
            "status": "running",
            "lastRun": "2 min ago",
            "errors": 0
        },
        "ai": {
            "status": "healthy",
            "responseTime": "230ms", 
            "tokens": 45678
        }
    }


@router.get("/recent-activity")
async def get_recent_activity(db: AsyncSession = Depends(get_db)):
    """Get recent system activity."""
    activities = []
    
    # Get recent news items
    recent_news = await db.execute(
        select(NewsItem)
        .order_by(desc(NewsItem.ingested_at))
        .limit(5)
    )
    
    for item in recent_news.scalars():
        activities.append({
            "type": "news",
            "message": f"New article: {item.title[:50]}...",
            "time": format_time_ago(item.ingested_at),
            "status": "success"
        })
    
    # Get recent broadcasts
    recent_broadcasts = await db.execute(
        select(BroadcastLog)
        .order_by(desc(BroadcastLog.timestamp))
        .limit(3)
    )
    
    for broadcast in recent_broadcasts.scalars():
        activities.append({
            "type": "broadcast",
            "message": f"{broadcast.platform.capitalize()} broadcast {broadcast.status}",
            "time": format_time_ago(broadcast.timestamp),
            "status": broadcast.status
        })
    
    # Add some system activities
    activities.extend([
        {
            "type": "system",
            "message": "Database backup completed",
            "time": "1 hour ago",
            "status": "success"
        },
        {
            "type": "warning", 
            "message": "High memory usage detected",
            "time": "2 hours ago",
            "status": "warning"
        }
    ])
    
    # Sort by time and return latest
    activities.sort(key=lambda x: x["time"])
    return activities[:10]


def format_time_ago(dt: datetime) -> str:
    """Format datetime as 'X time ago'."""
    from datetime import timezone
    
    # Ensure both datetimes have the same timezone
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    
    now = datetime.now(timezone.utc)
    diff = now - dt
    
    if diff < timedelta(minutes=1):
        return "just now"
    elif diff < timedelta(hours=1):
        minutes = int(diff.total_seconds() / 60)
        return f"{minutes} min ago"
    elif diff < timedelta(days=1):
        hours = int(diff.total_seconds() / 3600)
        return f"{hours} hour ago"
    else:
        days = diff.days
        return f"{days} day ago"
