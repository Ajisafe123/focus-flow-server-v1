from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from ..schemas.allah_names import AllahNameSchema
from ..utils.allah_names import get_all_names, get_name_by_id, get_random_name, search_names
from ..database import get_db

router = APIRouter(prefix="/names", tags=["99 Names of Allah"])

@router.get("/", response_model=List[AllahNameSchema])
async def get_names(db: AsyncIOMotorDatabase = Depends(get_db)):
    names_list = await get_all_names(db)
    return [AllahNameSchema(**name) for name in names_list]

@router.get("/{name_id}", response_model=AllahNameSchema)
async def get_specific_name(name_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    name = await get_name_by_id(db, name_id)
    if not name:
        raise HTTPException(status_code=404, detail="Name not found")
    return AllahNameSchema(**name)

@router.get("/random/", response_model=AllahNameSchema)
async def get_random(db: AsyncIOMotorDatabase = Depends(get_db)):
    name = await get_random_name(db)
    if not name:
        raise HTTPException(status_code=404, detail="No names found")
    return AllahNameSchema(**name)

@router.get("/search/", response_model=List[AllahNameSchema])
async def search_allah_names(q: str = Query(..., min_length=1), db: AsyncIOMotorDatabase = Depends(get_db)):
    results = await search_names(db, q)
    if not results:
        raise HTTPException(status_code=404, detail="No matching names found")
    return [AllahNameSchema(**name) for name in results]