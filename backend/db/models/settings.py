# backend/db/models/settings.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.db.models.base import Base, TimestampMixin
from datetime import datetime

class UserSettings(Base, TimestampMixin):
    """
    Model lưu trữ cài đặt người dùng
    """
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    
    # Cài đặt giao diện
    theme = Column(String(50), default="light")  # light, dark, system
    language = Column(String(10), default="vi")  # vi, en
    
    # Cài đặt thông báo
    notifications_enabled = Column(Boolean, default=True)
    email_notifications = Column(Boolean, default=True)
    
    # Cài đặt khác dưới dạng JSON
    meta_data = Column(JSON, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="settings")
    
    @staticmethod
    def get_user_settings(db, user_id):
        """
        Lấy cài đặt của người dùng, tạo mới nếu chưa có
        
        Args:
            db: Database session
            user_id: ID của người dùng
            
        Returns:
            UserSettings: Cài đặt người dùng
        """
        settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
        
        if not settings:
            # Tạo cài đặt mặc định
            settings = UserSettings(
                user_id=user_id,
                theme="light",
                language="vi",
                notifications_enabled=True,
                meta_data={}
            )
            db.add(settings)
            db.commit()
            db.refresh(settings)
            
        return settings
    
    def __repr__(self):
        return f"UserSettings(user_id={self.user_id})"