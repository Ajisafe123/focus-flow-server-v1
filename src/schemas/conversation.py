from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class ConversationCreate(BaseModel):
    userId: Optional[UUID]
    userName: Optional[str]
    userEmail: Optional[str]

class ConversationOut(BaseModel):
    id: UUID
    user_id: Optional[UUID]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
