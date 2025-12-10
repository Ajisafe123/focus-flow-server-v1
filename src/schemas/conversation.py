from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ConversationCreate(BaseModel):
    # Accept any string here; we will coerce to ObjectId in the router when valid.
    userId: Optional[str]
    userName: Optional[str]
    userEmail: Optional[str]


class ConversationOut(BaseModel):
    id: str
    user_id: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
