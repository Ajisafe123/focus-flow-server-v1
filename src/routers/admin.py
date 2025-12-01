from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import Optional
from datetime import datetime
from ..database import get_db
from ..utils.users import get_password_hash, get_current_user

router = APIRouter(prefix="/api/admin", tags=["Admin"])


async def admin_only(current_user = Depends(get_current_user)):
    """Admin role check"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.get("/users")
async def list_regular_users(
    limit: int = Query(20, gt=0),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    status_val: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db),
    admin = Depends(admin_only)
):
    filters = {}
    if search:
        filters["$or"] = [
            {"username": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}}
        ]
    
    if role:
        filters["role"] = role
    
    if status_val:
        filters["status"] = status_val

    users_collection = db["users"]
    total = await users_collection.count_documents(filters)
    
    cursor = users_collection.find(filters).skip(offset).limit(limit)
    users = await cursor.to_list(length=limit)
    
    out = []
    for u in users:
        reset_count = await db["password_reset_codes"].count_documents({"user_id": u["_id"]})
        out.append({
            "id": str(u["_id"]),
            "email": u.get("email"),
            "username": u.get("username"),
            "role": u.get("role", "user"), 
            "status": u.get("status", "active"),
            "created_at": u.get("created_at"),
            "updated_at": u.get("updated_at"),
            "reset_codes_count": reset_count,
            "hashed_password": u.get("hashed_password")
        })
    return {"total": total, "limit": limit, "offset": offset, "users": out}


@router.get("/users/stats")
async def regular_users_stats(
    db: AsyncIOMotorDatabase = Depends(get_db),
    admin = Depends(admin_only)
):
    users_collection = db["users"]
    
    total = await users_collection.count_documents({})
    active = await users_collection.count_documents({"status": "active"})
    suspended = await users_collection.count_documents({"status": "suspended"})
    editors = await users_collection.count_documents({"role": "editor"})
    admins = await users_collection.count_documents({"role": "admin"})
    
    return {
        "total_users": total, 
        "active_users": active, 
        "suspended_users": suspended, 
        "editors": editors, 
        "admins": admins
    }


@router.get("/users/{user_id}")
async def get_regular_user_full(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    admin = Depends(admin_only)
):
    try:
        obj_id = ObjectId(user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    users_collection = db["users"]
    u = await users_collection.find_one({"_id": obj_id})
    
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    
    reset_count = await db["password_reset_codes"].count_documents({"user_id": obj_id})
    
    return {
        "id": str(u["_id"]),
        "email": u.get("email"),
        "username": u.get("username"),
        "role": u.get("role", "user"),
        "status": u.get("status", "active"),
        "created_at": u.get("created_at"),
        "updated_at": u.get("updated_at"),
        "reset_codes_count": reset_count,
        "hashed_password": u.get("hashed_password"),
        "bio": u.get("bio"),
        "avatar_url": u.get("avatar_url"),
        "city": u.get("city"),
        "region": u.get("region"),
        "country": u.get("country"),
        "latitude": u.get("latitude"),
        "longitude": u.get("longitude"),
        "ip_address": u.get("ip_address"),
        "location_accuracy": u.get("location_accuracy"),
        "is_active": u.get("is_active", True),
        "is_verified": u.get("is_verified", False)
    }

@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_regular_user(
    payload: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    admin = Depends(admin_only)
):
    email = payload.get("email")
    username = payload.get("username")
    password = payload.get("password")
    role = payload.get("role", "user")
    status_val = payload.get("status", "active")
    
    if not email or not username or not password:
        raise HTTPException(status_code=400, detail="email, username and password are required")
    
    users_collection = db["users"]
    
    if await users_collection.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if await users_collection.find_one({"username": username}):
        raise HTTPException(status_code=400, detail="Username already taken")
    
    hashed = get_password_hash(password)
    new_user = {
        "email": email,
        "username": username,
        "hashed_password": hashed,
        "role": role,
        "status": status_val,
        "is_active": status_val == "active",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    result = await users_collection.insert_one(new_user)
    
    return {
        "id": str(result.inserted_id),
        "email": new_user["email"],
        "username": new_user["username"],
        "role": new_user["role"],
        "status": new_user["status"]
    }

@router.put("/users/{user_id}")
async def edit_regular_user(
    user_id: str,
    payload: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    admin = Depends(admin_only)
):
    try:
        obj_id = ObjectId(user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    users_collection = db["users"]
    u = await users_collection.find_one({"_id": obj_id})
    
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = {}
    
    if "email" in payload and payload.get("email") is not None:
        if await users_collection.find_one({"email": payload.get("email"), "_id": {"$ne": obj_id}}):
            raise HTTPException(status_code=400, detail="Email already registered")
        update_data["email"] = payload.get("email")
    
    if "username" in payload and payload.get("username") is not None:
        if await users_collection.find_one({"username": payload.get("username"), "_id": {"$ne": obj_id}}):
            raise HTTPException(status_code=400, detail="Username already taken")
        update_data["username"] = payload.get("username")
    
    if "password" in payload and payload.get("password") is not None:
        update_data["hashed_password"] = get_password_hash(payload.get("password"))
    
    if "role" in payload:
        update_data["role"] = payload.get("role")
    
    if "status" in payload:
        update_data["status"] = payload.get("status")
        update_data["is_active"] = payload.get("status") == "active"
    
    update_data["updated_at"] = datetime.utcnow().isoformat()
    
    await users_collection.update_one({"_id": obj_id}, {"$set": update_data})
    
    updated_user = await users_collection.find_one({"_id": obj_id})
    
    return {
        "id": str(updated_user["_id"]),
        "email": updated_user.get("email"),
        "username": updated_user.get("username"),
        "role": updated_user.get("role"),
        "status": updated_user.get("status")
    }

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_regular_user(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    admin = Depends(admin_only)
):
    try:
        obj_id = ObjectId(user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    users_collection = db["users"]
    result = await users_collection.delete_one({"_id": obj_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"detail": "deleted"}

@router.patch("/users/{user_id}/suspend")
async def suspend_regular_user(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    admin = Depends(admin_only)
):
    try:
        obj_id = ObjectId(user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    users_collection = db["users"]
    u = await users_collection.find_one({"_id": obj_id})
    
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    
    await users_collection.update_one(
        {"_id": obj_id},
        {"$set": {
            "status": "suspended",
            "is_active": False,
            "updated_at": datetime.utcnow().isoformat()
        }}
    )
    
    updated = await users_collection.find_one({"_id": obj_id})
    return {"detail": "suspended", "status": updated.get("status")}

@router.patch("/users/{user_id}/activate")
async def activate_regular_user(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    admin = Depends(admin_only)
):
    try:
        obj_id = ObjectId(user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    users_collection = db["users"]
    u = await users_collection.find_one({"_id": obj_id})
    
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    
    await users_collection.update_one(
        {"_id": obj_id},
        {"$set": {
            "status": "active",
            "is_active": True,
            "updated_at": datetime.utcnow().isoformat()
        }}
    )
    
    updated = await users_collection.find_one({"_id": obj_id})
    return {"detail": "activated", "status": updated.get("status")}

@router.patch("/users/{user_id}/role")
async def change_regular_user_role(
    user_id: str,
    payload: dict = Body(...),
    db: AsyncIOMotorDatabase = Depends(get_db),
    admin = Depends(admin_only)
):
    try:
        obj_id = ObjectId(user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    users_collection = db["users"]
    u = await users_collection.find_one({"_id": obj_id})
    
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_role = payload.get("role")
    if not new_role:
        raise HTTPException(status_code=400, detail="role is required")
    
    await users_collection.update_one(
        {"_id": obj_id},
        {"$set": {
            "role": new_role,
            "updated_at": datetime.utcnow().isoformat()
        }}
    )
    
    return {"detail": "role updated"}
