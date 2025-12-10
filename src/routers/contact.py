from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from typing import List, Optional
from ..database import get_db
from ..schemas.contact import ContactMessageCreate
from ..models.mongo_models import ContactMessageInDB
from ..services.email_service import send_contact_notification
from ..utils.users import get_current_user

router = APIRouter(prefix="/contact", tags=["Contact"])

@router.post("/send")
async def send_message(
    message: ContactMessageCreate, 
    background_tasks: BackgroundTasks,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    contact_collection = db["contact_messages"]
    
    new_message = message.dict()
    new_message["created_at"] = datetime.utcnow()
    new_message["is_read"] = False
    
    result = await contact_collection.insert_one(new_message)
    
    # Send email in background
    background_tasks.add_task(send_contact_notification, message, recipient="ajisafeibrahim54@gmail.com")

    # Create Admin Notification
    try:
        from ..utils.notifications import create_notifications
        await create_notifications(
            db,
            title="New Contact Message",
            message=f"From: {message.name}",
            notif_type="contact",
            recipient_role="admin",  # Notify all admins
            link="/admin/messages"
        )
    except Exception as e:
        print(f"Warning: Failed to create admin notification: {e}")
    
    return {"message": "Your message has been sent successfully."}

@router.get("", response_model=List[ContactMessageInDB])
async def list_messages(
    skip: int = 0,
    limit: int = 50,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
        
    cursor = db["contact_messages"].find().sort("created_at", -1).skip(skip).limit(limit)
    messages = await cursor.to_list(length=limit)
    return messages

@router.delete("/{message_id}")
async def delete_message(
    message_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
        
    from bson import ObjectId
    try:
        oid = ObjectId(message_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")
        
    result = await db["contact_messages"].delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Message not found")
        
    return {"message": "Message deleted"}
