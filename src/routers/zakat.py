from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.zakat import ZakatCreate, ZakatOut
from src.utils.zakat import (
    create_zakat_record,
    get_user_zakat_records,
    get_zakat_by_id,
    delete_zakat_record,
)
from src.database import get_db
from src.utils.users import get_current_user

from src.models.zakat import ZakatRecord


router = APIRouter(prefix="/zakat", tags=["Zakat"])

@router.post("/", response_model=ZakatOut, status_code=status.HTTP_201_CREATED)
async def create_zakat(
    data: ZakatCreate,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    zakat = await create_zakat_record(db, user_id=user.id, data=data)
    return zakat

@router.get("/", response_model=list[ZakatOut])
async def list_zakat_records(
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    return await get_user_zakat_records(db, user_id=user.id)

@router.post("/calculate", response_model=dict, status_code=status.HTTP_200_OK)
async def calculate_and_save_zakat(
    data: ZakatCreate,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    zakat_amount = round(float(data.assets_total) * 0.025, 2)
    zakat = ZakatRecord(
        user_id=user.id,
        name=data.name,
        assets_total=data.assets_total,
        savings=data.savings,
        gold_price_per_gram=data.gold_price_per_gram,
        note=data.note,
        type=data.type,
        zakat_amount=zakat_amount
    )
    db.add(zakat)
    await db.commit()
    await db.refresh(zakat)
    return {"zakat_due": zakat_amount, "type": data.type}
@router.get("/history", response_model=list[ZakatOut])
async def zakat_history(
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    return await get_user_zakat_records(db, user_id=user.id)
@router.get("/{record_id}", response_model=ZakatOut)
async def get_single_zakat(
    record_id: int,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    zakat = await get_zakat_by_id(db, record_id=record_id, user_id=user.id)
    if not zakat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zakat record not found")
    return zakat
@router.delete("/{record_id}")
async def delete_zakat(
    record_id: int,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    deleted = await delete_zakat_record(db, record_id, user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zakat record not found")
    return {"message": "Zakat record deleted successfully"}