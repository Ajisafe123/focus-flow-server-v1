from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId


class MongoModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        from_attributes = True


class VideoCreate(BaseModel):
    title: str
    url: HttpUrl
    description: Optional[str] = None
    thumbnail: Optional[HttpUrl] = None
    duration: Optional[str] = None
    category: Optional[str] = None
    speaker: Optional[str] = None
    rating: Optional[float] = None
    reviews: Optional[int] = None
    views: Optional[int] = None
    tags: Optional[list[str]] = None
    release_date: Optional[str] = None
    featured: bool = False


class VideoUpdate(BaseModel):
    title: Optional[str] = None
    url: Optional[HttpUrl] = None
    description: Optional[str] = None
    thumbnail: Optional[HttpUrl] = None
    duration: Optional[str] = None
    category: Optional[str] = None
    speaker: Optional[str] = None
    rating: Optional[float] = None
    reviews: Optional[int] = None
    views: Optional[int] = None
    tags: Optional[list[str]] = None
    release_date: Optional[str] = None
    featured: Optional[bool] = None


class VideoRead(MongoModel):
    title: str
    url: str
    description: Optional[str] = None
    thumbnail: Optional[str] = None
    duration: Optional[str] = None
    category: Optional[str] = None
    speaker: Optional[str] = None
    rating: Optional[float] = None
    reviews: Optional[int] = None
    views: Optional[int] = None
    tags: Optional[list[str]] = None
    release_date: Optional[str] = None
    featured: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AudioCreate(BaseModel):
    title: str
    url: HttpUrl
    description: Optional[str] = None
    cover_image: Optional[HttpUrl] = None
    duration: Optional[str] = None
    category: Optional[str] = None
    speaker: Optional[str] = None
    rating: Optional[float] = None
    reviews: Optional[int] = None
    downloads: Optional[int] = None
    tags: Optional[list[str]] = None
    language: Optional[str] = None
    quality: Optional[str] = None
    release_date: Optional[str] = None
    file_size: Optional[str] = None
    featured: bool = False


class AudioUpdate(BaseModel):
    title: Optional[str] = None
    url: Optional[HttpUrl] = None
    description: Optional[str] = None
    cover_image: Optional[HttpUrl] = None
    duration: Optional[str] = None
    category: Optional[str] = None
    speaker: Optional[str] = None
    rating: Optional[float] = None
    reviews: Optional[int] = None
    downloads: Optional[int] = None
    tags: Optional[list[str]] = None
    language: Optional[str] = None
    quality: Optional[str] = None
    release_date: Optional[str] = None
    file_size: Optional[str] = None
    featured: Optional[bool] = None


class AudioRead(MongoModel):
    title: str
    url: str
    description: Optional[str] = None
    cover_image: Optional[str] = None
    duration: Optional[str] = None
    category: Optional[str] = None
    speaker: Optional[str] = None
    rating: Optional[float] = None
    reviews: Optional[int] = None
    downloads: Optional[int] = None
    tags: Optional[list[str]] = None
    language: Optional[str] = None
    quality: Optional[str] = None
    release_date: Optional[str] = None
    file_size: Optional[str] = None
    featured: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

