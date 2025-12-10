from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks, Body
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import List, Optional
from datetime import datetime
from uuid import uuid4

from ..database import get_db
from ..schemas.message import MessageCreate, MessageOut
from ..utils.s3_clients import upload_bytes_to_s3, generate_presigned_url
from ..utils.ws_manager import manager

router = APIRouter(prefix="/api/messages", tags=["Messages"])
MAX_UPLOAD_SIZE = 50 * 1024 * 1024

@router.post("", response_model=None)
async def send_message(
    payload: dict | None = Body(default=None),
    background_tasks: BackgroundTasks = None,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    body = payload or {}
    print(f"DEBUG: send_message payload: {body}")
    conv_id_raw = body.get("conversationId")
    if not conv_id_raw:
        raise HTTPException(status_code=400, detail="conversationId is required")
    try:
        conv_id = ObjectId(conv_id_raw)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid conversationId")

    conversations_collection = db["conversations"]
    conv = await conversations_collection.find_one({"_id": conv_id})
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    file_url = body.get("fileUrl")

    messages_collection = db["messages"]
    message_text = body.get("text") or ""
    sender_type = body.get("senderType") or "user"
    sender_id = body.get("senderId")
    message_type = body.get("messageType") or ("audio" if file_url else "text")

    msg_data = {
        "conversation_id": conv_id,
        "message_text": message_text,
        "sender_type": sender_type,
        "sender_id": sender_id,
        "message_type": message_type,
        "file_url": file_url,
        "status": "sent",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    result = await messages_collection.insert_one(msg_data)
    
    # Update conversation updated_at
    await conversations_collection.update_one(
        {"_id": conv_id},
        {"$set": {"updated_at": datetime.utcnow().isoformat()}}
    )

    temp_id = body.get("tempId")

    if background_tasks:
        background_tasks.add_task(
            manager.broadcast_room, str(conv_id),
            {"event": "receive_message", "data": {
                "id": str(result.inserted_id),
                "tempId": temp_id,
                "conversation_id": str(conv_id),
                "sender_type": msg_data["sender_type"],
                "sender_id": msg_data["sender_id"],
                "message_text": msg_data["message_text"],
                "message_type": msg_data["message_type"],
                "file_url": msg_data["file_url"],
                "status": msg_data["status"],
                "created_at": msg_data["created_at"]
            }}
        )

    # Notify admin if message is from user
    if msg_data["sender_type"] == "user":
        from ..utils.notifications import create_notifications
        try:
             # Shorten message for preview
            preview = message_text[:50] + "..." if len(message_text) > 50 else message_text
            if not preview and file_url:
                preview = f"Sent a {message_type}"

            await create_notifications(
                db,
                title="New Chat Message",
                message=f"New message: {preview}",
                notif_type="chat",
                recipient_role="admin",
                link="/admin/chat" # or deep link to conversation
            )
        except Exception as e:
            print(f"Failed to create chat notification: {e}")

    return {
        "id": str(result.inserted_id),
        "conversation_id": str(conv_id),
        "sender_type": msg_data["sender_type"],
        "sender_id": msg_data["sender_id"],
        "message_text": msg_data["message_text"],
        "message_type": msg_data["message_type"],
        "file_url": msg_data["file_url"],
        "status": msg_data["status"],
        "created_at": msg_data["created_at"]
    }

@router.get("/{conversation_id}/messages", response_model=None)
async def get_messages(conversation_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    try:
        conv_id = ObjectId(conversation_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid conversation ID")
    
    messages_collection = db["messages"]
    cursor = messages_collection.find({"conversation_id": conv_id}).sort("created_at", 1)
    msgs = await cursor.to_list(length=None)
    
    return [{
        "id": str(m["_id"]),
        "conversation_id": str(m.get("conversation_id")),
        "sender_type": m.get("sender_type"),
        "sender_id": m.get("sender_id"),
        "message_text": m.get("message_text"),
        "message_type": m.get("message_type"),
        "file_url": m.get("file_url"),
        "status": m.get("status"),
        "created_at": m.get("created_at"),
        "updated_at": m.get("updated_at")
    } for m in msgs]

@router.post("/{conversation_id}/read", response_model=None)
async def mark_conversation_read(
    conversation_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        conv_id = ObjectId(conversation_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid conversation ID")
    
    messages_collection = db["messages"]
    conversations_collection = db["conversations"]

    # Update all unread messages to read
    result = await messages_collection.update_many(
        {"conversation_id": conv_id, "status": {"$ne": "read"}},
        {"$set": {"status": "read", "updated_at": datetime.utcnow().isoformat()}}
    )
    
    # Also reset unread count on conversation if we track it there (optional, but good practice)
    # For now just broadcast
    
    if result.modified_count > 0:
        if manager:
            await manager.broadcast_room(
                str(conv_id),
                {"event": "messages_read", "data": {"conversation_id": str(conv_id)}}
            )
            
    return {"ok": True, "marked_count": result.modified_count}

@router.put("/read", response_model=None)
async def mark_as_read(
    conversationId: str,
    messageIds: List[str],
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        conv_id = ObjectId(conversationId)
        msg_ids = [ObjectId(id) for id in messageIds]
    except:
        raise HTTPException(status_code=400, detail="Invalid IDs")
    
    messages_collection = db["messages"]
    await messages_collection.update_many(
        {"conversation_id": conv_id, "_id": {"$in": msg_ids}},
        {"$set": {"status": "read"}}
    )
    
    return {"ok": True}

@router.put("/{message_id}", response_model=None)
async def update_message(
    message_id: str,
    text: Optional[str] = Form(None),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        msg_id = ObjectId(message_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid message ID")
    
    messages_collection = db["messages"]
    msg = await messages_collection.find_one({"_id": msg_id})
    
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    
    if text:
        await messages_collection.update_one(
            {"_id": msg_id},
            {"$set": {
                "message_text": text,
                "updated_at": datetime.utcnow().isoformat()
            }}
        )
        
        updated_msg = await messages_collection.find_one({"_id": msg_id})
        
        if manager:
            await manager.broadcast_room(
                str(msg.get("conversation_id")),
                {"event": "update_message", "data": {
                    "id": str(msg_id),
                    "message_text": updated_msg.get("message_text")
                }}
            )
    
    return {
        "id": str(msg["_id"]),
        "message_text": msg.get("message_text"),
        "status": msg.get("status"),
        "created_at": msg.get("created_at")
    }

@router.delete("/{message_id}", response_model=None)
async def delete_message(message_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    try:
        msg_id = ObjectId(message_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid message ID")
    
    messages_collection = db["messages"]
    msg = await messages_collection.find_one({"_id": msg_id})
    
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    
    conv_id = msg.get("conversation_id")
    
    await messages_collection.delete_one({"_id": msg_id})
    
    if manager:
        await manager.broadcast_room(
            str(conv_id),
            {"event": "delete_message", "data": {"id": str(message_id)}}
        )
    
    return {"ok": True}
