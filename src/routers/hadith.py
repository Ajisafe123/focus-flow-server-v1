from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, Form, File, status
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from ..database import get_db
from ..utils import hadith as crud_hadith
from ..utils.users import get_current_user, get_optional_user
from ..schemas.hadith import (
    HadithRead, HadithCreate, HadithUpdate,
    HadithCategoryRead, HadithCategoryCreate, HadithCategoryUpdate, HadithStats, HadithItem
)
import csv
import json
from io import StringIO
from datetime import date
import random
import os
import shutil
import uuid
import pymongo.errors
import os.path as op
from ..utils.cloudinary_uploader import upload_bytes

HadithSchema = HadithRead 
cache: Dict[str, Any] = {}

async def _cache_key(prefix: str, suffix: str) -> str:
    return f"{prefix}:{suffix}"

def _normalize_row(hadith_dict: dict, view_count: int, favorite_count: int) -> HadithRead:
    hadith_dict['view_count'] = view_count
    hadith_dict['favorite_count'] = favorite_count
    return HadithRead(**hadith_dict)

router = APIRouter(prefix="/api", tags=["Hadiths"])


@router.get("/day", response_model=None)
async def hadith_of_day(db: AsyncIOMotorDatabase = Depends(get_db)):
    """Return a random hadith for daily display."""
    hadith = await crud_hadith.get_random_hadith(db)
    if not hadith:
        # Fallback if DB is empty to prevent 404
        return HadithRead(
            id=str(ObjectId()),
            arabic="إِنَّمَا الْأَعْمَالُ بِالنِّيَّاتِ",
            translation="Actions are judged by intentions.",
            narrator="Umar bin Al-Khattab",
            book="Sahih Al-Bukhari",
            number="1",
            view_count=0,
            favorite_count=0,
            category_id=None
        )
    hadith["view_count"] = 0
    hadith["favorite_count"] = 0
    return HadithRead(**hadith)

@router.get("/hadiths", response_model=None)
async def list_hadiths(db: AsyncIOMotorDatabase = Depends(get_db)):
    hadiths = await crud_hadith.get_all_hadiths(db)
    hadith_ids = [h.id for h in hadiths]
    
    views_map = await crud_hadith.get_views_bulk(db, hadith_ids)
    favorites_map = await crud_hadith.get_favorites_bulk(db, hadith_ids)

    hadiths_with_counts = []
    for h in hadiths:
        h_dict = h.model_dump(by_alias=True)
        h_dict["view_count"] = views_map.get(str(h.id), 0)
        h_dict["favorite_count"] = favorites_map.get(str(h.id), 0)
        hadiths_with_counts.append(HadithRead(**h_dict))
        
    return hadiths_with_counts

@router.get("/hadiths/paginated", response_model=None)
async def list_hadiths_paginated(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    sort_by: str = Query("_id"),
    sort_order: str = Query("asc"),
    q: Optional[str] = None,
    category_id: Optional[str] = None,
    featured: Optional[bool] = None,
    current_user: Optional[dict] = Depends(get_optional_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    hadiths, hadith_ids = await crud_hadith.get_paginated_hadiths(db, page, limit, sort_by, sort_order, q, category_id, featured)

    views_map = await crud_hadith.get_views_bulk(db, hadith_ids)
    favorites_map = await crud_hadith.get_favorites_bulk(db, hadith_ids)

    user_favorites_set = set()
    if current_user:
        user_uuid = current_user.get("_id")
        user_favorites_set = await crud_hadith.get_user_favorites_set(db, user_uuid, hadith_ids)
    
    hadiths_with_counts = []
    for h in hadiths:
        h_dict = h.model_dump(by_alias=True)
        h_dict["view_count"] = views_map.get(str(h.id), 0)
        h_dict["favorite_count"] = favorites_map.get(str(h.id), 0)
        h_dict["is_favorite"] = str(h.id) in user_favorites_set
        hadiths_with_counts.append(h_dict)

    total_count = await crud_hadith.count_hadiths(db, q, category_id, featured)

    return {
        "items": hadiths_with_counts,
        "total_count": total_count
    }

@router.post("/hadiths", response_model=None)
async def create_hadith_route(hadith_data: HadithCreate, db: AsyncIOMotorDatabase = Depends(get_db)):
    created = await crud_hadith.create_hadith(db, hadith_data.model_dump())
    try:
        await create_notifications(
            db,
            title="New Hadith Published",
            message=f"A new authentic hadith has been added to the collection",
            notif_type="info",
            user_ids=None,
            link=f"/hadiths?hadithId={created.id}",
        )
    except Exception:
        pass
    return HadithRead(**created)

@router.get("/hadiths/stats", response_model=None)
async def get_hadiths_stats(db: AsyncIOMotorDatabase = Depends(get_db)):
    all_hadiths = await crud_hadith.get_all_hadiths(db)
    
    total_hadiths = len(all_hadiths)
    hadith_ids = [h.id for h in all_hadiths]

    views_map = await crud_hadith.get_views_bulk(db, hadith_ids)
    favorites_map = await crud_hadith.get_favorites_bulk(db, hadith_ids)

    total_views = sum(views_map.get(str(hid), 0) for hid in hadith_ids)
    total_favorites = sum(favorites_map.get(str(hid), 0) for hid in hadith_ids)
    
    total_featured = sum(1 for h in all_hadiths if h.featured)
    
    featured_hadiths = [h for h in all_hadiths if h.featured]

    def safe_hadith_item(h):
        return HadithItem(
            id=h.id,
            number=h.number or "No Number"
        )

    top_featured = sorted(
        [(h, views_map.get(str(h.id), 0)) for h in featured_hadiths],
        key=lambda x: x[1],
        reverse=True
    )[:5]
    
    top_viewed = sorted(
        [(h, views_map.get(str(h.id), 0)) for h in all_hadiths],
        key=lambda x: x[1],
        reverse=True
    )[:5]

    return HadithStats(
        total_hadiths=total_hadiths,
        total_views=total_views,
        total_favorites=total_favorites,
        total_featured=total_featured,
        top_featured=[safe_hadith_item(h[0]) for h in top_featured],
        top_viewed=[safe_hadith_item(h[0]) for h in top_viewed],
    )

@router.delete("/hadiths/bulk", response_model=None)
async def delete_hadiths_bulk_route(
    hadith_ids: List[str], 
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if not hadith_ids:
        raise HTTPException(status_code=400, detail="Please provide a list of Hadith IDs to delete.")
    
    try:
        obj_ids = [ObjectId(id_str) for id_str in hadith_ids]
    except:
        raise HTTPException(status_code=400, detail="Invalid hadith IDs")
    
    deleted_count = await crud_hadith.delete_hadiths_bulk(db, obj_ids)

    if deleted_count == 0 and len(hadith_ids) > 0:
        raise HTTPException(status_code=404, detail="No Hadiths found with the provided IDs.")
        
    return {"detail": f"{deleted_count} Hadiths deleted successfully."}

@router.post("/hadiths/bulk-data-upload", response_model=None)
async def bulk_data_upload_route(
    file: UploadFile = File(...),
    category_id: Optional[str] = Form(None), 
    db: AsyncIOMotorDatabase = Depends(get_db),
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
                            hadith_data[model_key] = value or category_id
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
            
            # Handle nested structure with hadiths array
            if isinstance(data, dict) and "hadiths" in data:
                data_list = data["hadiths"]
            elif isinstance(data, list):
                data_list = data
            else:
                data_list = [data]
            
            for item in data_list:
                if item.get("arabic"):
                    item["category_id"] = category_id or item.get("category_id")
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
            "inserted_ids": [str(id) for id in inserted_ids], 
        }

    except HTTPException:
        raise
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file format.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing error: {e}")

@router.get("/hadiths/{hadith_id}", response_model=None)
async def get_hadith_route(hadith_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    try:
        obj_id = ObjectId(hadith_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid hadith ID")
    
    hadith = await crud_hadith.get_hadith(db, obj_id)
    
    if not hadith:
        raise HTTPException(status_code=404, detail="Hadith not found")
    
    view_count = await crud_hadith.get_views_count(db, obj_id)
    favorite_count = await crud_hadith.get_favorites_count(db, obj_id)
    
    hadith['view_count'] = view_count
    hadith['favorite_count'] = favorite_count
    
    return HadithRead(**hadith)

@router.put("/hadiths/{hadith_id}", response_model=None)
@router.patch("/hadiths/{hadith_id}", response_model=None)
async def update_hadith_route(
    hadith_id: str,
    hadith_data: HadithUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        obj_id = ObjectId(hadith_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid hadith ID")
    
    updated = await crud_hadith.update_hadith(db, obj_id, hadith_data.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Hadith not found")
    return HadithRead(**updated)

@router.delete("/hadiths/{hadith_id}", response_model=None)
async def delete_hadith_route(hadith_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    try:
        obj_id = ObjectId(hadith_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid hadith ID")
    
    success = await crud_hadith.delete_hadith(db, obj_id)
    if not success:
        raise HTTPException(status_code=404, detail="Hadith not found")
    return {"detail": "Hadith deleted successfully"}

@router.get("/day", response_model=None)
async def hadith_of_the_day(db: AsyncIOMotorDatabase = Depends(get_db)):
    today_key = await _cache_key("hadith_of_the_day", date.today().isoformat())
    cached = cache.get(today_key)
    if cached:
        return cached
    
    total = await crud_hadith.count_hadiths(db, None, None, None)
    
    if total == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hadiths found")
    
    seed = int(date.today().strftime("%Y%m%d"))
    random.seed(seed)
    offset = random.randint(0, total - 1)
    
    hadiths = await crud_hadith.get_paginated_hadiths(db, offset + 1, 1, "_id", "asc", None, None, None)
    
    if not hadiths[0]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hadith not found (Offset issue)")
    
    hadith = hadiths[0][0]
    
    view_count = await crud_hadith.get_views_count(db, hadith["_id"])
    favorite_count = await crud_hadith.get_favorites_count(db, hadith["_id"])
    
    response = _normalize_row(hadith, view_count, favorite_count)
    
    cache[today_key] = response
    return response

@router.patch("/hadiths/{hadith_id}/featured", response_model=None)
async def toggle_featured_route(hadith_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    try:
        obj_id = ObjectId(hadith_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid hadith ID")
    
    hadith = await crud_hadith.get_hadith(db, obj_id)
    if not hadith:
        raise HTTPException(status_code=404, detail="Hadith not found")
    
    new_featured = not hadith.get("featured", False)
    updated = await crud_hadith.update_hadith(db, obj_id, {"featured": new_featured})
    
    return {"id": hadith_id, "featured": updated.get("featured")}

@router.patch("/hadiths/{hadith_id}/increment-view", response_model=None)
async def increment_view_route(hadith_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    try:
        obj_id = ObjectId(hadith_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid hadith ID")
    
    success = await crud_hadith.increment_view(db, obj_id)
    if not success:
        raise HTTPException(status_code=404, detail="Hadith not found")
    return {"id": hadith_id, "status": "view incremented"}

@router.patch("/hadiths/{hadith_id}/toggle-favorite", response_model=None)
async def toggle_favorite_route(
    hadith_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        obj_id = ObjectId(hadith_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid hadith ID")
    
    user_uuid = current_user.get("_id")
    success = await crud_hadith.toggle_favorite(db, obj_id, user_uuid)
    if not success:
        raise HTTPException(status_code=404, detail="Hadith not found")
    count = await crud_hadith.get_favorites_count(db, obj_id)
    return {"id": hadith_id, "favorites": count}

@router.get("/hadith-categories", response_model=None)
async def list_categories(db: AsyncIOMotorDatabase = Depends(get_db)):
    categories = await crud_hadith.get_all_categories(db)
    return [cat.model_dump() for cat in categories]

@router.post("/hadith-categories", response_model=None)
async def create_category_route(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    is_active: bool = Form(True),
    image_file: Optional[UploadFile] = File(None),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create a new hadith category with optional image"""
    category_data = {
        "name": name,
        "description": description,
        "is_active": is_active,
        "image_url": None
    }
    
    # Process image if provided
    if image_file:
        allowed_types = ["image/jpeg", "image/png", "image/webp"]
        if image_file.content_type in allowed_types:
            file_extension = op.splitext(image_file.filename)[1]
            try:
                filename = f"cat_hadith_{uuid.uuid4().hex}{file_extension}"
                contents = await image_file.read()
                result = await upload_bytes(
                    contents=contents,
                    filename=filename,
                    folder="hadith/category_images",
                    resource_type="image",
                    content_type=image_file.content_type,
                )
                category_data["image_url"] = result.get("secure_url") or result.get("url")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")

    try:
        created = await crud_hadith.create_category(db, category_data)
    except pymongo.errors.DuplicateKeyError:
       raise HTTPException(status_code=400, detail="Category with this name already exists")
    return HadithCategoryRead(**created)

@router.put("/hadith-categories/{category_id}", response_model=None)
@router.patch("/hadith-categories/{category_id}", response_model=None)
async def update_category_route(
    category_id: str,
    category_data: HadithCategoryUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        cat_obj_id = ObjectId(category_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid category ID")
    
    updated = await crud_hadith.update_category(db, cat_obj_id, category_data.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Category not found")
    return HadithCategoryRead(**updated)

@router.delete("/hadith-categories/{category_id}", response_model=None)
async def delete_category_route(category_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    try:
        cat_obj_id = ObjectId(category_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid category ID")
    
    category = await crud_hadith.get_category(db, cat_obj_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    success = await crud_hadith.delete_category(db, cat_obj_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete category.")

    return {"detail": "Category deleted successfully (associated Hadiths' category was set to null)."}
