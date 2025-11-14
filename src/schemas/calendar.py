from pydantic import BaseModel
from typing import List

class CalendarDate(BaseModel):
    gregorian: str
    hijri: str

class CalendarMonthResponse(BaseModel):
    month: int
    year: int
    days: List[CalendarDate]
