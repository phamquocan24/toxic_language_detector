# # db/models/role.py
# from sqlalchemy import Column, Integer, String
# from sqlalchemy.orm import relationship
# from backend.db.models.base import Base

# class Role(Base):
#     __tablename__ = "roles"
    
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, unique=True, index=True)
#     description = Column(String)
    
#     # Relationships
#     users = relationship("User", back_populates="role")
# db/models/role.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from backend.db.models.base import Base, TimestampMixin
from datetime import datetime

class Role(Base, TimestampMixin):
    """
    Model định nghĩa vai trò người dùng và phân quyền
    """
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255))
    is_system_role = Column(Boolean, default=False)  # Đánh dấu vai trò hệ thống không được xóa
    is_default = Column(Boolean, default=False)  # Đánh dấu vai trò mặc định cho người dùng mới
    
    # Relationships
    users = relationship("User", back_populates="role")
    permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")
    
    @staticmethod
    def get_role_by_name(db, name):
        """
        Lấy vai trò theo tên
        
        Args:
            db: Database session
            name: Tên vai trò
            
        Returns:
            Role: Vai trò
        """
        return db.query(Role).filter(Role.name == name).first()
    
    @staticmethod
    def get_default_role(db):
        """
        Lấy vai trò mặc định
        
        Args:
            db: Database session
            
        Returns:
            Role: Vai trò mặc định
        """
        default_role = db.query(Role).filter(Role.is_default == True).first()
        if not default_role:
            # Nếu không có vai trò mặc định, lấy vai trò "user"
            default_role = db.query(Role).filter(Role.name == "user").first()
        return default_role
    
    def has_permission(self, db, permission_code):
        """
        Kiểm tra vai trò có quyền cụ thể không
        
        Args:
            db: Database session
            permission_code: Mã quyền
            
        Returns:
            bool: True nếu có quyền, False nếu không
        """
        from backend.db.models.permission import Permission, RolePermission
        
        permission = db.query(Permission).filter(Permission.code == permission_code).first()
        if not permission:
            return False
            
        role_permission = db.query(RolePermission).filter(
            RolePermission.role_id == self.id,
            RolePermission.permission_id == permission.id
        ).first()
        
        return role_permission is not None
    
    def get_permissions(self, db):
        """
        Lấy danh sách các quyền của vai trò
        
        Args:
            db: Database session
            
        Returns:
            list: Danh sách các quyền
        """
        from backend.db.models.permission import Permission, RolePermission
        
        permissions = db.query(Permission).join(
            RolePermission, RolePermission.permission_id == Permission.id
        ).filter(
            RolePermission.role_id == self.id
        ).all()
        
        return permissions
    
    def add_permission(self, db, permission_code):
        """
        Thêm quyền cho vai trò
        
        Args:
            db: Database session
            permission_code: Mã quyền
            
        Returns:
            bool: True nếu thành công, False nếu không
        """
        from backend.db.models.permission import Permission, RolePermission
        
        permission = db.query(Permission).filter(Permission.code == permission_code).first()
        if not permission:
            return False
            
        # Kiểm tra nếu đã có quyền
        existing = db.query(RolePermission).filter(
            RolePermission.role_id == self.id,
            RolePermission.permission_id == permission.id
        ).first()
        
        if existing:
            return True  # Đã có quyền
            
        # Thêm quyền mới
        role_permission = RolePermission(
            role_id=self.id,
            permission_id=permission.id
        )
        db.add(role_permission)
        db.commit()
        
        return True
    
    def remove_permission(self, db, permission_code):
        """
        Xóa quyền khỏi vai trò
        
        Args:
            db: Database session
            permission_code: Mã quyền
            
        Returns:
            bool: True nếu thành công, False nếu không
        """
        from backend.db.models.permission import Permission, RolePermission
        
        permission = db.query(Permission).filter(Permission.code == permission_code).first()
        if not permission:
            return False
            
        # Tìm và xóa quyền
        role_permission = db.query(RolePermission).filter(
            RolePermission.role_id == self.id,
            RolePermission.permission_id == permission.id
        ).first()
        
        if role_permission:
            db.delete(role_permission)
            db.commit()
            
        return True