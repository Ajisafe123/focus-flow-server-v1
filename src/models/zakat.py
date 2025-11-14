from sqlalchemy import Column, Integer, Float, String, DateTime, Text
from datetime import datetime
from src.database import Base

class ZakatRecord(Base):
    __tablename__ = "zakat_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    name = Column(String, nullable=True)
    assets_total = Column(Float, nullable=False)
    savings = Column(Float, nullable=False, default=0)
    gold_price_per_gram = Column(Float, nullable=True)
    nisab = Column(Float, nullable=True)
    zakat_amount = Column(Float, nullable=False, default=0)  # store calculated Zakat
    type = Column(String, nullable=False, default="cash")    # add type column
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
