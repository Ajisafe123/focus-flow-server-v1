from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from src.models.zakat import ZakatRecord
from src.services.zakat_service import calculate_zakat_amount

async def create_zakat_record(db: AsyncSession, user_id: int, data):
    zakat_amount, nisab = calculate_zakat_amount(
        data.assets_total,
        data.savings,
        data.gold_price_per_gram,
    )
    record = ZakatRecord(
        user_id=user_id,
        name=data.name,
        assets_total=data.assets_total,
        savings=data.savings,
        gold_price_per_gram=data.gold_price_per_gram,
        nisab=nisab,
        zakat_amount=zakat_amount,
        note=data.note,
        type=data.type,
        zakat_due=data.zakat_due
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record

async def get_user_zakat_records(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(ZakatRecord)
        .filter(ZakatRecord.user_id == user_id)
        .order_by(desc(ZakatRecord.created_at))
    )
    return result.scalars().all()

async def get_zakat_by_id(db: AsyncSession, record_id: int, user_id: int):
    result = await db.execute(
        select(ZakatRecord).filter(
            ZakatRecord.id == record_id,
            ZakatRecord.user_id == user_id
        )
    )
    return result.scalars().first()

async def delete_zakat_record(db: AsyncSession, record_id: int, user_id: int):
    record = await get_zakat_by_id(db, record_id, user_id)
    if not record:
        return None
    await db.delete(record)
    await db.commit()
    return record
