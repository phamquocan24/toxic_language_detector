"""
Improved Rate Limiter with Redis support

This module provides rate limiting functionality that uses Redis when available,
falling back to in-memory storage. Backward compatible with existing code.
"""

import time
import logging
from typing import Optional, Dict
from fastapi import Request, HTTPException, status

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate limiter with Redis support and in-memory fallback
    """
    
    def __init__(
        self,
        requests: int = 100,
        period: int = 60,
        enabled: bool = True
    ):
        """
        Initialize rate limiter
        
        Args:
            requests: Maximum requests allowed
            period: Time period in seconds
            enabled: Whether rate limiting is enabled
        """
        self.requests = requests
        self.period = period
        self.enabled = enabled
        self._memory_store: Dict[str, list] = {}
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def _check_rate_limit_redis(self, client_id: str) -> tuple[bool, Optional[int]]:
        """
        Check rate limit using Redis
        
        Returns:
            (is_allowed, retry_after)
        """
        from backend.services.redis_service import get_redis_service
        
        redis = get_redis_service()
        key = f"rate_limit:{client_id}"
        
        try:
            # Get current request count
            current = redis.get(key)
            
            if current is None:
                # First request in this period
                redis.set(key, "1", ex=self.period)
                return True, None
            
            count = int(current)
            
            if count >= self.requests:
                # Rate limit exceeded
                ttl = redis.ttl(key)
                return False, max(ttl, 1)
            
            # Increment counter
            redis.incr(key)
            return True, None
            
        except Exception as e:
            logger.error(f"Redis rate limit check failed: {e}")
            # Fallback to memory
            return self._check_rate_limit_memory(client_id)
    
    def _check_rate_limit_memory(self, client_id: str) -> tuple[bool, Optional[int]]:
        """
        Check rate limit using in-memory storage
        
        Returns:
            (is_allowed, retry_after)
        """
        current_time = time.time()
        
        if client_id not in self._memory_store:
            self._memory_store[client_id] = []
        
        # Remove old timestamps outside the period
        self._memory_store[client_id] = [
            ts for ts in self._memory_store[client_id]
            if current_time - ts < self.period
        ]
        
        if len(self._memory_store[client_id]) >= self.requests:
            # Rate limit exceeded
            oldest_timestamp = min(self._memory_store[client_id])
            retry_after = int(self.period - (current_time - oldest_timestamp)) + 1
            return False, retry_after
        
        # Add current timestamp
        self._memory_store[client_id].append(current_time)
        return True, None
    
    def check_rate_limit(self, request: Request) -> tuple[bool, Optional[int]]:
        """
        Check if request is within rate limit
        
        Args:
            request: FastAPI request object
            
        Returns:
            (is_allowed, retry_after)
        """
        if not self.enabled:
            return True, None
        
        client_id = self._get_client_ip(request)
        
        # Try Redis first
        from backend.services.redis_service import get_redis_service
        redis = get_redis_service()
        
        if redis.enabled:
            return self._check_rate_limit_redis(client_id)
        else:
            return self._check_rate_limit_memory(client_id)
    
    async def __call__(self, request: Request):
        """
        FastAPI dependency for rate limiting
        
        Usage:
            @app.get("/endpoint")
            async def endpoint(rate_limiter: RateLimiter = Depends()):
                ...
        """
        is_allowed, retry_after = self.check_rate_limit(request)
        
        if not is_allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many requests. Please try again in {retry_after} seconds.",
                headers={"Retry-After": str(retry_after)}
            )


class IPRateLimiter:
    """
    IP-based rate limiter with customizable limits
    """
    
    def __init__(self):
        self._limiters: Dict[str, RateLimiter] = {}
    
    def get_limiter(
        self,
        requests: int = 100,
        period: int = 60,
        enabled: bool = True
    ) -> RateLimiter:
        """Get or create a rate limiter with specific settings"""
        key = f"{requests}:{period}:{enabled}"
        
        if key not in self._limiters:
            self._limiters[key] = RateLimiter(
                requests=requests,
                period=period,
                enabled=enabled
            )
        
        return self._limiters[key]
    
    def limit(
        self,
        requests: int = 100,
        period: int = 60
    ):
        """
        Decorator for rate limiting specific endpoints
        
        Usage:
            ip_limiter = IPRateLimiter()
            
            @app.get("/endpoint")
            @ip_limiter.limit(requests=10, period=60)
            async def endpoint():
                ...
        """
        def decorator(func):
            async def wrapper(*args, **kwargs):
                from fastapi import Request
                
                # Find request in args or kwargs
                request = None
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
                
                if request is None:
                    request = kwargs.get('request')
                
                if request:
                    limiter = self.get_limiter(requests, period)
                    await limiter(request)
                
                return await func(*args, **kwargs)
            
            return wrapper
        return decorator


# Global rate limiter instance
_global_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance"""
    global _global_limiter
    
    if _global_limiter is None:
        from backend.config.settings import settings
        _global_limiter = RateLimiter(
            requests=settings.RATE_LIMIT_REQUESTS,
            period=settings.RATE_LIMIT_PERIOD,
            enabled=settings.RATE_LIMIT_ENABLED
        )
    
    return _global_limiter


def reset_rate_limiter():
    """Reset global rate limiter (for testing)"""
    global _global_limiter
    _global_limiter = None


# Convenience function for FastAPI dependency
async def rate_limit_dependency(request: Request):
    """
    FastAPI dependency for rate limiting
    
    Usage:
        @app.get("/endpoint")
        async def endpoint(_: None = Depends(rate_limit_dependency)):
            ...
    """
    limiter = get_rate_limiter()
    await limiter(request)
