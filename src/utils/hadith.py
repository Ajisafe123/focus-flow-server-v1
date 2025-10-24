from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, func, String
from src.models.hadith import Hadith
from typing import List


async def get_hadith(db: AsyncSession, id: int):
    q = select(Hadith).where(Hadith.id == id)
    result = await db.execute(q)
    return result.scalar_one_or_none()

async def get_paginated_hadith(db: AsyncSession, limit: int = 10, offset: int = 0):
    q = select(Hadith).offset(offset).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()

async def search_hadith_text(db: AsyncSession, query: str, skip: int = 0, limit: int = 50) -> List[Hadith]:
    stmt = select(Hadith).where(
        or_(
            Hadith.arabic.ilike(f"%{query}%"),
            func.cast(Hadith.english['transliteration'], String).ilike(f"%{query}%"),
            func.cast(Hadith.english['translation'], String).ilike(f"%{query}%")
        )
    ).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_total_count(db: AsyncSession):
    q = select(func.count()).select_from(Hadith)
    result = await db.execute(q)
    return result.scalar_one()
