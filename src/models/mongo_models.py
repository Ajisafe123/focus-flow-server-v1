"""MongoDB Models using Pydantic"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, schema: Dict[str, Any], model_type) -> Dict[str, Any]:
        json_schema = super().__get_pydantic_json_schema__(schema, model_type)
        json_schema = {**json_schema, "examples": ["507f1f77bcf86cd799439011"]}
        return json_schema


# User Models
class UserInDB(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    email: str
    username: str
    hashed_password: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    status: str = "active"
    role: str = "user"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    reset_sent_at: Optional[datetime] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    ip_address: Optional[str] = None
    location_accuracy: Optional[str] = None

    class Config:
        populate_by_name = True


# Dua Models
class DuaCategoryInDB(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


class DuaInDB(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    title: str
    arabic: str
    transliteration: Optional[str] = None
    translation: Optional[str] = None
    notes: Optional[str] = None
    benefits: Optional[str] = None
    source: Optional[str] = None
    category_id: Optional[PyObjectId] = None
    audio_path: Optional[str] = None
    is_active: bool = True
    featured: bool = False
    arabic_segments_json: Optional[List[Dict]] = None
    transliteration_segments_json: Optional[List[Dict]] = None
    translation_segments_json: Optional[List[Dict]] = None
    view_count: int = 0
    favorite_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


class DuaViewInDB(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    dua_id: PyObjectId
    user_id: Optional[PyObjectId] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


class DuaFavoriteInDB(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    dua_id: PyObjectId
    user_id: PyObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


class DuaShareLinkInDB(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    dua_id: PyObjectId
    short_code: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


# Hadith Models
class HadithCategoryInDB(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    name: str
    description: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


class HadithInDB(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    arabic: str
    translation: Optional[str] = None
    narrator: Optional[str] = None
    book: Optional[str] = None
    number: Optional[str] = None
    status: Optional[str] = None
    rating: float = 0.0
    category_id: Optional[PyObjectId] = None
    is_active: bool = True
    featured: bool = False
    view_count: int = 0
    favorite_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


class HadithViewInDB(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    hadith_id: PyObjectId
    user_id: Optional[PyObjectId] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


class HadithFavoriteInDB(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    hadith_id: PyObjectId
    user_id: PyObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


# Article Models
class ArticleCategoryInDB(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


class ArticleInDB(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    title: str
    content: str
    excerpt: Optional[str] = None
    author: Optional[str] = None
    category_id: Optional[PyObjectId] = None
    cover_image_url: Optional[str] = None
    is_active: bool = True
    featured: bool = False
    view_count: int = 0
    favorite_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


class ArticleViewInDB(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    article_id: PyObjectId
    user_id: Optional[PyObjectId] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


class ArticleFavoriteInDB(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    article_id: PyObjectId
    user_id: PyObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
