from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.models.contact import ContactMessage
from src.schemas.contact import ContactMessageCreate
from src.services.email_service import send_contact_notification

router = APIRouter(prefix="/contact", tags=["Contact"])

@router.post("/send")
async def send_message(message: ContactMessageCreate, db: AsyncSession = Depends(get_db)):
    new_message = ContactMessage(
        name=message.name,
        email=message.email,
        subject=message.subject,
        message=message.message
    )
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)
    await send_contact_notification(message, recipient="ajisafeibrahim54@gmail.com")
    return {"message": "Your message has been sent successfully."}
