"""
Unit Tests for Redis Service

Tests the Redis service with in-memory fallback.
"""

import pytest
from backend.services.redis_service import RedisService, get_redis_service, reset_redis_service


class TestRedisService:
    """Test Redis service functionality"""
    
    def test_redis_service_disabled(self):
        """Test Redis service when disabled"""
        redis = RedisService(redis_url=None, enabled=False)
        
        assert redis.enabled == False
        assert redis.redis_client is None
        
        # Should use in-memory fallback
        redis.set("test_key", "test_value", ex=60)
        value = redis.get("test_key")
        assert value == "test_value"
    
    def test_set_get(self):
        """Test set and get operations"""
        redis = RedisService(redis_url=None, enabled=False)
        
        redis.set("key1", "value1")
        assert redis.get("key1") == "value1"
        
        redis.set("key2", "value2", ex=60)
        assert redis.get("key2") == "value2"
    
    def test_delete(self):
        """Test delete operation"""
        redis = RedisService(redis_url=None, enabled=False)
        
        redis.set("key_to_delete", "value")
        assert redis.get("key_to_delete") == "value"
        
        redis.delete("key_to_delete")
        assert redis.get("key_to_delete") is None
    
    def test_exists(self):
        """Test exists check"""
        redis = RedisService(redis_url=None, enabled=False)
        
        assert redis.exists("nonexistent") == False
        
        redis.set("existing_key", "value")
        assert redis.exists("existing_key") == True
    
    def test_incr(self):
        """Test increment operation"""
        redis = RedisService(redis_url=None, enabled=False)
        
        redis.set("counter", "0")
        assert redis.incr("counter") == 1
        assert redis.incr("counter") == 2
        assert redis.incr("counter", amount=5) == 7
    
    def test_expire_ttl(self):
        """Test expire and TTL operations"""
        redis = RedisService(redis_url=None, enabled=False)
        
        redis.set("expiring_key", "value")
        redis.expire("expiring_key", 60)
        
        ttl = redis.ttl("expiring_key")
        assert ttl > 0 and ttl <= 60
    
    def test_json_operations(self):
        """Test JSON get/set operations"""
        redis = RedisService(redis_url=None, enabled=False)
        
        data = {"name": "Test", "value": 123, "items": [1, 2, 3]}
        
        redis.set_json("json_key", data, ex=60)
        retrieved = redis.get_json("json_key")
        
        assert retrieved == data
    
    def test_clear_pattern(self):
        """Test pattern-based clearing"""
        redis = RedisService(redis_url=None, enabled=False)
        
        redis.set("user:1:profile", "data1")
        redis.set("user:2:profile", "data2")
        redis.set("user:1:settings", "data3")
        redis.set("other:key", "data4")
        
        count = redis.clear_pattern("user:*:profile")
        assert count == 2
        
        assert redis.get("user:1:profile") is None
        assert redis.get("user:2:profile") is None
        assert redis.get("user:1:settings") == "data3"
        assert redis.get("other:key") == "data4"
    
    def test_health_check(self):
        """Test health check"""
        redis = RedisService(redis_url=None, enabled=False)
        
        health = redis.health_check()
        assert health["status"] == "disabled"
        assert health["type"] == "in-memory"
    
    def test_singleton(self):
        """Test singleton pattern"""
        reset_redis_service()
        
        redis1 = get_redis_service()
        redis2 = get_redis_service()
        
        assert redis1 is redis2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

