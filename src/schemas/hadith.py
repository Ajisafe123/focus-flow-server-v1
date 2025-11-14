from pydantic import BaseModel, field_validator
from typing import Optional, List

class HadithBase(BaseModel):
    arabic: str
    translation: Optional[str] = None
    narrator: Optional[str] = None
    book: Optional[str] = None
    number: Optional[str] = None
    status: Optional[str] = None
    rating: Optional[float] = None
    category_id: Optional[int] = None
    is_active: Optional[bool] = True
    featured: Optional[bool] = False

class HadithCreate(HadithBase):
    pass

class HadithUpdate(BaseModel):
    arabic: Optional[str] = None
    translation: Optional[str] = None
    narrator: Optional[str] = None
    book: Optional[str] = None
    number: Optional[str] = None
    status: Optional[str] = None
    rating: Optional[float] = None
    category_id: Optional[int] = None
    is_active: Optional[bool] = None
    featured: Optional[bool] = None

class HadithRead(HadithBase):
    id: int
    view_count: Optional[int] = 0
    favorite_count: Optional[int] = 0
    is_favorite: Optional[bool] = False 

    @field_validator("view_count", "favorite_count", mode="before")
    def convert_none_to_zero(cls, v):
        return v or 0

    class Config:
        from_attributes = True 

class HadithCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: Optional[bool] = True

class HadithCategoryCreate(HadithCategoryBase):
    pass

class HadithCategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class HadithCategoryRead(HadithCategoryBase):
    id: int

    class Config:
        from_attributes = True

class HadithItem(BaseModel):
    id: int
    number: str 

class HadithStats(BaseModel):
    total_hadiths: int
    total_views: int
    total_favorites: int
    total_featured: int
    top_featured: List[HadithItem]
    top_viewed: List[HadithItem]