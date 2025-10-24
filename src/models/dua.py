from sqlalchemy import Column, Integer, String, Text, JSON, Boolean
from ..database import Base

class Dua(Base):
    __tablename__ = "duas"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    arabic = Column(Text, nullable=False)
    transliteration = Column(Text, nullable=True)  # will store "latin"
    translation = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    benefits = Column(Text, nullable=True)
    source = Column(Text, nullable=True)
    category = Column(String(100), nullable=False)  # name of JSON file or category
    audio_map = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
