from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, or_, and_
from typing import Optional
from uuid import UUID
from datetime import datetime
from ..database import get_db
from ..models.users import User, PasswordResetCode
from ..models.admin import AdminUser
from ..utils.users import get_password_hash, admin_only

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/users")
async def list_regular_users(
    limit: int = Query(20, gt=0),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(admin_only)
):
    filters = []
    if search:
        term = f"%{search.lower()}%"
        filters.append(or_(func.lower(User.username).like(term), func.lower(User.email).like(term)))
    
    where_clause = None
    if filters:
        where_clause = filters[0] 

    if role:
        role_filter = (User.role == role)
        where_clause = and_(where_clause, role_filter) if where_clause is not None else role_filter
        
    if status:
        status_filter = (User.status == status)
        where_clause = and_(where_clause, status_filter) if where_clause is not None else status_filter

    if where_clause is not None:
        total = (await db.execute(select(func.count()).select_from(User).where(where_clause))).scalar() or 0
        result = await db.execute(select(User).where(where_clause).limit(limit).offset(offset))
    else:
        total = (await db.execute(select(func.count()).select_from(User))).scalar() or 0
        result = await db.execute(select(User).limit(limit).offset(offset))
    
    users = result.scalars().all()
    out = []
    for u in users:
        reset_count = (await db.execute(select(func.count()).select_from(PasswordResetCode).filter(PasswordResetCode.user_id == u.id))).scalar() or 0
        out.append({
            "id": str(u.id),
            "email": u.email,
            "username": u.username,
            "role": u.role, 
            "status": u.status,
            "created_at": u.created_at,
            "updated_at": u.updated_at,
            "reset_codes_count": reset_count,
            "hashed_password": u.hashed_password
        })
    return {"total": total, "limit": limit, "offset": offset, "users": out}


@router.get("/users/stats")
async def regular_users_stats(db: AsyncSession = Depends(get_db), admin: AdminUser = Depends(admin_only)):
    total = (await db.execute(select(func.count()).select_from(User))).scalar() or 0
    
    active = (await db.execute(select(func.count()).select_from(User).filter(User.status == "active"))).scalar() or 0
    suspended = (await db.execute(select(func.count()).select_from(User).filter(User.status == "suspended"))).scalar() or 0
    editors = (await db.execute(select(func.count()).select_from(User).filter(User.role == "editor"))).scalar() or 0
    admins = (await db.execute(select(func.count()).select_from(User).filter(User.role == "admin"))).scalar() or 0
    
    return {
        "total_users": total, 
        "active_users": active, 
        "suspended_users": suspended, 
        "editors": editors, 
        "admins": admins
    }


@router.get("/users/{user_id}")
async def get_regular_user_full(user_id: UUID, db: AsyncSession = Depends(get_db), admin: AdminUser = Depends(admin_only)):
    result = await db.execute(select(User).filter(User.id == user_id))
    u = result.scalars().first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    reset_count = (await db.execute(select(func.count()).select_from(PasswordResetCode).filter(PasswordResetCode.user_id == u.id))).scalar() or 0
    return {
        "id": str(u.id),
        "email": u.email,
        "username": u.username,
        "role": u.role,
        "status": u.status,
        "created_at": u.created_at,
        "updated_at": u.updated_at,
        "reset_codes_count": reset_count,
        "hashed_password": u.hashed_password,
        "bio": u.bio,
        "avatar_url": u.avatar_url,
        "city": u.city,
        "region": u.region,
        "country": u.country,
        "latitude": u.latitude,
        "longitude": u.longitude,
        "ip_address": u.ip_address,
        "location_accuracy": u.location_accuracy,
        "is_active": u.is_active,
        "is_verified": u.is_verified
    }

@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_regular_user(payload: dict = Body(...), db: AsyncSession = Depends(get_db), admin: AdminUser = Depends(admin_only)):
    email = payload.get("email")
    username = payload.get("username")
    password = payload.get("password")
    role = payload.get("role", "user")
    status_val = payload.get("status", "active")
    if not email or not username or not password:
        raise HTTPException(status_code=400, detail="email, username and password are required")
    result = await db.execute(select(User).filter(User.email == email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")
    result = await db.execute(select(User).filter(User.username == username))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Username already taken")
    hashed = get_password_hash(password)
    new_user = User(email=email, username=username, hashed_password=hashed)
    new_user.role = role
    new_user.status = status_val
    new_user.is_active = status_val == "active"
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"id": str(new_user.id), "email": new_user.email, "username": new_user.username, "role": new_user.role, "status": new_user.status}

@router.put("/users/{user_id}")
async def edit_regular_user(user_id: UUID, payload: dict = Body(...), db: AsyncSession = Depends(get_db), admin: AdminUser = Depends(admin_only)):
    result = await db.execute(select(User).filter(User.id == user_id))
    u = result.scalars().first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    if "email" in payload and payload.get("email") is not None:
        r = await db.execute(select(User).filter(and_(User.email == payload.get("email"), User.id != u.id)))
        if r.scalars().first():
            raise HTTPException(status_code=400, detail="Email already registered")
        u.email = payload.get("email")
    if "username" in payload and payload.get("username") is not None:
        r = await db.execute(select(User).filter(and_(User.username == payload.get("username"), User.id != u.id)))
        if r.scalars().first():
            raise HTTPException(status_code=400, detail="Username already taken")
        u.username = payload.get("username")
    if "password" in payload and payload.get("password") is not None:
        u.hashed_password = get_password_hash(payload.get("password"))
    if "role" in payload:
        u.role = payload.get("role")
    if "status" in payload:
        u.status = payload.get("status")
        u.is_active = payload.get("status") == "active"
    u.updated_at = datetime.utcnow()
    db.add(u)
    await db.commit()
    await db.refresh(u)
    return {"id": str(u.id), "email": u.email, "username": u.username, "role": u.role, "status": u.status}

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_regular_user(user_id: UUID, db: AsyncSession = Depends(get_db), admin: AdminUser = Depends(admin_only)):
    result = await db.execute(select(User).filter(User.id == user_id))
    u = result.scalars().first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    await db.delete(u)
    await db.commit()
    return {"detail": "deleted"}

@router.patch("/users/{user_id}/suspend")
async def suspend_regular_user(user_id: UUID, db: AsyncSession = Depends(get_db), admin: AdminUser = Depends(admin_only)):
    result = await db.execute(select(User).filter(User.id == user_id))
    u = result.scalars().first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    
    u.status = "suspended"
    u.is_active = False
    
    u.updated_at = datetime.utcnow()
    db.add(u)
    await db.commit()
    await db.refresh(u)
    return {"detail": "suspended", "status": u.status}

@router.patch("/users/{user_id}/activate")
async def activate_regular_user(user_id: UUID, db: AsyncSession = Depends(get_db), admin: AdminUser = Depends(admin_only)):
    result = await db.execute(select(User).filter(User.id == user_id))
    u = result.scalars().first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    
    u.status = "active"
    u.is_active = True
    
    u.updated_at = datetime.utcnow()
    db.add(u)
    await db.commit()
    await db.refresh(u)
    return {"detail": "activated", "status": u.status}

@router.patch("/users/{user_id}/role")
async def change_regular_user_role(user_id: UUID, payload: dict = Body(...), db: AsyncSession = Depends(get_db), admin: AdminUser = Depends(admin_only)):
    result = await db.execute(select(User).filter(User.id == user_id))
    u = result.scalars().first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    new_role = payload.get("role")
    if not new_role:
        raise HTTPException(status_code=400, detail="role is required")
    u.role = new_role
    u.updated_at = datetime.utcnow()
    db.add(u)
    await db.commit()
    await db.refresh(u)
    return {"detail": "role updated"}