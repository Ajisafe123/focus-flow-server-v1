from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any
import json
from io import StringIO
import uuid

class DuaSegment(BaseModel):
    text: str 
    start_time: float
    end_time: float
    type: Optional[str] = None
    
    class Config:
        from_attributes = True

class DuaReadSegmented(BaseModel):
    id: int
    title: Optional[str] = None
    audio_path: Optional[str] = None
    arabic_segments: List[DuaSegment] 
    transliteration_segments: Optional[List[DuaSegment]] = None
    translation_segments: Optional[List[DuaSegment]] = None
    
    class Config:
        from_attributes = True 

class DuaBase(BaseModel):
    title: str
    arabic: str
    transliteration: Optional[str] = None
    translation: Optional[str] = None
    notes: Optional[str] = None
    benefits: Optional[str] = None
    source: Optional[str] = None
    category_id: Optional[int] = None
    is_active: Optional[bool] = True
    featured: Optional[bool] = False
    
    arabic_segments_json: Optional[Any] = None 
    transliteration_segments_json: Optional[Any] = None
    translation_segments_json: Optional[Any] = None

    @field_validator(
        "arabic_segments_json", 
        "transliteration_segments_json", 
        "translation_segments_json", 
        mode="before"
    )
    def parse_json_string(cls, v):
        if isinstance(v, str) and v.strip():
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return None 
        return v
    
    class Config:
        from_attributes = True

class DuaCreate(DuaBase):
    pass

class DuaUpdate(BaseModel):
    title: Optional[str] = None
    arabic: Optional[str] = None
    transliteration: Optional[str] = None
    translation: Optional[str] = None
    notes: Optional[str] = None
    benefits: Optional[str] = None
    source: Optional[str] = None
    category_id: Optional[int] = None
    is_active: Optional[bool] = None
    featured: Optional[bool] = None
    
    arabic_segments_json: Optional[Any] = None 
    transliteration_segments_json: Optional[Any] = None
    translation_segments_json: Optional[Any] = None
    
    @field_validator(
        "arabic_segments_json", 
        "transliteration_segments_json", 
        "translation_segments_json", 
        mode="before"
    )
    def parse_json_string(cls, v):
        if isinstance(v, str) and v.strip():
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return None
        return v
    
    class Config:
        from_attributes = True

class DuaRead(DuaBase):
    id: int
    audio_path: Optional[str] = None
    view_count: Optional[int] = 0
    favorite_count: Optional[int] = 0
    is_favorite: Optional[bool] = False 
    
    @field_validator("view_count", "favorite_count", mode="before")
    def convert_none_to_zero(cls, v):
        return v or 0

    class Config:
        from_attributes = True 

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = True

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None

class CategoryRead(CategoryBase):
    id: int

    class Config:
        from_attributes = True

class DuaItem(BaseModel):
    id: int
    title: str

class DuaStats(BaseModel):
    total_duas: int
    total_views: int
    total_favorites: int
    top_featured: List[DuaItem]
    top_viewed: List[DuaItem]