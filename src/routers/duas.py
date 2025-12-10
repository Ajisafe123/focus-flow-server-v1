from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, Form, File, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, field_validator
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from ..database import get_db
from ..utils import dua as crud_dua
from ..utils.users import get_current_user, get_optional_user
from ..utils.notifications import create_notifications
from ..schemas.dua import (
    DuaRead, DuaCreate, DuaUpdate,
    CategoryRead, CategoryCreate, CategoryUpdate, DuaStats, DuaItem, DuaReadSegmented
)
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
FRONTEND_BASE_URL = "https://nibrasudeen.vercel.app"


@router.post("/duas/{dua_id}/share-link", response_model=None)
async def generate_dua_share_link(dua_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    try:
        obj_id = ObjectId(dua_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid dua ID")
    
    dua = await crud_dua.get_dua(db, obj_id)
    if not dua:
        raise HTTPException(status_code=404, detail="Dua not found")

    short_code = crud_dua.generate_short_code()
    share_link_obj = await crud_dua.create_share_link(db, obj_id, short_code)

    full_share_url = f"{SHARE_BASE_URL}{short_code}"
    
    return {"share_url": full_share_url}


@router.get("/s/{short_code}", response_model=None)
async def redirect_to_dua_page(short_code: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    dua_id = await crud_dua.get_dua_id_by_short_code(db, short_code)
    
    if dua_id is None:
        return RedirectResponse(url=FRONTEND_BASE_URL, status_code=307)
    
    target_url = f"{FRONTEND_BASE_URL}/?duaId={dua_id}"
    return RedirectResponse(url=target_url, status_code=307)


@router.get("/duas", response_model=None)
async def list_duas(db: AsyncIOMotorDatabase = Depends(get_db)):
    duas, views_map, favorites_map = await crud_dua.get_all_duas_with_counts(db)

    duas_with_counts = []
    for dua in duas:
        dua["view_count"] = views_map.get(str(dua["_id"]), 0)
        dua["favorite_count"] = favorites_map.get(str(dua["_id"]), 0)
        duas_with_counts.append(DuaRead(**dua))
        
    return duas_with_counts


@router.get("/duas/paginated", response_model=None)
async def list_duas_paginated(
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
    duas, dua_ids = await crud_dua.get_paginated_duas(db, page, limit, sort_by, sort_order, q, category_id, featured)

    views_map = await crud_dua.get_views_bulk(db, dua_ids)
    favorites_map = await crud_dua.get_favorites_bulk(db, dua_ids)

    user_favorites_set = set()
    if current_user:
        user_uuid = current_user.get("_id")
        user_favorites_set = await crud_dua.get_user_favorites_set(db, user_uuid, dua_ids)
    
    duas_with_counts = []
    for dua in duas:
        dua["view_count"] = views_map.get(str(dua["_id"]), 0)
        dua["favorite_count"] = favorites_map.get(str(dua["_id"]), 0)
        dua["is_favorite"] = str(dua["_id"]) in user_favorites_set
        duas_with_counts.append(DuaRead(**dua))

    return duas_with_counts


@router.post("/duas", response_model=None)
async def create_dua_route(dua_data: DuaCreate, db: AsyncIOMotorDatabase = Depends(get_db)):
    created = await crud_dua.create_dua(db, dua_data.model_dump())
    # broadcast notification to everyone
    try:
        await create_notifications(
            db,
            title="New dua added",
            message=f"{dua_data.title} is now available.",
            notif_type="info",
            user_ids=None,
            link=f"/dua/{created.get('_id')}",
        )
    except Exception:
        pass
    return DuaRead(**created)


@router.get("/duas/stats", response_model=None)
async def get_duas_stats(db: AsyncIOMotorDatabase = Depends(get_db)):
    all_duas = await crud_dua.get_all_duas(db)
    
    total_duas = len(all_duas)
    dua_ids = [dua["_id"] for dua in all_duas]

    views_map = await crud_dua.get_views_bulk(db, dua_ids)
    favorites_map = await crud_dua.get_favorites_bulk(db, dua_ids)

    total_views = sum(views_map.get(str(dua_id), 0) for dua_id in dua_ids)
    total_favorites = sum(favorites_map.get(str(dua_id), 0) for dua_id in dua_ids)

    featured_duas = [d for d in all_duas if d.get("featured")]
    
    def safe_dua_item(d):
        return DuaItem(
            id=d.get("_id"),
            title=d.get("title") or "No Title"
        )

    top_featured = sorted(
        [(d, views_map.get(str(d["_id"]), 0)) for d in featured_duas],
        key=lambda x: x[1],
        reverse=True
    )[:5]
    
    top_viewed = sorted(
        [(d, views_map.get(str(d["_id"]), 0)) for d in all_duas],
        key=lambda x: x[1],
        reverse=True
    )[:5]

    return DuaStats(
        total_duas=total_duas,
        total_views=total_views,
        total_favorites=total_favorites,
        top_featured=[safe_dua_item(d[0]) for d in top_featured],
        top_viewed=[safe_dua_item(d[0]) for d in top_viewed],
    )


@router.delete("/duas/bulk", response_model=None)
async def delete_duas_bulk_route(
    dua_ids: List[str], 
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if not dua_ids:
        raise HTTPException(status_code=400, detail="Please provide a list of dua IDs to delete.")
    
    try:
        obj_ids = [ObjectId(id_str) for id_str in dua_ids]
    except:
        raise HTTPException(status_code=400, detail="Invalid dua IDs")
    
    deleted_count = await crud_dua.delete_duas_bulk(db, obj_ids)

    if deleted_count == 0 and len(dua_ids) > 0:
        raise HTTPException(status_code=404, detail="No Duas found with the provided IDs.")
        
    return {"detail": f"{deleted_count} Duas deleted successfully."}


@router.post("/duas/bulk-data-upload", response_model=None)
async def bulk_data_upload_route(
    file: UploadFile = File(...),
    category_id: Optional[str] = Form(None), 
    db: AsyncIOMotorDatabase = Depends(get_db),
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
                    "category_id": category_id or row.get("category_id"),
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
                    item["category_id"] = category_id or item.get("category_id")
                    duas_to_create.append(item)
            elif isinstance(data, dict):
                data["category_id"] = category_id or data.get("category_id")
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
            "inserted_ids": [str(id) for id in inserted_ids], 
        }

    except HTTPException:
        raise
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file format.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing error: {e}")


@router.post("/categories/{category_id}/audio-update", response_model=None)
async def bulk_audio_update_by_category_route(
    category_id: str,
    audio_file: UploadFile = File(...), 
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        cat_obj_id = ObjectId(category_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid category ID")
    
    filename = audio_file.filename
    unique_filename = f"category_{category_id}_{os.path.basename(filename)}"
    unique_audio_path = op.join(AUDIO_DIR, unique_filename)
    
    try:
        with open(unique_audio_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)

        audio_url = f"/static/audio/{unique_filename}"

        updated_count = await crud_dua.update_dua_audio_path_by_category(
            db, 
            category_id=cat_obj_id, 
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


@router.get("/duas/{dua_id}", response_model=None)
async def get_dua_route(dua_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    try:
        obj_id = ObjectId(dua_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid dua ID")
    
    dua = await crud_dua.get_dua(db, obj_id)
    if not dua:
        raise HTTPException(status_code=404, detail="Dua not found")
    
    view_count = await crud_dua.get_views_count(db, obj_id)
    fav_count = await crud_dua.get_favorites_count(db, obj_id)
    
    dua["view_count"] = view_count
    dua["favorite_count"] = fav_count
    
    return DuaRead(**dua)


@router.get("/duas/{dua_id}/segments", response_model=None)
async def get_dua_segments_route(dua_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    try:
        obj_id = ObjectId(dua_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid dua ID")
    
    dua = await crud_dua.get_dua(db, obj_id)
    
    if not dua:
        raise HTTPException(status_code=404, detail="Dua not found")

    segments_data = dua.get("arabic_segments_json") or [] 
    transliteration_segments = dua.get("transliteration_segments_json") or []
    translation_segments = dua.get("translation_segments_json") or []

    response_data = {
        "id": dua["_id"],
        "title": dua.get("title"),
        "audio_path": dua.get("audio_path"),
        "arabic_segments": segments_data, 
        "transliteration_segments": transliteration_segments,
        "translation_segments": translation_segments,
    }
    
    return DuaReadSegmented(**response_data)


@router.get("/categories/{category_id}/full-segments", response_model=None)
async def get_category_full_segments_route(category_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    # Accept both ObjectId and plain ints/strings; return empty on failure instead of 400.
    cat_obj_id = None
    try:
        cat_obj_id = ObjectId(category_id)
    except Exception:
        # allow numeric categories; try as int match on a field if needed
        cat_obj_id = category_id

    try:
        duas = await crud_dua.get_duas_by_category_id(db, cat_obj_id)
    except Exception:
        duas = []
    
    if not duas:
        return {"arabic_segments": []}
    
    full_segment_list = []
    
    for dua in duas:
        if dua.get("arabic_segments_json"):
            full_segment_list.extend(dua["arabic_segments_json"])
    
    return {"arabic_segments": full_segment_list}


@router.put("/duas/{dua_id}", response_model=None)
@router.patch("/duas/{dua_id}", response_model=None)
async def update_dua_route(
    dua_id: str,
    dua_data: DuaUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        obj_id = ObjectId(dua_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid dua ID")
    
    updated = await crud_dua.update_dua(db, obj_id, dua_data.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Dua not found")
    return DuaRead(**updated)


@router.delete("/duas/{dua_id}", response_model=None)
async def delete_dua_route(dua_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    try:
        obj_id = ObjectId(dua_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid dua ID")
    
    success = await crud_dua.delete_dua(db, obj_id)
    if not success:
        raise HTTPException(status_code=404, detail="Dua not found")
    return {"detail": "Dua deleted successfully"}


@router.patch("/duas/{dua_id}/featured", response_model=None)
async def toggle_featured_route(dua_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    try:
        obj_id = ObjectId(dua_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid dua ID")
    
    dua = await crud_dua.get_dua(db, obj_id)
    if not dua:
        raise HTTPException(status_code=404, detail="Dua not found")
    
    new_featured = not dua.get("featured", False)
    updated = await crud_dua.update_dua(db, obj_id, {"featured": new_featured})
    
    return {"id": dua_id, "featured": updated.get("featured")}


@router.patch("/duas/{dua_id}/increment-view", response_model=None)
async def increment_view_route(dua_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    try:
        obj_id = ObjectId(dua_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid dua ID")
    
    success = await crud_dua.increment_view(db, obj_id)
    if not success:
        raise HTTPException(status_code=404, detail="Dua not found")
    return {"id": dua_id, "status": "view incremented"}


@router.patch("/duas/{dua_id}/toggle-favorite", response_model=None)
async def toggle_favorite_route(
    dua_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        obj_id = ObjectId(dua_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid dua ID")
    
    user_uuid = current_user.get("_id")
    success = await crud_dua.toggle_favorite(db, obj_id, user_uuid)
    if not success:
        raise HTTPException(status_code=404, detail="Dua not found")
    
    count = await crud_dua.get_favorites_count(db, obj_id)
    return {"id": dua_id, "favorites": count}


@router.get("/dua-categories", response_model=None)
async def list_dua_categories(db: AsyncIOMotorDatabase = Depends(get_db)):
    return [CategoryRead(**cat) for cat in await crud_dua.get_all_categories(db)]


@router.post("/dua-categories", response_model=None)
async def create_dua_category_route(category_data: CategoryCreate, db: AsyncIOMotorDatabase = Depends(get_db)):
    created = await crud_dua.create_category(db, category_data.model_dump())
    return CategoryRead(**created)


@router.post("/dua-categories/{category_id}/image-upload", response_model=None)
async def upload_category_image_route(
    category_id: str,
    image_file: UploadFile = File(...), 
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        cat_obj_id = ObjectId(category_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid category ID")
    
    category = await crud_dua.get_category(db, cat_obj_id)
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
            category_id=cat_obj_id, 
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
        "category_id": str(updated_category["_id"]),
        "category_name": updated_category.get("name")
    }


@router.put("/dua-categories/{category_id}", response_model=None)
@router.patch("/dua-categories/{category_id}", response_model=None)
async def update_dua_category_route(
    category_id: str,
    category_data: CategoryUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        cat_obj_id = ObjectId(category_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid category ID")
    
    updated = await crud_dua.update_category(db, cat_obj_id, category_data.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Dua Category not found")
    return CategoryRead(**updated)


@router.delete("/dua-categories/{category_id}", response_model=None)
async def delete_dua_category_route(category_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    try:
        cat_obj_id = ObjectId(category_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid category ID")
    
    category = await crud_dua.get_category(db, cat_obj_id)
    if not category:
        raise HTTPException(status_code=404, detail="Dua Category not found")
    
    success = await crud_dua.delete_category(db, cat_obj_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete Dua category.")

    return {"detail": "Dua Category deleted successfully (associated Duas' category was set to null)."}
