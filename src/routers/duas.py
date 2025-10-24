from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db
from ..utils import dua as crud_dua
from ..schemas.dua import DuaRead
import os

router = APIRouter(prefix="/duas", tags=["Duas"])

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

@router.get("/", response_model=List[DuaRead])
async def list_duas(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(crud_dua.Dua).order_by(crud_dua.Dua.category, crud_dua.Dua.id))
    return result.scalars().all()

@router.get("/search", response_model=List[DuaRead])
async def search_duas(q: str = Query(..., min_length=1), db: AsyncSession = Depends(get_db)):
    return await crud_dua.search_duas(db, q=q)

@router.get("/play")
async def play_dua(type: str = Query(default="morning", alias="type")):
    file_map = {
        "morning": os.path.join(STATIC_DIR, "audio", "morning_dua.mp3"),
        "evening": os.path.join(STATIC_DIR, "audio", "evening_dua.mp3")
    }

    dua_type = type.lower()
    if dua_type not in file_map:
        raise HTTPException(status_code=400, detail="Invalid dua type")

    file_path = file_map[dua_type]
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio not found")

    return {"audio_url": f"/static/audio/{dua_type}_dua.mp3"}

@router.get("/{dua_id}", response_model=DuaRead)
async def get_dua(dua_id: int, db: AsyncSession = Depends(get_db)):
    dua = await crud_dua.get_dua(db, dua_id)
    if not dua:
        raise HTTPException(status_code=404, detail="Dua not found")
    return dua

@router.get("/stop")
async def stop_dua():
    return {"status": "stopped"}
