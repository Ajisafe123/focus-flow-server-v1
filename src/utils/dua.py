"""MongoDB CRUD operations for Duas"""
import string
import random
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import List, Optional, Set, Tuple, Dict
from datetime import datetime
from ..models.mongo_models import DuaInDB, DuaCategoryInDB, DuaViewInDB, DuaFavoriteInDB, DuaShareLinkInDB
import logging

logger = logging.getLogger(__name__)


def generate_short_code(length: int = 8) -> str:
    """Generate a unique short code for share links"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


async def create_share_link(db: AsyncIOMotorDatabase, dua_id: ObjectId, short_code: str) -> DuaShareLinkInDB:
    """Create a share link for a dua"""
    MAX_RETRIES = 5
    current_short_code = short_code
    
    for attempt in range(MAX_RETRIES):
        try:
            share_link_data = {
                "dua_id": dua_id,
                "short_code": current_short_code,
                "created_at": datetime.utcnow()
            }
            result = await db["dua_share_links"].insert_one(share_link_data)
            share_link_data["_id"] = result.inserted_id
            return DuaShareLinkInDB(**share_link_data)
        except Exception:
            current_short_code = generate_short_code()
            continue
    
    raise Exception("Failed to generate a unique short code after 5 attempts.")


async def get_dua_id_by_short_code(db: AsyncIOMotorDatabase, short_code: str) -> Optional[ObjectId]:
    """Get dua ID from share link short code"""
    link = await db["dua_share_links"].find_one({"short_code": short_code})
    return link["dua_id"] if link else None


async def get_dua(db: AsyncIOMotorDatabase, dua_id) -> Optional[DuaInDB]:
    """Get a single dua by ID"""
    if isinstance(dua_id, str):
        dua_id = ObjectId(dua_id)
    
    dua = await db["duas"].find_one({"_id": dua_id})
    return DuaInDB(**dua) if dua else None


async def get_all_duas(db: AsyncIOMotorDatabase) -> List[DuaInDB]:
    """Get all duas"""
    duas = await db["duas"].find().to_list(None)
    return [DuaInDB(**dua) for dua in duas]


async def get_duas_by_category_id(db: AsyncIOMotorDatabase, category_id) -> List[DuaInDB]:
    """Get all duas in a specific category"""
    if isinstance(category_id, str):
        category_id = ObjectId(category_id)
    
    duas = await db["duas"].find({"category_id": category_id}).sort("_id", 1).to_list(None)
    return [DuaInDB(**dua) for dua in duas]


async def get_all_duas_with_counts(db: AsyncIOMotorDatabase) -> Tuple[List[DuaInDB], dict, dict]:
    """Get all duas with view and favorite counts"""
    duas = await db["duas"].find().to_list(None)
    duas_list = [DuaInDB(**dua) for dua in duas]
    dua_ids = [dua.id for dua in duas_list]
    
    views_map = await get_views_bulk(db, dua_ids)
    favorites_map = await get_favorites_bulk(db, dua_ids)
    
    return duas_list, views_map, favorites_map


async def get_paginated_duas(
    db: AsyncIOMotorDatabase,
    page: int,
    limit: int,
    sort_by: str,
    sort_order: str,
    q: Optional[str],
    category_id: Optional[str],
    featured: Optional[bool]
) -> Tuple[List[DuaInDB], List[ObjectId]]:
    """Get paginated duas with filtering"""
    query = {}
    
    if q:
        query["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"arabic": {"$regex": q, "$options": "i"}},
            {"transliteration": {"$regex": q, "$options": "i"}},
            {"translation": {"$regex": q, "$options": "i"}},
        ]
    
    if category_id:
        if isinstance(category_id, str):
            category_id = ObjectId(category_id)
        query["category_id"] = category_id
    
    if featured is not None:
        query["featured"] = featured
    
    # Get total count
    total_count = await db["duas"].count_documents(query)
    
    # Determine sort order
    sort_direction = -1 if sort_order.lower() == "desc" else 1
    sort_key = sort_by if sort_by != "id" else "_id"
    
    # Get paginated results
    skip = (page - 1) * limit
    duas = await db["duas"].find(query).sort(sort_key, sort_direction).skip(skip).limit(limit).to_list(None)
    
    duas_list = [DuaInDB(**dua) for dua in duas]
    dua_ids = [dua.id for dua in duas_list]
    
    return duas_list, dua_ids


async def create_dua(db: AsyncIOMotorDatabase, dua_data: dict) -> DuaInDB:
    """Create a new dua"""
    dua_data["created_at"] = datetime.utcnow()
    dua_data["updated_at"] = datetime.utcnow()
    
    result = await db["duas"].insert_one(dua_data)
    dua_data["_id"] = result.inserted_id
    
    return DuaInDB(**dua_data)


async def update_dua(db: AsyncIOMotorDatabase, dua_id, dua_data: dict) -> Optional[DuaInDB]:
    """Update a dua"""
    if isinstance(dua_id, str):
        dua_id = ObjectId(dua_id)
    
    dua_data["updated_at"] = datetime.utcnow()
    
    result = await db["duas"].update_one(
        {"_id": dua_id},
        {"$set": dua_data}
    )
    
    if result.matched_count == 0:
        return None
    
    updated_dua = await db["duas"].find_one({"_id": dua_id})
    return DuaInDB(**updated_dua)


async def delete_dua(db: AsyncIOMotorDatabase, dua_id) -> bool:
    """Delete a dua"""
    if isinstance(dua_id, str):
        dua_id = ObjectId(dua_id)
    
    # Delete views and favorites
    await db["dua_views"].delete_many({"dua_id": dua_id})
    await db["dua_favorites"].delete_many({"dua_id": dua_id})
    await db["dua_share_links"].delete_many({"dua_id": dua_id})
    
    result = await db["duas"].delete_one({"_id": dua_id})
    return result.deleted_count > 0


async def delete_duas_bulk(db: AsyncIOMotorDatabase, dua_ids: List) -> int:
    """Delete multiple duas"""
    if not dua_ids:
        return 0
    
    object_ids = [ObjectId(id) if isinstance(id, str) else id for id in dua_ids]
    
    # Delete views and favorites
    await db["dua_views"].delete_many({"dua_id": {"$in": object_ids}})
    await db["dua_favorites"].delete_many({"dua_id": {"$in": object_ids}})
    await db["dua_share_links"].delete_many({"dua_id": {"$in": object_ids}})
    
    result = await db["duas"].delete_many({"_id": {"$in": object_ids}})
    return result.deleted_count


async def bulk_create_duas(db: AsyncIOMotorDatabase, duas_data: List[dict]) -> List[str]:
    """Create multiple duas at once"""
    if not duas_data:
        return []
    
    for dua in duas_data:
        dua["created_at"] = datetime.utcnow()
        dua["updated_at"] = datetime.utcnow()
    
    result = await db["duas"].insert_many(duas_data)
    return [str(id) for id in result.inserted_ids]


async def search_duas(db: AsyncIOMotorDatabase, q: str, skip: int = 0, limit: int = 50) -> List[DuaInDB]:
    """Search duas by text"""
    query = {
        "$or": [
            {"title": {"$regex": q, "$options": "i"}},
            {"arabic": {"$regex": q, "$options": "i"}},
            {"transliteration": {"$regex": q, "$options": "i"}},
            {"translation": {"$regex": q, "$options": "i"}},
        ]
    }
    
    duas = await db["duas"].find(query).skip(skip).limit(limit).to_list(None)
    return [DuaInDB(**dua) for dua in duas]


async def toggle_featured(db: AsyncIOMotorDatabase, dua_id) -> Optional[DuaInDB]:
    """Toggle featured status of a dua"""
    if isinstance(dua_id, str):
        dua_id = ObjectId(dua_id)
    
    dua = await db["duas"].find_one({"_id": dua_id})
    if not dua:
        return None
    
    new_featured_status = not dua.get("featured", False)
    
    await db["duas"].update_one(
        {"_id": dua_id},
        {"$set": {"featured": new_featured_status, "updated_at": datetime.utcnow()}}
    )
    
    updated_dua = await db["duas"].find_one({"_id": dua_id})
    return DuaInDB(**updated_dua)


async def update_dua_audio_path_by_category(
    db: AsyncIOMotorDatabase,
    category_id,
    audio_url: str
) -> int:
    """Update audio path for all duas in a category"""
    if isinstance(category_id, str):
        category_id = ObjectId(category_id)
    
    result = await db["duas"].update_many(
        {"category_id": category_id},
        {"$set": {"audio_path": audio_url, "updated_at": datetime.utcnow()}}
    )
    
    return result.modified_count


async def update_dua_audio_path(
    db: AsyncIOMotorDatabase,
    dua_identifier: str,
    category_id,
    audio_url: str
) -> bool:
    """Update audio path for a specific dua"""
    if isinstance(category_id, str):
        category_id = ObjectId(category_id)
    
    # Try to parse as ObjectId
    dua_id = None
    try:
        dua_id = ObjectId(dua_identifier)
    except:
        pass
    
    if dua_id:
        query = {"_id": dua_id, "category_id": category_id}
    else:
        query = {"title": {"$regex": dua_identifier, "$options": "i"}, "category_id": category_id}
    
    result = await db["duas"].update_one(
        query,
        {"$set": {"audio_path": audio_url, "updated_at": datetime.utcnow()}}
    )
    
    return result.modified_count > 0


async def increment_view(db: AsyncIOMotorDatabase, dua_id) -> bool:
    """Increment view count for a dua"""
    if isinstance(dua_id, str):
        dua_id = ObjectId(dua_id)
    
    # Add view record
    await db["dua_views"].insert_one({
        "dua_id": dua_id,
        "user_id": None,
        "created_at": datetime.utcnow()
    })
    
    return True


async def get_views_count(db: AsyncIOMotorDatabase, dua_id) -> int:
    """Get total views for a dua"""
    if isinstance(dua_id, str):
        dua_id = ObjectId(dua_id)
    
    count = await db["dua_views"].count_documents({"dua_id": dua_id})
    return count


async def get_views_bulk(db: AsyncIOMotorDatabase, dua_ids: List) -> dict:
    """Get view counts for multiple duas"""
    if not dua_ids:
        return {}
    
    object_ids = [ObjectId(id) if isinstance(id, str) else id for id in dua_ids]
    
    pipeline = [
        {"$match": {"dua_id": {"$in": object_ids}}},
        {"$group": {"_id": "$dua_id", "count": {"$sum": 1}}}
    ]
    
    results = await db["dua_views"].aggregate(pipeline).to_list(None)
    return {str(r["_id"]): r["count"] for r in results}


async def toggle_favorite(db: AsyncIOMotorDatabase, dua_id, user_id) -> bool:
    """Toggle favorite status for a user"""
    if isinstance(dua_id, str):
        dua_id = ObjectId(dua_id)
    if isinstance(user_id, str):
        user_id = ObjectId(user_id)
    
    fav = await db["dua_favorites"].find_one({"dua_id": dua_id, "user_id": user_id})
    
    if fav:
        await db["dua_favorites"].delete_one({"dua_id": dua_id, "user_id": user_id})
    else:
        await db["dua_favorites"].insert_one({
            "dua_id": dua_id,
            "user_id": user_id,
            "created_at": datetime.utcnow()
        })
    
    return True


async def get_favorites_count(db: AsyncIOMotorDatabase, dua_id) -> int:
    """Get total favorites for a dua"""
    if isinstance(dua_id, str):
        dua_id = ObjectId(dua_id)
    
    count = await db["dua_favorites"].count_documents({"dua_id": dua_id})
    return count


async def get_favorites_bulk(db: AsyncIOMotorDatabase, dua_ids: List) -> dict:
    """Get favorite counts for multiple duas"""
    if not dua_ids:
        return {}
    
    object_ids = [ObjectId(id) if isinstance(id, str) else id for id in dua_ids]
    
    pipeline = [
        {"$match": {"dua_id": {"$in": object_ids}}},
        {"$group": {"_id": "$dua_id", "count": {"$sum": 1}}}
    ]
    
    results = await db["dua_favorites"].aggregate(pipeline).to_list(None)
    return {str(r["_id"]): r["count"] for r in results}


async def get_user_favorites_set(db: AsyncIOMotorDatabase, user_id, dua_ids: List) -> Set[str]:
    """Get set of favorite dua IDs for a user"""
    if not dua_ids:
        return set()
    
    if isinstance(user_id, str):
        user_id = ObjectId(user_id)
    
    object_ids = [ObjectId(id) if isinstance(id, str) else id for id in dua_ids]
    
    favorites = await db["dua_favorites"].find({
        "user_id": user_id,
        "dua_id": {"$in": object_ids}
    }).to_list(None)
    
    return {str(fav["dua_id"]) for fav in favorites}


async def get_all_categories(db: AsyncIOMotorDatabase) -> List[DuaCategoryInDB]:
    """Get all dua categories"""
    categories = await db["dua_categories"].find().sort("_id", 1).to_list(None)
    return [DuaCategoryInDB(**cat) for cat in categories]


async def get_category(db: AsyncIOMotorDatabase, category_id) -> Optional[DuaCategoryInDB]:
    """Get a single dua category"""
    if isinstance(category_id, str):
        category_id = ObjectId(category_id)
    
    category = await db["dua_categories"].find_one({"_id": category_id})
    return DuaCategoryInDB(**category) if category else None


async def create_category(db: AsyncIOMotorDatabase, category_data: dict) -> DuaCategoryInDB:
    """Create a new dua category"""
    category_data["created_at"] = datetime.utcnow()
    
    result = await db["dua_categories"].insert_one(category_data)
    category_data["_id"] = result.inserted_id
    
    return DuaCategoryInDB(**category_data)


async def update_category(db: AsyncIOMotorDatabase, category_id, category_data: dict) -> Optional[DuaCategoryInDB]:
    """Update a dua category"""
    if isinstance(category_id, str):
        category_id = ObjectId(category_id)
    
    result = await db["dua_categories"].update_one(
        {"_id": category_id},
        {"$set": category_data}
    )
    
    if result.matched_count == 0:
        return None
    
    updated_category = await db["dua_categories"].find_one({"_id": category_id})
    return DuaCategoryInDB(**updated_category)


async def update_category_image_url(
    db: AsyncIOMotorDatabase,
    category_id,
    image_url: str
) -> Optional[DuaCategoryInDB]:
    """Update category image URL"""
    if isinstance(category_id, str):
        category_id = ObjectId(category_id)
    
    result = await db["dua_categories"].update_one(
        {"_id": category_id},
        {"$set": {"image_url": image_url}}
    )
    
    if result.matched_count == 0:
        return None
    
    updated_category = await db["dua_categories"].find_one({"_id": category_id})
    return DuaCategoryInDB(**updated_category)


async def delete_category(db: AsyncIOMotorDatabase, category_id) -> bool:
    """Delete a dua category and update associated duas"""
    if isinstance(category_id, str):
        category_id = ObjectId(category_id)
    
    # Update duas to remove category reference
    await db["duas"].update_many(
        {"category_id": category_id},
        {"$set": {"category_id": None}}
    )
    
    result = await db["dua_categories"].delete_one({"_id": category_id})
    return result.deleted_count > 0
