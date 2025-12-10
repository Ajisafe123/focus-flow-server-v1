from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import List, Optional
from datetime import datetime
from ..database import get_db
from ..utils.users import get_current_user
from ..schemas.media import (
    VideoCreate,
    VideoUpdate,
    VideoRead,
    AudioCreate,
    AudioUpdate,
    AudioRead,
)

router = APIRouter(prefix="/api", tags=["Media"])


def serialize(doc):
    if not doc:
        return None
    doc["_id"] = str(doc.get("_id"))
    return doc


def ensure_object_id(id_str: str):
    try:
        return ObjectId(id_str)
    except Exception:
        return id_str


def admin_required(user: dict):
    if not user or user.get("role", "").lower() != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")


@router.get("/videos", response_model=List[VideoRead])
async def list_videos(
    db: AsyncIOMotorDatabase = Depends(get_db),
    featured: Optional[bool] = None,
    category: Optional[str] = None,
):
    query = {}
    if featured is not None:
        query["featured"] = featured
    if category:
        query["category"] = category
    cursor = db["videos"].find(query).sort("created_at", -1)
    items = []
    async for doc in cursor:
        items.append(VideoRead(**serialize(doc)))
    return items


@router.get("/videos/{video_id}", response_model=VideoRead)
async def get_video(video_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    vid = ensure_object_id(video_id)
    doc = await db["videos"].find_one({"_id": vid})
    if not doc:
        raise HTTPException(status_code=404, detail="Video not found")
    return VideoRead(**serialize(doc))


@router.post("/videos", response_model=VideoRead)
async def create_video(
    payload: VideoCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    admin_required(current_user)
    data = payload.model_dump()
    data["created_at"] = datetime.utcnow()
    data["updated_at"] = datetime.utcnow()
    result = await db["videos"].insert_one(data)
    doc = await db["videos"].find_one({"_id": result.inserted_id})
    return VideoRead(**serialize(doc))


@router.put("/videos/{video_id}", response_model=VideoRead)
@router.patch("/videos/{video_id}", response_model=VideoRead)
async def update_video(
    video_id: str,
    payload: VideoUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    admin_required(current_user)
    vid = ensure_object_id(video_id)
    update = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
    update["updated_at"] = datetime.utcnow()
    res = await db["videos"].update_one({"_id": vid}, {"$set": update})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Video not found")
    doc = await db["videos"].find_one({"_id": vid})
    return VideoRead(**serialize(doc))


@router.delete("/videos/{video_id}")
async def delete_video(
    video_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    admin_required(current_user)
    vid = ensure_object_id(video_id)
    res = await db["videos"].delete_one({"_id": vid})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Video not found")
    return {"detail": "Video deleted"}


@router.get("/audio", response_model=List[AudioRead])
async def list_audio(
    db: AsyncIOMotorDatabase = Depends(get_db),
    featured: Optional[bool] = None,
    category: Optional[str] = None,
):
    query = {}
    if featured is not None:
        query["featured"] = featured
    if category:
        query["category"] = category
    cursor = db["audio"].find(query).sort("created_at", -1)
    items = []
    async for doc in cursor:
        items.append(AudioRead(**serialize(doc)))
    return items


@router.get("/audio/{audio_id}", response_model=AudioRead)
async def get_audio(audio_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    aid = ensure_object_id(audio_id)
    doc = await db["audio"].find_one({"_id": aid})
    if not doc:
        raise HTTPException(status_code=404, detail="Audio not found")
    return AudioRead(**serialize(doc))


@router.post("/audio", response_model=AudioRead)
async def create_audio(
    payload: AudioCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    admin_required(current_user)
    data = payload.model_dump()
    data["created_at"] = datetime.utcnow()
    data["updated_at"] = datetime.utcnow()
    result = await db["audio"].insert_one(data)
    doc = await db["audio"].find_one({"_id": result.inserted_id})
    return AudioRead(**serialize(doc))


@router.put("/audio/{audio_id}", response_model=AudioRead)
@router.patch("/audio/{audio_id}", response_model=AudioRead)
async def update_audio(
    audio_id: str,
    payload: AudioUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    admin_required(current_user)
    aid = ensure_object_id(audio_id)
    update = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
    update["updated_at"] = datetime.utcnow()
    res = await db["audio"].update_one({"_id": aid}, {"$set": update})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Audio not found")
    doc = await db["audio"].find_one({"_id": aid})
    return AudioRead(**serialize(doc))


@router.delete("/audio/{audio_id}")
async def delete_audio(
    audio_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    admin_required(current_user)
    aid = ensure_object_id(audio_id)
    res = await db["audio"].delete_one({"_id": aid})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Audio not found")
    return {"detail": "Audio deleted"}

