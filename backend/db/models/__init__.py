# # db/models/__init__.py
# from backend.db.models.base import Base, engine, SessionLocal
# from backend.db.models.user import User
# from backend.db.models.role import Role
# from backend.db.models.comment import Comment
# from backend.db.models.log import Log

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
# db/models/__init__.py
from backend.db.models.base import Base, engine, SessionLocal
from backend.db.models.user import User
from backend.db.models.role import Role
from backend.db.models.permission import Permission, RolePermission
from backend.db.models.comment import Comment
from backend.db.models.log import Log
from backend.db.models.report import Report
from backend.db.models.settings import UserSettings
from backend.db.models.refresh_token import RefreshToken
from backend.config.settings import settings
from contextlib import contextmanager
import logging

# Thiết lập logging
logger = logging.getLogger("db.models")

# Tạo tất cả các bảng trong database nếu chưa tồn tại
def init_db():
    """Khởi tạo database schema"""
    try:
        Base.meta_data.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise

# Generator function để lấy database session
def get_db():
    """
    Hàm generator để lấy database session.
    Sử dụng trong Depends() của FastAPI.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Context manager để sử dụng trong các hàm thông thường
@contextmanager
def get_db_context():
    """
    Context manager để lấy database session.
    Sử dụng với câu lệnh 'with'.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Hàm tạo dữ liệu mẫu cho môi trường development
def create_initial_data():
    """Tạo dữ liệu ban đầu cho database (roles, permissions, admin user)"""
    from backend.core.security import get_password_hash
    from datetime import datetime
    
    # Chỉ thực hiện trong môi trường development hoặc khi được yêu cầu rõ ràng
    if not settings.CREATE_ADMIN_IF_NOT_EXISTS and settings.DEBUG is False:
        return
    
    with get_db_context() as db:
        # Tạo roles nếu chưa tồn tại
        role_admin = db.query(Role).filter(Role.name == "admin").first()
        if not role_admin:
            role_admin = Role(name="admin", description="Administrator")
            db.add(role_admin)
            db.commit()
            db.refresh(role_admin)
            
        role_user = db.query(Role).filter(Role.name == "user").first()
        if not role_user:
            role_user = Role(name="user", description="Regular user")
            db.add(role_user)
            db.commit()
            db.refresh(role_user)
            
        role_service = db.query(Role).filter(Role.name == "service").first()
        if not role_service:
            role_service = Role(name="service", description="Service account")
            db.add(role_service)
            db.commit()
            db.refresh(role_service)
        
        # Tạo permissions cơ bản
        permissions = [
            {"code": "view_dashboard", "name": "View Dashboard", "description": "Can view dashboard"},
            {"code": "manage_users", "name": "Manage Users", "description": "Can manage users"},
            {"code": "view_reports", "name": "View Reports", "description": "Can view reports"},
            {"code": "create_reports", "name": "Create Reports", "description": "Can create reports"},
            {"code": "manage_settings", "name": "Manage Settings", "description": "Can manage system settings"},
            {"code": "export_data", "name": "Export Data", "description": "Can export data from system"},
            {"code": "view_statistics", "name": "View Statistics", "description": "Can view statistics"},
            {"code": "analyze_text", "name": "Analyze Text", "description": "Can analyze text content"},
        ]
        
        for perm_data in permissions:
            perm = db.query(Permission).filter(Permission.code == perm_data["code"]).first()
            if not perm:
                perm = Permission(**perm_data)
                db.add(perm)
                db.commit()
                db.refresh(perm)
        
        # Gán tất cả quyền cho admin
        admin_permissions = db.query(Permission).all()
        for perm in admin_permissions:
            role_perm = db.query(RolePermission).filter(
                RolePermission.role_id == role_admin.id,
                RolePermission.permission_id == perm.id
            ).first()
            
            if not role_perm:
                role_perm = RolePermission(role_id=role_admin.id, permission_id=perm.id)
                db.add(role_perm)
                db.commit()
        
        # Gán quyền cơ bản cho user
        user_permission_codes = ["view_dashboard", "view_reports", "analyze_text", "view_statistics"]
        user_permissions = db.query(Permission).filter(Permission.code.in_(user_permission_codes)).all()
        
        for perm in user_permissions:
            role_perm = db.query(RolePermission).filter(
                RolePermission.role_id == role_user.id,
                RolePermission.permission_id == perm.id
            ).first()
            
            if not role_perm:
                role_perm = RolePermission(role_id=role_user.id, permission_id=perm.id)
                db.add(role_perm)
                db.commit()
        
        # Gán quyền cho service account
        service_permission_codes = ["analyze_text"]
        service_permissions = db.query(Permission).filter(Permission.code.in_(service_permission_codes)).all()
        
        for perm in service_permissions:
            role_perm = db.query(RolePermission).filter(
                RolePermission.role_id == role_service.id,
                RolePermission.permission_id == perm.id
            ).first()
            
            if not role_perm:
                role_perm = RolePermission(role_id=role_service.id, permission_id=perm.id)
                db.add(role_perm)
                db.commit()
        
        # Tạo tài khoản admin mặc định nếu chưa tồn tại
        admin_user = db.query(User).filter(User.username == settings.ADMIN_USERNAME).first()
        if not admin_user:
            admin_user = User(
                username=settings.ADMIN_USERNAME,
                email=settings.ADMIN_EMAIL,
                name="Administrator",
                hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
                role_id=role_admin.id,
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            
            # Tạo settings mặc định cho admin
            admin_settings = UserSettings(
                user_id=admin_user.id,
                theme="light",
                language="vi",
                notifications_enabled=True,
                meta_data="{}",
                created_at=datetime.utcnow()
            )
            db.add(admin_settings)
            db.commit()
            
            logger.info(f"Admin user '{settings.ADMIN_USERNAME}' created successfully")
            
        logger.info("Initial data created successfully")

# Hàm để làm sạch bộ nhớ đệm của session
def clear_session_cache():
    """Làm sạch bộ nhớ đệm của session"""
    SessionLocal.remove()