from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class FileOut(BaseModel):
    id: UUID
    message_id: Optional[UUID]
    file_name: Optional[str]
    file_type: Optional[str]
    file_size: Optional[int]
    file_url: Optional[str]
    uploaded_at: datetime

    class Config:
        from_attributes = True
