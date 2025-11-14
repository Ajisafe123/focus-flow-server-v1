import uuid
from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class Message(Base):
    __tablename__ = "messages"
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(PGUUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    sender_type = Column(String(10), nullable=False)
    sender_id = Column(PGUUID(as_uuid=True), nullable=True)
    message_text = Column(Text)
    message_type = Column(String(20), default="text")
    file_url = Column(String)
    status = Column(String(20), default="sent")
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    conversation = relationship("Conversation", backref="messages")
