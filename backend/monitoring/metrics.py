"""
Prometheus Metrics Integration

Provides comprehensive application monitoring with Prometheus.
Can be enabled/disabled via configuration without affecting the application.
"""

import time
import logging
from typing import Optional, Callable
from functools import wraps

logger = logging.getLogger(__name__)

# Try to import prometheus_client, but don't fail if not installed
try:
    from prometheus_client import (
        Counter, Histogram, Gauge, Info,
        generate_latest, CONTENT_TYPE_LATEST,
        CollectorRegistry, REGISTRY
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    logger.warning("prometheus_client not installed. Metrics collection disabled.")
    PROMETHEUS_AVAILABLE = False
    # Create dummy classes
    class Counter:
        def __init__(self, *args, **kwargs): pass
        def inc(self, *args, **kwargs): pass
        def labels(self, *args, **kwargs): return self
    
    class Histogram:
        def __init__(self, *args, **kwargs): pass
        def observe(self, *args, **kwargs): pass
        def labels(self, *args, **kwargs): return self
        def time(self): return DummyTimer()
    
    class Gauge:
        def __init__(self, *args, **kwargs): pass
        def set(self, *args, **kwargs): pass
        def inc(self, *args, **kwargs): pass
        def dec(self, *args, **kwargs): pass
        def labels(self, *args, **kwargs): return self
    
    class Info:
        def __init__(self, *args, **kwargs): pass
        def info(self, *args, **kwargs): pass
    
    class DummyTimer:
        def __enter__(self): return self
        def __exit__(self, *args): pass
    
    def generate_latest(): return b""
    CONTENT_TYPE_LATEST = "text/plain"


class MetricsCollector:
    """
    Central metrics collector for the application
    """
    
    def __init__(self, enabled: bool = True, prefix: str = "toxic_detector"):
        """
        Initialize metrics collector
        
        Args:
            enabled: Whether metrics collection is enabled
            prefix: Prefix for all metrics
        """
        self.enabled = enabled and PROMETHEUS_AVAILABLE
        self.prefix = prefix
        
        if not self.enabled:
            logger.info("Metrics collection is disabled")
            return
        
        logger.info("Initializing Prometheus metrics...")
        
        # Application info
        self.app_info = Info(
            f'{prefix}_app',
            'Application information'
        )
        
        # HTTP metrics
        self.http_requests_total = Counter(
            f'{prefix}_http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status']
        )
        
        self.http_request_duration_seconds = Histogram(
            f'{prefix}_http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint'],
            buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
        )
        
        self.http_requests_in_progress = Gauge(
            f'{prefix}_http_requests_in_progress',
            'HTTP requests currently in progress',
            ['method', 'endpoint']
        )
        
        # ML Model metrics
        self.ml_predictions_total = Counter(
            f'{prefix}_ml_predictions_total',
            'Total ML predictions',
            ['model_type', 'category']
        )
        
        self.ml_prediction_duration_seconds = Histogram(
            f'{prefix}_ml_prediction_duration_seconds',
            'ML prediction duration in seconds',
            ['model_type'],
            buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
        )
        
        self.ml_prediction_confidence = Histogram(
            f'{prefix}_ml_prediction_confidence',
            'ML prediction confidence scores',
            ['model_type', 'category'],
            buckets=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)
        )
        
        self.ml_model_loaded = Gauge(
            f'{prefix}_ml_model_loaded',
            'Whether ML model is loaded (1=loaded, 0=not loaded)',
            ['model_type']
        )
        
        # Database metrics
        self.db_queries_total = Counter(
            f'{prefix}_db_queries_total',
            'Total database queries',
            ['operation', 'table']
        )
        
        self.db_query_duration_seconds = Histogram(
            f'{prefix}_db_query_duration_seconds',
            'Database query duration in seconds',
            ['operation', 'table'],
            buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0)
        )
        
        self.db_connections_active = Gauge(
            f'{prefix}_db_connections_active',
            'Number of active database connections'
        )
        
        # Cache metrics
        self.cache_requests_total = Counter(
            f'{prefix}_cache_requests_total',
            'Total cache requests',
            ['operation', 'result']  # result: hit/miss
        )
        
        self.cache_items = Gauge(
            f'{prefix}_cache_items',
            'Number of items in cache'
        )
        
        # Extension metrics
        self.extension_requests_total = Counter(
            f'{prefix}_extension_requests_total',
            'Total extension API requests',
            ['platform', 'endpoint']
        )
        
        self.extension_comments_analyzed = Counter(
            f'{prefix}_extension_comments_analyzed',
            'Total comments analyzed by extension',
            ['platform', 'category']
        )
        
        # User metrics
        self.users_registered_total = Counter(
            f'{prefix}_users_registered_total',
            'Total registered users'
        )
        
        self.users_active = Gauge(
            f'{prefix}_users_active',
            'Number of active users'
        )
        
        self.user_logins_total = Counter(
            f'{prefix}_user_logins_total',
            'Total user logins',
            ['status']  # success/failed
        )
        
        # Error metrics
        self.errors_total = Counter(
            f'{prefix}_errors_total',
            'Total errors',
            ['type', 'endpoint']
        )
        
        self.exceptions_total = Counter(
            f'{prefix}_exceptions_total',
            'Total exceptions',
            ['exception_type']
        )
        
        # Rate limiting metrics
        self.rate_limit_hits_total = Counter(
            f'{prefix}_rate_limit_hits_total',
            'Total rate limit hits',
            ['client_type']
        )
        
        logger.info("✅ Prometheus metrics initialized")
    
    def track_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration: float
    ):
        """Track HTTP request"""
        if not self.enabled:
            return
        
        self.http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status=str(status_code)
        ).inc()
        
        self.http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    def track_prediction(
        self,
        model_type: str,
        category: str,
        confidence: float,
        duration: float
    ):
        """Track ML prediction"""
        if not self.enabled:
            return
        
        self.ml_predictions_total.labels(
            model_type=model_type,
            category=category
        ).inc()
        
        self.ml_prediction_duration_seconds.labels(
            model_type=model_type
        ).observe(duration)
        
        self.ml_prediction_confidence.labels(
            model_type=model_type,
            category=category
        ).observe(confidence)
    
    def track_db_query(
        self,
        operation: str,
        table: str,
        duration: float
    ):
        """Track database query"""
        if not self.enabled:
            return
        
        self.db_queries_total.labels(
            operation=operation,
            table=table
        ).inc()
        
        self.db_query_duration_seconds.labels(
            operation=operation,
            table=table
        ).observe(duration)
    
    def track_cache(self, operation: str, hit: bool):
        """Track cache operation"""
        if not self.enabled:
            return
        
        result = "hit" if hit else "miss"
        self.cache_requests_total.labels(
            operation=operation,
            result=result
        ).inc()
    
    def track_error(
        self,
        error_type: str,
        endpoint: str = "unknown"
    ):
        """Track error"""
        if not self.enabled:
            return
        
        self.errors_total.labels(
            type=error_type,
            endpoint=endpoint
        ).inc()
    
    def track_exception(self, exception_type: str):
        """Track exception"""
        if not self.enabled:
            return
        
        self.exceptions_total.labels(
            exception_type=exception_type
        ).inc()
    
    def set_model_loaded(self, model_type: str, loaded: bool):
        """Set model loaded status"""
        if not self.enabled:
            return
        
        self.ml_model_loaded.labels(
            model_type=model_type
        ).set(1 if loaded else 0)
    
    def set_active_users(self, count: int):
        """Set active users count"""
        if not self.enabled:
            return
        
        self.users_active.set(count)
    
    def get_metrics(self) -> bytes:
        """Get current metrics in Prometheus format"""
        if not self.enabled:
            return b"# Metrics disabled\n"
        
        return generate_latest()


# Global metrics collector
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector"""
    global _metrics_collector
    
    if _metrics_collector is None:
        from backend.config.settings import settings
        enabled = getattr(settings, 'PROMETHEUS_ENABLED', False)
        prefix = getattr(settings, 'PROMETHEUS_PREFIX', 'toxic_detector')
        
        _metrics_collector = MetricsCollector(
            enabled=enabled,
            prefix=prefix
        )
    
    return _metrics_collector


def reset_metrics_collector():
    """Reset metrics collector (for testing)"""
    global _metrics_collector
    _metrics_collector = None


# Decorators for easy metrics tracking

def track_time(
    metric_type: str = "function",
    labels: dict = None
):
    """
    Decorator to track function execution time
    
    Usage:
        @track_time(metric_type="prediction", labels={"model": "lstm"})
        def predict(text):
            return model.predict(text)
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            metrics = get_metrics_collector()
            
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                logger.debug(f"{func.__name__} took {duration:.3f}s")
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            metrics = get_metrics_collector()
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                logger.debug(f"{func.__name__} took {duration:.3f}s")
        
        # Return appropriate wrapper based on function type
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def track_errors(error_type: str = "general"):
    """
    Decorator to track errors
    
    Usage:
        @track_errors(error_type="api_error")
        def risky_function():
            # ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            metrics = get_metrics_collector()
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                metrics.track_exception(type(e).__name__)
                metrics.track_error(error_type, func.__name__)
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            metrics = get_metrics_collector()
            try:
                return func(*args, **kwargs)
            except Exception as e:
                metrics.track_exception(type(e).__name__)
                metrics.track_error(error_type, func.__name__)
                raise
        
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Middleware for automatic request tracking

class PrometheusMiddleware:
    """
    Middleware to automatically track HTTP requests
    """
    
    def __init__(self, app):
        self.app = app
        self.metrics = get_metrics_collector()
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        from fastapi import Request
        request = Request(scope, receive=receive)
        
        method = request.method
        path = request.url.path
        
        # Track request in progress
        if self.metrics.enabled:
            self.metrics.http_requests_in_progress.labels(
                method=method,
                endpoint=path
            ).inc()
        
        start_time = time.time()
        status_code = 500  # Default to error
        
        async def send_with_metrics(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)
        
        try:
            await self.app(scope, receive, send_with_metrics)
        finally:
            duration = time.time() - start_time
            
            if self.metrics.enabled:
                self.metrics.http_requests_in_progress.labels(
                    method=method,
                    endpoint=path
                ).dec()
                
                self.metrics.track_request(
                    method=method,
                    endpoint=path,
                    status_code=status_code,
                    duration=duration
                )

