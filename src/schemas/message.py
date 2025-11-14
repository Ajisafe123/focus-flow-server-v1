from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class MessageCreate(BaseModel):
    conversationId: UUID
    text: Optional[str]
    senderId: Optional[UUID]
    senderType: str
    messageType: Optional[str] = "text"
    fileUrl: Optional[str] = None

class MessageOut(BaseModel):
    id: UUID
    conversation_id: UUID
    sender_type: str
    sender_id: Optional[UUID]
    message_text: Optional[str]
    message_type: Optional[str]
    file_url: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
