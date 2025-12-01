import motor.motor_asyncio
from src.config import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)

client: Optional[motor.motor_asyncio.AsyncClient] = None
db = None

async def connect_to_mongo():
    """Establish MongoDB connection"""
    global client, db
    try:
        client = motor.motor_asyncio.AsyncClient(
            settings.DATABASE_URL,
            serverSelectionTimeoutMS=5000,
            retryWrites=True,
            w="majority"
        )
        # Verify connection
        await client.admin.command('ping')
        db = client[settings.MONGODB_DB_NAME]
        logger.info("✅ Connected to MongoDB successfully")
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
        raise

async def disconnect_from_mongo():
    """Close MongoDB connection"""
    global client
    if client is not None:
        client.close()
        logger.info("✅ Disconnected from MongoDB")

async def get_db():
    """Get database instance for dependency injection"""
    if db is None:
        raise RuntimeError("Database not initialized. Call connect_to_mongo() first.")
    return db

async def init_db() -> None:
    """Initialize database (create collections and indexes if needed)"""
    if db is None:
        raise RuntimeError("Database not initialized. Call connect_to_mongo() first.")
    
    # Create collections and indexes
    collections_to_create = {
        'users': [('email', True), ('username', True)],
        'duas': [('category_id', False), ('featured', False)],
        'dua_categories': [('name', True)],
        'hadiths': [('category_id', False), ('featured', False)],
        'hadith_categories': [('name', True)],
        'articles': [('category_id', False), ('featured', False)],
        'article_categories': [('name', True)],
        'dua_views': [('dua_id', False), ('user_id', False)],
        'dua_favorites': [('dua_id', False), ('user_id', False)],
        'hadith_views': [('hadith_id', False), ('user_id', False)],
        'hadith_favorites': [('hadith_id', False), ('user_id', False)],
        'article_views': [('article_id', False), ('user_id', False)],
        'article_favorites': [('article_id', False), ('user_id', False)],
    }
    
    for collection_name, indexes in collections_to_create.items():
        try:
            # Create collection if it doesn't exist
            if collection_name not in await db.list_collection_names():
                await db.create_collection(collection_name)
                logger.info(f"✅ Created collection: {collection_name}")
            
            # Create indexes
            collection = db[collection_name]
            for field, unique in indexes:
                await collection.create_index(field, unique=unique)
        except Exception as e:
            logger.warning(f"Index creation warning for {collection_name}: {e}")
    
    logger.info("✅ Database initialization complete")