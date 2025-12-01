from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from ..database import get_db
from ..schemas.zakat import ZakatCreate, ZakatOut
from ..utils.users import get_current_user

router = APIRouter(prefix="/zakat", tags=["Zakat"])

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_zakat(
    data: ZakatCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(get_current_user)
):
    zakat_collection = db["zakat_records"]
    user_id = current_user.get("_id")
    
    zakat_amount = round(float(data.assets_total) * 0.025, 2)
    
    zakat_data = {
        "user_id": user_id,
        "name": data.name,
        "assets_total": data.assets_total,
        "savings": data.savings,
        "gold_price_per_gram": data.gold_price_per_gram,
        "note": data.note,
        "type": data.type,
        "zakat_amount": zakat_amount,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    result = await zakat_collection.insert_one(zakat_data)
    
    return {
        "id": str(result.inserted_id),
        "user_id": str(user_id),
        "name": zakat_data["name"],
        "assets_total": zakat_data["assets_total"],
        "zakat_amount": zakat_data["zakat_amount"],
        "type": zakat_data["type"],
        "created_at": zakat_data["created_at"]
    }

@router.get("/", response_model=list)
async def list_zakat_records(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(get_current_user)
):
    zakat_collection = db["zakat_records"]
    user_id = current_user.get("_id")
    
    cursor = zakat_collection.find({"user_id": user_id}).sort("created_at", -1)
    records = await cursor.to_list(length=None)
    
    return [{
        "id": str(r["_id"]),
        "user_id": str(r.get("user_id")),
        "name": r.get("name"),
        "assets_total": r.get("assets_total"),
        "savings": r.get("savings"),
        "gold_price_per_gram": r.get("gold_price_per_gram"),
        "note": r.get("note"),
        "type": r.get("type"),
        "zakat_amount": r.get("zakat_amount"),
        "created_at": r.get("created_at")
    } for r in records]

@router.post("/calculate", response_model=dict, status_code=status.HTTP_200_OK)
async def calculate_and_save_zakat(
    data: ZakatCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(get_current_user)
):
    zakat_collection = db["zakat_records"]
    user_id = current_user.get("_id")
    
    zakat_amount = round(float(data.assets_total) * 0.025, 2)
    
    zakat_data = {
        "user_id": user_id,
        "name": data.name,
        "assets_total": data.assets_total,
        "savings": data.savings,
        "gold_price_per_gram": data.gold_price_per_gram,
        "note": data.note,
        "type": data.type,
        "zakat_amount": zakat_amount,
        "created_at": datetime.utcnow().isoformat()
    }
    
    await zakat_collection.insert_one(zakat_data)
    
    return {"zakat_due": zakat_amount, "type": data.type}

@router.get("/history", response_model=list)
async def zakat_history(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(get_current_user)
):
    zakat_collection = db["zakat_records"]
    user_id = current_user.get("_id")
    
    cursor = zakat_collection.find({"user_id": user_id}).sort("created_at", -1)
    records = await cursor.to_list(length=None)
    
    return [{
        "id": str(r["_id"]),
        "user_id": str(r.get("user_id")),
        "name": r.get("name"),
        "assets_total": r.get("assets_total"),
        "zakat_amount": r.get("zakat_amount"),
        "type": r.get("type"),
        "created_at": r.get("created_at")
    } for r in records]

@router.get("/{record_id}", response_model=dict)
async def get_single_zakat(
    record_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        obj_id = ObjectId(record_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid record ID")
    
    zakat_collection = db["zakat_records"]
    user_id = current_user.get("_id")
    
    record = await zakat_collection.find_one({"_id": obj_id, "user_id": user_id})
    
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zakat record not found")
    
    return {
        "id": str(record["_id"]),
        "user_id": str(record.get("user_id")),
        "name": record.get("name"),
        "assets_total": record.get("assets_total"),
        "savings": record.get("savings"),
        "gold_price_per_gram": record.get("gold_price_per_gram"),
        "note": record.get("note"),
        "type": record.get("type"),
        "zakat_amount": record.get("zakat_amount"),
        "created_at": record.get("created_at")
    }

@router.delete("/{record_id}")
async def delete_zakat(
    record_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        obj_id = ObjectId(record_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid record ID")
    
    zakat_collection = db["zakat_records"]
    user_id = current_user.get("_id")
    
    result = await zakat_collection.delete_one({"_id": obj_id, "user_id": user_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zakat record not found")
    
    return {"message": "Zakat record deleted successfully"}
