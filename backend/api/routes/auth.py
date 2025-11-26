# # api/routes/auth.py
# from fastapi import APIRouter, Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from sqlalchemy.orm import Session
# from typing import List
# from datetime import datetime, timedelta
# from jose import JWTError, jwt
# from backend.db.models import get_db, User, Role
# from backend.api.models.prediction import UserCreate, UserResponse, TokenResponse
# from backend.core.security import get_password_hash, verify_password
# from backend.config.settings import settings

# router = APIRouter()
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# def create_access_token(data: dict):
#     to_encode = data.copy()
#     expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
#     return encoded_jwt

# def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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
#     if user is None:
#         raise credentials_exception
#     return user

# def get_admin_user(current_user: User = Depends(get_current_user)):
#     if current_user.role.name != "admin":
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not enough permissions"
#         )
#     return current_user

# @router.post("/register", response_model=UserResponse)
# def register(user: UserCreate, db: Session = Depends(get_db)):
#     db_user = db.query(User).filter(User.username == user.username).first()
#     if db_user:
#         raise HTTPException(status_code=400, detail="Username already registered")
    
#     db_email = db.query(User).filter(User.email == user.email).first()
#     if db_email:
#         raise HTTPException(status_code=400, detail="Email already registered")
    
#     # Get default user role
#     role = db.query(Role).filter(Role.name == "user").first()
#     if not role:
#         role = Role(name="user", description="Regular user")
#         db.add(role)
#         db.commit()
#         db.refresh(role)
    
#     hashed_password = get_password_hash(user.password)
#     db_user = User(
#         username=user.username,
#         email=user.email,
#         hashed_password=hashed_password,
#         role_id=role.id
#     )
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
    
#     return db_user

# @router.post("/token", response_model=TokenResponse)
# def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.username == form_data.username).first()
#     if not user or not verify_password(form_data.password, user.hashed_password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
    
#     access_token = create_access_token(data={"sub": user.username})
#     return {"access_token": access_token, "token_type": "bearer"}

# @router.get("/me", response_model=UserResponse)
# def read_users_me(current_user: User = Depends(get_current_user)):
#     return current_user
# api/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.security.utils import get_authorization_scheme_param
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from backend.db.models import get_db, User, Role, Log
from backend.api.models.prediction import UserCreate, UserResponse, TokenResponse, PasswordResetRequest, PasswordReset
from backend.core.security import get_password_hash, verify_password
from backend.config.settings import settings
from backend.services.email import send_reset_password_email
import secrets
import time

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Class tùy chỉnh để xử lý authentication không bắt buộc
class OAuth2PasswordBearerOptional(OAuth2PasswordBearer):
    async def __call__(self, request: Request):
        authorization = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            return None
        return param

# Scheme tùy chọn cho authentication không bắt buộc
oauth2_scheme_optional = OAuth2PasswordBearerOptional(tokenUrl="/auth/token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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
        
    # Cập nhật thời gian đăng nhập cuối
    user.last_login = datetime.utcnow()
    db.commit()
    
    return user

def get_optional_current_user(token: Optional[str] = Depends(oauth2_scheme_optional), db: Session = Depends(get_db)):
    """Hàm xác thực không bắt buộc, trả về None nếu không xác thực được"""
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            return None
        return user
    except JWTError:
        return None

def get_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không đủ quyền truy cập. Yêu cầu quyền admin."
        )
    return current_user

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Kiểm tra username
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username đã được đăng ký")
    
    # Kiểm tra email
    db_email = db.query(User).filter(User.email == user.email).first()
    if db_email:
        raise HTTPException(status_code=400, detail="Email đã được đăng ký")
    
    # Lấy vai trò người dùng
    role = db.query(Role).filter(Role.name == "user").first()
    if not role:
        role = Role(name="user", description="Người dùng thông thường")
        db.add(role)
        db.commit()
        db.refresh(role)
    
    # Tạo người dùng mới
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        name=user.name or user.username,
        hashed_password=hashed_password,
        role_id=role.id,
        created_at=datetime.utcnow(),
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Tạo log
    log = Log(
        user_id=db_user.id,
        action="User registration",
        timestamp=datetime.utcnow()
    )
    db.add(log)
    db.commit()
    
    # Sử dụng utility function
    return prepare_user_response(db_user)

@router.post("/token", response_model=TokenResponse)
def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    # Kiểm tra đăng nhập
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không đúng",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Kiểm tra tài khoản bị khóa
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản đã bị khóa",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Lấy role name
    role_name = user.role.name if hasattr(user.role, 'name') else "user"
    
    # Tạo token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": role_name},
        expires_delta=access_token_expires
    )
    
    # Cập nhật thông tin đăng nhập
    user.last_login = datetime.utcnow()
    user.last_login_ip = request.client.host
    db.commit()
    
    # Tạo log
    log = Log(
        user_id=user.id,
        action="User login",
        timestamp=datetime.utcnow()
    )
    db.add(log)
    db.commit()
    
    # Trả về thông tin token
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "role": role_name,
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

from backend.utils.user_utils import prepare_user_response

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Lấy thông tin người dùng hiện tại
    """
    # Sử dụng utility function
    return prepare_user_response(current_user)

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Đăng xuất (chỉ tạo log server-side, client cần xóa token)
    """
    # Tạo log
    log = Log(
        user_id=current_user.id,
        action="User logout",
        timestamp=datetime.utcnow()
    )
    db.add(log)
    db.commit()
    
    return {"message": "Đăng xuất thành công"}

@router.post("/reset-password-request")
def request_password_reset(
    reset_request: PasswordResetRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Yêu cầu đặt lại mật khẩu
    """
    # Tìm user theo email
    user = db.query(User).filter(User.email == reset_request.email).first()
    if not user:
        # Không cho biết email không tồn tại vì lý do bảo mật
        return {"message": "Nếu email tồn tại, một email hướng dẫn đã được gửi"}
    
    # Tạo token reset
    reset_token = secrets.token_urlsafe(32)
    reset_token_expires = datetime.utcnow() + timedelta(hours=24)
    
    # Lưu thông tin reset token vào database
    user.reset_token = reset_token
    user.reset_token_expires = reset_token_expires
    db.commit()
    
    # Gửi email (ở background)
    background_tasks.add_task(
        send_reset_password_email,
        email=user.email,
        username=user.username,
        token=reset_token
    )
    
    # Tạo log
    log = Log(
        user_id=user.id,
        action="Password reset requested",
        timestamp=datetime.utcnow()
    )
    db.add(log)
    db.commit()
    
    return {"message": "Nếu email tồn tại, một email hướng dẫn đã được gửi"}

@router.post("/reset-password")
def reset_password(
    reset_data: PasswordReset,
    db: Session = Depends(get_db)
):
    """
    Đặt lại mật khẩu bằng token
    """
    # Tìm user có token reset hợp lệ
    user = db.query(User).filter(
        User.reset_token == reset_data.token,
        User.reset_token_expires > datetime.utcnow()
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token không hợp lệ hoặc đã hết hạn"
        )
    
    # Cập nhật mật khẩu
    user.hashed_password = get_password_hash(reset_data.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()
    
    # Tạo log
    log = Log(
        user_id=user.id,
        action="Password reset completed",
        timestamp=datetime.utcnow()
    )
    db.add(log)
    db.commit()
    
    return {"message": "Mật khẩu đã được đặt lại thành công"}

@router.post("/change-password")
def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Thay đổi mật khẩu (khi đã đăng nhập)
    """
    # Kiểm tra mật khẩu hiện tại
    if not verify_password(current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu hiện tại không đúng"
        )
    
    # Cập nhật mật khẩu mới
    current_user.hashed_password = get_password_hash(new_password)
    db.commit()
    
    # Tạo log
    log = Log(
        user_id=current_user.id,
        action="Password changed",
        timestamp=datetime.utcnow()
    )
    db.add(log)
    db.commit()
    
    return {"message": "Mật khẩu đã được thay đổi thành công"}

@router.get("/extension-auth")
def extension_auth(token: str, db: Session = Depends(get_db)):
    """
    Xác thực token từ extension
    """
    try:
        # Giải mã JWT token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token không hợp lệ")
        
        # Lấy thông tin user
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise HTTPException(status_code=401, detail="Người dùng không tồn tại")
        
        # Kiểm tra tài khoản bị khóa
        if not user.is_active:
            raise HTTPException(status_code=401, detail="Tài khoản đã bị khóa")
        
        # Trả về thông tin cơ bản cho extension
        return {
            "valid": True,
            "user_id": user.id,
            "username": user.username,
            "role": user.role.name
        }
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Token không hợp lệ hoặc đã hết hạn")