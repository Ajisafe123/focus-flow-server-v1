from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from bson import ObjectId


class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, info=None):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return str(ObjectId(v))

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        return {"type": "string"}


class HadithBase(BaseModel):
    arabic: Optional[str] = None
    translation: Optional[str] = None
    narrator: Optional[str] = None
    english: Optional[Dict[str, Any]] = None
    book: Optional[str] = None
    number: Optional[str] = None
    status: Optional[str] = None
    rating: Optional[float] = None
    category_id: Optional[str] = None
    is_active: Optional[bool] = True
    featured: Optional[bool] = False

    class Config:
        from_attributes = True
        populate_by_name = True


class HadithCreate(HadithBase):
    pass


class HadithUpdate(BaseModel):
    arabic: Optional[str] = None
    translation: Optional[str] = None
    narrator: Optional[str] = None
    english: Optional[Dict[str, Any]] = None
    book: Optional[str] = None
    number: Optional[str] = None
    status: Optional[str] = None
    rating: Optional[float] = None
    category_id: Optional[str] = None
    is_active: Optional[bool] = None
    featured: Optional[bool] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class HadithRead(HadithBase):
    id: PyObjectId = Field(alias="_id")
    view_count: Optional[int] = 0
    favorite_count: Optional[int] = 0
    is_favorite: Optional[bool] = False

    @field_validator("view_count", "favorite_count", mode="before")
    def convert_none_to_zero(cls, v):
        return v or 0

    class Config:
        from_attributes = True
        populate_by_name = True


class HadithCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: Optional[bool] = True

    class Config:
        from_attributes = True


class HadithCategoryCreate(HadithCategoryBase):
    pass


class HadithCategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True


class HadithCategoryRead(HadithCategoryBase):
    id: PyObjectId = Field(alias="_id")

    class Config:
        from_attributes = True
        populate_by_name = True


class HadithItem(BaseModel):
    id: PyObjectId = Field(alias="_id")
    number: str

    class Config:
        from_attributes = True
        populate_by_name = True


class HadithStats(BaseModel):
    total_hadiths: int
    total_views: int
    total_favorites: int
    total_featured: int
    top_featured: List[HadithItem] = []
    top_viewed: List[HadithItem] = []

    class Config:
        from_attributes = True
