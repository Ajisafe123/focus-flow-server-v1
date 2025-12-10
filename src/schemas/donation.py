from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DonationCreate(BaseModel):
    donor_name: Optional[str] = "Anonymous"
    donor_email: Optional[str] = None
    amount: float
    currency: str = "USD"
    message: Optional[str] = None
    payment_method: Optional[str] = None

class DonationRead(BaseModel):
    id: str
    donor_name: Optional[str]
    amount: float
    currency: str
    message: Optional[str]
    status: str
    created_at: datetime
