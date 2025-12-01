from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from ..database import get_db
from ..schemas.contact import ContactMessageCreate
from ..services.email_service import send_contact_notification

router = APIRouter(prefix="/contact", tags=["Contact"])

@router.post("/send")
async def send_message(message: ContactMessageCreate, db: AsyncIOMotorDatabase = Depends(get_db)):
    contact_collection = db["contact_messages"]
    
    new_message = {
        "name": message.name,
        "email": message.email,
        "subject": message.subject,
        "message": message.message,
        "created_at": datetime.utcnow().isoformat()
    }
    
    await contact_collection.insert_one(new_message)
    await send_contact_notification(message, recipient="ajisafeibrahim54@gmail.com")
    
    return {"message": "Your message has been sent successfully."}
