from pydantic import BaseModel, field_validator
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Optional, Union


class ZakatCreate(BaseModel):
    name: Optional[str] = None
    assets_total: Union[Decimal, float, int, str]
    savings: Optional[Union[Decimal, float, int, str]] = 0
    gold_price_per_gram: Optional[Union[Decimal, float, int, str]] = None
    note: Optional[str] = None
    type: str
    zakat_due: Optional[float] = None

    @field_validator("assets_total", "savings", "gold_price_per_gram", mode="before")
    def convert_str_to_decimal(cls, v):
        if v is None or v == "":
            return Decimal(0)
        if isinstance(v, (int, float, Decimal)):
            return Decimal(str(v))
        if isinstance(v, str):
            try:
                return Decimal(v)
            except InvalidOperation:
                raise ValueError("Invalid number format")
        raise ValueError("Invalid input type")


class ZakatOut(BaseModel):
    id: int
    user_id: int
    name: Optional[str]
    assets_total: float
    savings: float
    gold_price_per_gram: Optional[float]
    nisab: Optional[float]
    zakat_amount: float
    created_at: datetime
    note: Optional[str]

    class Config:
        from_attribute = True
