from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from datetime import datetime

from src.database import get_db
from src.schemas.conversation import ConversationCreate, ConversationOut
from src.models.conversation import Conversation
from src.models.users import User

router = APIRouter(prefix="/api/conversations", tags=["Conversations"])


@router.post("", response_model=ConversationOut)
async def create_conversation(payload: ConversationCreate, db: AsyncSession = Depends(get_db)):
    user_id = payload.userId
    if not user_id and payload.userEmail:
        result = await db.execute(select(User).where(User.email == payload.userEmail))
        user = result.scalars().first()
        if not user:
            user = User(
                email=payload.userEmail,
                username=payload.userName or "Guest",
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        user_id = user.id

    conv = Conversation(user_id=user_id)
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    return conv


@router.get("/{conversation_id}", response_model=ConversationOut)
async def get_conv(conversation_id: UUID, db: AsyncSession = Depends(get_db)):
    conv = await db.get(Conversation, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


@router.put("/{conversation_id}/status", response_model=ConversationOut)
async def update_status(conversation_id: UUID, status: str, db: AsyncSession = Depends(get_db)):
    conv = await db.get(Conversation, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    conv.status = status
    conv.updated_at = datetime.utcnow()
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    return conv