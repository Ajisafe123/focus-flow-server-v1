import uuid
from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from datetime import datetime
from ..database import Base

class File(Base):
    __tablename__ = "files"
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(PGUUID(as_uuid=True), ForeignKey("messages.id"), nullable=True)
    file_name = Column(String(255))
    file_type = Column(String(50))
    file_size = Column(BigInteger)
    file_url = Column(String)
    uploaded_at = Column(TIMESTAMP, default=datetime.utcnow)
