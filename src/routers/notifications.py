from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..database import get_db
from ..schemas.notification import NotificationCreate, NotificationOut
from ..utils.users import get_current_user, get_optional_user
from ..utils.notifications import create_notifications, mark_all_read, mark_read


router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


@router.get("", response_model=None)
async def list_notifications(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: Optional[dict] = Depends(get_optional_user),
    limit: int = 50,
):
    collection = db["notifications"]
    user_id = current_user["_id"] if current_user else None
    cursor = (
        collection.find(
            {"$or": ([{"user_id": user_id}] if user_id else []) + [{"user_id": None}]}
        )
        .sort("created_at", -1)
        .limit(limit)
    )
    docs = await cursor.to_list(length=limit)
    return [
        {
            "id": str(d["_id"]),
            "title": d.get("title"),
            "message": d.get("message"),
            "type": d.get("type", "info"),
            "user_id": str(d["user_id"]) if d.get("user_id") else None,
            "link": d.get("link"),
            "read": d.get("read", False),
            "created_at": d.get("created_at"),
        }
        for d in docs
    ]


@router.post("", response_model=None)
async def create_notification(
    payload: NotificationCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # allow only admins to create arbitrary notifications
    if current_user.get("role", "user") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    return await create_notifications(
        db,
        title=payload.title,
        message=payload.message,
        notif_type=payload.type,
        user_ids=payload.user_ids,
        link=payload.link,
    )


@router.post("/mark-read-all", response_model=None)
async def mark_all(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    await mark_all_read(db, current_user["_id"])
    return {"ok": True}


@router.post("/{notification_id}/read", response_model=None)
async def mark_single(
    notification_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    try:
        ObjectId(notification_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid notification id")

    await mark_read(db, notification_id, current_user["_id"])
    return {"ok": True}

