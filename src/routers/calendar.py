from fastapi import APIRouter
from typing import Optional
from src.services import calendar_service

router = APIRouter(prefix="/calendar", tags=["calendar"])

@router.get("/today")
async def get_today():
    return calendar_service.get_today_date()

@router.get("/month")
async def get_month(month: Optional[int] = None, year: Optional[int] = None):
    from datetime import date
    today = date.today()
    month = month or today.month
    year = year or today.year
    return calendar_service.get_month_dates(month, year)

# Frontend expects /api/day, so expose a lightweight alias.
@router.get("/api/day")
async def get_day_alias():
    return calendar_service.get_today_date()
