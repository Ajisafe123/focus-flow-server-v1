import asyncio
import json
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import Dict, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..services import prayer_service
from ..database import get_db
from ..schemas.users import UserResponse
from ..utils.users import get_current_user as get_current_user_util, get_optional_user as get_optional_user_util, oauth2_scheme, optional_oauth2_scheme
import httpx

router = APIRouter(prefix="/prayers", tags=["Prayers"])
scheduler = prayer_service.Scheduler()
USER_SETTINGS: Dict[str, Dict] = {}

DEFAULT_LAT = 7.3775
DEFAULT_LON = 3.947

async def get_optional_current_user(
    token: Optional[str] = Depends(optional_oauth2_scheme),
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> Optional[dict]:
    """Wrapper to get optional user with proper dependencies"""
    return await get_optional_user_util(token, db)

async def get_authenticated_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> dict:
    """Wrapper to get authenticated user with proper dependencies"""
    return await get_current_user_util(token, db)

@router.get("/times", response_model=None)
async def get_prayer_times_endpoint(
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None),
    method: str = Query("ISNA"),
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: Optional[dict] = Depends(get_optional_current_user) 
) -> dict:
    final_lat = lat
    final_lon = lon
    
    if current_user:
        if final_lat is None and current_user.get("latitude") is not None:
            final_lat = current_user.get("latitude")
        if final_lon is None and current_user.get("longitude") is not None:
            final_lon = current_user.get("longitude")
            
        if lat is not None and lon is not None:
            if current_user.get("latitude") != lat or current_user.get("longitude") != lon:
                users_collection = db["users"]
                await users_collection.update_one(
                    {"_id": current_user.get("_id")},
                    {"$set": {
                        "latitude": lat,
                        "longitude": lon
                    }}
                )

    if final_lat is None or final_lon is None:
        final_lat = DEFAULT_LAT
        final_lon = DEFAULT_LON
    
    data = await prayer_service.get_prayer_times(final_lat, final_lon, method)
    return data

@router.get("/reverse-geocode", response_model=None)
async def reverse_geocode_proxy(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude")
):
    nominatim_url = "https://nominatim.openstreetmap.org/reverse"

    headers = {
        "User-Agent": "NibrasPrayerApp/1.0 (contact@example.com)", 
        "Accept-Language": "en"
    }
    params = {
        "format": "json",
        "lat": lat,
        "lon": lon,
        "zoom": 18,
        "addressdetails": 1
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(nominatim_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Nominatim request failed: {e.response.status_code}")
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"An error occurred while requesting Nominatim: {str(e)}")

@router.get("/users/me", response_model=None)
async def read_users_me(current_user: dict = Depends(get_authenticated_user)):
    return {
        "id": str(current_user.get("_id")),
        "email": current_user.get("email"),
        "username": current_user.get("username"),
        "role": current_user.get("role"),
        "is_active": current_user.get("is_active"),
        "latitude": current_user.get("latitude"),
        "longitude": current_user.get("longitude")
    }

@router.post("/users/me/mute", response_model=None)
async def mute_azan(current_user: dict = Depends(get_authenticated_user)):
    user_id = str(current_user.get("_id"))
    USER_SETTINGS[user_id] = {"muted": True}
    return {"status": "success", "muted": True}

@router.post("/users/me/unmute", response_model=None)
async def unmute_azan(current_user: dict = Depends(get_authenticated_user)):
    user_id = str(current_user.get("_id"))
    USER_SETTINGS[user_id] = {"muted": False}
    return {"status": "success", "muted": False}

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, ws: WebSocket, user_id: str):
        await ws.accept()
        self.active_connections[user_id] = ws

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            try:
                ws = self.active_connections[user_id]
                asyncio.create_task(ws.close())
            except Exception:
                pass
            del self.active_connections[user_id]

    async def send_json(self, user_id: str, data: dict):
        ws = self.active_connections.get(user_id)
        if not ws:
            return

        try:
            muted = USER_SETTINGS.get(user_id, {}).get("muted", False)
            data["muted"] = muted
            await ws.send_json(data)
        except Exception:
            self.disconnect(user_id)

manager = ConnectionManager()

async def broadcaster():
    while True:
        try:
            results = await scheduler.run()
            for uid, payload in results.items():
                await manager.send_json(uid, payload)
        except Exception:
            pass
        await asyncio.sleep(30)

@router.on_event("startup")
async def start_broadcaster():
    asyncio.create_task(broadcaster())

@router.websocket("/ws")
async def prayer_ws(ws: WebSocket, db: AsyncIOMotorDatabase = Depends(get_db)):
    user_id = None
    try:
        raw = await ws.receive_text()
        try:
            data = json.loads(raw)
        except Exception:
            await ws.close(code=1003)
            return

        current_user = None
        token = data.get("token")
        if token:
            try:
                current_user = await get_optional_user_util(token, db)
            except Exception:
                pass
        
        user_id = str(current_user.get("_id")) if current_user else f"user_{id(ws)}"
        
        lat = data.get("lat")
        lon = data.get("lon")
        
        if not lat or not lon:
            if current_user and current_user.get("latitude") and current_user.get("longitude"):
                lat = current_user.get("latitude")
                lon = current_user.get("longitude")
            else:
                lat = DEFAULT_LAT
                lon = DEFAULT_LON
        
        method = data.get("method", "ISNA")
        scheduler.add_user(user_id, lat, lon, method)
        await manager.connect(ws, user_id)
        
        try:
            payload = await prayer_service.get_prayer_times(lat, lon, method)
            await manager.send_json(user_id, payload)
        except Exception:
            pass
        
        while True:
            msg = await ws.receive_text()
            try:
                obj = json.loads(msg)
                if "lat" in obj and "lon" in obj:
                    lat = obj["lat"]
                    lon = obj["lon"]
                    scheduler.add_user(user_id, lat, lon, obj.get("method", method))
                if obj.get("action") == "refresh":
                    payload = await prayer_service.get_prayer_times(lat, lon, obj.get("method", method))
                    await manager.send_json(user_id, payload)
            except Exception:
                pass
    except WebSocketDisconnect:
        if user_id:
            manager.disconnect(user_id)
    except Exception:
        try:
            if user_id:
                manager.disconnect(user_id)
        except:
            pass
