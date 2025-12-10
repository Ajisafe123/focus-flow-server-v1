from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta
import secrets
import httpx
from fastapi.responses import JSONResponse, RedirectResponse
from ..database import get_db
from ..utils import users as crud_users
from ..utils.notifications import create_notifications
from ..services.email_service import send_password_reset_email, send_login_notification
from ..config import settings
from ..schemas.users import (
    UserCreate,
    UserLogin,
    ForgotPasswordRequest,
    VerifyCodeRequest,
    ResetPasswordRequest,
    UserUpdate,
    Token,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register")
async def register(user_data: UserCreate, db: AsyncIOMotorDatabase = Depends(get_db)):
    if await crud_users.get_user_by_username(db, user_data.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if await crud_users.get_user_by_email(db, user_data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    code = secrets.token_hex(3).upper()
    user_dict = {
        "username": user_data.username,
        "email": user_data.email,
        "hashed_password": crud_users.get_password_hash(user_data.password),
        "is_verified": False,
        "verification_code": code,
        "verification_code_expires_at": datetime.utcnow() + timedelta(minutes=15)
    }
    await crud_users.create_user(db, user_dict)
    try:
        await send_password_reset_email(user_data.email, code)
    except:
        pass
    return {"message": "Check your email for verification code", "email": user_data.email}

@router.post("/verify-email")
async def verify_email(req: VerifyCodeRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    user = await crud_users.get_user_by_email(db, req.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.get("verification_code") != req.code:
        raise HTTPException(status_code=400, detail="Invalid code")
    if user.get("verification_code_expires_at", datetime.min) < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Code expired")
    await crud_users.update_user(db, user["_id"], {
        "is_verified": True,
        "verification_code": None,
        "verification_code_expires_at": None
    })
    token = crud_users.create_access_token({"sub": str(user["_id"])})
    return {"message": "Email verified", "token": token}


@router.post("/resend-verification")
async def resend_verification(req: ForgotPasswordRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Resend verification code to the user's email."""
    user = await crud_users.get_user_by_email(db, req.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.get("is_verified"):
        return {"message": "User already verified"}

    code = secrets.token_hex(3).upper()
    await crud_users.update_user(db, user["_id"], {
        "verification_code": code,
        "verification_code_expires_at": datetime.utcnow() + timedelta(minutes=15)
    })
    
    try:
        await send_password_reset_email(req.email, code)
    except:
        pass
        
    return {"message": "Verification code resent"}

@router.post("/login")
async def login(user_data: UserLogin, db: AsyncIOMotorDatabase = Depends(get_db)):
    user = await crud_users.authenticate_user(db, user_data.identifier, user_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.get("is_verified", False):
        code = secrets.token_hex(3).upper()
        await crud_users.update_user(db, user["_id"], {
            "verification_code": code,
            "verification_code_expires_at": datetime.utcnow() + timedelta(minutes=15)
        })
        try:
            await send_password_reset_email(user["email"], code)
        except:
            pass
        return JSONResponse(
            status_code=403,
            content={
                "detail": "Email not verified. A new code has been sent.",
                "message": "Email not verified. A new code has been sent.",
                "email": user["email"],
                "requires_verification": True
            }
        )
    token = crud_users.create_access_token({"sub": str(user["_id"])})
    # fire-and-forget login notification + email
    try:
        await create_notifications(
            db,
            title="Login successful",
            message="You just signed in to your account.",
            notif_type="info",
            user_ids=[str(user["_id"])],
        )
        await send_login_notification(user["email"])
    except Exception:
        # avoid blocking login on notification failure
        pass

    return {
        "token": token,
        "user_id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"],
        "role": user.get("role", "user")
    }

@router.post("/forgot-password")
async def forgot_password(req: ForgotPasswordRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    user = await crud_users.get_user_by_email(db, req.email)
    if not user:
        return {"message": "If the email exists, a reset code was sent"}
    code = secrets.token_hex(3).upper()
    await crud_users.create_password_reset_code(db, user["_id"], code)
    try:
        await send_password_reset_email(req.email, code)
    except:
        pass
    return {"message": "Reset code sent to email"}

@router.post("/verify-code")
async def verify_code(req: VerifyCodeRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    user = await crud_users.get_user_by_email(db, req.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    valid = await crud_users.verify_reset_code(db, user["_id"], req.code)
    if not valid:
        raise HTTPException(status_code=400, detail="Invalid or expired code")
    return {"message": "Code verified"}

@router.post("/reset-password")
async def reset_password(req: ResetPasswordRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    user = await crud_users.get_user_by_email(db, req.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    valid = await crud_users.verify_reset_code(db, user["_id"], req.code)
    if not valid:
        raise HTTPException(status_code=400, detail="Invalid or expired code")
    await crud_users.update_user(db, user["_id"], {
        "hashed_password": crud_users.get_password_hash(req.new_password)
    })
    await crud_users.delete_reset_code(db, user["_id"], req.code)
    return {"message": "Password reset successful"}


@router.post("/logout")
async def logout():
    """
    Stateless logout endpoint for clients to hit after clearing tokens.
    Kept for compatibility with frontend logout flow.
    """
    return {"message": "Logged out"}

@router.post("/profile/update")
async def update_profile(req: UserUpdate, current_user: dict = Depends(crud_users.get_current_user), db: AsyncIOMotorDatabase = Depends(get_db)):
    update_data = {k: v for k, v in req.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    await crud_users.update_user(db, current_user["_id"], update_data)
    user = await crud_users.get_user_by_id(db, current_user["_id"])
    return {
        "user_id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"],
        "full_name": user.get("full_name", ""),
        "bio": user.get("bio", ""),
        "avatar_url": user.get("avatar_url", "")
    }

@router.get("/me")
async def get_me(current_user: dict = Depends(crud_users.get_current_user)):
    return {
        "user_id": str(current_user["_id"]),
        "username": current_user["username"],
        "email": current_user["email"],
        "full_name": current_user.get("full_name", ""),
        "bio": current_user.get("bio", ""),
        "avatar_url": current_user.get("avatar_url", ""),
        "role": current_user.get("role", "user")
    }

GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET
FACEBOOK_APP_ID = settings.FACEBOOK_APP_ID
FACEBOOK_APP_SECRET = settings.FACEBOOK_APP_SECRET
FRONTEND_URL = settings.FRONTEND_URL
BACKEND_URL = settings.BACKEND_URL

@router.get("/login/google")
async def google_login():
    redirect_uri = f"{BACKEND_URL}/auth/callback/google"
    url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?response_type=code&client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        "&scope=openid%20email%20profile"
        "&access_type=offline&prompt=consent"
    )
    return RedirectResponse(url)

@router.get("/login/facebook")
async def facebook_login():
    redirect_uri = f"{BACKEND_URL}/auth/callback/facebook"
    url = (
        "https://www.facebook.com/v19.0/dialog/oauth"
        f"?client_id={FACEBOOK_APP_ID}"
        f"&redirect_uri={redirect_uri}"
        "&scope=email,public_profile&response_type=code"
    )
    return RedirectResponse(url)

async def handle_social_user(user_data, provider, db):
    email = user_data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email access denied")
    user = await crud_users.get_user_by_email(db, email)
    if not user:
        username_base = email.split("@")[0]
        username = username_base + "_" + provider[:3]
        counter = 1
        while await crud_users.get_user_by_username(db, username):
            username = f"{username_base}_{provider[:3]}{counter}"
            counter += 1
        user_dict = {
            "username": username,
            "email": email,
            "hashed_password": None,
            "is_verified": True,
            "full_name": user_data.get("name") or user_data.get("given_name", ""),
            "avatar_url": (
                user_data.get("picture", {}).get("data", {}).get("url")
                if provider == "facebook" else user_data.get("picture")
            ),
            "provider": provider,
        }
        user = await crud_users.create_user(db, user_dict)
    else:
        avatar = (
            user_data.get("picture", {}).get("data", {}).get("url")
            if provider == "facebook" else user_data.get("picture")
        )
        if avatar:
            await crud_users.update_user(db, user["_id"], {"avatar_url": avatar})
    token = crud_users.create_access_token({"sub": str(user["_id"])})
    return RedirectResponse(url=f"{FRONTEND_URL}/social-success?token={token}")

@router.get("/callback/google")
async def google_callback(code: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    redirect_uri = f"{BACKEND_URL}/auth/callback/google"
    async with httpx.AsyncClient(timeout=20.0) as client:
        token_res = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        if token_res.status_code != 200:
            raise HTTPException(status_code=400, detail="Invalid or expired code")
        token_data = token_res.json()
        user_res = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {token_data['access_token']}"},
        )
        user_data = user_res.json()
    return await handle_social_user(user_data, "google", db)

@router.get("/callback/facebook")
async def facebook_callback(code: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    redirect_uri = f"{BACKEND_URL}/auth/callback/facebook"
    async with httpx.AsyncClient(timeout=20.0) as client:
        token_res = await client.get(
            "https://graph.facebook.com/v19.0/oauth/access_token",
            params={
                "client_id": FACEBOOK_APP_ID,
                "client_secret": FACEBOOK_APP_SECRET,
                "redirect_uri": redirect_uri,
                "code": code,
            },
        )
        if token_res.status_code != 200:
            raise HTTPException(status_code=400, detail="Invalid or expired code")
        token_data = token_res.json()
        user_res = await client.get(
            "https://graph.facebook.com/me",
            params={
                "fields": "id,name,email,picture",
                "access_token": token_data["access_token"],
            },
        )
        user_data = user_res.json()
    return await handle_social_user(user_data, "facebook", db)
