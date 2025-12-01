from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import date, datetime

async def get_or_create_count(db: AsyncIOMotorDatabase, user_id: str):
    dhikr_collection = db["dhikr_counts"]
    count = await dhikr_collection.find_one({"user_id": user_id})
    if not count:
        insert_data = {
            "user_id": user_id,
            "count": 0,
            "last_reset": date.today().isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }
        result = await dhikr_collection.insert_one(insert_data)
        count = await dhikr_collection.find_one({"_id": result.inserted_id})
    return count

async def increment_dhikr(db: AsyncIOMotorDatabase, user_id: str):
    count = await get_or_create_count(db, user_id)
    dhikr_collection = db["dhikr_counts"]
    await dhikr_collection.update_one(
        {"_id": count["_id"]},
        {"$inc": {"count": 1}}
    )
    return await get_or_create_count(db, user_id)

async def reset_dhikr(db: AsyncIOMotorDatabase, user_id: str):
    count = await get_or_create_count(db, user_id)
    dhikr_collection = db["dhikr_counts"]
    await dhikr_collection.update_one(
        {"_id": count["_id"]},
        {"$set": {
            "count": 0,
            "last_reset": date.today().isoformat()
        }}
    )
    return await get_or_create_count(db, user_id)