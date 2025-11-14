from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.allah_names import AllahName
import random
from sqlalchemy.orm import selectinload

async def get_all_names(session: AsyncSession):
    query = select(AllahName)
    result = await session.execute(query)
    return result.scalars().all()

async def get_name_by_id(session: AsyncSession, name_id: int):
    query = select(AllahName).where(AllahName.id == name_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()
async def get_random_name(session: AsyncSession):
    query = select(AllahName)
    result = await session.execute(query)
    names = result.scalars().all()
    return random.choice(names) if names else None
async def search_names(db: AsyncSession, query: str):
    stmt = (
        select(AllahName)
        .where(
            (AllahName.arabic.ilike(f"%{query}%")) |
            (AllahName.transliteration.ilike(f"%{query}%")) |
            (AllahName.meaning.ilike(f"%{query}%"))
        )
        .options(selectinload("*"))
    )
    result = await db.execute(stmt)
    return result.scalars().all()