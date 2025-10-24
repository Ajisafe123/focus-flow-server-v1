from pydantic import BaseModel
from typing import Optional, Dict

class HadithSchema(BaseModel):
    id: int
    book: Optional[str] = None
    hadith_number: Optional[int] = None
    narrator: Optional[str] = None
    arabic: str
    english: Optional[Dict[str, str]] = None
    category: Optional[str] = None
    source: Optional[str] = None
    book_id: Optional[int] = None
    chapter_id: Optional[int] = None
    id_in_book: Optional[int] = None

    class Config:
        from_attributes = True
