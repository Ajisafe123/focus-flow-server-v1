from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from ..database import get_db
from ..schemas.rating import RatingCreate
from ..utils.users import get_current_user

router = APIRouter(prefix="/api/ratings", tags=["Ratings"])


@router.post("")
async def submit_rating(
    payload: RatingCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if payload.rating < 1 or payload.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    try:
        conv_id = ObjectId(payload.conversationId)
    except:
        raise HTTPException(status_code=400, detail="Invalid conversation ID")
    
    ratings_collection = db["ratings"]
    rating_data = {
        "conversation_id": conv_id,
        "user_id": current_user.get("_id"),
        "rating": payload.rating,
        "created_at": datetime.utcnow().isoformat()
    }
    
    result = await ratings_collection.insert_one(rating_data)
    
    return {"ok": True, "rating_id": str(result.inserted_id)}
