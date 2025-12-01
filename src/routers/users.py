from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import timedelta, datetime
from ..database import get_db
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
    get_current_user,
    create_user,
    update_user,
    verify_password,
    create_password_reset_code,
    verify_reset_code,
    delete_reset_code
)
from ..config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: AsyncIOMotorDatabase = Depends(get_db)):
    existing_email = await get_user_by_email(db, user.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    existing_username = await get_user_by_username(db, user.username)
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")
    hashed_password = get_password_hash(user.password)
    user_data = {
        "email": user.email,
        "username": user.username,
        "hashed_password": hashed_password
    }
    db_user = await create_user(db, user_data)
    return UserResponse(**db_user)

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: AsyncIOMotorDatabase = Depends(get_db)):
    user = await authenticate_user(db, credentials.identifier, credentials.password)
    
    if not user:
        temp_user = await get_user_by_username(db, credentials.identifier) or await get_user_by_email(db, credentials.identifier)

        if temp_user and verify_password(credentials.password, temp_user.get("hashed_password", "")) and not temp_user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account has been suspended.",
            )
        
        msg = "Incorrect email or password" if "@" in credentials.identifier else "Incorrect username or password"
        raise HTTPException(status_code=401, detail=msg)
    
    access_token = create_access_token(
        data={"sub": str(user["_id"]), "role": user.get("role", "user")},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.get("role", "user"),
        "username": user.get("username"),
        "email": user.get("email"),
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
    current_user = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    user_id = current_user.get("_id")
    update_data = {}
    
    if username:
        existing_user = await get_user_by_username(db, username)
        if existing_user and str(existing_user["_id"]) != str(user_id):
            raise HTTPException(status_code=400, detail="Username already taken")
        update_data["username"] = username
    if bio:
        update_data["bio"] = bio
    if city:
        update_data["city"] = city
    if region:
        update_data["region"] = region
    if country:
        update_data["country"] = country
    if latitude is not None:
        update_data["latitude"] = latitude
    if longitude is not None:
        update_data["longitude"] = longitude
    if avatar:
        update_data["avatar_url"] = f"/static/uploads/{avatar.filename}"
    
    if update_data:
        updated_user = await update_user(db, user_id, update_data)
        return UserResponse(**updated_user)
    return UserResponse(**current_user)

@router.put("/account/update", response_model=UserResponse)
async def update_account(
    update_data: UserUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(get_current_user)
):
    updated_user = await update_user(db, current_user["_id"], update_data.dict(exclude_unset=True))
    return UserResponse(**updated_user)

@router.post("/forgot-password")
async def forgot_password(req: ForgotPasswordRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    user = await get_user_by_email(db, req.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    code = await create_password_reset_code(db, user["_id"])
    await send_password_reset_email(req.email, code)
    return {"message": "Password reset code sent to email"}

@router.post("/verify-code")
async def verify_code(req: VerifyCodeRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    is_valid = await verify_reset_code(db, req.email, req.code)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid or expired code")
    return {"message": "Code verified"}

@router.post("/reset-password")
async def reset_password(req: ResetPasswordRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    user = await get_user_by_email(db, req.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    is_valid = await verify_reset_code(db, req.email, req.code)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid or expired code")
    
    hashed_password = get_password_hash(req.new_password)
    await update_user(db, user["_id"], {"hashed_password": hashed_password})
    await delete_reset_code(db, req.email)
    return {"message": "Password reset successfully"}

@router.get("/admin/dashboard")
async def get_admin_dashboard(current_user = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return {"message": f"Welcome Admin {current_user.get('username')}"}

@router.post("/chat/create", response_model=ChatUserOut)
async def create_chat_user(payload: ChatUserCreate, db: AsyncIOMotorDatabase = Depends(get_db)):
    existing = await get_user_by_email(db, payload.email)
    if existing:
        return ChatUserOut(**existing)
    
    user_data = {
        "username": payload.name,
        "email": payload.email,
        "avatar_url": None,
        "is_active": True,
        "is_verified": False,
        "role": "user",
        "created_at": datetime.utcnow().isoformat()
    }
    new_user = await create_user(db, user_data)
    return ChatUserOut(**new_user)

@router.put("/chat/{user_id}/status")
async def update_chat_status(user_id: str, isOnline: bool, db: AsyncIOMotorDatabase = Depends(get_db)):
    from bson import ObjectId
    try:
        obj_id = ObjectId(user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    updated_user = await update_user(db, obj_id, {"is_verified": isOnline, "updated_at": datetime.utcnow().isoformat()})
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"ok": True, "is_online": updated_user.get("is_verified")}