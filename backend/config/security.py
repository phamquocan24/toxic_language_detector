import secrets
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from jose.exceptions import JWTError

from backend.config.settings import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 configuration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# Token blacklist (for logged out tokens)
token_blacklist = set()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify that a plain password matches a hashed password
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt
    """
    return pwd_context.hash(password)

def create_access_token(
    data: Dict[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt

def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT token
    """
    try:
        # Check if token is blacklisted
        if token in token_blacklist:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Decode token
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        # Check expiration
        if "exp" in payload and datetime.fromtimestamp(payload["exp"]) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

def revoke_token(token: str) -> None:
    """
    Add a token to the blacklist (for logout)
    """
    token_blacklist.add(token)

def generate_api_key() -> str:
    """
    Generate a secure API key
    """
    return secrets.token_urlsafe(32)

def validate_api_key(api_key: str, valid_keys: List[str]) -> bool:
    """
    Validate an API key against a list of valid keys
    """
    return api_key in valid_keys

def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent XSS and other injection attacks
    """
    # Replace potentially dangerous characters
    sanitized = text
    sanitized = sanitized.replace("<", "&lt;")
    sanitized = sanitized.replace(">", "&gt;")
    sanitized = sanitized.replace("&", "&amp;")
    sanitized = sanitized.replace("\"", "&quot;")
    sanitized = sanitized.replace("'", "&#x27;")
    sanitized = sanitized.replace("/", "&#x2F;")
    
    return sanitized

def validate_email(email: str) -> bool:
    """
    Validate email format
    """
    import re
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email))

def validate_password_strength(password: str) -> Dict[str, Any]:
    """
    Validate password strength
    """
    min_length = 8
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    
    is_valid = (
        len(password) >= min_length and
        has_upper and
        has_lower and
        has_digit and
        has_special
    )
    
    return {
        "is_valid": is_valid,
        "length": len(password) >= min_length,
        "has_uppercase": has_upper,
        "has_lowercase": has_lower,
        "has_digit": has_digit,
        "has_special": has_special
    }

def rate_limit_check(
    ip_address: str, 
    endpoint: str, 
    max_requests: int = 100, 
    time_window: int = 3600
) -> bool:
    """
    Basic rate limiting function (implementation would need to use Redis or similar)
    """
    # This is a placeholder implementation
    # In production, use Redis or another caching system
    return True