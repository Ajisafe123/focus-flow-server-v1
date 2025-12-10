"""MongoDB CRUD operations for Users"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from ..config import settings
from ..database import get_db
import uuid

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login-json")
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login-json", auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hashed password"""
    plain_password = (plain_password or "")[:72]
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta=None) -> str:
    """Create JWT token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def get_user_by_username(db: AsyncIOMotorDatabase, username: str) -> Optional[dict]:
    """Get user by username"""
    return await db["users"].find_one({"username": username})


async def get_user_by_email(db: AsyncIOMotorDatabase, email: str) -> Optional[dict]:
    """Get user by email"""
    return await db["users"].find_one({"email": email})


async def get_user_by_id(db: AsyncIOMotorDatabase, user_id) -> Optional[dict]:
    """Get user by ID"""
    if isinstance(user_id, str):
        try:
            user_id = ObjectId(user_id)
        except:
            return None
    
    return await db["users"].find_one({"_id": user_id})


async def authenticate_user(db: AsyncIOMotorDatabase, identifier: str, password: str) -> Optional[dict]:
    """Authenticate user with username/email and password"""
    user = await get_user_by_username(db, identifier)
    if not user:
        user = await get_user_by_email(db, identifier)
    
    if not user or not verify_password(password, user.get("hashed_password", "")):
        return None
    
    if not user.get("is_active", True):
        return None
    
    return user


async def create_user(db: AsyncIOMotorDatabase, user_data: dict) -> dict:
    """Create a new user"""
    user_data["_id"] = ObjectId()
    user_data["created_at"] = datetime.utcnow()
    user_data["updated_at"] = datetime.utcnow()
    user_data["is_active"] = user_data.get("is_active", True)
    user_data["is_verified"] = user_data.get("is_verified", False)
    user_data["role"] = user_data.get("role", "user")
    user_data["status"] = user_data.get("status", "active")
    
    result = await db["users"].insert_one(user_data)
    user_data["_id"] = result.inserted_id
    return user_data


async def update_user(db: AsyncIOMotorDatabase, user_id, user_data: dict) -> Optional[dict]:
    """Update user data"""
    if isinstance(user_id, str):
        user_id = ObjectId(user_id)
    
    user_data["updated_at"] = datetime.utcnow()
    
    result = await db["users"].update_one(
        {"_id": user_id},
        {"$set": user_data}
    )
    
    if result.matched_count == 0:
        return None
    
    return await db["users"].find_one({"_id": user_id})


async def delete_user(db: AsyncIOMotorDatabase, user_id) -> bool:
    """Delete a user"""
    if isinstance(user_id, str):
        user_id = ObjectId(user_id)
    
    result = await db["users"].delete_one({"_id": user_id})
    return result.deleted_count > 0


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception
    
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been suspended or is inactive.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_optional_user(
    token: Optional[str] = Depends(optional_oauth2_scheme),
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> Optional[dict]:
    """Get optional authenticated user (returns None if not authenticated)"""
    if token is None:
        return None
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None
    
    return await get_user_by_id(db, user_id)


async def create_password_reset_code(db: AsyncIOMotorDatabase, user_id, code: str) -> dict:
    """Create password reset code"""
    reset_data = {
        "_id": ObjectId(),
        "user_id": ObjectId(user_id) if isinstance(user_id, str) else user_id,
        "code": code,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(minutes=settings.RESET_TOKEN_EXPIRE_MINUTES)
    }
    
    result = await db["password_reset_codes"].insert_one(reset_data)
    reset_data["_id"] = result.inserted_id
    return reset_data


async def verify_reset_code(db: AsyncIOMotorDatabase, user_id, code: str) -> bool:
    """Verify password reset code"""
    if isinstance(user_id, str):
        user_id = ObjectId(user_id)
    
    reset_record = await db["password_reset_codes"].find_one({
        "user_id": user_id,
        "code": code,
        "expires_at": {"$gt": datetime.utcnow()}
    })
    
    return reset_record is not None


async def delete_reset_code(db: AsyncIOMotorDatabase, user_id, code: str) -> bool:
    """Delete password reset code"""
    if isinstance(user_id, str):
        user_id = ObjectId(user_id)
    
    result = await db["password_reset_codes"].delete_one({
        "user_id": user_id,
        "code": code
    })
    
    return result.deleted_count > 0
