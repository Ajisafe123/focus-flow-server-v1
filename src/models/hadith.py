from sqlalchemy import Column, Integer, String, Text, JSON
from ..database import Base

class Hadith(Base):
    __tablename__ = "hadiths"

    id = Column(Integer, primary_key=True, index=True)
    id_in_book = Column(Integer, nullable=True)
    chapter_id = Column(Integer, nullable=True)
    book_id = Column(Integer, nullable=True)
    arabic = Column(Text, nullable=False)
    english = Column(JSON, nullable=False)
    category = Column(String, nullable=True)
    source = Column(String, nullable=True)
