# # config/security.py
# from passlib.context import CryptContext
# from fastapi import Depends, HTTPException, status
# from fastapi.security import APIKeyHeader
# from backend.config.settings import settings

# # Password hashing
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# # API key for extension
# api_key_header = APIKeyHeader(name="X-API-Key")

# def verify_password(plain_password, hashed_password):
#     """Verify password against hash"""
#     return pwd_context.verify(plain_password, hashed_password)

# def get_password_hash(password):
#     """Generate password hash"""
#     return pwd_context.hash(password)

# def verify_api_key(api_key: str = Depends(api_key_header)):
#     """Verify API key for extension"""
#     if api_key != settings.EXTENSION_API_KEY:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid API Key",
#         )
# config/security.py
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from backend.config.settings import settings
from backend.db.models import get_db, User
from sqlalchemy.orm import Session

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for JWT authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# API key header for backward compatibility
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_password(plain_password, hashed_password):
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Generate password hash"""
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
        
    # Get user from database
    user = db.query(User).filter(User.username == username).first()
    
    if user is None:
        raise credentials_exception
        
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account"
        )
        
    # Update last login time
    user.last_login = datetime.utcnow()
    db.commit()
    
    return user
async def get_admin_user(current_user: User = Depends(get_current_user)):
    """
    Kiểm tra nếu người dùng hiện tại có quyền admin
    """
    # Lấy role name
    role_name = None
    if hasattr(current_user, 'role'):
        if isinstance(current_user.role, str):
            role_name = current_user.role
        elif hasattr(current_user.role, 'name'):
            role_name = current_user.role.name
    
    if role_name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không đủ quyền hạn. Yêu cầu quyền admin."
        )
    return current_user

async def get_optional_current_user(
    token: Optional[str] = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):
    """Get current user if token is valid, otherwise return None"""
    try:
        return await get_current_user(token, db)
    except HTTPException:
        return None

async def rate_limit_check(request: Request, db: Session = Depends(get_db)):
    """Check rate limit for API requests"""
    client_ip = request.client.host
    
    # Skip rate limiting for local testing
    if client_ip in ["127.0.0.1", "::1"]:
        return
    
    # Implement rate limiting logic
    # For simplicity, we'll use a simple in-memory store
    # In production, use Redis or similar for distributed rate limiting
    
    from backend.utils.rate_limiter import check_rate_limit
    
    if not check_rate_limit(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests"
        )

async def verify_api_key(
    api_key: Optional[str] = Depends(api_key_header), 
    db: Session = Depends(get_db)
):
    """
    Verify API key for extension (backward compatibility)
    Falls back to JWT token if API key is not provided
    """
    # If API key is provided, verify it
    if api_key:
        if api_key == settings.EXTENSION_API_KEY:
            # Find the service account user
            service_user = db.query(User).filter(User.username == "extension_service").first()
            
            if not service_user:
                # Create a service account if it doesn't exist
                from backend.db.models import Role
                role = db.query(Role).filter(Role.name == "service").first()
                
                if not role:
                    role = Role(name="service", description="Service account role")
                    db.add(role)
                    db.commit()
                    db.refresh(role)
                
                service_user = User(
                    username="extension_service",
                    email="extension@service.local",
                    hashed_password=get_password_hash(settings.EXTENSION_API_KEY),
                    role_id=role.id,
                    is_active=True
                )
                db.add(service_user)
                db.commit()
                db.refresh(service_user)
            
            return service_user
            
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
    
    # If no API key, fall back to JWT token
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="API Key required",
        headers={"WWW-Authenticate": "Bearer"},
    )

def get_user_by_email(email: str, db: Session):
    """Helper function to get user by email"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(username: str, db: Session):
    """Helper function to get user by username"""
    return db.query(User).filter(User.username == username).first()

def get_user_by_reset_token(token: str, db: Session):
    """Helper function to get user by reset token"""
    user = db.query(User).filter(
        User.reset_token == token,
        User.reset_token_expires > datetime.utcnow()
    ).first()
    return user