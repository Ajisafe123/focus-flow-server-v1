from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import List, Optional
from datetime import datetime
from ..database import get_db
from ..utils.users import get_current_user
from ..schemas.donation import (
    DonationCreate,
    DonationRead,
)

router = APIRouter(prefix="/api", tags=["Donations"])

def ensure_object_id(id_str: str):
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")

def map_donation(doc):
    if not doc:
        return None
    doc["id"] = str(doc["_id"])
    return doc

def admin_required(user: dict):
    if not user or user.get("role", "").lower() != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

@router.post("/donations", response_model=DonationRead)
async def create_donation(
    payload: DonationCreate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    data = payload.model_dump()
    data["created_at"] = datetime.utcnow()
    data["status"] = "completed" # Mock success
    
    res = await db["donations"].insert_one(data)
    doc = await db["donations"].find_one({"_id": res.inserted_id})
    return DonationRead(**map_donation(doc))

@router.get("/donations", response_model=List[DonationRead])
async def list_donations(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    limit: int = 20,
    skip: int = 0
):
    admin_required(current_user)
    
    cursor = db["donations"].find({}).sort("created_at", -1).skip(skip).limit(limit)
    items = []
    async for doc in cursor:
        items.append(DonationRead(**map_donation(doc)))
    return items
