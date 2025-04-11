# backend/db/models/refresh_token.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.db.models.base import Base
from datetime import datetime, timedelta
import secrets

class RefreshToken(Base):
    """
    Model lưu trữ refresh token để làm mới access token
    """
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Thông tin bổ sung
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="refresh_tokens")
    
    @staticmethod
    def generate_token(db, user_id, expires_days=30, user_agent=None, ip_address=None):
        """
        Tạo refresh token mới
        
        Args:
            db: Database session
            user_id: ID của người dùng
            expires_days: Số ngày token có hiệu lực
            user_agent: User agent của client
            ip_address: Địa chỉ IP của client
            
        Returns:
            str: Token mới
        """
        # Tạo token ngẫu nhiên
        token = secrets.token_hex(32)
        
        # Tính thời gian hết hạn
        expires_at = datetime.utcnow() + timedelta(days=expires_days)
        
        # Tạo record mới
        refresh_token = RefreshToken(
            token=token,
            user_id=user_id,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address
        )
        
        db.add(refresh_token)
        db.commit()
        
        return token
    
    @staticmethod
    def validate_token(db, token):
        """
        Kiểm tra token có hợp lệ không
        
        Args:
            db: Database session
            token: Token cần kiểm tra
            
        Returns:
            RefreshToken or None: Token nếu hợp lệ, None nếu không
        """
        refresh_token = db.query(RefreshToken).filter(
            RefreshToken.token == token,
            RefreshToken.expires_at > datetime.utcnow(),
            RefreshToken.revoked == False
        ).first()
        
        return refresh_token
    
    @staticmethod
    def revoke_token(db, token):
        """
        Thu hồi token
        
        Args:
            db: Database session
            token: Token cần thu hồi
            
        Returns:
            bool: True nếu thành công, False nếu không
        """
        refresh_token = db.query(RefreshToken).filter(
            RefreshToken.token == token
        ).first()
        
        if refresh_token:
            refresh_token.revoked = True
            db.commit()
            return True
            
        return False
    
    def __repr__(self):
        return f"RefreshToken(id={self.id}, user_id={self.user_id})"