"""MongoDB CRUD operations for Articles"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import List, Optional, Set, Tuple
from datetime import datetime
from ..models.mongo_models import ArticleInDB, ArticleCategoryInDB, ArticleViewInDB, ArticleFavoriteInDB
import logging

logger = logging.getLogger(__name__)


async def get_article(db: AsyncIOMotorDatabase, article_id) -> Optional[ArticleInDB]:
    """Get a single article by ID"""
    if isinstance(article_id, str):
        article_id = ObjectId(article_id)
    
    article = await db["articles"].find_one({"_id": article_id})
    return ArticleInDB(**article) if article else None


async def create_article(db: AsyncIOMotorDatabase, article_data: dict) -> ArticleInDB:
    """Create a new article"""
    article_data["created_at"] = datetime.utcnow()
    article_data["updated_at"] = datetime.utcnow()
    
    result = await db["articles"].insert_one(article_data)
    article_data["_id"] = result.inserted_id
    
    return ArticleInDB(**article_data)


async def update_article(db: AsyncIOMotorDatabase, article_id, article_data: dict) -> Optional[ArticleInDB]:
    """Update an article"""
    if isinstance(article_id, str):
        article_id = ObjectId(article_id)
    
    article_data["updated_at"] = datetime.utcnow()
    
    result = await db["articles"].update_one(
        {"_id": article_id},
        {"$set": article_data}
    )
    
    if result.matched_count == 0:
        return None
    
    updated_article = await db["articles"].find_one({"_id": article_id})
    return ArticleInDB(**updated_article)


async def delete_article(db: AsyncIOMotorDatabase, article_id) -> bool:
    """Delete an article"""
    if isinstance(article_id, str):
        article_id = ObjectId(article_id)
    
    # Delete views and favorites
    await db["article_views"].delete_many({"article_id": article_id})
    await db["article_favorites"].delete_many({"article_id": article_id})
    
    result = await db["articles"].delete_one({"_id": article_id})
    return result.deleted_count > 0


async def delete_articles_bulk(db: AsyncIOMotorDatabase, article_ids: List) -> int:
    """Delete multiple articles"""
    if not article_ids:
        return 0
    
    object_ids = [ObjectId(id) if isinstance(id, str) else id for id in article_ids]
    
    # Delete views and favorites
    await db["article_views"].delete_many({"article_id": {"$in": object_ids}})
    await db["article_favorites"].delete_many({"article_id": {"$in": object_ids}})
    
    result = await db["articles"].delete_many({"_id": {"$in": object_ids}})
    return result.deleted_count


async def bulk_create_articles(db: AsyncIOMotorDatabase, articles_data: List[dict]) -> List[str]:
    """Create multiple articles at once"""
    if not articles_data:
        return []
    
    for article in articles_data:
        article["created_at"] = datetime.utcnow()
        article["updated_at"] = datetime.utcnow()
    
    result = await db["articles"].insert_many(articles_data)
    return [str(id) for id in result.inserted_ids]


async def search_articles(db: AsyncIOMotorDatabase, q: str, skip: int = 0, limit: int = 50) -> List[ArticleInDB]:
    """Search articles by text"""
    query = {
        "$or": [
            {"title": {"$regex": q, "$options": "i"}},
            {"content": {"$regex": q, "$options": "i"}},
            {"excerpt": {"$regex": q, "$options": "i"}},
            {"author": {"$regex": q, "$options": "i"}},
        ]
    }
    
    articles = await db["articles"].find(query).skip(skip).limit(limit).to_list(None)
    return [ArticleInDB(**article) for article in articles]


async def toggle_featured(db: AsyncIOMotorDatabase, article_id) -> Optional[ArticleInDB]:
    """Toggle featured status of an article"""
    if isinstance(article_id, str):
        article_id = ObjectId(article_id)
    
    article = await db["articles"].find_one({"_id": article_id})
    if not article:
        return None
    
    new_featured_status = not article.get("featured", False)
    
    await db["articles"].update_one(
        {"_id": article_id},
        {"$set": {"featured": new_featured_status, "updated_at": datetime.utcnow()}}
    )
    
    updated_article = await db["articles"].find_one({"_id": article_id})
    return ArticleInDB(**updated_article)


async def increment_view(db: AsyncIOMotorDatabase, article_id) -> bool:
    """Increment view count for an article"""
    if isinstance(article_id, str):
        article_id = ObjectId(article_id)
    
    # Add view record
    await db["article_views"].insert_one({
        "article_id": article_id,
        "user_id": None,
        "created_at": datetime.utcnow()
    })
    
    return True


async def get_views_count(db: AsyncIOMotorDatabase, article_id) -> int:
    """Get total views for an article"""
    if isinstance(article_id, str):
        article_id = ObjectId(article_id)
    
    count = await db["article_views"].count_documents({"article_id": article_id})
    return count


async def get_views_bulk(db: AsyncIOMotorDatabase, article_ids: List) -> dict:
    """Get view counts for multiple articles"""
    if not article_ids:
        return {}
    
    object_ids = [ObjectId(id) if isinstance(id, str) else id for id in article_ids]
    
    pipeline = [
        {"$match": {"article_id": {"$in": object_ids}}},
        {"$group": {"_id": "$article_id", "count": {"$sum": 1}}}
    ]
    
    results = await db["article_views"].aggregate(pipeline).to_list(None)
    return {str(r["_id"]): r["count"] for r in results}


async def toggle_favorite(db: AsyncIOMotorDatabase, article_id, user_id) -> bool:
    """Toggle favorite status for a user"""
    if isinstance(article_id, str):
        article_id = ObjectId(article_id)
    if isinstance(user_id, str):
        user_id = ObjectId(user_id)
    
    fav = await db["article_favorites"].find_one({"article_id": article_id, "user_id": user_id})
    
    if fav:
        await db["article_favorites"].delete_one({"article_id": article_id, "user_id": user_id})
    else:
        await db["article_favorites"].insert_one({
            "article_id": article_id,
            "user_id": user_id,
            "created_at": datetime.utcnow()
        })
    
    return True


async def get_favorites_count(db: AsyncIOMotorDatabase, article_id) -> int:
    """Get total favorites for an article"""
    if isinstance(article_id, str):
        article_id = ObjectId(article_id)
    
    count = await db["article_favorites"].count_documents({"article_id": article_id})
    return count


async def get_favorites_bulk(db: AsyncIOMotorDatabase, article_ids: List) -> dict:
    """Get favorite counts for multiple articles"""
    if not article_ids:
        return {}
    
    object_ids = [ObjectId(id) if isinstance(id, str) else id for id in article_ids]
    
    pipeline = [
        {"$match": {"article_id": {"$in": object_ids}}},
        {"$group": {"_id": "$article_id", "count": {"$sum": 1}}}
    ]
    
    results = await db["article_favorites"].aggregate(pipeline).to_list(None)
    return {str(r["_id"]): r["count"] for r in results}


async def get_user_favorites_set(db: AsyncIOMotorDatabase, user_id, article_ids: List) -> Set[str]:
    """Get set of favorite article IDs for a user"""
    if not article_ids:
        return set()
    
    if isinstance(user_id, str):
        user_id = ObjectId(user_id)
    
    object_ids = [ObjectId(id) if isinstance(id, str) else id for id in article_ids]
    
    favorites = await db["article_favorites"].find({
        "user_id": user_id,
        "article_id": {"$in": object_ids}
    }).to_list(None)
    
    return {str(fav["article_id"]) for fav in favorites}


async def get_all_articles(db: AsyncIOMotorDatabase) -> List[ArticleInDB]:
    """Get all articles"""
    articles = await db["articles"].find().to_list(None)
    return [ArticleInDB(**article) for article in articles]


async def get_articles_by_category_id(db: AsyncIOMotorDatabase, category_id) -> List[ArticleInDB]:
    """Get all articles in a specific category"""
    if isinstance(category_id, str):
        category_id = ObjectId(category_id)
    
    articles = await db["articles"].find({"category_id": category_id}).sort("_id", -1).to_list(None)
    return [ArticleInDB(**article) for article in articles]


async def get_paginated_articles(
    db: AsyncIOMotorDatabase,
    page: int,
    limit: int,
    sort_by: str,
    sort_order: str,
    q: Optional[str],
    category_id: Optional[str],
    featured: Optional[bool]
) -> Tuple[List[ArticleInDB], List[ObjectId]]:
    """Get paginated articles with filtering"""
    query = {}
    
    if q:
        query["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"content": {"$regex": q, "$options": "i"}},
            {"excerpt": {"$regex": q, "$options": "i"}},
            {"author": {"$regex": q, "$options": "i"}},
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
    articles = await db["articles"].find(query).sort(sort_key, sort_direction).skip(skip).limit(limit).to_list(None)
    
    articles_list = [ArticleInDB(**article) for article in articles]
    article_ids = [article.id for article in articles_list]
    
    return articles_list, article_ids


async def get_all_categories(db: AsyncIOMotorDatabase) -> List[ArticleCategoryInDB]:
    """Get all article categories"""
    categories = await db["article_categories"].find().sort("_id", 1).to_list(None)
    return [ArticleCategoryInDB(**cat) for cat in categories]


async def get_category(db: AsyncIOMotorDatabase, category_id) -> Optional[ArticleCategoryInDB]:
    """Get a single article category"""
    if isinstance(category_id, str):
        category_id = ObjectId(category_id)
    
    category = await db["article_categories"].find_one({"_id": category_id})
    return ArticleCategoryInDB(**category) if category else None


async def create_category(db: AsyncIOMotorDatabase, category_data: dict) -> ArticleCategoryInDB:
    """Create a new article category"""
    category_data["created_at"] = datetime.utcnow()
    
    result = await db["article_categories"].insert_one(category_data)
    category_data["_id"] = result.inserted_id
    
    return ArticleCategoryInDB(**category_data)


async def update_category(db: AsyncIOMotorDatabase, category_id, category_data: dict) -> Optional[ArticleCategoryInDB]:
    """Update an article category"""
    if isinstance(category_id, str):
        category_id = ObjectId(category_id)
    
    result = await db["article_categories"].update_one(
        {"_id": category_id},
        {"$set": category_data}
    )
    
    if result.matched_count == 0:
        return None
    
    updated_category = await db["article_categories"].find_one({"_id": category_id})
    return ArticleCategoryInDB(**updated_category)


async def update_category_image_url(
    db: AsyncIOMotorDatabase,
    category_id,
    image_url: str
) -> Optional[ArticleCategoryInDB]:
    """Update category image URL"""
    if isinstance(category_id, str):
        category_id = ObjectId(category_id)
    
    result = await db["article_categories"].update_one(
        {"_id": category_id},
        {"$set": {"image_url": image_url}}
    )
    
    if result.matched_count == 0:
        return None
    
    updated_category = await db["article_categories"].find_one({"_id": category_id})
    return ArticleCategoryInDB(**updated_category)


async def delete_category(db: AsyncIOMotorDatabase, category_id) -> bool:
    """Delete an article category and update associated articles"""
    if isinstance(category_id, str):
        category_id = ObjectId(category_id)
    
    # Update articles to remove category reference
    await db["articles"].update_many(
        {"category_id": category_id},
        {"$set": {"category_id": None}}
    )
    
    result = await db["article_categories"].delete_one({"_id": category_id})
    return result.deleted_count > 0
