from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.schemas.rating import RatingCreate
from src.models.rating import Rating

router = APIRouter(prefix="/api/ratings", tags=["Ratings"])


@router.post("")
async def submit_rating(payload: RatingCreate, db: AsyncSession = Depends(get_db)):
    if payload.rating < 1 or payload.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    rating = Rating(conversation_id=payload.conversationId, rating=payload.rating)
    db.add(rating)
    await db.commit()
    await db.refresh(rating)
    return {"ok": True, "rating_id": str(rating.id)}
