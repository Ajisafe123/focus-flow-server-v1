from sqlalchemy import Boolean, Column, Integer, String, Text, ForeignKey, DateTime, UniqueConstraint, JSON
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from ..database import Base

class DuaCategory(Base):
    __tablename__ = "dua_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    image_url = Column(String(512), nullable=True)
    is_active = Column(Boolean, default=True)

    duas = relationship(
        "Dua",
        back_populates="category_rel",
        cascade="all, delete-orphan",
    )

class Dua(Base):
    __tablename__ = "duas"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    arabic = Column(Text, nullable=False)
    transliteration = Column(Text, nullable=True)
    translation = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    benefits = Column(Text, nullable=True)
    source = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("dua_categories.id", ondelete="SET NULL"), nullable=True)
    audio_path = Column(String(512), nullable=True)
    is_active = Column(Boolean, default=True)
    featured = Column(Boolean, default=False)
    
    arabic_segments_json = Column(JSON, nullable=True)
    transliteration_segments_json = Column(JSON, nullable=True)
    translation_segments_json = Column(JSON, nullable=True)

    view_count = Column(Integer, default=0)
    favorite_count = Column(Integer, default=0)

    category_rel = relationship(
        "DuaCategory",
        back_populates="duas",
        lazy="selectin"
    )
    views = relationship(
        "DuaView",
        back_populates="dua",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    favorites = relationship(
        "DuaFavorite",
        back_populates="dua",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def get_view_count(self, db: Session) -> int:
        return db.query(func.count(DuaView.id)).filter(DuaView.dua_id == self.id).scalar()

    def get_favorite_count(self, db: Session) -> int:
        return db.query(func.count(DuaFavorite.id)).filter(DuaFavorite.dua_id == self.id).scalar()

    def is_favorited_by(self, db: Session, user_id) -> bool:
        return db.query(DuaFavorite).filter(
            DuaFavorite.dua_id == self.id,
            DuaFavorite.user_id == user_id
        ).first() is not None

class DuaView(Base):
    __tablename__ = "dua_views"

    id = Column(Integer, primary_key=True)
    dua_id = Column(Integer, ForeignKey("duas.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    dua = relationship(
        "Dua",
        back_populates="views",
        lazy="selectin"
    )
    user = relationship(
        "User", 
        back_populates="views", 
        lazy="selectin"
    )

class DuaFavorite(Base):
    __tablename__ = "dua_favorites"
    __table_args__ = (
        UniqueConstraint('dua_id', 'user_id', name='uq_dua_user'),
    )

    id = Column(Integer, primary_key=True)
    dua_id = Column(Integer, ForeignKey("duas.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    dua = relationship(
        "Dua",
        back_populates="favorites",
        lazy="selectin"
    )
    user = relationship(
        "User", 
        back_populates="favorites", 
        lazy="selectin"
    )

class DuaShareLink(Base):
    __tablename__ = "dua_share_links"

    id = Column(Integer, primary_key=True, index=True)
    short_code = Column(String(32), unique=True, index=True, nullable=False) 
    dua_id = Column(Integer, ForeignKey("duas.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    dua_rel = relationship(
        "Dua",
        backref="share_links",
        lazy="selectin"
    )

    __table_args__ = (
        UniqueConstraint('short_code', name='uq_share_short_code'),
    )