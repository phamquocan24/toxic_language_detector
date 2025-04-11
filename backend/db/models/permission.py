# backend/db/models/permission.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.db.models.base import Base, TimestampMixin
from datetime import datetime

class Permission(Base, TimestampMixin):
    """
    Model định nghĩa quyền hạn trong hệ thống
    """
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), index=True, nullable=False)
    description = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    roles = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")
    
    @staticmethod
    def get_permission_by_code(db, code):
        """
        Lấy quyền theo mã code
        
        Args:
            db: Database session
            code: Mã code của quyền
            
        Returns:
            Permission: Quyền tìm thấy hoặc None
        """
        return db.query(Permission).filter(Permission.code == code).first()
    
    @staticmethod
    def get_all_active_permissions(db):
        """
        Lấy tất cả quyền đang hoạt động
        
        Args:
            db: Database session
            
        Returns:
            list: Danh sách các quyền đang hoạt động
        """
        return db.query(Permission).filter(Permission.is_active == True).all()
    
    def __repr__(self):
        return f"Permission(id={self.id}, code={self.code}, name={self.name})"


class RolePermission(Base):
    """
    Model quan hệ nhiều-nhiều giữa Role và Permission
    """
    __tablename__ = "role_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), index=True)
    permission_id = Column(Integer, ForeignKey("permissions.id", ondelete="CASCADE"), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission", back_populates="roles")
    
    def __repr__(self):
        return f"RolePermission(role_id={self.role_id}, permission_id={self.permission_id})"