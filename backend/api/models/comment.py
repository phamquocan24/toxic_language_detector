import sys
print("Python version:", sys.version)
print("SQLAlchemy version:", __import__('sqlalchemy').__version__)
print("Available SQLAlchemy imports:", dir(__import__('sqlalchemy')))

from sqlalchemy import (
    Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Float, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.db.base import Base

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    source_platform = Column(String, nullable=False)  # facebook, twitter, youtube
    platform_comment_id = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    content_vector_json = Column(Text, nullable=True)  # Vector representation for similarity search
    
    # Prediction results
    is_checked = Column(Boolean, default=False)
    classification_result = Column(Integer)  # 0-clean, 1-offensive, 2-hate, 3-spam
    clean_score = Column(Float)
    offensive_score = Column(Float)
    hate_score = Column(Float)
    spam_score = Column(Float)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    checked_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="comments")

    # Add unique index to prevent duplicate platform + comment_id entries
    __table_args__ = (
        Index('uix_platform_comment', 'source_platform', 'platform_comment_id', unique=True),
    )