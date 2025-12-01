"""Articles API Router"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, Form, File, status
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from ..database import get_db
from ..utils import article as crud_article
from ..utils.users import get_current_user, get_optional_user
from ..schemas.article import (
    ArticleRead, ArticleCreate, ArticleUpdate,
    ArticleCategoryRead, ArticleCategoryCreate, ArticleCategoryUpdate, ArticleStats, ArticleItem
)
from ..models.users import User
import os
import shutil
import uuid
import os.path as op

CURRENT_DIR = op.dirname(op.abspath(__file__))
SRC_DIR = op.join(CURRENT_DIR, op.pardir)
STATIC_DIR = op.join(SRC_DIR, "static")
CATEGORY_IMAGE_DIR = op.join(STATIC_DIR, "article_images")
os.makedirs(CATEGORY_IMAGE_DIR, exist_ok=True)

router = APIRouter(prefix="/api", tags=["Articles"])


@router.get("/articles", response_model=List[ArticleRead])
async def list_articles(db: AsyncIOMotorDatabase = Depends(get_db)):
    """Get all articles"""
    articles = await crud_article.get_all_articles(db)
    article_ids = [article.id for article in articles]
    
    views_map = await crud_article.get_views_bulk(db, article_ids)
    favorites_map = await crud_article.get_favorites_bulk(db, article_ids)

    articles_with_counts = []
    for article in articles:
        article.view_count = views_map.get(str(article.id), 0)
        article.favorite_count = favorites_map.get(str(article.id), 0)
        articles_with_counts.append(article)
        
    return articles_with_counts


@router.get("/articles/paginated", response_model=List[ArticleRead])
async def list_articles_paginated(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    sort_by: str = Query("_id"),
    sort_order: str = Query("desc"),
    q: Optional[str] = None,
    category_id: Optional[str] = None,
    featured: Optional[bool] = None,
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get paginated articles with filtering"""
    articles, article_ids = await crud_article.get_paginated_articles(
        db, page, limit, sort_by, sort_order, q, category_id, featured
    )

    views_map = await crud_article.get_views_bulk(db, article_ids)
    favorites_map = await crud_article.get_favorites_bulk(db, article_ids)

    user_favorites_set = set()
    if current_user:
        user_favorites_set = await crud_article.get_user_favorites_set(db, current_user.id, article_ids)
    
    articles_with_counts = []
    for article in articles:
        article.view_count = views_map.get(str(article.id), 0)
        article.favorite_count = favorites_map.get(str(article.id), 0)
        article.is_favorite = str(article.id) in user_favorites_set
        articles_with_counts.append(article)

    return articles_with_counts


@router.post("/articles", response_model=ArticleRead)
async def create_article_route(article_data: ArticleCreate, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Create a new article"""
    article_dict = article_data.model_dump(exclude_unset=True)
    return await crud_article.create_article(db, article_dict)


@router.get("/articles/stats", response_model=ArticleStats)
async def get_articles_stats(db: AsyncIOMotorDatabase = Depends(get_db)):
    """Get articles statistics"""
    all_articles = await crud_article.get_all_articles(db)
    
    total_articles = len(all_articles)
    article_ids = [article.id for article in all_articles]

    views_map = await crud_article.get_views_bulk(db, article_ids)
    favorites_map = await crud_article.get_favorites_bulk(db, article_ids)

    for article in all_articles:
        article.view_count = views_map.get(str(article.id), 0)
        article.favorite_count = favorites_map.get(str(article.id), 0)

    total_views = sum(article.view_count for article in all_articles)
    total_favorites = sum(article.favorite_count for article in all_articles)

    featured_articles = [a for a in all_articles if a.featured]

    def safe_article_item(a):
        return ArticleItem(
            id=a.id,
            title=a.title or "No Title"
        )

    top_featured = sorted(featured_articles, key=lambda a: a.view_count, reverse=True)[:5]
    top_viewed = sorted(all_articles, key=lambda a: a.view_count, reverse=True)[:5]

    return ArticleStats(
        total_articles=total_articles,
        total_views=total_views,
        total_favorites=total_favorites,
        top_featured=[safe_article_item(a) for a in top_featured] if top_featured else [],
        top_viewed=[safe_article_item(a) for a in top_viewed] if top_viewed else [],
    )


@router.delete("/articles/bulk")
async def delete_articles_bulk_route(
    article_ids: List[str],
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Delete multiple articles"""
    if not article_ids:
        raise HTTPException(status_code=400, detail="Please provide a list of article IDs to delete.")
    
    deleted_count = await crud_article.delete_articles_bulk(db, article_ids)

    if deleted_count == 0 and len(article_ids) > 0:
        raise HTTPException(status_code=404, detail="No Articles found with the provided IDs.")
        
    return {"detail": f"{deleted_count} Articles deleted successfully."}


@router.get("/articles/{article_id}", response_model=ArticleRead)
async def get_article_route(article_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Get a single article by ID"""
    article = await crud_article.get_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Increment view
    await crud_article.increment_view(db, article_id)
    
    article.view_count = await crud_article.get_views_count(db, article_id)
    article.favorite_count = await crud_article.get_favorites_count(db, article_id)
    
    return article


@router.put("/articles/{article_id}", response_model=ArticleRead)
@router.patch("/articles/{article_id}", response_model=ArticleRead)
async def update_article_route(
    article_id: str,
    article_data: ArticleUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update an article"""
    updated = await crud_article.update_article(db, article_id, article_data.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Article not found")
    return updated


@router.delete("/articles/{article_id}")
async def delete_article_route(article_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Delete an article"""
    success = await crud_article.delete_article(db, article_id)
    if not success:
        raise HTTPException(status_code=404, detail="Article not found")
    return {"detail": "Article deleted successfully"}


@router.patch("/articles/{article_id}/featured")
async def toggle_featured_route(article_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Toggle featured status of an article"""
    article = await crud_article.get_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    updated = await crud_article.toggle_featured(db, article_id)
    return {"id": str(updated.id), "featured": updated.featured}


@router.patch("/articles/{article_id}/increment-view")
async def increment_view_route(article_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Increment view count for an article"""
    success = await crud_article.increment_view(db, article_id)
    if not success:
        raise HTTPException(status_code=404, detail="Article not found")
    return {"id": article_id, "status": "view incremented"}


@router.patch("/articles/{article_id}/toggle-favorite")
async def toggle_favorite_route(
    article_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Toggle favorite status for a user"""
    article = await crud_article.get_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    success = await crud_article.toggle_favorite(db, article_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Article not found")
    count = await crud_article.get_favorites_count(db, article_id)
    return {"id": article_id, "favorites": count}


@router.get("/article-categories", response_model=List[ArticleCategoryRead])
async def list_categories(db: AsyncIOMotorDatabase = Depends(get_db)):
    """Get all article categories"""
    return await crud_article.get_all_categories(db)


@router.post("/article-categories", response_model=ArticleCategoryRead)
async def create_category_route(
    category_data: ArticleCategoryCreate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Create a new article category"""
    return await crud_article.create_category(db, category_data.model_dump(exclude_unset=True))


@router.post("/article-categories/{category_id}/image-upload")
async def upload_category_image_route(
    category_id: str,
    image_file: UploadFile = File(...),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Upload category image"""
    category = await crud_article.get_category(db, category_id)
    if not category:
        raise HTTPException(
            status_code=404,
            detail=f"Article Category with ID {category_id} not found."
        )

    allowed_types = ["image/jpeg", "image/png", "image/webp"]
    if image_file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only JPEG, PNG, or WebP allowed."
        )
        
    file_extension = op.splitext(image_file.filename)[1]
    unique_filename = f"category_{category_id}_{uuid.uuid4().hex}{file_extension}"
    unique_image_path = op.join(CATEGORY_IMAGE_DIR, unique_filename)
    
    try:
        with open(unique_image_path, "wb") as buffer:
            shutil.copyfileobj(image_file.file, buffer)

        image_url = f"/static/article_images/{unique_filename}"

        updated_category = await crud_article.update_category_image_url(
            db,
            category_id=category_id,
            image_url=image_url
        )
        
    except Exception as e:
        if op.exists(unique_image_path):
            os.remove(unique_image_path)
        raise HTTPException(status_code=500, detail=f"Image processing or DB error: {str(e)}")

    return {
        "detail": f"Successfully updated image for Category {category_id}.",
        "image_url": image_url,
        "category_id": str(updated_category.id),
        "category_name": updated_category.name
    }


@router.put("/article-categories/{category_id}", response_model=ArticleCategoryRead)
@router.patch("/article-categories/{category_id}", response_model=ArticleCategoryRead)
async def update_category_route(
    category_id: str,
    category_data: ArticleCategoryUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update an article category"""
    updated = await crud_article.update_category(db, category_id, category_data.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Article Category not found")
    return updated


@router.delete("/article-categories/{category_id}")
async def delete_category_route(category_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Delete an article category"""
    category = await crud_article.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Article Category not found")
    
    success = await crud_article.delete_category(db, category_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete article category.")

    return {"detail": "Article Category deleted successfully (associated Articles' category was set to null)."}
