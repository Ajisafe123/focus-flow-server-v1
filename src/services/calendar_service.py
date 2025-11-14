from datetime import date
import calendar
from hijri_converter import Gregorian, Hijri
from src.schemas.calendar import CalendarDate

def get_today_date() -> CalendarDate:
    today = date.today()
    hijri = Gregorian(today.year, today.month, today.day).to_hijri()
    return CalendarDate(
        gregorian=today.strftime("%d %B %Y"),
        hijri=f"{hijri.day} {hijri.month_name()} {hijri.year} H"
    )

def get_month_dates(month: int, year: int):
    num_days = calendar.monthrange(year, month)[1]
    days = []

    for day in range(1, num_days + 1):
        g_date = date(year, month, day)
        hijri = Gregorian(g_date.year, g_date.month, g_date.day).to_hijri()
        days.append({
            "gregorian": g_date.strftime("%Y-%m-%d"),
            "hijri": f"{hijri.day} {hijri.month_name()} {hijri.year} H"
        })

    return {"days": days}
