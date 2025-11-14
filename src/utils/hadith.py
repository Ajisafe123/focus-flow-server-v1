from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func, delete, update
from sqlalchemy.orm import selectinload
from ..models.hadith import Hadith, HadithCategory, HadithFavorite, HadithView
from typing import List, Optional, Set
import uuid
from sqlalchemy.dialects.postgresql import insert

async def get_hadith(db: AsyncSession, hadith_id: int) -> Optional[Hadith]:
    result = await db.execute(
        select(Hadith)
        .options(
            selectinload(Hadith.category_rel), 
            selectinload(Hadith.favorites),
            selectinload(Hadith.views)
        )
        .where(Hadith.id == hadith_id)
    )
    return result.scalars().first()

async def create_hadith(db: AsyncSession, hadith_data: dict) -> Hadith:
    hadith = Hadith(**hadith_data)
    db.add(hadith)
    await db.commit()
    await db.refresh(hadith)
    return hadith

async def update_hadith(db: AsyncSession, hadith_id: int, hadith_data: dict) -> Optional[Hadith]:
    hadith = await get_hadith(db, hadith_id) 
    if not hadith:
        return None
    for key, value in hadith_data.items():
        setattr(hadith, key, value)
    await db.commit()
    await db.refresh(hadith)
    return hadith

async def delete_hadith(db: AsyncSession, hadith_id: int) -> bool:
    hadith = await get_hadith(db, hadith_id)
    if not hadith:
        return False
    await db.delete(hadith)
    await db.commit()
    return True

async def delete_hadiths_bulk(db: AsyncSession, hadith_ids: List[int]) -> int:
    if not hadith_ids:
        return 0
    
    stmt = delete(Hadith).where(Hadith.id.in_(hadith_ids))
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount

async def bulk_create_hadiths(db: AsyncSession, hadiths_data: List[dict]) -> List[int]:
    if not hadiths_data:
        return []
    stmt = insert(Hadith).values(hadiths_data).returning(Hadith.id)
    result = await db.execute(stmt)
    await db.commit()
    inserted_ids = [row[0] for row in result.all()]
    return inserted_ids

async def search_hadiths(db: AsyncSession, q: str, skip: int = 0, limit: int = 50) -> List[Hadith]:
    term = f"%{q}%"
    stmt = (
        select(Hadith)
        .options(
            selectinload(Hadith.category_rel), 
            selectinload(Hadith.favorites),
            selectinload(Hadith.views)
        )
        .where(
            or_(
                Hadith.arabic.ilike(term),
                Hadith.translation.ilike(term),
                Hadith.narrator.ilike(term),
                Hadith.book.ilike(term),
            )
        )
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def toggle_featured(db: AsyncSession, hadith_id: int) -> Optional[Hadith]:
    hadith = await get_hadith(db, hadith_id) 
    if not hadith:
        return None
    hadith.featured = not hadith.featured
    await db.commit()
    await db.refresh(hadith)
    return hadith

async def increment_view(db: AsyncSession, hadith_id: int) -> bool:
    view = HadithView(hadith_id=hadith_id)
    db.add(view)
    await db.commit()
    return True

async def get_views_count(db: AsyncSession, hadith_id: int) -> int:
    result = await db.execute(select(func.count(HadithView.id)).where(HadithView.hadith_id == hadith_id))
    return result.scalar() or 0

async def get_views_bulk(db: AsyncSession, hadith_ids: List[int]) -> dict:
    if not hadith_ids:
        return {}
    result = await db.execute(
        select(HadithView.hadith_id, func.count(HadithView.id))
        .where(HadithView.hadith_id.in_(hadith_ids))
        .group_by(HadithView.hadith_id)
    )
    rows = result.all() or []
    return {int(row[0]): int(row[1] or 0) for row in rows}

async def toggle_favorite(db: AsyncSession, hadith_id: int, user_id: uuid.UUID) -> bool:
    fav = await db.execute(
        select(HadithFavorite).where(
            HadithFavorite.hadith_id == hadith_id,
            HadithFavorite.user_id == user_id
        )
    )
    fav = fav.scalars().first()
    if fav:
        await db.delete(fav)
    else:
        db.add(HadithFavorite(hadith_id=hadith_id, user_id=user_id))
    await db.commit()
    return True

async def get_favorites_count(db: AsyncSession, hadith_id: int) -> int:
    result = await db.execute(select(func.count(HadithFavorite.id)).where(HadithFavorite.hadith_id == hadith_id))
    return result.scalar() or 0

async def get_favorites_bulk(db: AsyncSession, hadith_ids: List[int]) -> dict:
    if not hadith_ids:
        return {}
    result = await db.execute(
        select(HadithFavorite.hadith_id, func.count(HadithFavorite.id))
        .where(HadithFavorite.hadith_id.in_(hadith_ids))
        .group_by(HadithFavorite.hadith_id)
    )
    rows = result.all() or []
    return {int(row[0]): int(row[1] or 0) for row in rows}

async def get_user_favorites_set(db: AsyncSession, user_id: uuid.UUID, hadith_ids: List[int]) -> Set[int]:
    if not hadith_ids:
        return set()
    result = await db.execute(
        select(HadithFavorite.hadith_id)
        .where(
            HadithFavorite.user_id == user_id,
            HadithFavorite.hadith_id.in_(hadith_ids)
        )
    )
    return set(result.scalars().all())

async def get_category(db: AsyncSession, category_id: int) -> Optional[HadithCategory]:
    result = await db.execute(
        select(HadithCategory)
        .options(selectinload(HadithCategory.hadiths)) 
        .where(HadithCategory.id == category_id)
    )
    return result.scalars().first()

async def create_category(db: AsyncSession, category_data: dict) -> HadithCategory:
    category = HadithCategory(**category_data)
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category

async def update_category(db: AsyncSession, category_id: int, category_data: dict) -> Optional[HadithCategory]:
    category = await get_category(db, category_id)
    if not category:
        return None
    for key, value in category_data.items():
        setattr(category, key, value)
    await db.commit()
    await db.refresh(category)
    return category

async def delete_category(db: AsyncSession, category_id: int) -> bool:
    category = await get_category(db, category_id)
    if not category:
        return False
    
    if category.hadiths:
        pass
        
    await db.delete(category)
    await db.commit()
    return True