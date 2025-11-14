from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from uuid import UUID
from datetime import datetime

class AdminCreate(BaseModel):
    name: constr(min_length=1, max_length=255)
    email: EmailStr
    password: constr(min_length=8, max_length=128)

class AdminLogin(BaseModel):
    email: EmailStr
    password: str

class AdminOut(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    is_online: Optional[bool]
    created_at: Optional[datetime]
    class Config:
        orm_mode = True

class AdminTokenOut(BaseModel):
    access_token: str
    token_type: str
    email: Optional[EmailStr]
    name: Optional[str]
