from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
from .ws_manager import manager


async def create_notifications(
    db: AsyncIOMotorDatabase,
    title: str,
    message: str,
    notif_type: str = "info",
    user_ids: Optional[List[str]] = None,
    link: Optional[str] = None,
    recipient_role: Optional[str] = None,
):
    """
    Persist notifications and broadcast over websockets.
    If user_ids is None or empty AND recipient_role is None, treat as a global notification.
    """
    collection = db["notifications"]
    now = datetime.utcnow()
    
    # If role specified, we create one doc for that role (shared)
    if recipient_role:
        doc = {
            "title": title,
            "message": message,
            "type": notif_type,
            "user_id": None,
            "recipient_role": recipient_role,
            "link": link,
            "read": False,
            "created_at": now,
        }
        res = await collection.insert_one(doc)
        # Broadcast to role room
        room = f"notifications:role:{recipient_role}"
        payload = {
            "id": str(res.inserted_id),
            "title": title,
            "message": message,
            "type": notif_type,
            "recipient_role": recipient_role,
            "link": link,
            "read": False,
            "created_at": now.isoformat(),
        }
        await manager.broadcast_room(room, {"event": "notification", "data": payload})
        return [payload]

    targets = user_ids or [None]
    inserted = []

    for uid in targets:
        doc = {
            "title": title,
            "message": message,
            "type": notif_type,
            "user_id": ObjectId(uid) if uid else None,
            "recipient_role": None,
            "link": link,
            "read": False,
            "created_at": now,
        }
        res = await collection.insert_one(doc)
        payload = {
            "id": str(res.inserted_id),
            "title": title,
            "message": message,
            "type": notif_type,
            "user_id": uid,
            "link": link,
            "read": False,
            "created_at": now.isoformat(),
        }
        room = f"notifications:{uid}" if uid else "notifications:all"
        inserted.append(payload)
        # fire-and-forget websocket broadcast; ignore failures
        await manager.broadcast_room(room, {"event": "notification", "data": payload})

    return inserted


async def mark_all_read(db: AsyncIOMotorDatabase, user_id: ObjectId):
    collection = db["notifications"]
    await collection.update_many(
        {"$or": [{"user_id": user_id}, {"user_id": None}]},
        {"$set": {"read": True}},
    )


async def mark_read(db: AsyncIOMotorDatabase, notif_id: str, user_id: ObjectId):
    collection = db["notifications"]
    await collection.update_one(
        {"_id": ObjectId(notif_id), "$or": [{"user_id": user_id}, {"user_id": None}]},
        {"$set": {"read": True}},
    )

