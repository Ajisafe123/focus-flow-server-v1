"""MongoDB Models using Pydantic"""
from pydantic import BaseModel, Field, GetJsonSchemaHandler, field_validator, field_serializer
from pydantic_core import core_schema
from typing import Optional, List, Dict, Any, Annotated
from datetime import datetime
from bson import ObjectId
import json


class PyObjectId(str):
    """Custom type for MongoDB ObjectId that serializes to string"""
    
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.str_schema(),
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda v: str(v) if isinstance(v, ObjectId) else v,
                return_schema=core_schema.str_schema(),
            ),
        )

    @classmethod
    def validate(cls, v):
        if v is None or v == "":
            return None
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str):
            if not ObjectId.is_valid(v):
                raise ValueError("Invalid objectid")
            return v
        raise ValueError("Invalid objectid type")

    @classmethod
    def __get_pydantic_json_schema__(cls, schema: Dict[str, Any], handler: GetJsonSchemaHandler) -> Dict[str, Any]:
        json_schema = handler(schema)
        json_schema = {**json_schema, "examples": ["507f1f77bcf86cd799439011"], "type": "string"}
        return json_schema


def convert_objectid_to_str(obj):
    """Recursively convert ObjectId instances to strings in dictionaries and lists"""
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: convert_objectid_to_str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid_to_str(item) for item in obj]
    return obj


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
    category_id: Optional[str] = None
    audio_path: Optional[str] = None
    is_active: bool = True
    featured: bool = False
    arabic_segments_json: Optional[List[Dict]] = None
    transliteration_segments_json: Optional[List[Dict]] = None
    translation_segments_json: Optional[List[Dict]] = None
    view_count: int = 0
    favorite_count: int = 0
    is_favorite: bool = False
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
    category_id: Optional[str] = None
    is_active: bool = True
    featured: bool = False
    view_count: int = 0
    favorite_count: int = 0
    is_favorite: bool = False
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
    category_id: Optional[str] = None
    cover_image_url: Optional[str] = None
    is_active: bool = True
    featured: bool = False
    view_count: int = 0
    favorite_count: int = 0
    is_favorite: bool = False
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


# Shop Models
class ShopCategoryInDB(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    slug: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


class ProductInDB(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    name: str
    description: str
    price: float
    currency: str = "USD"
    image_urls: List[str] = []
    category_id: Optional[str] = None
    is_active: bool = True
    stock_quantity: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


class OrderInDB(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    user_id: Optional[PyObjectId] = None
    items: List[Dict[str, Any]]  # stores product_id, quantity, price_at_purchase
    total_amount: float
    currency: str = "USD"
    status: str = "pending"  # pending, paid, shipped, cancelled
    shipping_address: Optional[Dict[str, Any]] = None
    payment_info: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


# Donation Models
class DonationInDB(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    donor_name: Optional[str] = "Anonymous"
    donor_email: Optional[str] = None
    amount: float
    currency: str = "USD"
    message: Optional[str] = None
    payment_method: Optional[str] = None
    status: str = "completed"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
# Contact Models
class ContactMessageInDB(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    name: str
    email: str
    subject: str
    message: str
    is_read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


# Notification Models
class NotificationInDB(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    type: str  # "login", "contact", "chat", "system"
    title: str
    message: str
    recipient_role: str = "admin"  # or user_id
    is_read: bool = False
    link: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True

