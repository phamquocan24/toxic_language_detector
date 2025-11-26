"""
Unit Tests for Rate Limiter

Tests rate limiting functionality.
"""

import pytest
import time
from unittest.mock import Mock
from backend.core.rate_limiter import RateLimiter


class TestRateLimiter:
    """Test rate limiter"""
    
    def test_rate_limiter_allows_requests(self):
        """Test rate limiter allows requests within limit"""
        limiter = RateLimiter(requests=5, period=60, enabled=True)
        
        request = Mock()
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.headers = {}
        
        # Should allow first 5 requests
        for i in range(5):
            is_allowed, retry_after = limiter.check_rate_limit(request)
            assert is_allowed == True
            assert retry_after is None
    
    def test_rate_limiter_blocks_excess_requests(self):
        """Test rate limiter blocks requests over limit"""
        limiter = RateLimiter(requests=3, period=60, enabled=True)
        
        request = Mock()
        request.client = Mock()
        request.client.host = "192.168.1.1"
        request.headers = {}
        
        # Allow first 3 requests
        for i in range(3):
            is_allowed, _ = limiter.check_rate_limit(request)
            assert is_allowed == True
        
        # Block 4th request
        is_allowed, retry_after = limiter.check_rate_limit(request)
        assert is_allowed == False
        assert retry_after is not None
        assert retry_after > 0
    
    def test_rate_limiter_disabled(self):
        """Test rate limiter when disabled"""
        limiter = RateLimiter(requests=1, period=60, enabled=False)
        
        request = Mock()
        request.client = Mock()
        request.client.host = "10.0.0.1"
        request.headers = {}
        
        # Should allow unlimited requests
        for i in range(100):
            is_allowed, retry_after = limiter.check_rate_limit(request)
            assert is_allowed == True
            assert retry_after is None
    
    def test_rate_limiter_different_ips(self):
        """Test rate limiter tracks different IPs separately"""
        limiter = RateLimiter(requests=2, period=60, enabled=True)
        
        request1 = Mock()
        request1.client = Mock()
        request1.client.host = "1.1.1.1"
        request1.headers = {}
        
        request2 = Mock()
        request2.client = Mock()
        request2.client.host = "2.2.2.2"
        request2.headers = {}
        
        # IP 1: Use both requests
        limiter.check_rate_limit(request1)
        limiter.check_rate_limit(request1)
        is_allowed, _ = limiter.check_rate_limit(request1)
        assert is_allowed == False  # 3rd request blocked
        
        # IP 2: Should still be allowed
        is_allowed, _ = limiter.check_rate_limit(request2)
        assert is_allowed == True
    
    def test_rate_limiter_period_expiry(self):
        """Test rate limiter resets after period"""
        limiter = RateLimiter(requests=2, period=1, enabled=True)
        
        request = Mock()
        request.client = Mock()
        request.client.host = "3.3.3.3"
        request.headers = {}
        
        # Use up limit
        limiter.check_rate_limit(request)
        limiter.check_rate_limit(request)
        is_allowed, _ = limiter.check_rate_limit(request)
        assert is_allowed == False
        
        # Wait for period to expire
        time.sleep(1.5)
        
        # Should be allowed again
        is_allowed, _ = limiter.check_rate_limit(request)
        assert is_allowed == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

