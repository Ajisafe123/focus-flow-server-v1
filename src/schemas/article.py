"""Pydantic schemas for Articles"""
from pydantic import BaseModel, Field
from typing import Optional, List
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


class ArticleItem(BaseModel):
    id: PyObjectId = Field(alias="_id")
    title: str

    class Config:
        from_attributes = True
        populate_by_name = True


class ArticleCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool = True

    class Config:
        from_attributes = True


class ArticleCategoryCreate(ArticleCategoryBase):
    pass


class ArticleCategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True


class ArticleCategoryRead(ArticleCategoryBase):
    id: PyObjectId = Field(alias="_id")
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


class ArticleBase(BaseModel):
    title: str
    content: str
    excerpt: Optional[str] = None
    author: Optional[str] = None
    category_id: Optional[PyObjectId] = None
    cover_image_url: Optional[str] = None
    is_active: bool = True
    featured: bool = False

    class Config:
        from_attributes = True
        populate_by_name = True


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    excerpt: Optional[str] = None
    author: Optional[str] = None
    category_id: Optional[PyObjectId] = None
    cover_image_url: Optional[str] = None
    is_active: Optional[bool] = None
    featured: Optional[bool] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class ArticleRead(ArticleBase):
    id: PyObjectId = Field(alias="_id")
    view_count: int = 0
    favorite_count: int = 0
    is_favorite: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


class ArticleStats(BaseModel):
    total_articles: int
    total_views: int
    total_favorites: int
    top_featured: List[ArticleItem] = []
    top_viewed: List[ArticleItem] = []

    class Config:
        from_attributes = True
