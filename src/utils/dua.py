from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from ..models.dua import Dua
from typing import List, Optional

async def get_dua(db: AsyncSession, dua_id: int) -> Optional[Dua]:
    result = await db.execute(select(Dua).where(Dua.id == dua_id))
    return result.scalars().first()

async def list_duas(db: AsyncSession, skip: int = 0, limit: int = 50) -> List[Dua]:
    result = await db.execute(
        select(Dua).where(Dua.is_active == True).offset(skip).limit(limit)
    )
    return result.scalars().all()

async def search_duas(db: AsyncSession, q: str, skip: int = 0, limit: int = 50) -> List[Dua]:
    term = f"%{q}%"
    stmt = select(Dua).where(
        or_(
            Dua.title.ilike(term),
            Dua.arabic.ilike(term),
            Dua.transliteration.ilike(term),
            Dua.translation.ilike(term)
        )
    ).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()
