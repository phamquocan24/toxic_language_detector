# # services/user_service.py
# from sqlalchemy.orm import Session
# from backend.db.models import User, Role
# from backend.core.security import get_password_hash, verify_password
# from typing import Optional, List

# class UserService:
#     @staticmethod
#     def get_user_by_username(db: Session, username: str) -> Optional[User]:
#         """Get a user by username"""
#         return db.query(User).filter(User.username == username).first()
    
#     @staticmethod
#     def get_user_by_email(db: Session, email: str) -> Optional[User]:
#         """Get a user by email"""
#         return db.query(User).filter(User.email == email).first()
    
#     @staticmethod
#     def create_user(db: Session, username: str, email: str, password: str, role_name: str = "user") -> User:
#         """Create a new user"""
#         # Get role
#         role = db.query(Role).filter(Role.name == role_name).first()
#         if not role:
#             role = Role(name=role_name, description=f"{role_name.capitalize()} role")
#             db.add(role)
#             db.commit()
#             db.refresh(role)
        
#         # Create user
#         hashed_password = get_password_hash(password)
#         user = User(
#             username=username,
#             email=email,
#             hashed_password=hashed_password,
#             role_id=role.id
#         )
#         db.add(user)
#         db.commit()
#         db.refresh(user)
        
#         return user
    
#     @staticmethod
#     def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
#         """Authenticate a user"""
#         user = UserService.get_user_by_username(db, username)
#         if not user or not verify_password(password, user.hashed_password):
#             return None
#         return user
    
#     @staticmethod
#     def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
#         """Get all users with pagination"""
#         return db.query(User).offset(skip).limit(limit).all()
    
#     @staticmethod
#     def update_user(db: Session, user_id: int, **kwargs) -> Optional[User]:
#         """Update user details"""
#         user = db.query(User).filter(User.id == user_id).first()
#         if not user:
#             return None
        
#         for key, value in kwargs.items():
#             if key == "password":
#                 value = get_password_hash(value)
#                 key = "hashed_password"
            
#             if hasattr(user, key):
#                 setattr(user, key, value)
        
#         db.commit()
#         db.refresh(user)
#         return user
# services/user_service.py
from sqlalchemy.orm import Session
from backend.db.models import User, Role, Log, Comment, RefreshToken
from backend.core.security import get_password_hash, verify_password, generate_reset_token
from typing import Optional, List, Dict, Any, Tuple
import logging
from datetime import datetime, timedelta
import json

# Thiết lập logging
logger = logging.getLogger("services.user_service")

class UserService:
    """
    Service xử lý các thao tác liên quan đến người dùng
    """
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """
        Lấy người dùng theo username
        
        Args:
            db: Database session
            username: Tên đăng nhập
            
        Returns:
            Optional[User]: Người dùng hoặc None nếu không tìm thấy
        """
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        Lấy người dùng theo email
        
        Args:
            db: Database session
            email: Địa chỉ email
            
        Returns:
            Optional[User]: Người dùng hoặc None nếu không tìm thấy
        """
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """
        Lấy người dùng theo ID
        
        Args:
            db: Database session
            user_id: ID người dùng
            
        Returns:
            Optional[User]: Người dùng hoặc None nếu không tìm thấy
        """
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def create_user(
        db: Session, 
        username: str, 
        email: str, 
        password: str, 
        role_name: str = "user", 
        name: Optional[str] = None,
        is_active: bool = True,
        is_verified: bool = False,
        client_ip: Optional[str] = None
    ) -> User:
        """
        Tạo người dùng mới
        
        Args:
            db: Database session
            username: Tên đăng nhập
            email: Địa chỉ email
            password: Mật khẩu
            role_name: Tên vai trò
            name: Tên hiển thị
            is_active: Người dùng có hoạt động không
            is_verified: Email đã được xác thực chưa
            client_ip: IP của người dùng khi đăng ký
            
        Returns:
            User: Người dùng mới tạo
        """
        try:
            # Kiểm tra username đã tồn tại chưa
            existing_user = UserService.get_user_by_username(db, username)
            if existing_user:
                raise ValueError(f"Username '{username}' đã tồn tại")
            
            # Kiểm tra email đã tồn tại chưa
            existing_email = UserService.get_user_by_email(db, email)
            if existing_email:
                raise ValueError(f"Email '{email}' đã tồn tại")
            
            # Lấy vai trò
            role = db.query(Role).filter(Role.name == role_name).first()
            if not role:
                role = Role(name=role_name, description=f"{role_name.capitalize()} role")
                db.add(role)
                db.commit()
                db.refresh(role)
            
            # Tạo người dùng mới
            hashed_password = get_password_hash(password)
            user = User(
                username=username,
                email=email,
                name=name or username,
                hashed_password=hashed_password,
                role_id=role.id,
                is_active=is_active,
                is_verified=is_verified,
                created_at=datetime.utcnow(),
                last_login_ip=client_ip
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Tạo settings mặc định
            UserService.initialize_user_settings(db, user.id)
            
            # Ghi log
            log = Log(
                user_id=user.id,
                action="User registration",
                timestamp=datetime.utcnow(),
                client_ip=client_ip
            )
            db.add(log)
            db.commit()
            
            logger.info(f"Đã tạo người dùng mới: {username} ({email})")
            return user
            
        except Exception as e:
            db.rollback()
            logger.error(f"Lỗi khi tạo người dùng: {str(e)}")
            raise
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str, client_ip: Optional[str] = None) -> Optional[User]:
        """
        Xác thực người dùng
        
        Args:
            db: Database session
            username: Tên đăng nhập
            password: Mật khẩu
            client_ip: IP của người dùng khi đăng nhập
            
        Returns:
            Optional[User]: Người dùng nếu xác thực thành công, None nếu thất bại
        """
        # Kiểm tra cả username và email
        user = db.query(User).filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user:
            logger.warning(f"Đăng nhập thất bại: Không tìm thấy người dùng '{username}'")
            return None
        
        if not verify_password(password, user.hashed_password):
            logger.warning(f"Đăng nhập thất bại: Mật khẩu không đúng cho người dùng '{username}'")
            
            # Ghi log đăng nhập thất bại
            log = Log(
                user_id=user.id,
                action="Failed login attempt",
                timestamp=datetime.utcnow(),
                client_ip=client_ip,
                is_error=True
            )
            db.add(log)
            db.commit()
            
            return None
        
        # Kiểm tra tài khoản bị khóa
        if not user.is_active:
            logger.warning(f"Đăng nhập thất bại: Tài khoản '{username}' đã bị khóa")
            return None
        
        # Cập nhật thông tin đăng nhập
        user.last_login = datetime.utcnow()
        user.last_activity = datetime.utcnow()
        if client_ip:
            user.last_login_ip = client_ip
        
        # Ghi log đăng nhập thành công
        log = Log(
            user_id=user.id,
            action="Successful login",
            timestamp=datetime.utcnow(),
            client_ip=client_ip
        )
        db.add(log)
        db.commit()
        
        logger.info(f"Đăng nhập thành công: {username}")
        return user
    
    @staticmethod
    def create_refresh_token(db: Session, user_id: int, token: str, expires_at: datetime) -> RefreshToken:
        """
        Tạo refresh token mới
        
        Args:
            db: Database session
            user_id: ID người dùng
            token: Refresh token
            expires_at: Thời gian hết hạn
            
        Returns:
            RefreshToken: Token đã tạo
        """
        # Xóa các token cũ của người dùng này
        db.query(RefreshToken).filter(RefreshToken.user_id == user_id).delete()
        
        # Tạo token mới
        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            created_at=datetime.utcnow()
        )
        db.add(refresh_token)
        db.commit()
        db.refresh(refresh_token)
        
        return refresh_token
    
    @staticmethod
    def validate_refresh_token(db: Session, token: str) -> Optional[User]:
        """
        Xác thực refresh token
        
        Args:
            db: Database session
            token: Refresh token
            
        Returns:
            Optional[User]: Người dùng nếu token hợp lệ, None nếu không
        """
        refresh_token = db.query(RefreshToken).filter(
            RefreshToken.token == token,
            RefreshToken.expires_at > datetime.utcnow()
        ).first()
        
        if not refresh_token:
            return None
        
        # Lấy người dùng
        user = db.query(User).filter(User.id == refresh_token.user_id).first()
        if not user or not user.is_active:
            return None
        
        return user
    
    @staticmethod
    def get_all_users(
        db: Session, 
        skip: int = 0, 
        limit: int = 100, 
        search: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[User], int]:
        """
        Lấy danh sách người dùng với bộ lọc và phân trang
        
        Args:
            db: Database session
            skip: Số lượng bản ghi bỏ qua
            limit: Số lượng bản ghi tối đa
            search: Từ khóa tìm kiếm
            role: Lọc theo vai trò
            is_active: Lọc theo trạng thái hoạt động
            sort_by: Sắp xếp theo trường
            sort_order: Thứ tự sắp xếp ('asc' hoặc 'desc')
            
        Returns:
            Tuple[List[User], int]: (Danh sách người dùng, tổng số người dùng thỏa mãn bộ lọc)
        """
        # Xây dựng query cơ sở
        query = db.query(User)
        
        # Áp dụng các bộ lọc
        if search:
            query = query.filter(
                (User.username.ilike(f"%{search}%")) | 
                (User.email.ilike(f"%{search}%")) |
                (User.name.ilike(f"%{search}%"))
            )
        
        if role:
            query = query.join(Role).filter(Role.name == role)
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        # Đếm tổng số bản ghi
        total = query.count()
        
        # Sắp xếp
        if sort_order.lower() == "asc":
            query = query.order_by(getattr(User, sort_by).asc())
        else:
            query = query.order_by(getattr(User, sort_by).desc())
        
        # Phân trang
        users = query.offset(skip).limit(limit).all()
        
        return users, total
    
    @staticmethod
    def update_user(
        db: Session, 
        user_id: int, 
        updated_by_id: Optional[int] = None, 
        log_action: bool = True, 
        **kwargs
    ) -> Optional[User]:
        """
        Cập nhật thông tin người dùng
        
        Args:
            db: Database session
            user_id: ID người dùng cần cập nhật
            updated_by_id: ID người dùng thực hiện cập nhật
            log_action: Có ghi log không
            **kwargs: Các trường cần cập nhật
            
        Returns:
            Optional[User]: Người dùng sau khi cập nhật hoặc None nếu không tìm thấy
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning(f"Không tìm thấy người dùng với ID {user_id}")
            return None
        
        # Lưu lại thông tin cũ để ghi log
        old_values = {}
        
        # Cập nhật các trường
        for key, value in kwargs.items():
            if key == "password":
                old_values["password"] = "******"  # Không lưu mật khẩu thật
                value = get_password_hash(value)
                key = "hashed_password"
            elif hasattr(user, key):
                old_values[key] = getattr(user, key)
            
            if hasattr(user, key):
                setattr(user, key, value)
        
        # Cập nhật updated_at
        user.updated_at = datetime.utcnow()
        
        # Lưu các thay đổi
        try:
            db.commit()
            db.refresh(user)
            
            # Ghi log nếu cần
            if log_action and updated_by_id:
                log = Log(
                    user_id=updated_by_id,
                    action=f"Updated user: {user.username} (ID: {user.id})",
                    timestamp=datetime.utcnow(),
                    metadata=json.dumps({
                        "user_id": user.id,
                        "old_values": old_values,
                        "new_values": {k: v for k, v in kwargs.items() if k != "password"}
                    })
                )
                db.add(log)
                db.commit()
            
            logger.info(f"Đã cập nhật người dùng: {user.username} (ID: {user.id})")
            return user
            
        except Exception as e:
            db.rollback()
            logger.error(f"Lỗi khi cập nhật người dùng: {str(e)}")
            raise
    
    @staticmethod
    def delete_user(db: Session, user_id: int, deleted_by_id: Optional[int] = None) -> bool:
        """
        Xóa người dùng
        
        Args:
            db: Database session
            user_id: ID người dùng cần xóa
            deleted_by_id: ID người dùng thực hiện xóa
            
        Returns:
            bool: True nếu xóa thành công, False nếu không
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.warning(f"Không tìm thấy người dùng với ID {user_id}")
            return False
        
        # Lưu thông tin để ghi log
        username = user.username
        email = user.email
        
        try:
            # Xóa các refresh token
            db.query(RefreshToken).filter(RefreshToken.user_id == user_id).delete()
            
            # Xóa người dùng
            db.delete(user)
            
            # Ghi log
            if deleted_by_id:
                log = Log(
                    user_id=deleted_by_id,
                    action=f"Deleted user: {username} (ID: {user_id})",
                    timestamp=datetime.utcnow(),
                    metadata=json.dumps({
                        "user_id": user_id,
                        "username": username,
                        "email": email
                    })
                )
                db.add(log)
            
            db.commit()
            logger.info(f"Đã xóa người dùng: {username} (ID: {user_id})")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Lỗi khi xóa người dùng: {str(e)}")
            return False
    
    @staticmethod
    def change_password(
        db: Session, 
        user_id: int, 
        current_password: str, 
        new_password: str, 
        client_ip: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Đổi mật khẩu người dùng
        
        Args:
            db: Database session
            user_id: ID người dùng
            current_password: Mật khẩu hiện tại
            new_password: Mật khẩu mới
            client_ip: IP của người dùng
            
        Returns:
            Tuple[bool, str]: (Thành công hay không, Thông báo)
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False, "Không tìm thấy người dùng"
        
        # Kiểm tra mật khẩu hiện tại
        if not verify_password(current_password, user.hashed_password):
            # Ghi log
            log = Log(
                user_id=user_id,
                action="Failed password change - incorrect current password",
                timestamp=datetime.utcnow(),
                client_ip=client_ip,
                is_error=True
            )
            db.add(log)
            db.commit()
            
            return False, "Mật khẩu hiện tại không đúng"
        
        # Cập nhật mật khẩu mới
        user.hashed_password = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        
        # Xóa tất cả refresh token
        db.query(RefreshToken).filter(RefreshToken.user_id == user_id).delete()
        
        # Ghi log
        log = Log(
            user_id=user_id,
            action="Password changed successfully",
            timestamp=datetime.utcnow(),
            client_ip=client_ip
        )
        db.add(log)
        
        db.commit()
        logger.info(f"Đã đổi mật khẩu cho người dùng: {user.username} (ID: {user_id})")
        
        return True, "Đổi mật khẩu thành công"
    
    @staticmethod
    def request_password_reset(db: Session, email: str, client_ip: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """
        Yêu cầu đặt lại mật khẩu
        
        Args:
            db: Database session
            email: Email của người dùng
            client_ip: IP của người dùng
            
        Returns:
            Tuple[bool, Optional[str]]: (Thành công hay không, Token reset nếu thành công)
        """
        user = db.query(User).filter(User.email == email).first()
        if not user:
            # Không trả về lỗi cụ thể vì lý do bảo mật
            logger.info(f"Yêu cầu đặt lại mật khẩu với email không tồn tại: {email}")
            return False, None
        
        # Kiểm tra tài khoản bị khóa
        if not user.is_active:
            logger.info(f"Yêu cầu đặt lại mật khẩu cho tài khoản bị khóa: {email}")
            return False, None
        
        # Tạo token đặt lại mật khẩu
        reset_token = generate_reset_token()
        user.reset_token = reset_token
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=24)
        
        # Ghi log
        log = Log(
            user_id=user.id,
            action="Password reset requested",
            timestamp=datetime.utcnow(),
            client_ip=client_ip
        )
        db.add(log)
        
        db.commit()
        logger.info(f"Đã tạo token đặt lại mật khẩu cho người dùng: {user.username} (ID: {user.id})")
        
        return True, reset_token
    
    @staticmethod
    def reset_password(db: Session, token: str, new_password: str, client_ip: Optional[str] = None) -> Tuple[bool, str]:
        """
        Đặt lại mật khẩu bằng token
        
        Args:
            db: Database session
            token: Token đặt lại mật khẩu
            new_password: Mật khẩu mới
            client_ip: IP của người dùng
            
        Returns:
            Tuple[bool, str]: (Thành công hay không, Thông báo)
        """
        user = db.query(User).filter(
            User.reset_token == token,
            User.reset_token_expires > datetime.utcnow()
        ).first()
        
        if not user:
            logger.warning(f"Token đặt lại mật khẩu không hợp lệ hoặc đã hết hạn: {token[:10]}...")
            return False, "Token không hợp lệ hoặc đã hết hạn"
        
        # Cập nhật mật khẩu mới
        user.hashed_password = get_password_hash(new_password)
        user.reset_token = None
        user.reset_token_expires = None
        user.updated_at = datetime.utcnow()
        
        # Xóa tất cả refresh token
        db.query(RefreshToken).filter(RefreshToken.user_id == user.id).delete()
        
        # Ghi log
        log = Log(
            user_id=user.id,
            action="Password reset completed",
            timestamp=datetime.utcnow(),
            client_ip=client_ip
        )
        db.add(log)
        
        db.commit()
        logger.info(f"Đã đặt lại mật khẩu cho người dùng: {user.username} (ID: {user.id})")
        
        return True, "Đặt lại mật khẩu thành công"
    
    @staticmethod
    def get_user_stats(db: Session, user_id: int) -> Dict[str, Any]:
        """
        Lấy thống kê của người dùng
        
        Args:
            db: Database session
            user_id: ID người dùng
            
        Returns:
            Dict[str, Any]: Thông tin thống kê
        """
        # Đếm tổng số comment
        total_comments = db.query(Comment).filter(Comment.user_id == user_id).count()
        
        # Đếm số comment theo loại
        clean_comments = db.query(Comment).filter(
            Comment.user_id == user_id, 
            Comment.prediction == 0
        ).count()
        
        offensive_comments = db.query(Comment).filter(
            Comment.user_id == user_id, 
            Comment.prediction == 1
        ).count()
        
        hate_comments = db.query(Comment).filter(
            Comment.user_id == user_id, 
            Comment.prediction == 2
        ).count()
        
        spam_comments = db.query(Comment).filter(
            Comment.user_id == user_id, 
            Comment.prediction == 3
        ).count()
        
        # Lấy số lượng theo platform
        platform_stats = db.query(
            Comment.platform, 
            db.func.count(Comment.id).label('count')
        ).filter(
            Comment.user_id == user_id
        ).group_by(Comment.platform).all()
        
        platforms = {platform: count for platform, count in platform_stats}
        
        # Lấy thời gian hoạt động gần đây nhất
        user = db.query(User).filter(User.id == user_id).first()
        last_activity = user.last_activity if user else None
        last_login = user.last_login if user else None
        
        return {
            "total_comments": total_comments,
            "clean_comments": clean_comments,
            "offensive_comments": offensive_comments,
            "hate_comments": hate_comments,
            "spam_comments": spam_comments,
            "platforms": platforms,
            "last_activity": last_activity,
            "last_login": last_login
        }
    
    @staticmethod
    def initialize_user_settings(db: Session, user_id: int) -> None:
        """
        Khởi tạo cài đặt mặc định cho người dùng mới
        
        Args:
            db: Database session
            user_id: ID người dùng
        """
        from backend.db.models import UserSettings
        
        # Kiểm tra xem đã có settings chưa
        existing = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
        if existing:
            return
        
        # Tạo settings mặc định
        settings = UserSettings(
            user_id=user_id,
            theme="light",
            language="vi",
            notifications_enabled=True,
            extension_settings=json.dumps({
                "enabled_platforms": ["facebook", "youtube", "twitter", "tiktok"],
                "auto_analyze": True,
                "highlight_comments": True,
                "notification": True,
                "store_clean": False,
                "threshold": 0.7
            }),
            created_at=datetime.utcnow()
        )
        
        db.add(settings)
        db.commit()