import asyncio
import json
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, Depends
from typing import Dict
from src.services import prayer_service
from ..models.users import User
from ..database import get_db
from sqlalchemy.orm import Session
from ..schemas.users import UserResponse
from ..utils.users import get_current_active_user, get_current_user

router = APIRouter(prefix="/prayers", tags=["Prayers"])
scheduler = prayer_service.Scheduler()
USER_SETTINGS: Dict[int, Dict] = {}  
@router.get("/times")
async def get_prayer_times_endpoint(
    lat: float = Query(None),
    lon: float = Query(None),
    method: str = Query("ISNA"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    lat = lat or current_user.latitude
    lon = lon or current_user.longitude
    if lat is None or lon is None:
        lat = 7.3775
        lon = 3.947   
    current_user.latitude = lat
    current_user.longitude = lon
    db.commit()
    db.refresh(current_user)
    data = await prayer_service.get_prayer_times(lat, lon, method)
    return data
@router.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user
@router.post("/users/me/mute")
async def mute_azan(current_user: User = Depends(get_current_active_user)):
    USER_SETTINGS[current_user.id] = {"muted": True}
    return {"status": "success", "muted": True}
@router.post("/users/me/unmute")
async def unmute_azan(current_user: User = Depends(get_current_active_user)):
    USER_SETTINGS[current_user.id] = {"muted": False}
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
async def prayer_ws(ws: WebSocket, db: Session = Depends(get_db)):
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
            current_user = await get_current_user(token, db)
        user_id = data.get("user_id", f"user_{id(ws)}")
        lat = data.get("lat")
        lon = data.get("lon")
        if not lat or not lon:
            if current_user and current_user.latitude and current_user.longitude:
                lat = current_user.latitude
                lon = current_user.longitude
            else:
                lat = 7.3775
                lon = 3.947
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
        manager.disconnect(user_id)
    except Exception:
        try:
            manager.disconnect(user_id)
        except:
            pass