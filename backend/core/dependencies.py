# # core/dependencies.py
# from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
# from jose import JWTError, jwt
# from sqlalchemy.orm import Session
# from backend.db.models import get_db, User
# from backend.config.settings import settings
# from datetime import datetime, timedelta
# from typing import Optional

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
#     """
#     Create a new JWT access token
    
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

# def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     """
#     Get the current authenticated user
    
#     Args:
#         token (str, optional): JWT token. Defaults to Depends(oauth2_scheme).
#         db (Session, optional): Database session. Defaults to Depends(get_db).
        
#     Raises:
#         HTTPException: If the token is invalid or the user doesn't exist
        
#     Returns:
#         User: Authenticated user
#     """
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
    
#     try:
#         payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
#         username: str = payload.get("sub")
        
#         if username is None:
#             raise credentials_exception
            
#     except JWTError:
#         raise credentials_exception
        
#     user = db.query(User).filter(User.username == username).first()
    
#     if user is None or not user.is_active:
#         raise credentials_exception
        
#     return user

# def get_current_active_user(current_user: User = Depends(get_current_user)):
#     """
#     Get the current active user
    
#     Args:
#         current_user (User, optional): Current user. Defaults to Depends(get_current_user).
        
#     Raises:
#         HTTPException: If the user is inactive
        
#     Returns:
#         User: Active user
#     """
#     if not current_user.is_active:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Inactive user"
#         )
#     return current_user

# def get_admin_user(current_user: User = Depends(get_current_user)):
#     """
#     Get the current admin user
    
#     Args:
#         current_user (User, optional): Current user. Defaults to Depends(get_current_user).
        
#     Raises:
#         HTTPException: If the user is not an admin
        
#     Returns:
#         User: Admin user
#     """
#     if current_user.role.name != "admin":
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not enough permissions"
#         )
#     return current_user
# core/dependencies.py
from fastapi import Depends, HTTPException, status, Request, Header
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from backend.db.models import get_db, User, Log
from backend.config.settings import settings
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Union
import time
import ipaddress
from backend.utils.rate_limiter import check_rate_limit, RateLimiter

# Rate limiter instance
rate_limiter = RateLimiter()

# OAuth2 scheme for JWT authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)

# API key header for extension
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a new JWT access token
    
    Args:
        data (dict): Data to encode in the token
        expires_delta (Optional[timedelta]): Token expiration time
        
    Returns:
        str: JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt

def create_refresh_token(user_id: int) -> str:
    """
    Create a new JWT refresh token
    
    Args:
        user_id (int): User ID
        
    Returns:
        str: JWT refresh token
    """
    expires = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return create_access_token(
        data={"sub": f"refresh:{user_id}", "type": "refresh"},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )

async def get_current_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token
    
    Args:
        request (Request): FastAPI request object
        token (Optional[str]): JWT token
        db (Session): Database session
        
    Raises:
        HTTPException: If the token is invalid or the user doesn't exist
        
    Returns:
        User: Authenticated user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực người dùng",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Check if token is provided
    if token is None:
        raise credentials_exception
    
    try:
        # Decode JWT token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        
        # Check if username is in the token
        if username is None:
            raise credentials_exception
            
        # Check if token is a refresh token
        if payload.get("type") == "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token không thể sử dụng cho API này",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    except JWTError:
        raise credentials_exception
        
    # Get user from database
    user = db.query(User).filter(User.username == username).first()
    
    # Check if user exists
    if user is None:
        raise credentials_exception
        
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị vô hiệu hóa",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last activity
    user.last_activity = datetime.utcnow()
    db.commit()
    
    # Log the API access if not in development mode
    if not settings.DEBUG:
        log = Log(
            user_id=user.id,
            action=f"API Access: {request.method} {request.url.path}",
            timestamp=datetime.utcnow(),
            client_ip=request.client.host
        )
        db.add(log)
        db.commit()
    
    return user

async def get_optional_current_user(
    token: Optional[str] = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get the current user if token is valid, otherwise return None
    
    Args:
        token (Optional[str]): JWT token
        db (Session): Database session
        
    Returns:
        Optional[User]: User if token is valid, None otherwise
    """
    if token is None:
        return None
        
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            return None
            
        user = db.query(User).filter(User.username == username).first()
        
        if user is None or not user.is_active:
            return None
            
        return user
        
    except JWTError:
        return None

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get the current active user
    
    Args:
        current_user (User): Current user
        
    Raises:
        HTTPException: If the user is inactive
        
    Returns:
        User: Active user
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đã bị vô hiệu hóa"
        )
    return current_user

async def get_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get the current admin user
    
    Args:
        current_user (User): Current user
        
    Raises:
        HTTPException: If the user is not an admin
        
    Returns:
        User: Admin user
    """
    if current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không đủ quyền hạn"
        )
    return current_user

async def verify_api_key_or_token(
    api_key: Optional[str] = Depends(api_key_header), 
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Verify API key or JWT token
    
    Args:
        api_key (Optional[str]): API key
        token (Optional[str]): JWT token
        db (Session): Database session
        
    Raises:
        HTTPException: If neither API key nor token is valid
        
    Returns:
        User: Authenticated user
    """
    # Try API key first
    if api_key and api_key == settings.EXTENSION_API_KEY:
        # Find the extension service account
        service_user = db.query(User).filter(User.username == "extension_service").first()
        
        if service_user:
            return service_user
    
    # If API key is not valid, try JWT token
    if token:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            username: str = payload.get("sub")
            
            if username:
                user = db.query(User).filter(User.username == username).first()
                
                if user and user.is_active:
                    return user
        except JWTError:
            pass
    
    # If neither is valid, raise exception
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Xác thực không hợp lệ",
        headers={"WWW-Authenticate": "Bearer"},
    )

async def rate_limit_dependency(
    request: Request,
    x_forwarded_for: Optional[str] = Header(None)
) -> None:
    """
    Check rate limit for request
    
    Args:
        request (Request): FastAPI request object
        x_forwarded_for (Optional[str]): X-Forwarded-For header
        
    Raises:
        HTTPException: If rate limit is exceeded
    """
    if not settings.RATE_LIMIT_ENABLED:
        return
        
    # Get client IP, considering X-Forwarded-For header if present
    client_ip = x_forwarded_for.split(',')[0].strip() if x_forwarded_for else request.client.host
    
    # Skip rate limiting for localhost
    try:
        ip_obj = ipaddress.ip_address(client_ip)
        if ip_obj.is_loopback:
            return
    except ValueError:
        # If IP is invalid, apply rate limiting
        pass
        
    # Check rate limit
    if not rate_limiter.check_rate(client_ip):
        retry_after = rate_limiter.get_retry_after(client_ip)
        
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Quá nhiều yêu cầu, vui lòng thử lại sau",
            headers={"Retry-After": str(retry_after)}
        )

async def validate_permissions(
    required_permissions: List[str],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    """
    Validate if user has required permissions
    
    Args:
        required_permissions (List[str]): List of required permission codes
        current_user (User): Current user
        db (Session): Database session
        
    Raises:
        HTTPException: If user doesn't have required permissions
    """
    # Admin has all permissions
    if current_user.role.name == "admin":
        return
        
    # Get user permissions
    from backend.db.models import Permission, RolePermission
    
    role_permissions = db.query(RolePermission).filter(
        RolePermission.role_id == current_user.role_id
    ).all()
    
    # Get permission codes
    permission_ids = [rp.permission_id for rp in role_permissions]
    
    permissions = db.query(Permission).filter(
        Permission.id.in_(permission_ids)
    ).all()
    
    user_permission_codes = [p.code for p in permissions]
    
    # Check if user has all required permissions
    if not all(code in user_permission_codes for code in required_permissions):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không đủ quyền hạn"
        )