import uuid
from sqlalchemy import Column, Integer, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from datetime import datetime
from ..database import Base

class Rating(Base):
    __tablename__ = "ratings"
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(PGUUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
