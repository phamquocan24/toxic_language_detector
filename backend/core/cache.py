"""
Caching decorators and utilities

Provides easy-to-use caching decorators that work with Redis or in-memory fallback.
"""

import functools
import hashlib
import json
import logging
from typing import Optional, Callable, Any

logger = logging.getLogger(__name__)


def cache_key(*args, **kwargs) -> str:
    """
    Generate cache key from function arguments
    
    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        Cache key string
    """
    # Create a deterministic string from args and kwargs
    key_data = {
        'args': [str(arg) for arg in args],
        'kwargs': {k: str(v) for k, v in sorted(kwargs.items())}
    }
    key_str = json.dumps(key_data, sort_keys=True)
    # Hash it to keep key short
    return hashlib.md5(key_str.encode()).hexdigest()


def cached(
    ttl: int = 300,
    key_prefix: Optional[str] = None,
    key_builder: Optional[Callable] = None
):
    """
    Cache decorator for functions
    
    Args:
        ttl: Time to live in seconds (default: 5 minutes)
        key_prefix: Prefix for cache key (default: function name)
        key_builder: Custom key builder function
        
    Usage:
        @cached(ttl=600)
        def expensive_function(param1, param2):
            # ... expensive computation
            return result
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            from backend.services.redis_service import get_redis_service
            
            redis = get_redis_service()
            
            # Build cache key
            prefix = key_prefix or f"cache:{func.__module__}.{func.__name__}"
            if key_builder:
                key_suffix = key_builder(*args, **kwargs)
            else:
                key_suffix = cache_key(*args, **kwargs)
            
            full_key = f"{prefix}:{key_suffix}"
            
            # Try to get from cache
            cached_value = redis.get_json(full_key)
            if cached_value is not None:
                logger.debug(f"Cache HIT: {full_key}")
                return cached_value
            
            # Cache miss - execute function
            logger.debug(f"Cache MISS: {full_key}")
            result = func(*args, **kwargs)
            
            # Store in cache
            redis.set_json(full_key, result, ex=ttl)
            
            return result
        
        # Add cache management methods
        wrapper.clear_cache = lambda: clear_function_cache(func, key_prefix)
        wrapper.cache_key = lambda *args, **kwargs: (
            f"{key_prefix or func.__name__}:{cache_key(*args, **kwargs)}"
        )
        
        return wrapper
    return decorator


def clear_function_cache(func: Callable, key_prefix: Optional[str] = None):
    """Clear all cached values for a function"""
    from backend.services.redis_service import get_redis_service
    
    redis = get_redis_service()
    prefix = key_prefix or f"cache:{func.__module__}.{func.__name__}"
    pattern = f"{prefix}:*"
    
    count = redis.clear_pattern(pattern)
    logger.info(f"Cleared {count} cached values for {func.__name__}")
    return count


def invalidate_cache(pattern: str):
    """
    Invalidate cache by pattern
    
    Args:
        pattern: Cache key pattern (e.g., "cache:dashboard:*")
    """
    from backend.services.redis_service import get_redis_service
    
    redis = get_redis_service()
    count = redis.clear_pattern(pattern)
    logger.info(f"Invalidated {count} cache entries matching '{pattern}'")
    return count


class CacheManager:
    """Cache manager for manual cache operations"""
    
    def __init__(self):
        from backend.services.redis_service import get_redis_service
        self.redis = get_redis_service()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache"""
        value = self.redis.get_json(key)
        return value if value is not None else default
    
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache"""
        return self.redis.set_json(key, value, ex=ttl)
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        return self.redis.delete(key)
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        return self.redis.exists(key)
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        return self.redis.clear_pattern(pattern)
    
    def clear_all(self):
        """Clear all cache (use with caution!)"""
        return self.clear_pattern("cache:*")


# Global cache manager instance
cache_manager = CacheManager()


# Convenience functions
def get_cache(key: str, default: Any = None) -> Any:
    """Get value from cache"""
    return cache_manager.get(key, default)


def set_cache(key: str, value: Any, ttl: int = 300) -> bool:
    """Set value in cache"""
    return cache_manager.set(key, value, ttl)


def delete_cache(key: str) -> bool:
    """Delete key from cache"""
    return cache_manager.delete(key)


def clear_cache(pattern: str = "cache:*") -> int:
    """Clear cache by pattern"""
    return cache_manager.clear_pattern(pattern)

