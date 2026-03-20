from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models import Source
from schemas import SourceOut, SourceCreateRequest

router = APIRouter()


@router.get("", response_model=list[SourceOut])
async def list_sources(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Source).order_by(Source.name))
    return result.scalars().all()


@router.post("", response_model=SourceOut)
async def add_source(req: SourceCreateRequest, db: AsyncSession = Depends(get_db)):
    source = Source(**req.model_dump())
    db.add(source)
    await db.commit()
    await db.refresh(source)
    return source


@router.patch("/{source_id}/toggle")
async def toggle_source(source_id: int, db: AsyncSession = Depends(get_db)):
    source = await db.get(Source, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    source.active = not source.active
    await db.commit()
    return {"id": source.id, "active": source.active}
