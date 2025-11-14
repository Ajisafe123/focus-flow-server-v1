from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, Form, File, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, field_validator
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from ..database import get_db
from ..utils import dua as crud_dua
from ..utils.users import get_current_user, get_optional_user
from ..schemas.dua import (
    DuaRead, DuaCreate, DuaUpdate,
    CategoryRead, CategoryCreate, CategoryUpdate, DuaStats, DuaItem, DuaReadSegmented
)
from ..models.users import User
import os
import shutil
import csv
import json
from io import StringIO
import uuid
import os.path as op

CURRENT_DIR = op.dirname(op.abspath(__file__))
SRC_DIR = op.join(CURRENT_DIR, op.pardir)
STATIC_DIR = op.join(SRC_DIR, "static")
AUDIO_DIR = op.join(STATIC_DIR, "audio")
CATEGORY_IMAGE_DIR = op.join(STATIC_DIR, "category_images")
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(CATEGORY_IMAGE_DIR, exist_ok=True)

router = APIRouter(prefix="/api", tags=["Duas"])

class ShareLinkResponse(BaseModel):
    share_url: str

SHARE_BASE_URL = "https://focus-flow-server-v1.onrender.com/api/s/" 
FRONTEND_BASE_URL = "https://nibra-al-deen-v1.vercel.app" 

@router.post("/duas/{dua_id}/share-link", response_model=ShareLinkResponse)
async def generate_dua_share_link(dua_id: int, db: AsyncSession = Depends(get_db)):
    dua = await crud_dua.get_dua(db, dua_id)
    if not dua:
        raise HTTPException(status_code=404, detail="Dua not found")

    short_code = crud_dua.generate_short_code()
    share_link_obj = await crud_dua.create_share_link(db, dua_id, short_code)

    full_share_url = f"{SHARE_BASE_URL}{share_link_obj.short_code}"
    
    return {"share_url": full_share_url}

@router.get("/s/{short_code}")
async def redirect_to_dua_page(short_code: str, db: AsyncSession = Depends(get_db)):
    dua_id = await crud_dua.get_dua_id_by_short_code(db, short_code)
    
    if dua_id is None:
        return RedirectResponse(url=FRONTEND_BASE_URL, status_code=307)
    
    target_url = f"{FRONTEND_BASE_URL}/?duaId={dua_id}"
    
    return RedirectResponse(url=target_url, status_code=307)


@router.get("/duas", response_model=List[DuaRead])
async def list_duas(db: AsyncSession = Depends(get_db)):
    duas, views_map, favorites_map = await crud_dua.get_all_duas_with_counts(db)

    duas_with_counts = []
    for dua in duas:
        setattr(dua, 'view_count', views_map.get(dua.id, 0))
        setattr(dua, 'favorite_count', favorites_map.get(dua.id, 0))
        duas_with_counts.append(DuaRead.model_validate(dua))
        
    return duas_with_counts

@router.get("/duas/paginated", response_model=List[DuaRead])
async def list_duas_paginated(
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
    duas, dua_ids = await crud_dua.get_paginated_duas(db, page, limit, sort_by, sort_order, q, category_id, featured)

    views_map = await crud_dua.get_views_bulk(db, dua_ids)
    favorites_map = await crud_dua.get_favorites_bulk(db, dua_ids)

    user_favorites_set = set()
    if current_user:
        user_uuid = current_user.id
        user_favorites_set = await crud_dua.get_user_favorites_set(db, user_uuid, dua_ids)
    
    duas_with_counts = []
    for dua in duas:
        setattr(dua, 'view_count', views_map.get(dua.id, 0))
        setattr(dua, 'favorite_count', favorites_map.get(dua.id, 0))
        setattr(dua, 'is_favorite', dua.id in user_favorites_set)
        duas_with_counts.append(DuaRead.model_validate(dua))

    return duas_with_counts

@router.post("/duas", response_model=DuaRead)
async def create_dua_route(dua_data: DuaCreate, db: AsyncSession = Depends(get_db)):
    return await crud_dua.create_dua(db, dua_data.model_dump())

@router.get("/duas/stats", response_model=DuaStats)
async def get_duas_stats(db: AsyncSession = Depends(get_db)):
    all_duas = await crud_dua.get_all_duas(db)
    
    total_duas = len(all_duas)
    dua_ids = [dua.id for dua in all_duas]

    views_map = await crud_dua.get_views_bulk(db, dua_ids)
    favorites_map = await crud_dua.get_favorites_bulk(db, dua_ids)

    for dua in all_duas:
        setattr(dua, 'view_count', views_map.get(dua.id, 0))
        setattr(dua, 'favorite_count', favorites_map.get(dua.id, 0))

    total_views = sum(getattr(d, "view_count", 0) for d in all_duas)
    total_favorites = sum(getattr(d, "favorite_count", 0) for d in all_duas)

    featured_duas = [d for d in all_duas if getattr(d, "featured", False)]

    def safe_dua_item(d):
        return DuaItem(
            id=getattr(d, "id", 0) or 0,
            title=getattr(d, "title", "No Title") or "No Title"
        )

    top_featured = sorted(featured_duas, key=lambda d: getattr(d, "view_count", 0), reverse=True)[:5]
    top_viewed = sorted(all_duas, key=lambda d: getattr(d, "view_count", 0), reverse=True)[:5]

    return DuaStats(
        total_duas=total_duas,
        total_views=total_views,
        total_favorites=total_favorites,
        top_featured=[safe_dua_item(d) for d in top_featured] if top_featured else [],
        top_viewed=[safe_dua_item(d) for d in top_viewed] if top_viewed else [],
    )

@router.delete("/duas/bulk")
async def delete_duas_bulk_route(
    dua_ids: List[int], 
    db: AsyncSession = Depends(get_db)
):
    if not dua_ids:
        raise HTTPException(status_code=400, detail="Please provide a list of dua IDs to delete.")
    
    deleted_count = await crud_dua.delete_duas_bulk(db, dua_ids)

    if deleted_count == 0 and len(dua_ids) > 0:
        raise HTTPException(status_code=404, detail="No Duas found with the provided IDs.")
        
    return {"detail": f"{deleted_count} Duas deleted successfully."}

@router.post("/duas/bulk-data-upload")
async def bulk_data_upload_route(
    file: UploadFile = File(...),
    category_id: int = Form(None), 
    db: AsyncSession = Depends(get_db),
):
    duas_to_create = []
    try:
        content = await file.read()
        file_content = content.decode('utf-8')

        if file.content_type == "text/csv":
            csv_reader = csv.DictReader(StringIO(file_content))
            for row in csv_reader:
                dua_data = {
                    "title": row.get("title"),
                    "arabic": row.get("arabic"),
                    "transliteration": row.get("transliteration"),
                    "translation": row.get("translation"),
                    "notes": row.get("notes"),
                    "benefits": row.get("benefits"),
                    "source": row.get("source"),
                    "category_id": int(row.get("category_id") or category_id) if row.get("category_id") or category_id else None,
                    "audio_path": row.get("audio_path"),
                    "arabic_segments_json": row.get("arabic_segments_json"),
                    "transliteration_segments_json": row.get("transliteration_segments_json"),
                    "translation_segments_json": row.get("translation_segments_json"),
                }
                if dua_data["title"]: 
                    for key in ["arabic_segments_json", "transliteration_segments_json", "translation_segments_json"]:
                        val = dua_data.get(key)
                        if isinstance(val, str) and val.strip():
                            try:
                                dua_data[key] = json.loads(val)
                            except json.JSONDecodeError:
                                dua_data[key] = None
                    
                    duas_to_create.append({k: v for k, v in dua_data.items() if v is not None})

        elif file.content_type == "application/json":
            data = json.loads(file_content)
            if isinstance(data, list):
                for item in data:
                    item["category_id"] = int(item.get("category_id") or category_id) if item.get("category_id") or category_id else None
                    duas_to_create.append(item)
            elif isinstance(data, dict):
                data["category_id"] = int(data.get("category_id") or category_id) if data.get("category_id") or category_id else None
                duas_to_create.append(data)
        
        inserted_ids = await crud_dua.bulk_create_duas(db, duas_to_create)
        processed_count = len(inserted_ids)

        if processed_count == 0:
            raise HTTPException(
                status_code=422, detail="No valid Duas found in the uploaded file."
            )
        return {
            "detail": f"Successfully created {processed_count} Duas under category {category_id or 'auto-mapped'}",
            "filename": file.filename,
            "inserted_ids": inserted_ids, 
        }

    except HTTPException:
        raise
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file format.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing error: {e}")

@router.post("/categories/{category_id}/audio-update")
async def bulk_audio_update_by_category_route(
    category_id: int,
    audio_file: UploadFile = File(...), 
    db: AsyncSession = Depends(get_db)
):
    
    filename = audio_file.filename
    unique_filename = f"category_{category_id}_{os.path.basename(filename)}"
    unique_audio_path = op.join(AUDIO_DIR, unique_filename)
    
    try:
        with open(unique_audio_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)

        audio_url = f"/static/audio/{unique_filename}"

        updated_count = await crud_dua.update_dua_audio_path_by_category(
            db, 
            category_id=category_id, 
            audio_url=audio_url
        )
        
        if updated_count == 0:
            raise HTTPException(
                status_code=404, 
                detail=f"Category ID {category_id} not found or no Duas associated with it."
            )
        
    except HTTPException:
        raise
    except Exception as e:
        if op.exists(unique_audio_path):
            os.remove(unique_audio_path)
        raise HTTPException(status_code=500, detail=f"Audio processing or DB error: {str(e)}")

    return {
        "detail": f"Successfully updated audio path for {updated_count} Duas in Category {category_id}.", 
        "audio_url": audio_url
    }

@router.get("/duas/{dua_id}", response_model=DuaRead)
async def get_dua_route(dua_id: int, db: AsyncSession = Depends(get_db)):
    dua = await crud_dua.get_dua(db, dua_id)
    if not dua:
        raise HTTPException(status_code=404, detail="Dua not found")
    
    setattr(dua, 'view_count', await crud_dua.get_views_count(db, dua.id))
    setattr(dua, 'favorite_count', await crud_dua.get_favorites_count(db, dua.id))
    
    return DuaRead.model_validate(dua)

@router.get("/duas/{dua_id}/segments", response_model=DuaReadSegmented)
async def get_dua_segments_route(dua_id: int, db: AsyncSession = Depends(get_db)):
    dua = await crud_dua.get_dua(db, dua_id)
    
    if not dua:
        raise HTTPException(status_code=404, detail="Dua not found")

    segments_data = dua.arabic_segments_json if dua.arabic_segments_json else [] 
    transliteration_segments = getattr(dua, 'transliteration_segments_json', []) or []
    translation_segments = getattr(dua, 'translation_segments_json', []) or []

    response_data = {
        "id": dua.id,
        "title": dua.title,
        "audio_path": dua.audio_path,
        "arabic_segments": segments_data, 
        "transliteration_segments": transliteration_segments,
        "translation_segments": translation_segments,
    }
    
    return DuaReadSegmented.model_validate(response_data)


@router.get("/categories/{category_id}/full-segments")
async def get_category_full_segments_route(category_id: int, db: AsyncSession = Depends(get_db)):
    duas = await crud_dua.get_duas_by_category_id(db, category_id)
    
    if not duas:
        raise HTTPException(status_code=404, detail="Category not found or no Duas associated.")
    
    full_segment_list = []
    
    for dua in duas:
        if dua.arabic_segments_json:
            full_segment_list.extend(dua.arabic_segments_json)
    
    return {"arabic_segments": full_segment_list}


@router.put("/duas/{dua_id}", response_model=DuaRead)
@router.patch("/duas/{dua_id}", response_model=DuaRead)
async def update_dua_route(dua_id: int, dua_data: DuaUpdate, db: AsyncSession = Depends(get_db)):
    updated = await crud_dua.update_dua(db, dua_id, dua_data.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Dua not found")
    return updated

@router.delete("/duas/{dua_id}")
async def delete_dua_route(dua_id: int, db: AsyncSession = Depends(get_db)):
    success = await crud_dua.delete_dua(db, dua_id)
    if not success:
        raise HTTPException(status_code=404, detail="Dua not found")
    return {"detail": "Dua deleted successfully"}

@router.patch("/duas/{dua_id}/featured")
async def toggle_featured_route(dua_id: int, db: AsyncSession = Depends(get_db)):
    dua = await crud_dua.get_dua(db, dua_id)
    if not dua:
        raise HTTPException(status_code=404, detail="Dua not found")
    dua.featured = not dua.featured
    await db.commit()
    await db.refresh(dua)
    return {"id": dua_id, "featured": dua.featured}

@router.patch("/duas/{dua_id}/increment-view")
async def increment_view_route(dua_id: int, db: AsyncSession = Depends(get_db)):
    success = await crud_dua.increment_view(db, dua_id)
    if not success:
        raise HTTPException(status_code=404, detail="Dua not found")
    return {"id": dua_id, "status": "view incremented"}

@router.patch("/duas/{dua_id}/toggle-favorite")
async def toggle_favorite_route(
    dua_id: int, 
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    user_uuid = current_user.id
    success = await crud_dua.toggle_favorite(db, dua_id, user_uuid)
    if not success:
        raise HTTPException(status_code=404, detail="Dua not found")
    count = await crud_dua.get_favorites_count(db, dua_id)
    return {"id": dua_id, "favorites": count}

@router.get("/dua-categories", response_model=List[CategoryRead])
async def list_dua_categories(db: AsyncSession = Depends(get_db)):
    return await crud_dua.get_all_categories(db)

@router.post("/dua-categories", response_model=CategoryRead)
async def create_dua_category_route(category_data: CategoryCreate, db: AsyncSession = Depends(get_db)):
    return await crud_dua.create_category(db, category_data.model_dump())

@router.post("/dua-categories/{category_id}/image-upload")
async def upload_category_image_route(
    category_id: int,
    image_file: UploadFile = File(...), 
    db: AsyncSession = Depends(get_db)
):
    
    category = await crud_dua.get_category(db, category_id)
    if not category:
        raise HTTPException(
            status_code=404, 
            detail=f"Dua Category with ID {category_id} not found."
        )

    allowed_types = ["image/jpeg", "image/png", "image/webp"]
    if image_file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only JPEG, PNG, or WebP allowed."
        )
        
    file_extension = op.splitext(image_file.filename)[1]
    unique_filename = f"category_{category_id}_{uuid.uuid4().hex}{file_extension}"
    unique_image_path = op.join(CATEGORY_IMAGE_DIR, unique_filename)
    
    try:
        with open(unique_image_path, "wb") as buffer:
            shutil.copyfileobj(image_file.file, buffer)

        image_url = f"/static/category_images/{unique_filename}" 

        updated_category = await crud_dua.update_category_image_url(
            db, 
            category_id=category_id, 
            image_url=image_url
        )
        
    except HTTPException:
        raise
    except Exception as e:
        if op.exists(unique_image_path):
            os.remove(unique_image_path)
        raise HTTPException(status_code=500, detail=f"Image processing or DB error: {str(e)}")

    return {
        "detail": f"Successfully updated image for Category {category_id}.", 
        "image_url": image_url,
        "category_id": updated_category.id,
        "category_name": updated_category.name
    }

@router.put("/dua-categories/{category_id}", response_model=CategoryRead)
@router.patch("/dua-categories/{category_id}", response_model=CategoryRead)
async def update_dua_category_route(category_id: int, category_data: CategoryUpdate, db: AsyncSession = Depends(get_db)):
    updated = await crud_dua.update_category(db, category_id, category_data.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Dua Category not found")
    return updated

@router.delete("/dua-categories/{category_id}")
async def delete_dua_category_route(category_id: int, db: AsyncSession = Depends(get_db)):
    category = await crud_dua.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Dua Category not found")
    
    success = await crud_dua.delete_category(db, category_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete Dua category.")

    return {"detail": "Dua Category deleted successfully (associated Duas' category was set to null)."}