from datetime import timedelta
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.db.base import get_db
from backend.db.models.user import User
from backend.db.models.role import Role
from backend.db.models.log import Log
from backend.core.security import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_current_active_user
)
from backend.config.settings import settings

router = APIRouter()

@router.post("/login", response_model=Dict[str, Any])
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    # Log successful login
    log_entry = Log(
        user_id=user.id,
        action="login",
        endpoint="/api/auth/login",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status_code=200,
        details=f"Successful login for user {user.username}"
    )
    db.add(log_entry)
    await db.commit()
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role.name
    }

@router.post("/register", response_model=Dict[str, Any])
async def register_user(
    request: Request,
    user_data: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user
    """
    email = user_data.get("email")
    username = user_data.get("username")
    password = user_data.get("password")
    
    # Validate required fields
    if not email or not username or not password:
        raise HTTPException(status_code=400, detail="Email, username and password are required")
    
    # Check if email already exists
    result = await db.execute(select(User).filter(User.email == email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if username already exists
    result = await db.execute(select(User).filter(User.username == username))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Get default user role (or create it if it doesn't exist)
    result = await db.execute(select(Role).filter(Role.name == "user"))
    role = result.scalars().first()
    
    if not role:
        # Create user role
        role = Role(name="user", description="Regular user role")
        db.add(role)
        await db.commit()
        await db.refresh(role)
    
    # Create user
    hashed_password = get_password_hash(password)
    new_user = User(
        email=email,
        username=username,
        hashed_password=hashed_password,
        role_id=role.id,
        is_active=True
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Log registration
    log_entry = Log(
        user_id=new_user.id,
        action="register",
        endpoint="/api/auth/register",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status_code=200,
        details=f"User registered: {username}"
    )
    db.add(log_entry)
    await db.commit()
    
    # Generate access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "role": role.name
    }

@router.get("/me", response_model=Dict[str, Any])
async def read_users_me(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user info
    """
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role.name,
        "is_active": current_user.is_active
    }

@router.post("/change-password", response_model=Dict[str, Any])
async def change_password(
    request: Request,
    password_data: Dict[str, str] = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Change user password
    """
    current_password = password_data.get("current_password")
    new_password = password_data.get("new_password")
    
    if not current_password or not new_password:
        raise HTTPException(status_code=400, detail="Current password and new password are required")
    
    # Verify current password
    user = await authenticate_user(db, current_user.email, current_password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect current password")
    
    # Update password
    current_user.hashed_password = get_password_hash(new_password)
    db.add(current_user)
    await db.commit()
    
    # Log password change
    log_entry = Log(
        user_id=current_user.id,
        action="change_password",
        endpoint="/api/auth/change-password",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        status_code=200,
        details=f"Password changed for user {current_user.username}"
    )
    db.add(log_entry)
    await db.commit()
    
    return {"message": "Password updated successfully"}