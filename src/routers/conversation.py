from fastapi import APIRouter, Depends, HTTPException, Body
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from ..database import get_db
from ..schemas.conversation import ConversationCreate, ConversationOut
from ..utils.users import get_current_user

router = APIRouter(prefix="/api/conversations", tags=["Conversations"])


@router.get("", response_model=None)
async def list_conversations(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    limit: int = 50,
):
    if current_user.get("role", "user") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    conversations_collection = db["conversations"]
    messages_collection = db["messages"]
    users_collection = db["users"]

    cursor = (
        conversations_collection.find({})
        .sort("updated_at", -1)
        .limit(limit)
    )
    convs = await cursor.to_list(length=limit)
    result = []
    for conv in convs:
        user = await users_collection.find_one({"_id": conv.get("user_id")})
        last_msg = await messages_collection.find_one(
            {"conversation_id": conv["_id"]}, sort=[("created_at", -1)]
        )
        result.append(
            {
                "id": str(conv["_id"]),
                "user_id": str(conv.get("user_id")),
                "user_email": user.get("email") if user else None,
                "user_name": user.get("username") or user.get("full_name") if user else None,
                "status": conv.get("status"),
                "created_at": conv.get("created_at"),
                "updated_at": conv.get("updated_at"),
                "last_message": last_msg.get("message_text") if last_msg else None,
            }
        )
    return result


@router.post("", response_model=None)
async def create_conversation(
    payload: dict | None = Body(default=None),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    users_collection = db["users"]
    conversations_collection = db["conversations"]

    body = payload or {}
    user_id = None
    user_email = body.get("userEmail")
    user_name = body.get("userName") or "Guest"
    user_id_raw = body.get("userId")

    if user_id_raw:
        try:
            user_id = ObjectId(user_id_raw)
        except Exception:
            user_id = None

    if not user_id and user_email:
        user = await users_collection.find_one({"email": user_email})
        if not user:
            new_user = {
                "email": user_email,
                "username": user_name,
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


@router.get("/{conversation_id}", response_model=None)
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


@router.put("/{conversation_id}/status", response_model=None)
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
