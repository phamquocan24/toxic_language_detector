from typing import Generator, Optional, Dict, Any
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from backend.db.base import get_db
from backend.db.models.user import User
from backend.db.models.log import Log
from backend.core.security import (
    ROLE_PERMISSIONS, 
    get_user_by_email, 
    has_permission
)
from backend.config.settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get the current authenticated user based on JWT token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        # Get email from token
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    user = await get_user_by_email(db, email)
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Check if the current user is active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user

def require_permission(required_permission: str):
    """
    Dependency for requiring a specific permission
    """
    async def _require_permission(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        if not has_permission(current_user, required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions. Required permission: {required_permission}"
            )
        return current_user
    
    return _require_permission

def admin_required(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependency for requiring admin role
    """
    if current_user.role.name.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

def moderator_required(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependency for requiring at least moderator role
    """
    role = current_user.role.name.lower()
    if role != "admin" and role != "moderator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Moderator privileges required"
        )
    return current_user

async def log_activity(
    db: AsyncSession,
    user_id: int,
    action: str,
    endpoint: str,
    request_data: Optional[Dict[str, Any]] = None,
    response_data: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    status_code: Optional[int] = None,
    details: Optional[str] = None
) -> Log:
    """
    Log user activity
    """
    # Create log entry
    log_entry = Log(
        user_id=user_id,
        action=action,
        endpoint=endpoint,
        request_data=request_data,
        response_data=response_data,
        ip_address=ip_address,
        user_agent=user_agent,
        status_code=status_code,
        details=details
    )
    
    # Add to database
    db.add(log_entry)
    await db.commit()
    await db.refresh(log_entry)
    
    return log_entry

class LoggingDependency:
    """
    Dependency for logging requests automatically
    """
    def __init__(self, action: str, details: Optional[str] = None):
        self.action = action
        self.details = details
    
    async def __call__(
        self,
        request: Request,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
    ):
        # Get request body if available
        try:
            request_body = await request.json()
        except:
            request_body = {}
        
        # Create log entry
        log_entry = await log_activity(
            db=db,
            user_id=current_user.id,
            action=self.action,
            endpoint=str(request.url),
            request_data=request_body,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            details=self.details
        )
        
        return log_entry