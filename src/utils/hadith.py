"""MongoDB CRUD operations for Hadiths"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import List, Optional, Set, Tuple
from datetime import datetime
from ..models.mongo_models import HadithInDB, HadithCategoryInDB, HadithViewInDB, HadithFavoriteInDB
import logging

logger = logging.getLogger(__name__)


async def get_hadith(db: AsyncIOMotorDatabase, hadith_id) -> Optional[HadithInDB]:
    """Get a single hadith by ID"""
    if isinstance(hadith_id, str):
        hadith_id = ObjectId(hadith_id)
    
    hadith = await db["hadiths"].find_one({"_id": hadith_id})
    return HadithInDB(**hadith) if hadith else None


async def create_hadith(db: AsyncIOMotorDatabase, hadith_data: dict) -> HadithInDB:
    """Create a new hadith"""
    hadith_data["created_at"] = datetime.utcnow()
    hadith_data["updated_at"] = datetime.utcnow()
    
    result = await db["hadiths"].insert_one(hadith_data)
    hadith_data["_id"] = result.inserted_id
    
    return HadithInDB(**hadith_data)


async def update_hadith(db: AsyncIOMotorDatabase, hadith_id, hadith_data: dict) -> Optional[HadithInDB]:
    """Update a hadith"""
    if isinstance(hadith_id, str):
        hadith_id = ObjectId(hadith_id)
    
    hadith_data["updated_at"] = datetime.utcnow()
    
    result = await db["hadiths"].update_one(
        {"_id": hadith_id},
        {"$set": hadith_data}
    )
    
    if result.matched_count == 0:
        return None
    
    updated_hadith = await db["hadiths"].find_one({"_id": hadith_id})
    return HadithInDB(**updated_hadith)


async def delete_hadith(db: AsyncIOMotorDatabase, hadith_id) -> bool:
    """Delete a hadith"""
    if isinstance(hadith_id, str):
        hadith_id = ObjectId(hadith_id)
    
    # Delete views and favorites
    await db["hadith_views"].delete_many({"hadith_id": hadith_id})
    await db["hadith_favorites"].delete_many({"hadith_id": hadith_id})
    
    result = await db["hadiths"].delete_one({"_id": hadith_id})
    return result.deleted_count > 0


async def delete_hadiths_bulk(db: AsyncIOMotorDatabase, hadith_ids: List) -> int:
    """Delete multiple hadiths"""
    if not hadith_ids:
        return 0
    
    object_ids = [ObjectId(id) if isinstance(id, str) else id for id in hadith_ids]
    
    # Delete views and favorites
    await db["hadith_views"].delete_many({"hadith_id": {"$in": object_ids}})
    await db["hadith_favorites"].delete_many({"hadith_id": {"$in": object_ids}})
    
    result = await db["hadiths"].delete_many({"_id": {"$in": object_ids}})
    return result.deleted_count


async def bulk_create_hadiths(db: AsyncIOMotorDatabase, hadiths_data: List[dict]) -> List[str]:
    """Create multiple hadiths at once"""
    if not hadiths_data:
        return []
    
    for hadith in hadiths_data:
        hadith["created_at"] = datetime.utcnow()
        hadith["updated_at"] = datetime.utcnow()
    
    result = await db["hadiths"].insert_many(hadiths_data)
    return [str(id) for id in result.inserted_ids]


async def search_hadiths(db: AsyncIOMotorDatabase, q: str, skip: int = 0, limit: int = 50) -> List[HadithInDB]:
    """Search hadiths by text"""
    query = {
        "$or": [
            {"arabic": {"$regex": q, "$options": "i"}},
            {"translation": {"$regex": q, "$options": "i"}},
            {"narrator": {"$regex": q, "$options": "i"}},
            {"book": {"$regex": q, "$options": "i"}},
        ]
    }
    
    hadiths = await db["hadiths"].find(query).skip(skip).limit(limit).to_list(None)
    return [HadithInDB(**hadith) for hadith in hadiths]


async def toggle_featured(db: AsyncIOMotorDatabase, hadith_id) -> Optional[HadithInDB]:
    """Toggle featured status of a hadith"""
    if isinstance(hadith_id, str):
        hadith_id = ObjectId(hadith_id)
    
    hadith = await db["hadiths"].find_one({"_id": hadith_id})
    if not hadith:
        return None
    
    new_featured_status = not hadith.get("featured", False)
    
    await db["hadiths"].update_one(
        {"_id": hadith_id},
        {"$set": {"featured": new_featured_status, "updated_at": datetime.utcnow()}}
    )
    
    updated_hadith = await db["hadiths"].find_one({"_id": hadith_id})
    return HadithInDB(**updated_hadith)


async def increment_view(db: AsyncIOMotorDatabase, hadith_id) -> bool:
    """Increment view count for a hadith"""
    if isinstance(hadith_id, str):
        hadith_id = ObjectId(hadith_id)
    
    # Add view record
    await db["hadith_views"].insert_one({
        "hadith_id": hadith_id,
        "user_id": None,
        "created_at": datetime.utcnow()
    })
    
    return True


async def get_views_count(db: AsyncIOMotorDatabase, hadith_id) -> int:
    """Get total views for a hadith"""
    if isinstance(hadith_id, str):
        hadith_id = ObjectId(hadith_id)
    
    count = await db["hadith_views"].count_documents({"hadith_id": hadith_id})
    return count


async def get_views_bulk(db: AsyncIOMotorDatabase, hadith_ids: List) -> dict:
    """Get view counts for multiple hadiths"""
    if not hadith_ids:
        return {}
    
    object_ids = [ObjectId(id) if isinstance(id, str) else id for id in hadith_ids]
    
    pipeline = [
        {"$match": {"hadith_id": {"$in": object_ids}}},
        {"$group": {"_id": "$hadith_id", "count": {"$sum": 1}}}
    ]
    
    results = await db["hadith_views"].aggregate(pipeline).to_list(None)
    return {str(r["_id"]): r["count"] for r in results}


async def toggle_favorite(db: AsyncIOMotorDatabase, hadith_id, user_id) -> bool:
    """Toggle favorite status for a user"""
    if isinstance(hadith_id, str):
        hadith_id = ObjectId(hadith_id)
    if isinstance(user_id, str):
        user_id = ObjectId(user_id)
    
    fav = await db["hadith_favorites"].find_one({"hadith_id": hadith_id, "user_id": user_id})
    
    if fav:
        await db["hadith_favorites"].delete_one({"hadith_id": hadith_id, "user_id": user_id})
    else:
        await db["hadith_favorites"].insert_one({
            "hadith_id": hadith_id,
            "user_id": user_id,
            "created_at": datetime.utcnow()
        })
    
    return True


async def get_favorites_count(db: AsyncIOMotorDatabase, hadith_id) -> int:
    """Get total favorites for a hadith"""
    if isinstance(hadith_id, str):
        hadith_id = ObjectId(hadith_id)
    
    count = await db["hadith_favorites"].count_documents({"hadith_id": hadith_id})
    return count


async def get_favorites_bulk(db: AsyncIOMotorDatabase, hadith_ids: List) -> dict:
    """Get favorite counts for multiple hadiths"""
    if not hadith_ids:
        return {}
    
    object_ids = [ObjectId(id) if isinstance(id, str) else id for id in hadith_ids]
    
    pipeline = [
        {"$match": {"hadith_id": {"$in": object_ids}}},
        {"$group": {"_id": "$hadith_id", "count": {"$sum": 1}}}
    ]
    
    results = await db["hadith_favorites"].aggregate(pipeline).to_list(None)
    return {str(r["_id"]): r["count"] for r in results}


async def get_user_favorites_set(db: AsyncIOMotorDatabase, user_id, hadith_ids: List) -> Set[str]:
    """Get set of favorite hadith IDs for a user"""
    if not hadith_ids:
        return set()
    
    if isinstance(user_id, str):
        user_id = ObjectId(user_id)
    
    object_ids = [ObjectId(id) if isinstance(id, str) else id for id in hadith_ids]
    
    favorites = await db["hadith_favorites"].find({
        "user_id": user_id,
        "hadith_id": {"$in": object_ids}
    }).to_list(None)
    
    return {str(fav["hadith_id"]) for fav in favorites}


async def get_all_hadiths(db: AsyncIOMotorDatabase) -> List[HadithInDB]:
    """Get all hadiths"""
    hadiths = await db["hadiths"].find().to_list(None)
    return [HadithInDB(**hadith) for hadith in hadiths]


async def get_paginated_hadiths(
    db: AsyncIOMotorDatabase,
    page: int,
    limit: int,
    sort_by: str,
    sort_order: str,
    q: Optional[str],
    category_id: Optional[str],
    featured: Optional[bool]
) -> Tuple[List[HadithInDB], List[ObjectId]]:
    """Get paginated hadiths with filtering"""
    query = {}
    
    if q:
        query["$or"] = [
            {"arabic": {"$regex": q, "$options": "i"}},
            {"translation": {"$regex": q, "$options": "i"}},
            {"narrator": {"$regex": q, "$options": "i"}},
            {"book": {"$regex": q, "$options": "i"}},
        ]
    
    if category_id:
        if isinstance(category_id, str):
            category_id = ObjectId(category_id)
        query["category_id"] = category_id
    
    if featured is not None:
        query["featured"] = featured
    
    # Determine sort order
    sort_direction = -1 if sort_order.lower() == "desc" else 1
    sort_key = sort_by if sort_by != "id" else "_id"
    
    # Get paginated results
    skip = (page - 1) * limit
    hadiths = await db["hadiths"].find(query).sort(sort_key, sort_direction).skip(skip).limit(limit).to_list(None)
    
    hadiths_list = [HadithInDB(**hadith) for hadith in hadiths]
    hadith_ids = [hadith.id for hadith in hadiths_list]
    
    return hadiths_list, hadith_ids


async def get_all_categories(db: AsyncIOMotorDatabase) -> List[HadithCategoryInDB]:
    """Get all hadith categories"""
    categories = await db["hadith_categories"].find().sort("_id", 1).to_list(None)
    return [HadithCategoryInDB(**cat) for cat in categories]


async def get_category(db: AsyncIOMotorDatabase, category_id) -> Optional[HadithCategoryInDB]:
    """Get a single hadith category"""
    if isinstance(category_id, str):
        category_id = ObjectId(category_id)
    
    category = await db["hadith_categories"].find_one({"_id": category_id})
    return HadithCategoryInDB(**category) if category else None


async def create_category(db: AsyncIOMotorDatabase, category_data: dict) -> HadithCategoryInDB:
    """Create a new hadith category"""
    category_data["created_at"] = datetime.utcnow()
    
    result = await db["hadith_categories"].insert_one(category_data)
    category_data["_id"] = result.inserted_id
    
    return HadithCategoryInDB(**category_data)


async def update_category(db: AsyncIOMotorDatabase, category_id, category_data: dict) -> Optional[HadithCategoryInDB]:
    """Update a hadith category"""
    if isinstance(category_id, str):
        category_id = ObjectId(category_id)
    
    result = await db["hadith_categories"].update_one(
        {"_id": category_id},
        {"$set": category_data}
    )
    
    if result.matched_count == 0:
        return None
    
    updated_category = await db["hadith_categories"].find_one({"_id": category_id})
    return HadithCategoryInDB(**updated_category)


async def delete_category(db: AsyncIOMotorDatabase, category_id) -> bool:
    """Delete a hadith category and update associated hadiths"""
    if isinstance(category_id, str):
        category_id = ObjectId(category_id)
    
    # Update hadiths to remove category reference
    await db["hadiths"].update_many(
        {"category_id": category_id},
        {"$set": {"category_id": None}}
    )
    
    result = await db["hadith_categories"].delete_one({"_id": category_id})
    return result.deleted_count > 0
