from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from typing import Optional

from database import get_db
from models import NewsItem, Favorite, Source
from schemas import NewsListResponse, NewsItemOut
from ingestion.scheduler import run_ingestion

router = APIRouter()


@router.get("", response_model=NewsListResponse)
async def list_news(
    page: int = Query(1, ge=1),
    page_size: int = Query(30, ge=5, le=100),
    source_id: Optional[int] = None,
    category: Optional[str] = None,
    q: Optional[str] = None,
    sort_by: str = Query("date", regex="^(date|impact|source)$"),
    include_duplicates: bool = False,
    db: AsyncSession = Depends(get_db),
):
    filters = []
    if not include_duplicates:
        filters.append(NewsItem.is_duplicate == False)
    if source_id:
        filters.append(NewsItem.source_id == source_id)
    if q:
        filters.append(
            NewsItem.title.ilike(f"%{q}%") | NewsItem.summary.ilike(f"%{q}%")
        )
    if category:
        filters.append(Source.category == category)

    order = {
        "date": NewsItem.published_at.desc(),
        "impact": NewsItem.impact_score.desc(),
        "source": Source.name.asc(),
    }.get(sort_by, NewsItem.published_at.desc())

    stmt = (
        select(NewsItem)
        .options(selectinload(NewsItem.source))
        .join(Source, isouter=True)
        .where(and_(*filters))
        .order_by(order)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    items = result.scalars().all()

    count_stmt = (
        select(func.count(NewsItem.id))
        .join(Source, isouter=True)
        .where(and_(*filters))
    )
    total = (await db.execute(count_stmt)).scalar_one()

    # Enrich with favorite status (user_id=1 for MVP)
    fav_ids = set()
    fav_result = await db.execute(
        select(Favorite.news_item_id).where(Favorite.user_id == None)
    )
    fav_ids = {r[0] for r in fav_result.all()}

    out = []
    for item in items:
        d = NewsItemOut.model_validate(item)
        d.is_favorited = item.id in fav_ids
        out.append(d)

    return NewsListResponse(items=out, total=total, page=page, page_size=page_size)


@router.post("/refresh")
async def refresh_news(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_ingestion)
    return {"message": "Ingestion started in the background."}


@router.get("/{item_id}", response_model=NewsItemOut)
async def get_news_item(item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(NewsItem)
        .options(selectinload(NewsItem.source))
        .where(NewsItem.id == item_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="News item not found")
    return NewsItemOut.model_validate(item)
