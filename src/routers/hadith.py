from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, Form, File, status
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, update
from ..database import get_db
from ..utils import hadith as crud_hadith
from ..utils.users import get_current_user, get_optional_user
from ..schemas.hadith import (
    HadithRead, HadithCreate, HadithUpdate,
    HadithCategoryRead, HadithCategoryCreate, HadithCategoryUpdate, HadithStats, HadithItem
)
from ..models.users import User
from ..models.hadith import Hadith, HadithCategory
import csv
import json
from io import StringIO
from datetime import date
import random

HadithSchema = HadithRead 
cache: Dict[str, Any] = {}

async def _cache_key(prefix: str, suffix: str) -> str:
    return f"{prefix}:{suffix}"

def _normalize_row(hadith_model: Hadith, view_count: int, favorite_count: int) -> HadithRead:
    setattr(hadith_model, 'view_count', view_count)
    setattr(hadith_model, 'favorite_count', favorite_count)
    return HadithRead.model_validate(hadith_model)

router = APIRouter(prefix="/api", tags=["Hadiths"])

@router.get("/hadiths", response_model=List[HadithRead])
async def list_hadiths(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Hadith).order_by(Hadith.category_id, Hadith.id))
    hadiths = result.scalars().all()

    hadith_ids = [h.id for h in hadiths]
    views_map = await crud_hadith.get_views_bulk(db, hadith_ids)
    favorites_map = await crud_hadith.get_favorites_bulk(db, hadith_ids)

    hadiths_with_counts = []
    for h in hadiths:
        setattr(h, 'view_count', views_map.get(h.id, 0))
        setattr(h, 'favorite_count', favorites_map.get(h.id, 0))
        hadiths_with_counts.append(HadithRead.model_validate(h))
        
    return hadiths_with_counts

@router.get("/hadiths/paginated", response_model=Dict[str, Any])
async def list_hadiths_paginated(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    sort_by: str = Query("id"),
    sort_order: str = Query("asc"),
    q: Optional[str] = None,
    category_id: Optional[int] = None,
    featured: Optional[bool] = None,
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    base_query = select(Hadith)
    if q:
        base_query = base_query.where(
            (Hadith.arabic.ilike(f"%{q}%")) |
            (Hadith.translation.ilike(f"%{q}%")) |
            (Hadith.book.ilike(f"%{q}%")) |
            (Hadith.narrator.ilike(f"%{q}%"))
        )
    if category_id:
        base_query = base_query.where(Hadith.category_id == category_id)
    if featured is not None:
        base_query = base_query.where(Hadith.featured == featured)

    total_count_query = select(func.count()).select_from(base_query.subquery())
    total_count_result = await db.execute(total_count_query)
    total_count = total_count_result.scalar_one()

    query = base_query
    sort_column = getattr(Hadith, sort_by, Hadith.id)
    if sort_order.lower() == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(sort_column)

    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    hadiths = result.scalars().all()

    hadith_ids = [h.id for h in hadiths]
    views_map = await crud_hadith.get_views_bulk(db, hadith_ids)
    favorites_map = await crud_hadith.get_favorites_bulk(db, hadith_ids)

    user_favorites_set = set()
    
    if current_user:
        user_uuid = current_user.id
        user_favorites_set = await crud_hadith.get_user_favorites_set(db, user_uuid, hadith_ids)
    
    hadiths_with_counts = []
    for h in hadiths:
        setattr(h, 'view_count', views_map.get(h.id, 0))
        setattr(h, 'favorite_count', favorites_map.get(h.id, 0))
        setattr(h, 'is_favorite', h.id in user_favorites_set)
        hadiths_with_counts.append(HadithRead.model_validate(h))

    return {
        "items": hadiths_with_counts,
        "total_count": total_count
    }

@router.post("/hadiths", response_model=HadithRead)
async def create_hadith_route(hadith_data: HadithCreate, db: AsyncSession = Depends(get_db)):
    return await crud_hadith.create_hadith(db, hadith_data.model_dump())

@router.get("/hadiths/stats", response_model=HadithStats)
async def get_hadiths_stats(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Hadith))
    all_hadiths = result.scalars().all() or []
    
    total_hadiths = len(all_hadiths)
    hadith_ids = [h.id for h in all_hadiths]

    views_map = await crud_hadith.get_views_bulk(db, hadith_ids)
    favorites_map = await crud_hadith.get_favorites_bulk(db, hadith_ids)

    for h in all_hadiths:
        setattr(h, 'view_count', views_map.get(h.id, 0))
        setattr(h, 'favorite_count', favorites_map.get(h.id, 0))

    total_views = sum(getattr(h, "view_count", 0) for h in all_hadiths)
    total_favorites = sum(getattr(h, "favorite_count", 0) for h in all_hadiths)
    
    featured_count_query = select(func.count()).select_from(Hadith).where(Hadith.featured == True)
    total_featured_result = await db.execute(featured_count_query)
    total_featured = total_featured_result.scalar_one_or_none() or 0
    
    featured_hadiths = [h for h in all_hadiths if getattr(h, "featured", False)]

    def safe_hadith_item(h):
        return HadithItem(
            id=getattr(h, "id", 0) or 0,
            number=getattr(h, "number", "No Number") or "No Number"
        )

    top_featured = sorted(featured_hadiths, key=lambda h: getattr(h, "view_count", 0), reverse=True)[:5]
    top_viewed = sorted(all_hadiths, key=lambda h: getattr(h, "view_count", 0), reverse=True)[:5]

    return HadithStats(
        total_hadiths=total_hadiths,
        total_views=total_views,
        total_favorites=total_favorites,
        total_featured=total_featured,
        top_featured=[safe_hadith_item(h) for h in top_featured] if top_featured else [],
        top_viewed=[safe_hadith_item(h) for h in top_viewed] if top_viewed else [],
    )

@router.delete("/hadiths/bulk")
async def delete_hadiths_bulk_route(
    hadith_ids: List[int], 
    db: AsyncSession = Depends(get_db)
):
    if not hadith_ids:
        raise HTTPException(status_code=400, detail="Please provide a list of Hadith IDs to delete.")
    
    deleted_count = await crud_hadith.delete_hadiths_bulk(db, hadith_ids)

    if deleted_count == 0 and len(hadith_ids) > 0:
        raise HTTPException(status_code=404, detail="No Hadiths found with the provided IDs.")
        
    return {"detail": f"{deleted_count} Hadiths deleted successfully."}

@router.post("/hadiths/bulk-data-upload")
async def bulk_data_upload_route(
    file: UploadFile = File(...),
    category_id: int = Form(None), 
    db: AsyncSession = Depends(get_db),
):
    hadiths_to_create = []
    try:
        content = await file.read()
        file_content = content.decode('utf-8')

        field_map = {
            "arabic": "arabic",
            "translation": "translation", 
            "narrator": "narrator",
            "book": "book",
            "number": "number",
            "status": "status",
            "rating": "rating",
            "category_id": "category_id"
        }

        if file.content_type == "text/csv":
            csv_reader = csv.DictReader(StringIO(file_content))
            for row in csv_reader:
                hadith_data = {}
                for csv_key, model_key in field_map.items():
                    value = row.get(csv_key)
                    if value is not None:
                        if model_key == "category_id":
                            hadith_data[model_key] = int(value or category_id) if value or category_id else None
                        elif model_key == "rating":
                            try:
                                hadith_data[model_key] = float(value)
                            except (ValueError, TypeError):
                                pass 
                        else:
                            hadith_data[model_key] = value
                
                if hadith_data.get("arabic"): 
                    hadiths_to_create.append(hadith_data)

        elif file.content_type == "application/json":
            data = json.loads(file_content)
            data_list = data if isinstance(data, list) else [data]
            
            for item in data_list:
                item["category_id"] = int(item.get("category_id") or category_id) if item.get("category_id") or category_id else None
                hadiths_to_create.append(item)
        
        inserted_ids = await crud_hadith.bulk_create_hadiths(db, hadiths_to_create)
        processed_count = len(inserted_ids)

        if processed_count == 0:
            raise HTTPException(
                status_code=422, detail="No valid Hadiths found in the uploaded file."
            )
        return {
            "detail": f"Successfully created {processed_count} Hadiths under category {category_id or 'auto-mapped'}",
            "filename": file.filename,
            "inserted_ids": inserted_ids, 
        }

    except HTTPException:
        raise
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file format.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing error: {e}")

@router.get("/hadiths/{hadith_id}", response_model=HadithRead)
async def get_hadith_route(hadith_id: int, db: AsyncSession = Depends(get_db)):
    update_stmt = (
        update(Hadith)
        .where(Hadith.id == hadith_id)
        .values(view_count=Hadith.view_count + 1)
    )
    await db.execute(update_stmt)
    await db.commit() 

    hadith_result = await db.execute(select(Hadith).where(Hadith.id == hadith_id))
    hadith = hadith_result.scalar_one_or_none()
    
    if not hadith:
        raise HTTPException(status_code=404, detail="Hadith not found")
    
    setattr(hadith, 'view_count', await crud_hadith.get_views_count(db, hadith.id))
    setattr(hadith, 'favorite_count', await crud_hadith.get_favorites_count(db, hadith.id))
    
    return HadithRead.model_validate(hadith)

@router.put("/hadiths/{hadith_id}", response_model=HadithRead)
@router.patch("/hadiths/{hadith_id}", response_model=HadithRead)
async def update_hadith_route(hadith_id: int, hadith_data: HadithUpdate, db: AsyncSession = Depends(get_db)):
    updated = await crud_hadith.update_hadith(db, hadith_id, hadith_data.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Hadith not found")
    return updated

@router.delete("/hadiths/{hadith_id}")
async def delete_hadith_route(hadith_id: int, db: AsyncSession = Depends(get_db)):
    success = await crud_hadith.delete_hadith(db, hadith_id)
    if not success:
        raise HTTPException(status_code=404, detail="Hadith not found")
    return {"detail": "Hadith deleted successfully"}

@router.get("/day", response_model=HadithSchema)
async def hadith_of_the_day(db: AsyncSession = Depends(get_db)):
    today_key = await _cache_key("hadith_of_the_day", date.today().isoformat())
    cached = cache.get(today_key)
    if cached:
        return cached
    
    total_result = await db.execute(select(func.count()).select_from(Hadith))
    total = total_result.scalar() or 0
    
    if total == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hadiths found")
    
    seed = int(date.today().strftime("%Y%m%d"))
    random.seed(seed)
    offset = random.randint(0, total - 1)
    
    result = await db.execute(select(Hadith).offset(offset).limit(1))
    r = result.scalar_one_or_none()
    
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hadith not found (Offset issue)")
    
    view_count = await crud_hadith.get_views_count(db, r.id)
    favorite_count = await crud_hadith.get_favorites_count(db, r.id)
    
    response = _normalize_row(r, view_count, favorite_count)
    
    cache[today_key] = response
    return response

@router.patch("/hadiths/{hadith_id}/featured")
async def toggle_featured_route(hadith_id: int, db: AsyncSession = Depends(get_db)):
    hadith = await crud_hadith.get_hadith(db, hadith_id)
    if not hadith:
        raise HTTPException(status_code=404, detail="Hadith not found")
    hadith.featured = not hadith.featured
    await db.commit()
    await db.refresh(hadith)
    return {"id": hadith_id, "featured": hadith.featured}

@router.patch("/hadiths/{hadith_id}/increment-view")
async def increment_view_route(hadith_id: int, db: AsyncSession = Depends(get_db)):
    success = await crud_hadith.increment_view(db, hadith_id)
    if not success:
        raise HTTPException(status_code=404, detail="Hadith not found")
    return {"id": hadith_id, "status": "view incremented"}

@router.patch("/hadiths/{hadith_id}/toggle-favorite")
async def toggle_favorite_route(
    hadith_id: int, 
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    user_uuid = current_user.id
    success = await crud_hadith.toggle_favorite(db, hadith_id, user_uuid)
    if not success:
        raise HTTPException(status_code=404, detail="Hadith not found")
    count = await crud_hadith.get_favorites_count(db, hadith_id)
    return {"id": hadith_id, "favorites": count}

@router.get("/hadith-categories", response_model=List[HadithCategoryRead])
async def list_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(HadithCategory).order_by(HadithCategory.id))
    return result.scalars().all()

@router.post("/hadith-categories", response_model=HadithCategoryRead)
async def create_category_route(category_data: HadithCategoryCreate, db: AsyncSession = Depends(get_db)):
    return await crud_hadith.create_category(db, category_data.model_dump())

@router.put("/hadith-categories/{category_id}", response_model=HadithCategoryRead)
@router.patch("/hadith-categories/{category_id}", response_model=HadithCategoryRead)
async def update_category_route(category_id: int, category_data: HadithCategoryUpdate, db: AsyncSession = Depends(get_db)):
    updated = await crud_hadith.update_category(db, category_id, category_data.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Category not found")
    return updated

@router.delete("/hadith-categories/{category_id}")
async def delete_category_route(category_id: int, db: AsyncSession = Depends(get_db)):
    category = await crud_hadith.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    if category.hadiths:
        pass
    
    success = await crud_hadith.delete_category(db, category_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete category.")

    return {"detail": "Category deleted successfully (associated Hadiths' category was set to null)."}