from sqlalchemy import select, update, insert
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.dhikr_count import DhikrCount
from datetime import date
async def get_or_create_count(session: AsyncSession, user_id: str):
    query = select(DhikrCount).where(DhikrCount.user_id == user_id)
    result = await session.execute(query)
    count = result.scalar_one_or_none()
    if not count:
        stmt = insert(DhikrCount).values(user_id=user_id, count=0, last_reset=date.today())
        await session.execute(stmt)
        await session.commit()
        result = await session.execute(query)
        count = result.scalar_one_or_none()
    return count
async def increment_dhikr(session: AsyncSession, user_id: str):
    count = await get_or_create_count(session, user_id)
    await session.execute(update(DhikrCount).where(DhikrCount.id == count.id).values(count=DhikrCount.count + 1))
    await session.commit()
    return await get_or_create_count(session, user_id)
async def reset_dhikr(session: AsyncSession, user_id: str):
    count = await get_or_create_count(session, user_id)
    await session.execute(update(DhikrCount).where(DhikrCount.id == count.id).values(count=0, last_reset=date.today()))
    await session.commit()
    return await get_or_create_count(session, user_id)