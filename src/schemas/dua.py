from pydantic import BaseModel
from typing import Optional, Dict

class DuaBase(BaseModel):
    title: str
    arabic: str
    transliteration: Optional[str] = None
    translation: Optional[str] = None
    notes: Optional[str] = None
    benefits: Optional[str] = None
    source: Optional[str] = None
    category: str
    is_active: Optional[bool] = True

class DuaRead(DuaBase):
    id: int
    audio_map: Optional[Dict[str, str]] = None

    class Config:
        from_attributes = True
