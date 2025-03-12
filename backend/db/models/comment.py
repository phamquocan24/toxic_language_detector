# Import các thư viện cần thiết, bỏ pgvector
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.db.base import Base

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    source_platform = Column(String, nullable=False)
    platform_comment_id = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    # Thay thế pgvector bằng text để lưu trữ vector dưới dạng JSON string
    content_vector_json = Column(Text, nullable=True)
    
    # Các trường khác giữ nguyên
    is_checked = Column(Boolean, default=False)
    classification_result = Column(Integer)
    clean_score = Column(Float)
    offensive_score = Column(Float)
    hate_score = Column(Float)
    spam_score = Column(Float)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    checked_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="comments")

    # UniqueConstraint giữ nguyên
    __table_args__ = (
        UniqueConstraint('source_platform', 'platform_comment_id', name='uix_platform_comment'),
    )