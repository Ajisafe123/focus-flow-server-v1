from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from typing import List, Optional
from uuid import UUID
from datetime import datetime
import io
from uuid import uuid4

from src.database import get_db
from src.schemas.message import MessageCreate, MessageOut
from src.models.message import Message
from src.models.conversation import Conversation
from src.utils.s3_clients import upload_bytes_to_s3, generate_presigned_url
from src.utils.ws_manager import manager

router = APIRouter(prefix="/api/messages", tags=["Messages"])
MAX_UPLOAD_SIZE = 50 * 1024 * 1024

@router.post("", response_model=MessageOut)
async def send_message(
    payload: MessageCreate,
    file: Optional[UploadFile] = File(None),
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db)
):
    conv_id = payload.conversationId
    if not isinstance(conv_id, UUID):
        raise HTTPException(status_code=400, detail="Invalid conversationId UUID")

    result = await db.execute(select(Conversation).where(Conversation.id == conv_id))
    conv = result.scalars().first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    file_url = payload.fileUrl
    if file:
        contents = await file.read()
        if len(contents) == 0 or len(contents) > MAX_UPLOAD_SIZE:
            raise HTTPException(status_code=413, detail="File too large or empty")
        key = upload_bytes_to_s3(contents, file.filename or f"upload-{uuid4().hex}", prefix="messages")
        file_url = generate_presigned_url(key, expires_in=3600*24)

    msg = Message(
        conversation_id=conv.id,
        message_text=payload.text,
        sender_type=payload.senderType,
        sender_id=payload.senderId,
        message_type=payload.messageType or ("audio" if file else "text"),
        file_url=file_url,
        created_at=datetime.utcnow()
    )
    db.add(msg)
    conv.updated_at = datetime.utcnow()
    db.add(conv)

    await db.commit()
    await db.refresh(msg)

    background_tasks.add_task(
        manager.broadcast_room, str(conv.id),
        {"event": "receive_message", "data": {
            "id": str(msg.id),
            "conversation_id": str(msg.conversation_id),
            "sender_type": msg.sender_type,
            "sender_id": str(msg.sender_id) if msg.sender_id else None,
            "message_text": msg.message_text,
            "message_type": msg.message_type,
            "file_url": msg.file_url,
            "status": msg.status,
            "created_at": msg.created_at.isoformat()
        }}
    )

    return msg

@router.get("/{conversation_id}/messages", response_model=List[MessageOut])
async def get_messages(conversation_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at.asc())
    )
    msgs = result.scalars().all()
    return msgs

@router.put("/read")
async def mark_as_read(conversationId: UUID, messageIds: List[UUID], db: AsyncSession = Depends(get_db)):
    await db.execute(
        update(Message)
        .where(Message.conversation_id == conversationId, Message.id.in_(messageIds))
        .values(status="read")
    )
    await db.commit()
    return {"ok": True}

@router.put("/{message_id}")
async def update_message(message_id: UUID, text: Optional[str] = Form(None), db: AsyncSession = Depends(get_db)):
    msg = await db.get(Message, message_id)
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    if text:
        msg.message_text = text
        msg.updated_at = datetime.utcnow()
        db.add(msg)
        await db.commit()
        await db.refresh(msg)
        await manager.broadcast_room(str(msg.conversation_id), {"event": "update_message", "data": {
            "id": str(msg.id), "message_text": msg.message_text
        }})
    return msg

@router.delete("/{message_id}")
async def delete_message(message_id: UUID, db: AsyncSession = Depends(get_db)):
    msg = await db.get(Message, message_id)
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    conv_id = msg.conversation_id
    await db.delete(msg)
    await db.commit()
    await manager.broadcast_room(str(conv_id), {"event": "delete_message", "data": {"id": str(message_id)}})
    return {"ok": True}
