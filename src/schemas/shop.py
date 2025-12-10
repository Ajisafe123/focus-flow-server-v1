from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ShopCategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None

class ShopCategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None

class ShopCategoryRead(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    slug: Optional[str] = None
    created_at: datetime
    
class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    currency: str = "USD"
    image_urls: List[str] = []
    category_id: Optional[str] = None
    stock_quantity: int = 0

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    image_urls: Optional[List[str]] = None
    category_id: Optional[str] = None
    is_active: Optional[bool] = None
    stock_quantity: Optional[int] = None

class ProductRead(BaseModel):
    id: str
    name: str
    description: str
    price: float
    currency: str
    image_urls: List[str]
    category_id: Optional[str]
    is_active: bool
    stock_quantity: int
    created_at: datetime
    updated_at: datetime

class OrderCreate(BaseModel):
    items: List[Dict[str, Any]] # [{"product_id": "...", "quantity": 1}]
    shipping_address: Optional[Dict[str, Any]] = None
    payment_info: Optional[Dict[str, Any]] = None

class OrderRead(BaseModel):
    id: str
    user_id: Optional[str]
    items: List[Dict[str, Any]]
    total_amount: float
    status: str
    created_at: datetime
