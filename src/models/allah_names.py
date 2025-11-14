from sqlalchemy import Column, Integer, String
from ..database import Base

class AllahName(Base):
    __tablename__ = "allah_names"

    id = Column(Integer, primary_key=True, index=True)
    arabic = Column(String)
    transliteration = Column(String)
    meaning = Column(String)