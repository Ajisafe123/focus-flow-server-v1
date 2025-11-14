from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from ..config import settings
from ..database import get_db
from ..models.users import User, PasswordResetCode
from ..schemas.users import UserUpdate
import random
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login-json")
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login-json", auto_error=False)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    plain_password = (plain_password or "")[:72]
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta=None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=getattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", 60)))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=getattr(settings, "ALGORITHM", "HS256"))

async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()

async def authenticate_user(db: AsyncSession, identifier: str, password: str) -> Optional[User]:
    user = await get_user_by_username(db, identifier)
    if not user:
        user = await get_user_by_email(db, identifier)
    if not user or not verify_password(password, user.hashed_password):
        return None
    
    if not user.is_active:
        return None
        
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[getattr(settings, "ALGORITHM", "HS256")])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalars().first()
    if not user:
        raise credentials_exception
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been suspended or is inactive.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    return user

async def get_optional_user(token: Optional[str] = Depends(optional_oauth2_scheme), db: AsyncSession = Depends(get_db)) -> Optional[User]:
    if token is None:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[getattr(settings, "ALGORITHM", "HS256")])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            return None
    except JWTError:
        return None
    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalars().first()
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def update_user_account(db: AsyncSession, user_id: uuid.UUID, update_data: UserUpdate):
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if update_data.email is not None:
        email_check = await db.execute(select(User).filter(User.email == update_data.email))
        existing_email = email_check.scalars().first()
        if existing_email and existing_email.id != user.id:
            raise HTTPException(status_code=400, detail="Email already registered")
        user.email = update_data.email
    if update_data.password or update_data.confirm_password:
        if not update_data.password or not update_data.confirm_password:
            raise HTTPException(status_code=400, detail="Both password and confirm_password are required")
        if update_data.password != update_data.confirm_password:
            raise HTTPException(status_code=400, detail="Passwords do not match")
        user.hashed_password = get_password_hash(update_data.password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

def generate_reset_code():
    return str(random.randint(100000, 999999))

RESET_CODE_EXPIRE_MINUTES = 15

async def create_reset_code(db: AsyncSession, user: User) -> str:
    code = generate_reset_code()
    expires_at = datetime.utcnow() + timedelta(minutes=RESET_CODE_EXPIRE_MINUTES)
    reset_entry = PasswordResetCode(user_id=user.id, code=code, expires_at=expires_at)
    db.add(reset_entry)
    await db.commit()
    await db.refresh(reset_entry)
    return code

async def verify_reset_code(db: AsyncSession, email: str, code: str) -> User:
    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    res = await db.execute(
        select(PasswordResetCode)
        .filter(PasswordResetCode.user_id == user.id, PasswordResetCode.code == code)
    )
    reset_code = res.scalars().first()
    if not reset_code:
        raise HTTPException(status_code=400, detail="Invalid code")
    if reset_code.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Code expired")
    return user

async def admin_only(current_user: User = Depends(get_current_user)):
    if getattr(current_user, "role", None) != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only")
    return current_user