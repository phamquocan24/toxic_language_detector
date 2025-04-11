# backend/db/models/report.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from backend.db.models.base import Base, TimestampMixin
from datetime import datetime

class Report(Base, TimestampMixin):
    """
    Model lưu trữ báo cáo phát hiện ngôn từ tiêu cực
    """
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(50), default="pending")  # pending, processing, completed, rejected
    report_type = Column(String(50), default="toxic_detection")
    
    # Dữ liệu tổng hợp, lưu dưới dạng JSON
    report_data = Column(JSON, nullable=True)
    
    # Thông tin bổ sung
    is_public = Column(Boolean, default=False)
    exported_formats = Column(String(255), nullable=True)  # csv,pdf,xlsx
    
    # Relationships
    user = relationship("User", back_populates="reports")
    
    @staticmethod
    def get_user_reports(db, user_id, limit=10, offset=0):
        """
        Lấy danh sách báo cáo của người dùng
        
        Args:
            db: Database session
            user_id: ID của người dùng
            limit: Số lượng báo cáo tối đa
            offset: Vị trí bắt đầu
            
        Returns:
            list: Danh sách báo cáo
        """
        return db.query(Report).filter(
            Report.user_id == user_id
        ).order_by(
            Report.created_at.desc()
        ).offset(offset).limit(limit).all()
    
    @staticmethod
    def get_public_reports(db, limit=10, offset=0):
        """
        Lấy danh sách báo cáo công khai
        
        Args:
            db: Database session
            limit: Số lượng báo cáo tối đa
            offset: Vị trí bắt đầu
            
        Returns:
            list: Danh sách báo cáo
        """
        return db.query(Report).filter(
            Report.is_public == True
        ).order_by(
            Report.created_at.desc()
        ).offset(offset).limit(limit).all()
    
    def __repr__(self):
        return f"Report(id={self.id}, title={self.title})"