import string
import random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func, delete, update, desc
from sqlalchemy.orm import selectinload
from ..models.dua import Dua, DuaCategory, DuaFavorite, DuaView, DuaShareLink
from typing import List, Optional, Set, Tuple
import uuid
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError


def generate_short_code(length: int = 8) -> str:
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


async def create_share_link(db: AsyncSession, dua_id: int, short_code: str) -> DuaShareLink:
    MAX_RETRIES = 5
    current_short_code = short_code
    
    for attempt in range(MAX_RETRIES):
        try:
            # FIX: A new DuaShareLink object is created for every attempt.
            new_link = DuaShareLink(dua_id=dua_id, short_code=current_short_code)
            db.add(new_link)
            await db.commit()
            await db.refresh(new_link)
            return new_link
        
        except IntegrityError:
            await db.rollback()
            # Generate a new code for the next iteration
            current_short_code = generate_short_code() 
            continue
            
    raise Exception("Failed to generate a unique short code after 5 attempts.")


async def get_dua_id_by_short_code(db: AsyncSession, short_code: str) -> Optional[int]:
    result = await db.execute(
        select(DuaShareLink.dua_id)
        .filter(DuaShareLink.short_code == short_code)
    )
    return result.scalar_one_or_none()


async def get_dua(db: AsyncSession, dua_id: int) -> Optional[Dua]:
    result = await db.execute(
        select(Dua)
        .options(
            selectinload(Dua.category_rel), 
            selectinload(Dua.favorites),
            selectinload(Dua.views)
        )
        .where(Dua.id == dua_id)
    )
    return result.scalars().first()


async def get_all_duas(db: AsyncSession) -> List[Dua]:
    result = await db.execute(select(Dua))
    return result.scalars().all() or []


async def get_duas_by_category_id(db: AsyncSession, category_id: int) -> List[Dua]:
    result = await db.execute(
        select(Dua)
        .where(Dua.category_id == category_id)
        .order_by(Dua.id)
    )
    return result.scalars().all() or []


async def get_all_duas_with_counts(db: AsyncSession) -> Tuple[List[Dua], dict, dict]:
    result = await db.execute(select(Dua).order_by(Dua.category_id, Dua.id))
    duas = result.scalars().all() or []
    dua_ids = [dua.id for dua in duas]
    views_map = await get_views_bulk(db, dua_ids)
    favorites_map = await get_favorites_bulk(db, dua_ids)
    return duas, views_map, favorites_map


async def get_paginated_duas(
    db: AsyncSession, 
    page: int, 
    limit: int, 
    sort_by: str, 
    sort_order: str, 
    q: Optional[str], 
    category_id: Optional[int], 
    featured: Optional[bool]
) -> Tuple[List[Dua], List[int]]:
    query = select(Dua)
    if q:
        query = query.where(Dua.title.ilike(f"%{q}%"))
    if category_id:
        query = query.where(Dua.category_id == category_id)
    if featured is not None:
        query = query.where(Dua.featured == featured)

    sort_column = getattr(Dua, sort_by, Dua.id)
    if sort_order.lower() == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(sort_column)

    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    duas = result.scalars().all()
    dua_ids = [dua.id for dua in duas]
    return duas, dua_ids


async def create_dua(db: AsyncSession, dua_data: dict) -> Dua:
    dua = Dua(**dua_data)
    db.add(dua)
    await db.commit()
    await db.refresh(dua)
    return dua


async def update_dua(db: AsyncSession, dua_id: int, dua_data: dict) -> Optional[Dua]:
    dua = await get_dua(db, dua_id) 
    if not dua:
        return None
    for key, value in dua_data.items():
        setattr(dua, key, value)
    await db.commit()
    await db.refresh(dua)
    return dua


async def delete_dua(db: AsyncSession, dua_id: int) -> bool:
    dua = await get_dua(db, dua_id)
    if not dua:
        return False
    await db.delete(dua)
    await db.commit()
    return True


async def delete_duas_bulk(db: AsyncSession, dua_ids: List[int]) -> int:
    if not dua_ids:
        return 0
    
    stmt = delete(Dua).where(Dua.id.in_(dua_ids))
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount


async def bulk_create_duas(db: AsyncSession, duas_data: List[dict]) -> List[int]:
    if not duas_data:
        return []
    stmt = insert(Dua).values(duas_data).returning(Dua.id)
    result = await db.execute(stmt)
    await db.commit()
    inserted_ids = [row[0] for row in result.all()]
    return inserted_ids


async def search_duas(db: AsyncSession, q: str, skip: int = 0, limit: int = 50) -> List[Dua]:
    term = f"%{q}%"
    stmt = (
        select(Dua)
        .options(
            selectinload(Dua.category_rel), 
            selectinload(Dua.favorites),
            selectinload(Dua.views)
        )
        .where(
            or_(
                Dua.title.ilike(term),
                Dua.arabic.ilike(term),
                Dua.transliteration.ilike(term),
                Dua.translation.ilike(term),
            )
        )
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def toggle_featured(db: AsyncSession, dua_id: int) -> Optional[Dua]:
    dua = await get_dua(db, dua_id) 
    if not dua:
        return None
    dua.featured = not dua.featured
    await db.commit()
    await db.refresh(dua)
    return dua


async def update_dua_audio_path_by_category(
    db: AsyncSession, 
    category_id: int, 
    audio_url: str
) -> int:
    stmt = update(Dua).where(
        Dua.category_id == category_id
    ).values(audio_path=audio_url)

    result = await db.execute(stmt)
    await db.commit()

    return result.rowcount


async def update_dua_audio_path(
    db: AsyncSession, 
    dua_identifier: str, 
    category_id: int, 
    audio_url: str
) -> bool:
    
    dua_id = None
    try:
        dua_id = int(dua_identifier)
    except ValueError:
        pass

    if dua_id is not None:
        stmt = update(Dua).where(
            Dua.id == dua_id,
            Dua.category_id == category_id
        ).values(audio_path=audio_url)
    else:
        stmt = update(Dua).where(
            Dua.title.ilike(dua_identifier),
            Dua.category_id == category_id
        ).values(audio_path=audio_url)

    result = await db.execute(stmt)
    await db.commit()

    return result.rowcount > 0


async def increment_view(db: AsyncSession, dua_id: int) -> bool:
    view = DuaView(dua_id=dua_id)
    db.add(view)
    await db.commit()
    return True


async def get_views_count(db: AsyncSession, dua_id: int) -> int:
    result = await db.execute(select(func.count(DuaView.id)).where(DuaView.dua_id == dua_id))
    return result.scalar() or 0


async def get_views_bulk(db: AsyncSession, dua_ids: List[int]) -> dict:
    if not dua_ids:
        return {}
    result = await db.execute(
        select(DuaView.dua_id, func.count(DuaView.id))
        .where(DuaView.dua_id.in_(dua_ids))
        .group_by(DuaView.dua_id)
    )
    rows = result.all() or []
    return {int(row[0]): int(row[1] or 0) for row in rows}


async def toggle_favorite(db: AsyncSession, dua_id: int, user_id: uuid.UUID) -> bool:
    fav = await db.execute(
        select(DuaFavorite).where(
            DuaFavorite.dua_id == dua_id,
            DuaFavorite.user_id == user_id
        )
    )
    fav = fav.scalars().first()
    if fav:
        await db.delete(fav)
    else:
        db.add(DuaFavorite(dua_id=dua_id, user_id=user_id))
    await db.commit()
    return True


async def get_favorites_count(db: AsyncSession, dua_id: int) -> int:
    result = await db.execute(select(func.count(DuaFavorite.id)).where(DuaFavorite.dua_id == dua_id))
    return result.scalar() or 0


async def get_favorites_bulk(db: AsyncSession, dua_ids: List[int]) -> dict:
    if not dua_ids:
        return {}
    result = await db.execute(
        select(DuaFavorite.dua_id, func.count(DuaFavorite.id))
        .where(DuaFavorite.dua_id.in_(dua_ids))
        .group_by(DuaFavorite.dua_id)
    )
    rows = result.all() or []
    return {int(row[0]): int(row[1] or 0) for row in rows}


async def get_user_favorites_set(db: AsyncSession, user_id: uuid.UUID, dua_ids: List[int]) -> Set[int]:
    if not dua_ids:
        return set()
    result = await db.execute(
        select(DuaFavorite.dua_id)
        .where(
            DuaFavorite.user_id == user_id,
            DuaFavorite.dua_id.in_(dua_ids)
        )
    )
    return set(result.scalars().all())


async def get_all_categories(db: AsyncSession) -> List[DuaCategory]:
    result = await db.execute(select(DuaCategory).order_by(DuaCategory.id))
    return result.scalars().all()


async def get_category(db: AsyncSession, category_id: int) -> Optional[DuaCategory]:
    result = await db.execute(
        select(DuaCategory)
        .options(selectinload(DuaCategory.duas)) 
        .where(DuaCategory.id == category_id)
    )
    return result.scalars().first()


async def create_category(db: AsyncSession, category_data: dict) -> DuaCategory:
    category = DuaCategory(**category_data)
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def update_category(db: AsyncSession, category_id: int, category_data: dict) -> Optional[DuaCategory]:
    category = await get_category(db, category_id)
    if not category:
        return None
    for key, value in category_data.items():
        setattr(category, key, value)
    await db.commit()
    await db.refresh(category)
    return category


async def update_category_image_url(
    db: AsyncSession, 
    category_id: int, 
    image_url: str
) -> Optional[DuaCategory]:
    
    category = await get_category(db, category_id)
    if not category:
        return None
        
    category.image_url = image_url
    await db.commit()
    await db.refresh(category)
    return category


async def delete_category(db: AsyncSession, category_id: int) -> bool:
    category = await get_category(db, category_id)
    if not category:
        return False
    
    await db.delete(category)
    await db.commit()
    return True