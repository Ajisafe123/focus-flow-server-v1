from fastapi import APIRouter, HTTPException, Query, Depends, Body
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from ..services.quran_service import (
    get_surah_list,
    get_surah_detail,
    get_ayah,
    get_translation,
    list_reciters,
    search_quran,
    get_page_detail,
)
from ..utils.cache import cache
from ..database import get_db
from ..utils.users import get_current_user, get_optional_user

router = APIRouter(prefix="/quran", tags=["Quran"])

async def mark_bookmarks(verses, current_user, db: AsyncIOMotorDatabase):
    if not current_user:
        return verses
    
    ayah_keys = [v["verse_key"] for v in verses]
    bookmarks_collection = db["bookmarks"]
    user_bookmarks = await bookmarks_collection.find(
        {"user_id": current_user.get("_id"), "ayah_key": {"$in": ayah_keys}}
    ).to_list(length=None)
    
    bookmarked_keys = {b["ayah_key"] for b in user_bookmarks}
    for verse in verses:
        verse["bookmarked"] = verse["verse_key"] in bookmarked_keys
    return verses

@router.get("/surahs", response_model=None)
@cache(ttl=3600)
async def list_surahs_route():
    data = await get_surah_list()
    if not data:
        raise HTTPException(status_code=500, detail="Failed to fetch surah list")
    return data

@router.get("/surah/{surah_number}", response_model=None)
@cache(ttl=3600)
async def read_surah_route(
    surah_number: int,
    translation: str = Query("en.sahih"),
    tafsir_sources: Optional[List[str]] = Query(None),
    reciter: Optional[str] = Query(None),
    current_user: Optional[dict] = Depends(get_optional_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    data = await get_surah_detail(surah_number, translation, tafsir_sources, reciter)
    if not data:
        raise HTTPException(status_code=404, detail="Surah not found")
    if current_user:
        data["verses"] = await mark_bookmarks(data["verses"], current_user, db)
    return data

@router.get("/page/{page_number}", response_model=None)
@cache(ttl=3600)
async def read_quran_page_route(
    page_number: int,
    translation: str = Query("en.sahih"),
    tafsir_sources: Optional[List[str]] = Query(None),
    reciter: Optional[str] = Query(None),
    current_user: Optional[dict] = Depends(get_optional_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if not 1 <= page_number <= 604:
        raise HTTPException(status_code=400, detail="Page number must be between 1 and 604.")
        
    data = await get_page_detail(page_number, translation, tafsir_sources, reciter)
    
    if not data or not data.get("verses"):
        raise HTTPException(status_code=404, detail=f"No verses found for Page {page_number}")
        
    if current_user:
        data["verses"] = await mark_bookmarks(data["verses"], current_user, db)
        
    return data

@router.get("/ayah/{ayah_key}", response_model=None)
async def read_ayah_route(
    ayah_key: str,
    tafsir_sources: Optional[List[str]] = Query(None),
    reciter: Optional[str] = Query(None),
    current_user: Optional[dict] = Depends(get_optional_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    data = await get_ayah(ayah_key, tafsir_sources, reciter)
    if not data:
        raise HTTPException(status_code=404, detail="Ayah not found")
    
    if current_user:
        bookmarks_collection = db["bookmarks"]
        bookmark = await bookmarks_collection.find_one({
            "user_id": current_user.get("_id"),
            "ayah_key": ayah_key
        })
        data["bookmarked"] = bookmark is not None
    
    return data

@router.get("/translation/{lang}", response_model=None)
@cache(ttl=86400)
async def translation_route(lang: str):
    data = await get_translation(lang)
    if not data:
        raise HTTPException(status_code=404, detail="Translation not found")
    return data

@router.get("/reciters", response_model=None)
async def reciters_route():
    return {"reciters": list_reciters()}

@router.get("/search", response_model=None)
async def search_route(
    q: str,
    tafsir_source: Optional[str] = Query(None),
    current_user: Optional[dict] = Depends(get_optional_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    results = await search_quran(q, tafsir_source)
    if current_user:
        await mark_bookmarks(results, current_user, db)
    return results

@router.post("/bookmark", response_model=None)
async def toggle_bookmark(
    ayah_key: str = Body(...),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    bookmarks_collection = db["bookmarks"]
    
    bookmark = await bookmarks_collection.find_one({
        "user_id": current_user.get("_id"),
        "ayah_key": ayah_key
    })
    
    if bookmark:
        await bookmarks_collection.delete_one({"_id": bookmark["_id"]})
        return {"status": "removed", "ayah_key": ayah_key}
    else:
        from datetime import datetime
        bm_data = {
            "user_id": current_user.get("_id"),
            "ayah_key": ayah_key,
            "created_at": datetime.utcnow().isoformat()
        }
        await bookmarks_collection.insert_one(bm_data)
        return {"status": "added", "ayah_key": ayah_key}
