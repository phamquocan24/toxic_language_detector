# # core/security.py
# from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
# from jose import JWTError, jwt
# from passlib.context import CryptContext
# from datetime import datetime, timedelta
# from backend.config.settings import settings
# from typing import Optional
# from backend.db.models import User

# # Password context for hashing
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# # OAuth2 scheme for token authentication
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# # API key header for extension
# api_key_header = APIKeyHeader(name="X-API-Key")

# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     """
#     Verify if the plain password matches the hashed password
    
#     Args:
#         plain_password (str): Plain text password
#         hashed_password (str): Hashed password
        
#     Returns:
#         bool: True if passwords match, False otherwise
#     """
#     return pwd_context.verify(plain_password, hashed_password)

# def get_password_hash(password: str) -> str:
#     """
#     Hash a password
    
#     Args:
#         password (str): Plain text password
        
#     Returns:
#         str: Hashed password
#     """
#     return pwd_context.hash(password)

# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
#     """
#     Create JWT access token
    
#     Args:
#         data (dict): Data to encode in the token
#         expires_delta (Optional[timedelta], optional): Token expiration time. Defaults to None.
        
#     Returns:
#         str: JWT token
#     """
#     to_encode = data.copy()
    
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
#     return encoded_jwt

# def verify_api_key(api_key: str = Depends(api_key_header)) -> str:
#     """
#     Verify API key for extension
    
#     Args:
#         api_key (str, optional): API key. Defaults to Depends(api_key_header).
        
#     Raises:
#         HTTPException: If the API key is invalid
        
#     Returns:
#         str: Verified API key
#     """
#     if api_key != settings.EXTENSION_API_KEY:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid API Key",
#         )
#     return api_key
# core/security.py
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.config.settings import settings
from backend.db.models import User, Log, get_db
from typing import Optional, Dict, Any, Union
import secrets
import re
import logging

# Thiết lập logger
logger = logging.getLogger("security")
logger.setLevel(logging.INFO)

# Password context cho hashing với cấu hình bảo mật cao
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Số vòng lặp cao hơn cho bảo mật tốt hơn
)

# OAuth2 scheme cho token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)

# API key header cho extension
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Kiểm tra mật khẩu thường khớp với mật khẩu đã hash
    
    Args:
        plain_password (str): Mật khẩu dạng text
        hashed_password (str): Mật khẩu đã hash
        
    Returns:
        bool: True nếu mật khẩu khớp, False nếu không
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hash mật khẩu
    
    Args:
        password (str): Mật khẩu dạng text
        
    Returns:
        str: Mật khẩu đã hash
    """
    return pwd_context.hash(password)

def is_strong_password(password: str) -> bool:
    """
    Kiểm tra xem mật khẩu có đủ mạnh hay không
    
    Args:
        password (str): Mật khẩu cần kiểm tra
        
    Returns:
        bool: True nếu mật khẩu đủ mạnh, False nếu không
    """
    # Kiểm tra độ dài
    if len(password) < 8:
        return False
    
    # Kiểm tra sự kết hợp của các ký tự
    has_upper = re.search(r'[A-Z]', password) is not None
    has_lower = re.search(r'[a-z]', password) is not None
    has_digit = re.search(r'\d', password) is not None
    has_special = re.search(r'[!@#$%^&*(),.?":{}|<>]', password) is not None
    
    # Yêu cầu ít nhất 3 trong 4 điều kiện
    return sum([has_upper, has_lower, has_digit, has_special]) >= 3

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Tạo JWT access token
    
    Args:
        data (dict): Dữ liệu để mã hóa trong token
        expires_delta (Optional[timedelta]): Thời gian hết hạn token
        
    Returns:
        str: JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    to_encode.update({"iat": datetime.utcnow()})  # Thêm thời gian tạo token
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt

def create_refresh_token(user_id: int) -> str:
    """
    Tạo JWT refresh token
    
    Args:
        user_id (int): ID của người dùng
        
    Returns:
        str: JWT refresh token
    """
    expires = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return create_access_token(
        data={"sub": f"refresh:{user_id}", "type": "refresh"},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )

def decode_token(token: str) -> Dict[str, Any]:
    """
    Giải mã JWT token
    
    Args:
        token (str): JWT token
        
    Returns:
        Dict[str, Any]: Dữ liệu từ token
        
    Raises:
        JWTError: Nếu token không hợp lệ
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    request: Request = None
) -> Optional[User]:
    """
    Lấy người dùng hiện tại từ JWT token
    
    Args:
        token (Optional[str]): JWT token
        db (Session): Database session
        request (Request): FastAPI request
        
    Raises:
        HTTPException: Nếu token không hợp lệ hoặc người dùng không tồn tại
        
    Returns:
        User: Người dùng đã xác thực, hoặc None nếu không có token
    """
    # Nếu không có token, trả về None (không xác thực)
    if token is None:
        return None
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực thông tin đăng nhập",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Giải mã JWT token
        payload = decode_token(token)
        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
        
        # Kiểm tra xem token có phải là refresh token không
        if payload.get("type") == "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Cannot use refresh token for authentication",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Lấy thông tin người dùng từ database
        user = db.query(User).filter(User.username == username).first()
        
        if user is None:
            raise credentials_exception
        
        # Kiểm tra xem tài khoản có bị khóa không
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is disabled",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Ghi log
        try:
            if request:
                log = Log(
                    user_id=user.id,
                    action=f"Authentication: {request.method} {request.url.path}",
                    timestamp=datetime.utcnow(),
                    ip_address=request.client.host if request.client else None
                )
                db.add(log)
                db.commit()
        except Exception as e:
            logger.error(f"Lỗi khi ghi log xác thực: {str(e)}")
        
        return user
    except JWTError:
        raise credentials_exception

async def verify_api_key(
    api_key: Optional[str] = Depends(api_key_header),
    db: Session = Depends(get_db)
) -> Union[User, str]:
    """
    Xác thực API key cho extension
    
    Args:
        api_key (Optional[str]): API key
        db (Session): Database session
        
    Raises:
        HTTPException: Nếu API key không hợp lệ
        
    Returns:
        Union[User, str]: Người dùng service hoặc API key
    """
    if api_key is None or api_key != settings.EXTENSION_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key không hợp lệ",
        )
    
    # Tìm tài khoản service cho extension
    service_user = db.query(User).filter(User.username == "extension_service").first()
    
    # Trả về người dùng service nếu có, nếu không thì trả về API key
    return service_user if service_user else api_key

async def verify_api_key_or_token(
    api_key: Optional[str] = Depends(api_key_header),
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Xác thực API key hoặc JWT token
    
    Args:
        api_key (Optional[str]): API key
        token (Optional[str]): JWT token
        db (Session): Database session
        
    Raises:
        HTTPException: Nếu không có phương thức xác thực nào hợp lệ
        
    Returns:
        User: Người dùng đã xác thực
    """
    # Thử xác thực bằng API key trước
    if api_key and api_key == settings.EXTENSION_API_KEY:
        # Tìm tài khoản service cho extension
        service_user = db.query(User).filter(User.username == "extension_service").first()
        
        if service_user:
            return service_user
            
        # Nếu không có tài khoản service, tạo mới
        from backend.db.models import Role
        role = db.query(Role).filter(Role.name == "service").first()
        
        if not role:
            role = Role(name="service", description="Tài khoản dịch vụ")
            db.add(role)
            db.commit()
            db.refresh(role)
        
        service_user = User(
            username="extension_service",
            email="extension@service.local",
            name="Extension Service",
            hashed_password=get_password_hash(secrets.token_urlsafe(32)),
            role_id=role.id,
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.add(service_user)
        db.commit()
        db.refresh(service_user)
        
        # Ghi log
        log = Log(
            user_id=service_user.id,
            action="Service account created",
            timestamp=datetime.utcnow()
        )
        db.add(log)
        db.commit()
        
        return service_user
    
    # Nếu không có API key hợp lệ, thử JWT token
    if token:
        try:
            # Giải mã JWT token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            username: str = payload.get("sub")
            
            if username:
                # Lấy người dùng từ database
                user = db.query(User).filter(User.username == username).first()
                
                if user and user.is_active:
                    # Cập nhật thời gian hoạt động
                    user.last_activity = datetime.utcnow()
                    db.commit()
                    return user
        except JWTError:
            pass
    
    # Nếu không có phương thức xác thực nào hợp lệ
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Yêu cầu xác thực hợp lệ",
        headers={"WWW-Authenticate": "Bearer"},
    )

def generate_reset_token() -> str:
    """
    Tạo token để đặt lại mật khẩu
    
    Returns:
        str: Token đặt lại mật khẩu
    """
    return secrets.token_urlsafe(64)

def get_user_info_from_token(token: str) -> Dict[str, Any]:
    """
    Lấy thông tin người dùng từ token mà không cần kiểm tra hết hạn
    
    Args:
        token (str): JWT token
        
    Returns:
        Dict[str, Any]: Thông tin người dùng hoặc None nếu token không hợp lệ
    """
    try:
        # Giải mã JWT token mà không kiểm tra hết hạn
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": False}
        )
        return payload
    except JWTError:
        return None