from sqlalchemy import Boolean, Column, Integer, String, Text, ForeignKey, DateTime, UniqueConstraint, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from ..database import Base

class HadithCategory(Base):
    __tablename__ = "hadith_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

    hadiths = relationship(
        "Hadith",
        back_populates="category_rel",
        cascade="all, delete-orphan",
    )

class Hadith(Base):
    __tablename__ = "hadiths"

    id = Column(Integer, primary_key=True, index=True)
    arabic = Column(Text, nullable=False)
    translation = Column(Text, nullable=True)
    narrator = Column(String(255), nullable=True)
    book = Column(String(255), nullable=True)
    number = Column(String(50), nullable=True)
    status = Column(String(50), nullable=True)
    rating = Column(Float, default=0.0)
    
    category_id = Column(Integer, ForeignKey("hadith_categories.id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, default=True)
    featured = Column(Boolean, default=False)

    view_count = Column(Integer, default=0)
    favorite_count = Column(Integer, default=0)

    category_rel = relationship(
        "HadithCategory",
        back_populates="hadiths",
        lazy="selectin"
    )
    views = relationship(
        "HadithView",
        back_populates="hadith",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    favorites = relationship(
        "HadithFavorite",
        back_populates="hadith",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

class HadithView(Base):
    __tablename__ = "hadith_views"

    id = Column(Integer, primary_key=True)
    hadith_id = Column(Integer, ForeignKey("hadiths.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    hadith = relationship(
        "Hadith",
        back_populates="views",
        lazy="selectin"
    )

class HadithFavorite(Base):
    __tablename__ = "hadith_favorites"
    __table_args__ = (
        UniqueConstraint('hadith_id', 'user_id', name='uq_hadith_user'),
    )

    id = Column(Integer, primary_key=True)
    hadith_id = Column(Integer, ForeignKey("hadiths.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    hadith = relationship(
        "Hadith",
        back_populates="favorites",
        lazy="selectin"
    )