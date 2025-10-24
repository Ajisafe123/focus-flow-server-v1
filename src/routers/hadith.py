from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from typing import List
from aiocache import SimpleMemoryCache
from datetime import date
import random, json

from ..database import get_db
from src.utils import hadith
from src.schemas.hadith import HadithSchema

cache = SimpleMemoryCache()
router = APIRouter(prefix="/hadiths", tags=["Hadith"])

def _cache_key(*parts) -> str:
    return ":".join(str(p) for p in parts)

def _parse_english(raw):
    if not raw:
        return {"translation": ""}
    if isinstance(raw, dict):
        return raw
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            return data
        elif isinstance(data, str):
            return {"translation": data}
    except json.JSONDecodeError:
        return {"translation": str(raw)}
    return {"translation": str(raw)}

def _normalize_row(r):
    english = _parse_english(r.english)
    translation = english.get("translation") or english.get("text") or ""
    return {
        "id": r.id,
        "book": getattr(r, "book", "") or "",
        "hadith_number": getattr(r, "id_in_book", 0),
        "narrator": getattr(r, "narrator", ""),
        "arabic": r.arabic,
        "english": {"translation": translation},
        "category": getattr(r, "category", "") or "",
        "source": getattr(r, "source", "") or "",
        "book_id": getattr(r, "book_id", None),
        "chapter_id": getattr(r, "chapter_id", None),
        "id_in_book": getattr(r, "id_in_book", None)
    }

@router.get("/", response_model=List[HadithSchema])
async def list_hadiths(page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=200), db: AsyncSession = Depends(get_db)):
    offset = (page - 1) * limit
    key = _cache_key("list", page, limit)
    cached = await cache.get(key)
    if cached:
        return cached
    rows = await hadith.get_paginated_hadith(db, limit=limit, offset=offset)
    result = [_normalize_row(r) for r in rows if r.arabic and r.arabic.strip() not in ["id", "metadata", "chapters", "hadiths"]]
    await cache.set(key, result, ttl=600)
    return result

@router.get("/search", response_model=List[HadithSchema])
async def search_hadiths(q: str = Query(..., min_length=1), page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=200), db: AsyncSession = Depends(get_db)):
    offset = (page - 1) * limit
    key = _cache_key("search", q, page, limit)
    cached = await cache.get(key)
    if cached:
        return cached
    rows = await hadith.search_hadith_text(db, query=q, skip=offset, limit=limit)
    result = [_normalize_row(r) for r in rows if r.arabic and r.arabic.strip() not in ["id", "metadata", "chapters", "hadiths"]]
    await cache.set(key, result, ttl=600)
    return result

@router.get("/day", response_model=HadithSchema)
async def hadith_of_the_day(db: AsyncSession = Depends(get_db)):
    today_key = _cache_key("hadith_of_the_day", date.today().isoformat())
    cached = await cache.get(today_key)
    if cached:
        return cached
    total_result = await db.execute(select(func.count()).select_from(hadith.Hadith))
    total = total_result.scalar() or 0
    if total == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hadiths found")
    seed = int(date.today().strftime("%Y%m%d"))
    random.seed(seed)
    offset = random.randint(0, total - 1)
    result = await db.execute(select(hadith.Hadith).offset(offset).limit(1))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hadith not found")
    response = _normalize_row(r)
    await cache.set(today_key, response, ttl=86400)
    return response
