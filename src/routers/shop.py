from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..database import get_db
from ..utils.users import get_current_user
from ..schemas.shop import (
    ProductCreate,
    ProductUpdate,
    ProductRead,
    OrderCreate,
    OrderRead,
)

router = APIRouter(prefix="/api", tags=["Shop"])

def ensure_object_id(id_str: str):
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")

def map_product(doc):
    if not doc:
        return None
    doc["id"] = str(doc["_id"])
    return doc

def map_order(doc):
    if not doc:
        return None
    doc["id"] = str(doc["_id"])
    doc["user_id"] = str(doc["user_id"]) if doc.get("user_id") else None
    return doc

def admin_required(user: dict):
    if not user or user.get("role", "").lower() != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

# --- Products ---

@router.get("/products", response_model=List[ProductRead])
async def list_products(
    db: AsyncIOMotorDatabase = Depends(get_db),
    category_id: Optional[str] = None,
    limit: int = 20,
    skip: int = 0
):
    query = {"is_active": True}
    if category_id:
        query["category_id"] = ensure_object_id(category_id)
        
    cursor = db["products"].find(query).skip(skip).limit(limit).sort("created_at", -1)
    products = []
    async for doc in cursor:
        products.append(ProductRead(**map_product(doc)))
    return products

@router.get("/products/{product_id}", response_model=ProductRead)
async def get_product(
    product_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    pid = ensure_object_id(product_id)
    doc = await db["products"].find_one({"_id": pid, "is_active": True})
    if not doc:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductRead(**map_product(doc))

@router.post("/products", response_model=ProductRead)
async def create_product(
    payload: ProductCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    admin_required(current_user)
    data = payload.model_dump()
    data["created_at"] = datetime.utcnow()
    data["updated_at"] = datetime.utcnow()
    data["is_active"] = True
    if data.get("category_id"):
        data["category_id"] = ensure_object_id(data["category_id"])
        
    res = await db["products"].insert_one(data)
    doc = await db["products"].find_one({"_id": res.inserted_id})
    return ProductRead(**map_product(doc))

# --- Orders ---

@router.post("/orders", response_model=OrderRead)
async def create_order(
    payload: OrderCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user) # Optional auth for guests?
    # actually, usually shop requires auth or guest checkout. Let's assume auth for now or handle guest.
    # The schema has user_id optional.
):
    user_id = current_user["_id"] if current_user else None
    
    # Calculate total (mock logic, ideally verify prices from DB)
    # For now, trust frontend payload or simple sum if we fetched products.
    # PROPER IMPLEMENTATION: Fetch products to get prices.
    
    item_details = []
    total_amount = 0.0
    
    for item in payload.items:
        pid = ensure_object_id(item["product_id"])
        p_doc = await db["products"].find_one({"_id": pid})
        if not p_doc:
            continue # or raise error
        
        # Check stock?
        
        price = p_doc["price"]
        qty = item["quantity"]
        total_amount += price * qty
        
        item_details.append({
            "product_id": str(pid),
            "name": p_doc["name"],
            "quantity": qty,
            "price_at_purchase": price
        })
        
    data = {
        "user_id": user_id,
        "items": item_details,
        "total_amount": total_amount,
        "currency": "USD",
        "status": "pending",
        "shipping_address": payload.shipping_address,
        "payment_info": payload.payment_info,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    res = await db["orders"].insert_one(data)
    doc = await db["orders"].find_one({"_id": res.inserted_id})
    return OrderRead(**map_order(doc))
