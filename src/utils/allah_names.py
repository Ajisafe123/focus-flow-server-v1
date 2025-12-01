"""MongoDB CRUD operations for Allah Names (99 Names)"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import List, Optional
from datetime import datetime
import random


async def get_all_names(db: AsyncIOMotorDatabase) -> List[dict]:
    """Get all Allah names"""
    names = await db["allah_names"].find().to_list(None)
    return names


async def get_name_by_id(db: AsyncIOMotorDatabase, name_id) -> Optional[dict]:
    """Get Allah name by ID"""
    if isinstance(name_id, str):
        name_id = ObjectId(name_id)
    
    return await db["allah_names"].find_one({"_id": name_id})


async def get_random_name(db: AsyncIOMotorDatabase) -> Optional[dict]:
    """Get random Allah name"""
    names = await db["allah_names"].find().to_list(None)
    return random.choice(names) if names else None


async def search_names(db: AsyncIOMotorDatabase, query: str) -> List[dict]:
    """Search Allah names by text"""
    search_query = {
        "$or": [
            {"arabic": {"$regex": query, "$options": "i"}},
            {"transliteration": {"$regex": query, "$options": "i"}},
            {"meaning": {"$regex": query, "$options": "i"}}
        ]
    }
    
    names = await db["allah_names"].find(search_query).to_list(None)
    return names


async def create_name(db: AsyncIOMotorDatabase, name_data: dict) -> dict:
    """Create Allah name"""
    name_data["_id"] = ObjectId()
    name_data["created_at"] = datetime.utcnow()
    
    result = await db["allah_names"].insert_one(name_data)
    name_data["_id"] = result.inserted_id
    return name_data


async def update_name(db: AsyncIOMotorDatabase, name_id, name_data: dict) -> Optional[dict]:
    """Update Allah name"""
    if isinstance(name_id, str):
        name_id = ObjectId(name_id)
    
    result = await db["allah_names"].update_one(
        {"_id": name_id},
        {"$set": name_data}
    )
    
    if result.matched_count == 0:
        return None
    
    return await db["allah_names"].find_one({"_id": name_id})


async def delete_name(db: AsyncIOMotorDatabase, name_id) -> bool:
    """Delete Allah name"""
    if isinstance(name_id, str):
        name_id = ObjectId(name_id)
    
    result = await db["allah_names"].delete_one({"_id": name_id})
    return result.deleted_count > 0


async def bulk_create_names(db: AsyncIOMotorDatabase, names_data: List[dict]) -> List[str]:
    """Bulk create Allah names"""
    if not names_data:
        return []
    
    for name in names_data:
        name["_id"] = ObjectId()
        name["created_at"] = datetime.utcnow()
    
    result = await db["allah_names"].insert_many(names_data)
    return [str(id) for id in result.inserted_ids]
