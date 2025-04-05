# api/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt

from db.models.base import get_db
from db.models.user import User
from db.models.role import Role
from api.models.auth import UserCreate, UserResponse, TokenResponse, UserLogin
from core.security import get_password_hash, verify_password
from core.config import settings

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={401: {"description": "Unauthorized"}},
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create JWT access token
    
    Args:
        data (dict): Data to encode in token
        expires_delta (Optional[timedelta], optional): Token expiration time
        
    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Get current authenticated user from JWT token
    
    Args:
        token (str): JWT token
        db (Session): Database session
        
    Returns:
        User: User object
        
    Raises:
        HTTPException: If credentials are invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.username == username).first()
    
    if user is None:
        raise credentials_exception
        
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)):
    """
    Get current active user
    
    Args:
        current_user (User): Current user
        
    Returns:
        User: Active user
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_admin_user(current_user: User = Depends(get_current_user)):
    """
    Get current admin user
    
    Args:
        current_user (User): Current user
        
    Returns:
        User: Admin user
        
    Raises:
        HTTPException: If user is not admin
    """
    if current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    return current_user

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    
    Args:
        user (UserCreate): User data
        db (Session): Database session
        
    Returns:
        UserResponse: Created user
        
    Raises:
        HTTPException: If username or email already exists
    """
    # Check if username exists
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Check if email exists
    db_email = db.query(User).filter(User.email == user.email).first()
    if db_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Get default user role
    role = db.query(Role).filter(Role.name == "user").first()
    if not role:
        role = Role(name="user", description="Regular user")
        db.add(role)
        db.commit()
        db.refresh(role)
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role_id=role.id,
        is_active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=TokenResponse)
async def login(form_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login user and get access token
    
    Args:
        form_data (UserLogin): Login credentials
        db (Session): Database session
        
    Returns:
        TokenResponse: Access token
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by username
    user = db.query(User).filter(User.username == form_data.username).first()
    
    # Verify user exists and password is correct
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.name}
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": user.role.name
    }

@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    OAuth2 compatible token login endpoint
    
    Args:
        form_data (OAuth2PasswordRequestForm): Login form
        db (Session): Database session
        
    Returns:
        TokenResponse: Access token
    """
    # Find user by username
    user = db.query(User).filter(User.username == form_data.username).first()
    
    # Verify user exists and password is correct
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.name}
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": user.role.name
    }

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Get current user profile
    
    Args:
        current_user (User): Current user
        
    Returns:
        UserResponse: User profile
    """
    return current_user

@router.post("/reset-password")
async def request_password_reset(email: str, db: Session = Depends(get_db)):
    """
    Request password reset
    
    Args:
        email (str): User email
        db (Session): Database session
        
    Returns:
        dict: Success message
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # Always return success to prevent email enumeration
        return {"message": "If your email is registered, you will receive password reset instructions"}
    
    # In a real implementation, you would:
    # 1. Generate a password reset token
    # 2. Send an email with reset link
    # 3. Store the token in the database with expiration
    
    return {"message": "If your email is registered, you will receive password reset instructions"}