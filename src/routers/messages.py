from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
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

@router.post("", response_model=dict)
async def send_message(
    payload: MessageCreate,
    file: Optional[UploadFile] = File(None),
    background_tasks: BackgroundTasks = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        conv_id = ObjectId(payload.conversationId)
    except:
        raise HTTPException(status_code=400, detail="Invalid conversationId")

    conversations_collection = db["conversations"]
    conv = await conversations_collection.find_one({"_id": conv_id})
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    file_url = payload.fileUrl
    if file:
        contents = await file.read()
        if len(contents) == 0 or len(contents) > MAX_UPLOAD_SIZE:
            raise HTTPException(status_code=413, detail="File too large or empty")
        key = upload_bytes_to_s3(contents, file.filename or f"upload-{uuid4().hex}", prefix="messages")
        file_url = generate_presigned_url(key, expires_in=3600*24)

    messages_collection = db["messages"]
    msg_data = {
        "conversation_id": conv_id,
        "message_text": payload.text,
        "sender_type": payload.senderType,
        "sender_id": payload.senderId,
        "message_type": payload.messageType or ("audio" if file else "text"),
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

    if background_tasks:
        background_tasks.add_task(
            manager.broadcast_room, str(conv_id),
            {"event": "receive_message", "data": {
                "id": str(result.inserted_id),
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

@router.get("/{conversation_id}/messages", response_model=List[dict])
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

@router.put("/read")
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

@router.put("/{message_id}")
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

@router.delete("/{message_id}")
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
