"""
Redis Service for Caching and Rate Limiting

This service provides Redis integration that can be enabled/disabled via config.
Falls back to in-memory storage if Redis is not available.
"""

import json
import logging
from typing import Optional, Any, Dict
from datetime import timedelta

logger = logging.getLogger(__name__)


class RedisService:
    """
    Redis service with automatic fallback to in-memory storage.
    Maintains backward compatibility with existing code.
    """
    
    def __init__(self, redis_url: Optional[str] = None, enabled: bool = True):
        self.enabled = enabled and redis_url is not None
        self.redis_client = None
        self._memory_store: Dict[str, Any] = {}
        self._memory_expiry: Dict[str, float] = {}
        
        if self.enabled:
            try:
                import redis
                self.redis_client = redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
                # Test connection
                self.redis_client.ping()
                logger.info("✅ Redis connected successfully")
            except ImportError:
                logger.warning("⚠️ redis-py not installed. Install with: pip install redis")
                self.enabled = False
            except Exception as e:
                logger.warning(f"⚠️ Redis connection failed: {e}. Using in-memory fallback.")
                self.enabled = False
    
    def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        if self.enabled and self.redis_client:
            try:
                return self.redis_client.get(key)
            except Exception as e:
                logger.error(f"Redis GET error: {e}")
                return self._memory_store.get(key)
        else:
            # In-memory fallback
            import time
            if key in self._memory_expiry:
                if time.time() > self._memory_expiry[key]:
                    # Expired
                    self._memory_store.pop(key, None)
                    self._memory_expiry.pop(key, None)
                    return None
            return self._memory_store.get(key)
    
    def set(
        self, 
        key: str, 
        value: str, 
        ex: Optional[int] = None,
        px: Optional[int] = None
    ) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to store
            ex: Expiry in seconds
            px: Expiry in milliseconds
        """
        if self.enabled and self.redis_client:
            try:
                return self.redis_client.set(key, value, ex=ex, px=px)
            except Exception as e:
                logger.error(f"Redis SET error: {e}")
                # Fallback to memory
                self._set_memory(key, value, ex, px)
                return True
        else:
            # In-memory fallback
            self._set_memory(key, value, ex, px)
            return True
    
    def _set_memory(
        self, 
        key: str, 
        value: str, 
        ex: Optional[int] = None,
        px: Optional[int] = None
    ):
        """Set value in memory store with expiry"""
        import time
        self._memory_store[key] = value
        if ex:
            self._memory_expiry[key] = time.time() + ex
        elif px:
            self._memory_expiry[key] = time.time() + (px / 1000)
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if self.enabled and self.redis_client:
            try:
                return bool(self.redis_client.delete(key))
            except Exception as e:
                logger.error(f"Redis DELETE error: {e}")
                self._memory_store.pop(key, None)
                self._memory_expiry.pop(key, None)
                return True
        else:
            self._memory_store.pop(key, None)
            self._memory_expiry.pop(key, None)
            return True
    
    def incr(self, key: str, amount: int = 1) -> int:
        """Increment value"""
        if self.enabled and self.redis_client:
            try:
                return self.redis_client.incr(key, amount)
            except Exception as e:
                logger.error(f"Redis INCR error: {e}")
                current = int(self._memory_store.get(key, 0))
                new_value = current + amount
                self._memory_store[key] = str(new_value)
                return new_value
        else:
            current = int(self._memory_store.get(key, 0))
            new_value = current + amount
            self._memory_store[key] = str(new_value)
            return new_value
    
    def expire(self, key: str, seconds: int) -> bool:
        """Set expiry on key"""
        if self.enabled and self.redis_client:
            try:
                return self.redis_client.expire(key, seconds)
            except Exception as e:
                logger.error(f"Redis EXPIRE error: {e}")
                import time
                self._memory_expiry[key] = time.time() + seconds
                return True
        else:
            import time
            self._memory_expiry[key] = time.time() + seconds
            return True
    
    def ttl(self, key: str) -> int:
        """Get time to live for key"""
        if self.enabled and self.redis_client:
            try:
                return self.redis_client.ttl(key)
            except Exception as e:
                logger.error(f"Redis TTL error: {e}")
                import time
                if key in self._memory_expiry:
                    remaining = self._memory_expiry[key] - time.time()
                    return int(max(0, remaining))
                return -1
        else:
            import time
            if key in self._memory_expiry:
                remaining = self._memory_expiry[key] - time.time()
                return int(max(0, remaining))
            return -1
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        if self.enabled and self.redis_client:
            try:
                return bool(self.redis_client.exists(key))
            except Exception as e:
                logger.error(f"Redis EXISTS error: {e}")
                return key in self._memory_store
        else:
            return key in self._memory_store
    
    def get_json(self, key: str) -> Optional[Any]:
        """Get JSON value from cache"""
        value = self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return None
    
    def set_json(
        self, 
        key: str, 
        value: Any, 
        ex: Optional[int] = None
    ) -> bool:
        """Set JSON value in cache"""
        try:
            json_str = json.dumps(value)
            return self.set(key, json_str, ex=ex)
        except (TypeError, ValueError) as e:
            logger.error(f"JSON serialization error: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        if self.enabled and self.redis_client:
            try:
                keys = self.redis_client.keys(pattern)
                if keys:
                    return self.redis_client.delete(*keys)
                return 0
            except Exception as e:
                logger.error(f"Redis CLEAR error: {e}")
                return 0
        else:
            # In-memory: simple pattern matching
            import fnmatch
            count = 0
            keys_to_delete = [
                k for k in self._memory_store.keys() 
                if fnmatch.fnmatch(k, pattern)
            ]
            for key in keys_to_delete:
                self._memory_store.pop(key, None)
                self._memory_expiry.pop(key, None)
                count += 1
            return count
    
    def health_check(self) -> dict:
        """Check Redis health"""
        if self.enabled and self.redis_client:
            try:
                self.redis_client.ping()
                info = self.redis_client.info('server')
                return {
                    "status": "healthy",
                    "type": "redis",
                    "version": info.get('redis_version', 'unknown'),
                    "used_memory": info.get('used_memory_human', 'unknown')
                }
            except Exception as e:
                return {
                    "status": "unhealthy",
                    "type": "redis",
                    "error": str(e)
                }
        else:
            return {
                "status": "disabled",
                "type": "in-memory",
                "keys": len(self._memory_store)
            }


# Singleton instance
_redis_service: Optional[RedisService] = None


def get_redis_service() -> RedisService:
    """Get Redis service singleton"""
    global _redis_service
    if _redis_service is None:
        from backend.config.settings import settings
        _redis_service = RedisService(
            redis_url=settings.REDIS_URL,
            enabled=settings.REDIS_ENABLED
        )
    return _redis_service


def reset_redis_service():
    """Reset singleton (for testing)"""
    global _redis_service
    _redis_service = None

