# # db/models/user.py
# from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
# from sqlalchemy.orm import relationship
# from sqlalchemy.sql import func
# from backend.db.models.base import Base

# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True, index=True)
#     username = Column(String, unique=True, index=True)
#     email = Column(String, unique=True, index=True)
#     hashed_password = Column(String)
#     is_active = Column(Boolean, default=True)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
    
#     # Relationships
#     role_id = Column(Integer, ForeignKey("roles.id"))
#     role = relationship("Role", back_populates="users")
#     comments = relationship("Comment", back_populates="user")
# db/models/user.py
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.db.models.base import Base, TimestampMixin
from datetime import datetime
import json

class User(Base, TimestampMixin):
    """
    Model lưu trữ thông tin người dùng
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=True)  # Tên hiển thị
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False, index=True)  # Email đã xác thực chưa
    
    # Trường cho quản lý phiên
    last_login = Column(DateTime(timezone=True), nullable=True)
    last_activity = Column(DateTime(timezone=True), nullable=True)
    last_login_ip = Column(String(45), nullable=True)  # Hỗ trợ cả IPv6
    
    # Trường cho đặt lại mật khẩu
    reset_token = Column(String(255), nullable=True, unique=True)
    reset_token_expires = Column(DateTime(timezone=True), nullable=True)
    
    # Trường cho xác thực email
    verification_token = Column(String(255), nullable=True, unique=True)
    verification_token_expires = Column(DateTime(timezone=True), nullable=True)
    
    # Cài đặt người dùng
    extension_settings = Column(JSON, nullable=True)  # Cài đặt extension
    ui_settings = Column(JSON, nullable=True)  # Cài đặt giao diện người dùng
    notification_settings = Column(JSON, nullable=True)  # Cài đặt thông báo
    
    # Thông tin cá nhân bổ sung
    avatar_url = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)  # Giới thiệu ngắn
    
    # Relationships
    role_id = Column(Integer, ForeignKey("roles.id"))
    role = relationship("Role", back_populates="users")
    comments = relationship("Comment", back_populates="user")
    logs = relationship("Log", back_populates="user")
    
    def is_admin(self):
        """
        Kiểm tra người dùng có phải admin không
        
        Returns:
            bool: True nếu là admin, False nếu không
        """
        return self.role and self.role.name == "admin"
    
    def has_permission(self, db, permission_code):
        """
        Kiểm tra người dùng có quyền cụ thể không
        
        Args:
            db: Database session
            permission_code: Mã quyền
            
        Returns:
            bool: True nếu có quyền, False nếu không
        """
        # Admin luôn có tất cả quyền
        if self.is_admin():
            return True
            
        # Kiểm tra quyền theo vai trò
        if self.role:
            return self.role.has_permission(db, permission_code)
            
        return False
    
    def get_permissions(self, db):
        """
        Lấy danh sách quyền của người dùng
        
        Args:
            db: Database session
            
        Returns:
            list: Danh sách quyền
        """
        if not self.role:
            return []
            
        return self.role.get_permissions(db)
    
    def get_extension_settings(self):
        """
        Lấy cài đặt extension
        
        Returns:
            dict: Cài đặt extension
        """
        from backend.config.settings import settings
        
        # Nếu không có cài đặt, trả về mặc định
        if not self.extension_settings:
            return settings.EXTENSION_DEFAULT_SETTINGS
            
        try:
            # Nếu đã lưu dưới dạng string
            if isinstance(self.extension_settings, str):
                return json.loads(self.extension_settings)
            return self.extension_settings
        except:
            return settings.EXTENSION_DEFAULT_SETTINGS
    
    def set_extension_settings(self, settings_dict):
        """
        Cập nhật cài đặt extension
        
        Args:
            settings_dict: Cài đặt mới
        """
        if isinstance(settings_dict, dict):
            self.extension_settings = settings_dict
        else:
            self.extension_settings = json.loads(settings_dict)
    
    def generate_password_reset_token(self):
        """
        Tạo token để đặt lại mật khẩu
        
        Returns:
            str: Token đặt lại mật khẩu
        """
        from backend.core.security import generate_reset_token
        from datetime import datetime, timedelta
        
        # Tạo token mới
        token = generate_reset_token()
        self.reset_token = token
        self.reset_token_expires = datetime.utcnow() + timedelta(hours=24)
        
        return token
    
    def invalidate_password_reset_token(self):
        """
        Vô hiệu hóa token đặt lại mật khẩu
        """
        self.reset_token = None
        self.reset_token_expires = None
    
    def generate_verification_token(self):
        """
        Tạo token để xác thực email
        
        Returns:
            str: Token xác thực email
        """
        from backend.core.security import generate_reset_token
        from datetime import datetime, timedelta
        
        # Tạo token mới
        token = generate_reset_token()
        self.verification_token = token
        self.verification_token_expires = datetime.utcnow() + timedelta(hours=72)
        
        return token
    
    def verify_email(self):
        """
        Xác thực email
        """
        self.is_verified = True
        self.verification_token = None
        self.verification_token_expires = None
    
    def update_last_login(self, ip=None):
        """
        Cập nhật thời gian đăng nhập cuối
        
        Args:
            ip: Địa chỉ IP
        """
        self.last_login = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        if ip:
            self.last_login_ip = ip
    
    def update_last_activity(self):
        """
        Cập nhật thời gian hoạt động cuối
        """
        self.last_activity = datetime.utcnow()
    
    @staticmethod
    def get_by_username(db, username):
        """
        Lấy người dùng theo username
        
        Args:
            db: Database session
            username: Tên đăng nhập
            
        Returns:
            User: Người dùng
        """
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_by_email(db, email):
        """
        Lấy người dùng theo email
        
        Args:
            db: Database session
            email: Địa chỉ email
            
        Returns:
            User: Người dùng
        """
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_by_reset_token(db, token):
        """
        Lấy người dùng theo token đặt lại mật khẩu
        
        Args:
            db: Database session
            token: Token đặt lại mật khẩu
            
        Returns:
            User: Người dùng
        """
        return db.query(User).filter(
            User.reset_token == token,
            User.reset_token_expires > datetime.utcnow()
        ).first()
    
    @staticmethod
    def get_active_users(db, days=30):
        """
        Lấy danh sách người dùng hoạt động trong khoảng thời gian
        
        Args:
            db: Database session
            days: Số ngày
            
        Returns:
            list: Danh sách người dùng
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return db.query(User).filter(
            User.last_activity >= cutoff_date
        ).all()