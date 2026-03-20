from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from database import get_db
from models import Favorite, NewsItem, Source
from schemas import FavoriteOut, NewsItemOut

router = APIRouter()


@router.get("", response_model=list[FavoriteOut])
async def list_favorites(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Favorite)
        .options(
            selectinload(Favorite.news_item).selectinload(NewsItem.source)
        )
        .order_by(Favorite.created_at.desc())
    )
    favs = result.scalars().all()
    out = []
    for f in favs:
        fav_out = FavoriteOut.model_validate(f)
        if f.news_item:
            fav_out.news_item = NewsItemOut.model_validate(f.news_item)
        out.append(fav_out)
    return out


@router.post("/{news_item_id}", response_model=FavoriteOut)
async def add_favorite(news_item_id: int, db: AsyncSession = Depends(get_db)):
    # Check item exists
    item = await db.get(NewsItem, news_item_id)
    if not item:
        raise HTTPException(status_code=404, detail="News item not found")

    # Check not already favorited
    existing = await db.execute(
        select(Favorite).where(
            Favorite.news_item_id == news_item_id,
            Favorite.user_id == None
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Already in favorites")

    fav = Favorite(news_item_id=news_item_id, user_id=None)
    db.add(fav)
    await db.commit()
    await db.refresh(fav)
    return FavoriteOut.model_validate(fav)


@router.delete("/{news_item_id}")
async def remove_favorite(news_item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Favorite).where(
            Favorite.news_item_id == news_item_id,
            Favorite.user_id == None
        )
    )
    fav = result.scalar_one_or_none()
    if not fav:
        raise HTTPException(status_code=404, detail="Not in favorites")
    await db.delete(fav)
    await db.commit()
    return {"message": "Removed from favorites"}
