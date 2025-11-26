"""
Token Management with Rotation Support

Provides JWT token management with automatic rotation, refresh tokens,
and blacklisting support.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class TokenManager:
    """
    Advanced token manager with rotation and blacklist support
    """
    
    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 60,
        refresh_token_expire_days: int = 30
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
    
    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT access token
        
        Args:
            data: Data to encode in token
            expires_delta: Custom expiration time
            
        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.access_token_expire_minutes
            )
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(
            to_encode,
            self.secret_key,
            algorithm=self.algorithm
        )
        
        return encoded_jwt
    
    def create_refresh_token(
        self,
        user_id: int,
        db: Session
    ) -> str:
        """
        Create refresh token and store in database
        
        Args:
            user_id: User ID
            db: Database session
            
        Returns:
            Refresh token string
        """
        from backend.db.models.user import RefreshToken
        import secrets
        
        # Generate random token
        token = secrets.token_urlsafe(32)
        
        # Calculate expiry
        expires_at = datetime.utcnow() + timedelta(
            days=self.refresh_token_expire_days
        )
        
        # Store in database
        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        
        db.add(refresh_token)
        db.commit()
        
        logger.info(f"Created refresh token for user {user_id}")
        
        return token
    
    def verify_access_token(
        self,
        token: str
    ) -> Optional[Dict[str, Any]]:
        """
        Verify and decode access token
        
        Args:
            token: JWT token to verify
            
        Returns:
            Decoded token data or None if invalid
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            
            # Check token type
            if payload.get("type") != "access":
                logger.warning("Invalid token type")
                return None
            
            # Check if blacklisted
            if self._is_token_blacklisted(token):
                logger.warning("Token is blacklisted")
                return None
            
            return payload
            
        except JWTError as e:
            logger.error(f"Token verification failed: {e}")
            return None
    
    def verify_refresh_token(
        self,
        token: str,
        db: Session
    ) -> Optional[int]:
        """
        Verify refresh token and return user_id
        
        Args:
            token: Refresh token
            db: Database session
            
        Returns:
            User ID if valid, None otherwise
        """
        from backend.db.models.user import RefreshToken
        
        # Query token from database
        refresh_token = db.query(RefreshToken).filter(
            RefreshToken.token == token,
            RefreshToken.revoked == False
        ).first()
        
        if not refresh_token:
            logger.warning("Refresh token not found or revoked")
            return None
        
        # Check expiry
        if refresh_token.expires_at < datetime.utcnow():
            logger.warning("Refresh token expired")
            # Clean up expired token
            db.delete(refresh_token)
            db.commit()
            return None
        
        return refresh_token.user_id
    
    def rotate_tokens(
        self,
        refresh_token: str,
        db: Session
    ) -> Optional[Dict[str, str]]:
        """
        Rotate access and refresh tokens
        
        Args:
            refresh_token: Current refresh token
            db: Database session
            
        Returns:
            New tokens dict or None if invalid
        """
        from backend.db.models.user import User, RefreshToken as RefreshTokenModel
        
        # Verify refresh token
        user_id = self.verify_refresh_token(refresh_token, db)
        
        if not user_id:
            return None
        
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or not user.is_active:
            return None
        
        # Revoke old refresh token
        old_token = db.query(RefreshTokenModel).filter(
            RefreshTokenModel.token == refresh_token
        ).first()
        
        if old_token:
            old_token.revoked = True
            old_token.revoked_at = datetime.utcnow()
            db.commit()
        
        # Create new tokens
        access_token = self.create_access_token(
            data={
                "sub": user.username,
                "role": user.role.name if user.role else "user"
            }
        )
        
        new_refresh_token = self.create_refresh_token(user_id, db)
        
        logger.info(f"Rotated tokens for user {user_id}")
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
    
    def revoke_refresh_token(
        self,
        token: str,
        db: Session
    ) -> bool:
        """
        Revoke a refresh token
        
        Args:
            token: Refresh token to revoke
            db: Database session
            
        Returns:
            True if revoked, False otherwise
        """
        from backend.db.models.user import RefreshToken
        
        refresh_token = db.query(RefreshToken).filter(
            RefreshToken.token == token
        ).first()
        
        if refresh_token:
            refresh_token.revoked = True
            refresh_token.revoked_at = datetime.utcnow()
            db.commit()
            logger.info(f"Revoked refresh token for user {refresh_token.user_id}")
            return True
        
        return False
    
    def revoke_all_user_tokens(
        self,
        user_id: int,
        db: Session
    ) -> int:
        """
        Revoke all refresh tokens for a user
        
        Args:
            user_id: User ID
            db: Database session
            
        Returns:
            Number of tokens revoked
        """
        from backend.db.models.user import RefreshToken
        
        tokens = db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked == False
        ).all()
        
        count = 0
        for token in tokens:
            token.revoked = True
            token.revoked_at = datetime.utcnow()
            count += 1
        
        db.commit()
        logger.info(f"Revoked {count} tokens for user {user_id}")
        
        return count
    
    def cleanup_expired_tokens(self, db: Session) -> int:
        """
        Clean up expired refresh tokens
        
        Args:
            db: Database session
            
        Returns:
            Number of tokens deleted
        """
        from backend.db.models.user import RefreshToken
        
        expired_tokens = db.query(RefreshToken).filter(
            RefreshToken.expires_at < datetime.utcnow()
        ).all()
        
        count = len(expired_tokens)
        for token in expired_tokens:
            db.delete(token)
        
        db.commit()
        logger.info(f"Cleaned up {count} expired refresh tokens")
        
        return count
    
    def _is_token_blacklisted(self, token: str) -> bool:
        """
        Check if token is blacklisted (Redis-based)
        
        Args:
            token: JWT token
            
        Returns:
            True if blacklisted, False otherwise
        """
        from backend.services.redis_service import get_redis_service
        
        try:
            redis = get_redis_service()
            key = f"blacklist:token:{token}"
            return redis.exists(key)
        except Exception as e:
            logger.error(f"Blacklist check failed: {e}")
            return False
    
    def blacklist_token(
        self,
        token: str,
        expires_in: int = 3600
    ) -> bool:
        """
        Add token to blacklist
        
        Args:
            token: JWT token to blacklist
            expires_in: TTL in seconds
            
        Returns:
            True if blacklisted, False otherwise
        """
        from backend.services.redis_service import get_redis_service
        
        try:
            redis = get_redis_service()
            key = f"blacklist:token:{token}"
            redis.set(key, "1", ex=expires_in)
            logger.info("Token blacklisted")
            return True
        except Exception as e:
            logger.error(f"Token blacklist failed: {e}")
            return False


# Global token manager instance
_token_manager: Optional[TokenManager] = None


def get_token_manager() -> TokenManager:
    """Get token manager singleton"""
    global _token_manager
    
    if _token_manager is None:
        from backend.config.settings import settings
        _token_manager = TokenManager(
            secret_key=settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
            access_token_expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            refresh_token_expire_days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    
    return _token_manager


def reset_token_manager():
    """Reset singleton (for testing)"""
    global _token_manager
    _token_manager = None

