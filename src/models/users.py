from sqlalchemy import Boolean, Column, String, DateTime, Float, ForeignKey, TIMESTAMP, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta
import uuid
from sqlalchemy.dialects.postgresql import UUID
from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    avatar_url = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    status = Column(String, default="active")
    role = Column(String, default="user")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    reset_sent_at = Column(DateTime, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    city = Column(String, nullable=True)
    region = Column(String, nullable=True)
    country = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    location_accuracy = Column(String, nullable=True)

    reset_codes = relationship("PasswordResetCode", back_populates="user", cascade="all, delete-orphan")
    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")
    favorites = relationship("DuaFavorite", back_populates="user", cascade="all, delete-orphan")
    views = relationship("DuaView", back_populates="user", cascade="all, delete-orphan")

    def has_favorited(self, dua_id: int) -> bool:
        return any(fav.dua_id == dua_id for fav in self.favorites)

    def has_viewed(self, dua_id: int) -> bool:
        return any(view.dua_id == dua_id for view in self.views)


class Bookmark(Base):
    __tablename__ = "bookmarks"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    ayah_key = Column(String, index=True)

    user = relationship("User", back_populates="bookmarks")


class PasswordResetCode(Base):
    __tablename__ = "password_reset_codes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    code = Column(String(6), index=True)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(minutes=10))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="reset_codes")


class ChatUser(Base):
    __tablename__ = "chat_users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    avatar_letter = Column(String(1))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    last_seen = Column(TIMESTAMP)
    is_online = Column(Boolean, default=False)
