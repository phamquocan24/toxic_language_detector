# # db/models/log.py
# from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
# from sqlalchemy.orm import relationship
# from sqlalchemy.sql import func
# from backend.db.models.base import Base

# class Log(Base):
#     __tablename__ = "logs"
    
#     id = Column(Integer, primary_key=True, index=True)
#     request_path = Column(String)
#     request_method = Column(String)
#     request_body = Column(Text, nullable=True)
#     response_status = Column(Integer)
#     response_body = Column(Text, nullable=True)
#     client_ip = Column(String)
#     user_agent = Column(String)
#     timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
#     # If request was authenticated, store user info
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
#     # Additional log_metadata
#     log_metadata = Column(JSON, nullable=True)
# db/models/log.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.db.models.base import Base
from datetime import datetime

class Log(Base):
    """
    Model lưu trữ các log hệ thống và hoạt động người dùng
    """
    __tablename__ = "logs"
    
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(255), nullable=True, index=True)  # Mô tả hành động (login, analyze, export, etc.)
    request_path = Column(String(255), nullable=True, index=True)
    request_method = Column(String(20), nullable=True)
    request_query = Column(String(512), nullable=True)
    request_body = Column(Text, nullable=True)
    response_status = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    client_ip = Column(String(45), nullable=True)  # Hỗ trợ cả IPv6
    user_agent = Column(String(512), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Nếu request được xác thực, lưu thông tin người dùng
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    user = relationship("User", back_populates="logs")
    
    # Trường để phân loại log
    log_type = Column(String(50), nullable=True, index=True)  # 'system', 'security', 'user_activity', 'api', etc.
    log_level = Column(String(20), nullable=True, index=True)  # 'info', 'warning', 'error', 'critical'
    
    # Trạng thái và xử lý log
    is_error = Column(Boolean, default=False, index=True)  # Đánh dấu log lỗi
    is_sensitive = Column(Boolean, default=False)  # Đánh dấu log chứa thông tin nhạy cảm
    is_reviewed = Column(Boolean, default=False)  # Đánh dấu log đã được xem xét
    
    # Thông tin bổ sung
    metadata = Column(JSON, nullable=True)
    
    # Tạo indexes để tối ưu hóa truy vấn
    __table_args__ = (
        Index('idx_log_timestamp_type', 'timestamp', 'log_type'),
        Index('idx_log_user_action', 'user_id', 'action'),
        Index('idx_log_error_timestamp', 'is_error', 'timestamp'),
    )
    
    @classmethod
    def create_system_log(cls, db, message, level="info", metadata=None):
        """
        Tạo log hệ thống
        
        Args:
            db: Database session
            message: Nội dung log
            level: Mức độ log ('info', 'warning', 'error', 'critical')
            metadata: Thông tin bổ sung
        
        Returns:
            Log: Log đã tạo
        """
        log = cls(
            action=message,
            log_type="system",
            log_level=level,
            is_error=level in ["error", "critical"],
            timestamp=datetime.utcnow(),
            metadata=metadata
        )
        db.add(log)
        db.commit()
        return log
    
    @classmethod
    def create_security_log(cls, db, action, user_id=None, client_ip=None, is_error=False, metadata=None):
        """
        Tạo log bảo mật
        
        Args:
            db: Database session
            action: Hành động ('login', 'logout', 'failed_login', etc.)
            user_id: ID người dùng (nếu có)
            client_ip: Địa chỉ IP
            is_error: Đánh dấu log lỗi
            metadata: Thông tin bổ sung
        
        Returns:
            Log: Log đã tạo
        """
        log = cls(
            action=action,
            user_id=user_id,
            client_ip=client_ip,
            log_type="security",
            log_level="error" if is_error else "info",
            is_error=is_error,
            is_sensitive=True,
            timestamp=datetime.utcnow(),
            metadata=metadata
        )
        db.add(log)
        db.commit()
        return log
    
    @classmethod
    def create_user_activity_log(cls, db, user_id, action, metadata=None):
        """
        Tạo log hoạt động người dùng
        
        Args:
            db: Database session
            user_id: ID người dùng
            action: Hành động
            metadata: Thông tin bổ sung
        
        Returns:
            Log: Log đã tạo
        """
        log = cls(
            action=action,
            user_id=user_id,
            log_type="user_activity",
            log_level="info",
            timestamp=datetime.utcnow(),
            metadata=metadata
        )
        db.add(log)
        db.commit()
        return log
    
    @classmethod
    def get_recent_logs(cls, db, limit=100, log_type=None, user_id=None, is_error=None):
        """
        Lấy logs gần đây
        
        Args:
            db: Database session
            limit: Số lượng logs tối đa
            log_type: Loại log
            user_id: ID người dùng
            is_error: Lọc theo lỗi
            
        Returns:
            list: Danh sách logs
        """
        query = db.query(cls).order_by(cls.timestamp.desc())
        
        if log_type:
            query = query.filter(cls.log_type == log_type)
        
        if user_id:
            query = query.filter(cls.user_id == user_id)
            
        if is_error is not None:
            query = query.filter(cls.is_error == is_error)
            
        return query.limit(limit).all()
    
    @classmethod
    def count_logs_by_type(cls, db):
        """
        Đếm số lượng logs theo loại
        
        Args:
            db: Database session
            
        Returns:
            dict: Số lượng logs theo loại
        """
        from sqlalchemy import func
        counts = db.query(
            cls.log_type,
            func.count(cls.id).label('count')
        ).group_by(cls.log_type).all()
        
        return {log_type: count for log_type, count in counts}
    
    @classmethod
    def clean_old_logs(cls, db, days=30, exclude_types=None):
        """
        Xóa logs cũ
        
        Args:
            db: Database session
            days: Số ngày giữ lại
            exclude_types: Loại logs không xóa
            
        Returns:
            int: Số lượng logs đã xóa
        """
        from datetime import datetime, timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        query = db.query(cls).filter(cls.timestamp < cutoff_date)
        
        if exclude_types:
            query = query.filter(cls.log_type.notin_(exclude_types))
            
        count = query.count()
        query.delete(synchronize_session=False)
        db.commit()
        
        return count