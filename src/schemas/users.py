from pydantic import BaseModel, EmailStr, constr, validator, Field
from typing import Optional, Union
from datetime import datetime
from bson import ObjectId


class UserBase(BaseModel):
    email: EmailStr
    username: constr(min_length=3, max_length=20, pattern=r"^[a-zA-Z0-9_]+$")


class UserCreate(UserBase):
    password: constr(min_length=8, max_length=128)

    @validator("password")
    def validate_password(cls, value):
        if not any(c.isupper() for c in value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in value):
            raise ValueError("Password must contain at least one digit")
        return value


class UserResponse(BaseModel):
    id: Optional[Union[str, ObjectId]] = Field(None, alias="_id")
    username: str
    email: str
    full_name: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    created_at: Optional[datetime] = None
    role: Optional[str] = "user"

    @validator("id", pre=True, always=True)
    def convert_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        from_attributes = True
        populate_by_name = True
        arbitrary_types_allowed = True


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)
    confirm_password: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str
    role: Optional[str] = "user"


class UserLogin(BaseModel):
    identifier: str
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class VerifyCodeRequest(BaseModel):
    email: EmailStr
    code: constr(min_length=6, max_length=6)


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    code: constr(min_length=6, max_length=6)
    new_password: constr(min_length=8, max_length=128)

    @classmethod
    def validate_password(cls, value: str):
        if not any(c.isupper() for c in value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in value):
            raise ValueError("Password must contain at least one digit")
        return value

class ChatUserCreate(BaseModel):
    name: str
    email: EmailStr


class ChatUserOut(BaseModel):
    id: Optional[Union[str, ObjectId]] = Field(None, alias="_id")
    name: str
    email: EmailStr
    avatar_letter: Optional[str]
    is_online: Optional[bool]
    created_at: Optional[datetime]

    @validator("id", pre=True, always=True)
    def convert_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        from_attributes = True
        populate_by_name = True
        arbitrary_types_allowed = True
