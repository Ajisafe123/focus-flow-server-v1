from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class NotificationCreate(BaseModel):
    title: str
    message: str
    type: str = Field(default="info", description="info|success|warning|error")
    user_ids: Optional[List[str]] = None  # None => broadcast to all
    link: Optional[str] = None


class NotificationOut(BaseModel):
    id: str
    title: str
    message: str
    type: str
    user_id: Optional[str] = None
    link: Optional[str] = None
    read: bool = False
    created_at: datetime

