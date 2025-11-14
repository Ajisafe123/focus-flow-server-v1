import uuid
from sqlalchemy import Column, String, Boolean, TIMESTAMP, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from datetime import datetime
from ..database import Base

class AdminUser(Base):
    __tablename__ = "admin_users"
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    is_online = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

class AdminNote(Base):
    __tablename__ = "admin_notes"
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(PGUUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    admin_id = Column(PGUUID(as_uuid=True), ForeignKey("admin_users.id"), nullable=False)
    note_text = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow)
