"""
Unit Tests for Cache Module

Tests caching decorators and utilities.
"""

import pytest
import time
from backend.core.cache import cached, cache_key, CacheManager


class TestCacheKey:
    """Test cache key generation"""
    
    def test_cache_key_simple(self):
        """Test simple cache key generation"""
        key1 = cache_key("arg1", "arg2")
        key2 = cache_key("arg1", "arg2")
        key3 = cache_key("arg2", "arg1")
        
        assert key1 == key2  # Same args = same key
        assert key1 != key3  # Different order = different key
    
    def test_cache_key_with_kwargs(self):
        """Test cache key with keyword arguments"""
        key1 = cache_key("arg1", param1="value1", param2="value2")
        key2 = cache_key("arg1", param2="value2", param1="value1")
        key3 = cache_key("arg1", param1="value1", param2="different")
        
        assert key1 == key2  # Order of kwargs doesn't matter
        assert key1 != key3  # Different values = different key


class TestCachedDecorator:
    """Test @cached decorator"""
    
    def test_cached_function(self):
        """Test basic caching functionality"""
        call_count = 0
        
        @cached(ttl=60)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call - should execute
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1
        
        # Second call - should use cache
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # Not incremented
        
        # Different argument - should execute
        result3 = expensive_function(10)
        assert result3 == 20
        assert call_count == 2
    
    def test_cache_expiry(self):
        """Test cache TTL"""
        call_count = 0
        
        @cached(ttl=1)  # 1 second TTL
        def short_ttl_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call
        result1 = short_ttl_function(5)
        assert result1 == 10
        assert call_count == 1
        
        # Immediate second call - cached
        result2 = short_ttl_function(5)
        assert result2 == 10
        assert call_count == 1
        
        # Wait for expiry
        time.sleep(1.5)
        
        # After expiry - should execute
        result3 = short_ttl_function(5)
        assert result3 == 10
        assert call_count == 2
    
    def test_cache_clear(self):
        """Test cache clearing"""
        call_count = 0
        
        @cached(ttl=60)
        def clearable_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # Call function
        result1 = clearable_function(5)
        assert call_count == 1
        
        # Call again - cached
        result2 = clearable_function(5)
        assert call_count == 1
        
        # Clear cache
        clearable_function.clear_cache()
        
        # Call again - should execute
        result3 = clearable_function(5)
        assert call_count == 2


class TestCacheManager:
    """Test CacheManager class"""
    
    def test_cache_manager_operations(self):
        """Test basic cache manager operations"""
        manager = CacheManager()
        
        # Set and get
        manager.set("test_key", {"data": "value"}, ttl=60)
        result = manager.get("test_key")
        assert result == {"data": "value"}
        
        # Exists
        assert manager.exists("test_key") == True
        assert manager.exists("nonexistent") == False
        
        # Delete
        manager.delete("test_key")
        assert manager.exists("test_key") == False
    
    def test_cache_manager_pattern_clear(self):
        """Test pattern-based cache clearing"""
        manager = CacheManager()
        
        # Set multiple keys
        manager.set("cache:user:1", "data1")
        manager.set("cache:user:2", "data2")
        manager.set("cache:post:1", "data3")
        
        # Clear user cache
        count = manager.clear_pattern("cache:user:*")
        assert count == 2
        
        # Verify
        assert manager.exists("cache:user:1") == False
        assert manager.exists("cache:user:2") == False
        assert manager.exists("cache:post:1") == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

