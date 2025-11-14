from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta, datetime
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from ..database import get_db
from ..models.users import User
from ..schemas.users import (
    UserCreate, UserResponse, Token, UserLogin, UserUpdate,
    ForgotPasswordRequest, VerifyCodeRequest, ResetPasswordRequest,
    ChatUserCreate, ChatUserOut
)
from ..services.email_service import send_password_reset_email
from ..utils.users import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_user_by_username,
    get_user_by_email,
    get_current_active_user,
    update_user_account,
    create_reset_code,
    verify_reset_code,
    verify_password,
    admin_only
)
from ..config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_email = await get_user_by_email(db, user.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    existing_username = await get_user_by_username(db, user.username)
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, credentials.identifier, credentials.password)
    
    if not user:
        temp_user = await get_user_by_username(db, credentials.identifier) or await get_user_by_email(db, credentials.identifier)

        if temp_user and verify_password(credentials.password, temp_user.hashed_password) and not temp_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account has been suspended.",
            )
        
        msg = "Incorrect email or password" if "@" in credentials.identifier else "Incorrect username or password"
        raise HTTPException(status_code=401, detail=msg)
    
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "username": user.username,
        "email": user.email,
    }

@router.post("/logout")
async def logout():
    return {"message": "Successfully logged out"}

@router.put("/profile/update", response_model=UserResponse)
async def update_profile(
    bio: str = Form(None),
    avatar: UploadFile = File(None),
    username: str = Form(None),
    city: str = Form(None),
    region: str = Form(None),
    country: str = Form(None),
    latitude: float = Form(None),
    longitude: float = Form(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    if username:
        existing_user = await get_user_by_username(db, username)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(status_code=400, detail="Username already taken")
        current_user.username = username
    if bio:
        current_user.bio = bio
    if city:
        current_user.city = city
    if region:
        current_user.region = region
    if country:
        current_user.country = country
    if latitude is not None:
        current_user.latitude = latitude
    if longitude is not None:
        current_user.longitude = longitude
    if avatar:
        current_user.avatar_url = f"/static/uploads/{avatar.filename}"
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user

@router.put("/account/update", response_model=UserResponse)
async def update_account(update_data: UserUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    updated_user = await update_user_account(db, current_user.id, update_data)
    return updated_user

@router.post("/forgot-password")
async def forgot_password(req: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, req.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    code = await create_reset_code(db, user)
    await send_password_reset_email(req.email, code)
    return {"message": "Password reset code sent to email"}

@router.post("/verify-code")
async def verify_code(req: VerifyCodeRequest, db: AsyncSession = Depends(get_db)):
    await verify_reset_code(db, req.email, req.code)
    return {"message": "Code verified"}

@router.post("/reset-password")
async def reset_password(req: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    user = await verify_reset_code(db, req.email, req.code)
    user.hashed_password = get_password_hash(req.new_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"message": "Password reset successfully"}

@router.get("/admin/dashboard")
async def get_admin_dashboard(current_user: User = Depends(admin_only)):
    return {"message": f"Welcome Admin {current_user.username}"}

@router.post("/chat/create", response_model=ChatUserOut)
async def create_chat_user(payload: ChatUserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.email == payload.email))
    existing = result.scalars().first()
    if existing:
        return existing
    new_user = User(
        username=payload.name,
        email=payload.email,
        avatar_url=None
    )
    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Could not create chat user")
    return new_user

@router.put("/chat/{user_id}/status")
async def update_chat_status(user_id: int, isOnline: bool, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_verified = isOnline 
    user.updated_at = datetime.utcnow()
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"ok": True, "is_online": user.is_verified}