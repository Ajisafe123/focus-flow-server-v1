from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from ..services.zakat_service import calculate_zakat_amount

async def create_zakat_record(db: AsyncIOMotorDatabase, user_id, data):
    zakat_amount, nisab = calculate_zakat_amount(
        data.assets_total,
        data.savings,
        data.gold_price_per_gram,
    )
    zakat_collection = db["zakat_records"]
    record = {
        "user_id": user_id,
        "name": data.name,
        "assets_total": data.assets_total,
        "savings": data.savings,
        "gold_price_per_gram": data.gold_price_per_gram,
        "nisab": nisab,
        "zakat_amount": zakat_amount,
        "note": data.note,
        "type": data.type,
        "zakat_due": data.zakat_due,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    result = await zakat_collection.insert_one(record)
    record["_id"] = result.inserted_id
    return record

async def get_user_zakat_records(db: AsyncIOMotorDatabase, user_id):
    zakat_collection = db["zakat_records"]
    cursor = zakat_collection.find({"user_id": user_id}).sort("created_at", -1)
    return await cursor.to_list(length=None)

async def get_zakat_by_id(db: AsyncIOMotorDatabase, record_id, user_id):
    try:
        obj_id = ObjectId(record_id)
    except:
        return None
    zakat_collection = db["zakat_records"]
    return await zakat_collection.find_one({"_id": obj_id, "user_id": user_id})

async def delete_zakat_record(db: AsyncIOMotorDatabase, record_id, user_id):
    record = await get_zakat_by_id(db, record_id, user_id)
    if not record:
        return None
    zakat_collection = db["zakat_records"]
    await zakat_collection.delete_one({"_id": record["_id"]})
    return record
