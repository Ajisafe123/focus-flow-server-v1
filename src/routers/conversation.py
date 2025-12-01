from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from ..database import get_db
from ..schemas.conversation import ConversationCreate, ConversationOut
from ..utils.users import get_current_user

router = APIRouter(prefix="/api/conversations", tags=["Conversations"])


@router.post("", response_model=dict)
async def create_conversation(payload: ConversationCreate, db: AsyncIOMotorDatabase = Depends(get_db)):
    users_collection = db["users"]
    conversations_collection = db["conversations"]
    
    user_id = payload.userId
    if not user_id and payload.userEmail:
        user = await users_collection.find_one({"email": payload.userEmail})
        if not user:
            new_user = {
                "email": payload.userEmail,
                "username": payload.userName or "Guest",
                "is_active": True,
                "is_verified": False,
                "role": "user",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            result = await users_collection.insert_one(new_user)
            user_id = result.inserted_id
        else:
            user_id = user["_id"]

    conv_data = {
        "user_id": user_id,
        "status": "active",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    result = await conversations_collection.insert_one(conv_data)
    
    return {
        "id": str(result.inserted_id),
        "user_id": str(user_id),
        "status": conv_data["status"],
        "created_at": conv_data["created_at"],
        "updated_at": conv_data["updated_at"]
    }


@router.get("/{conversation_id}", response_model=dict)
async def get_conv(conversation_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    try:
        obj_id = ObjectId(conversation_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid conversation ID")
    
    conversations_collection = db["conversations"]
    conv = await conversations_collection.find_one({"_id": obj_id})
    
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {
        "id": str(conv["_id"]),
        "user_id": str(conv.get("user_id")),
        "status": conv.get("status"),
        "created_at": conv.get("created_at"),
        "updated_at": conv.get("updated_at")
    }


@router.put("/{conversation_id}/status", response_model=dict)
async def update_status(
    conversation_id: str,
    status: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        obj_id = ObjectId(conversation_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid conversation ID")
    
    conversations_collection = db["conversations"]
    conv = await conversations_collection.find_one({"_id": obj_id})
    
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    await conversations_collection.update_one(
        {"_id": obj_id},
        {"$set": {
            "status": status,
            "updated_at": datetime.utcnow().isoformat()
        }}
    )
    
    updated = await conversations_collection.find_one({"_id": obj_id})
    
    return {
        "id": str(updated["_id"]),
        "user_id": str(updated.get("user_id")),
        "status": updated.get("status"),
        "created_at": updated.get("created_at"),
        "updated_at": updated.get("updated_at")
    }
