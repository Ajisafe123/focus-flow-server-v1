from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MessageCreate(BaseModel):
    # Accept string IDs; router will coerce to ObjectId when valid.
    conversationId: str
    text: Optional[str]
    senderId: Optional[str]
    senderType: str
    messageType: Optional[str] = "text"
    fileUrl: Optional[str] = None


class MessageOut(BaseModel):
    id: str
    conversation_id: str
    sender_type: str
    sender_id: Optional[str]
    message_text: Optional[str]
    message_type: Optional[str]
    file_url: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
