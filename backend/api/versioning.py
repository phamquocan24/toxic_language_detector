"""
API Versioning Support

Provides backward-compatible API versioning without breaking existing endpoints.
Supports both URL-based (/api/v1/) and header-based versioning.
"""

from typing import Optional, Callable
from fastapi import Request, HTTPException, status
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class APIVersion:
    """API version constants"""
    V1 = "1.0"
    V2 = "2.0"
    LATEST = V1  # Current latest version


def get_api_version(request: Request) -> str:
    """
    Extract API version from request
    
    Priority:
    1. URL path (/api/v1/, /api/v2/)
    2. Accept-Version header
    3. Default to latest version
    
    Args:
        request: FastAPI request
        
    Returns:
        API version string (e.g., "1.0", "2.0")
    """
    # Check URL path first
    path = request.url.path
    if "/api/v1/" in path:
        return APIVersion.V1
    elif "/api/v2/" in path:
        return APIVersion.V2
    
    # Check Accept-Version header
    version_header = request.headers.get("Accept-Version")
    if version_header:
        # Normalize version (v1 -> 1.0, 1 -> 1.0, etc.)
        version_header = version_header.lower().replace("v", "")
        if version_header == "1" or version_header == "1.0":
            return APIVersion.V1
        elif version_header == "2" or version_header == "2.0":
            return APIVersion.V2
    
    # Default to latest
    return APIVersion.LATEST


def versioned_endpoint(min_version: str = APIVersion.V1):
    """
    Decorator to mark endpoint as version-specific
    
    Usage:
        @router.get("/data")
        @versioned_endpoint(min_version="1.0")
        async def get_data_v1():
            return {"version": "1.0", "data": [...]}
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            current_version = get_api_version(request)
            
            # Version comparison (simple string comparison works for X.Y format)
            if current_version < min_version:
                raise HTTPException(
                    status_code=status.HTTP_426_UPGRADE_REQUIRED,
                    detail=f"API version {min_version} or higher is required. Current: {current_version}"
                )
            
            return await func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def deprecated(
    message: str = None,
    sunset_date: str = None,
    replacement: str = None
):
    """
    Decorator to mark endpoint as deprecated
    
    Usage:
        @router.get("/old-endpoint")
        @deprecated(
            message="Use /new-endpoint instead",
            sunset_date="2024-12-31",
            replacement="/api/v2/new-endpoint"
        )
        async def old_endpoint():
            return {"data": "..."}
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # Log deprecation warning
            logger.warning(
                f"Deprecated endpoint accessed: {request.url.path} "
                f"by {request.client.host if request.client else 'unknown'}"
            )
            
            # Add deprecation headers
            response = await func(request, *args, **kwargs)
            
            # Note: FastAPI doesn't allow direct header modification here
            # Headers should be added via Response object or middleware
            # This is just for tracking
            
            return response
        
        # Store deprecation info as function attribute
        wrapper._deprecated = True
        wrapper._deprecation_message = message
        wrapper._sunset_date = sunset_date
        wrapper._replacement = replacement
        
        return wrapper
    return decorator


class APIVersionMiddleware:
    """
    Middleware to handle API versioning
    Adds version headers to responses
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive=receive)
            api_version = get_api_version(request)
            
            async def send_with_headers(message):
                if message["type"] == "http.response.start":
                    headers = list(message.get("headers", []))
                    
                    # Add API version header
                    headers.append((b"X-API-Version", api_version.encode()))
                    
                    # Add deprecation headers if endpoint is deprecated
                    # (Would need to access route info here)
                    
                    message["headers"] = headers
                
                await send(message)
            
            await self.app(scope, receive, send_with_headers)
        else:
            await self.app(scope, receive, send)


def create_versioned_router(version: str, prefix: str = None):
    """
    Create a versioned API router
    
    Usage:
        # Create v1 router
        router_v1 = create_versioned_router("1.0", prefix="/api/v1")
        
        @router_v1.get("/users")
        async def get_users_v1():
            return {"version": "1.0", "users": [...]}
        
        # Create v2 router
        router_v2 = create_versioned_router("2.0", prefix="/api/v2")
        
        @router_v2.get("/users")
        async def get_users_v2():
            return {"version": "2.0", "users": [...], "metadata": {...}}
    """
    from fastapi import APIRouter
    
    router = APIRouter(
        prefix=prefix or f"/api/v{version.split('.')[0]}",
        tags=[f"v{version}"]
    )
    
    # Store version info
    router.version = version
    
    return router


# Helper functions for response formatting

def v1_response(data: dict) -> dict:
    """
    Format response for API v1
    
    Simple format: just the data
    """
    return data


def v2_response(data: dict, metadata: dict = None) -> dict:
    """
    Format response for API v2
    
    Enhanced format: data + metadata
    """
    response = {
        "version": "2.0",
        "data": data
    }
    
    if metadata:
        response["metadata"] = metadata
    
    return response


# Migration utilities

class VersionedResponse:
    """
    Helper to create version-aware responses
    
    Usage:
        @router.get("/data")
        async def get_data(request: Request):
            data = {"items": [...]}
            
            return VersionedResponse.format(
                request,
                data,
                v1_formatter=lambda d: d,
                v2_formatter=lambda d: {"data": d, "count": len(d["items"])}
            )
    """
    
    @staticmethod
    def format(
        request: Request,
        data: dict,
        v1_formatter: Callable = None,
        v2_formatter: Callable = None
    ) -> dict:
        """Format response based on API version"""
        version = get_api_version(request)
        
        if version == APIVersion.V2 and v2_formatter:
            return v2_formatter(data)
        elif v1_formatter:
            return v1_formatter(data)
        else:
            return data


# Compatibility layer

def ensure_backward_compatibility(v1_data: dict, v2_data: dict) -> dict:
    """
    Ensure v2 response is backward compatible with v1
    
    Args:
        v1_data: Expected v1 response structure
        v2_data: New v2 response structure
        
    Returns:
        Compatible response
    """
    # Check if all v1 keys exist in v2
    missing_keys = set(v1_data.keys()) - set(v2_data.keys())
    
    if missing_keys:
        logger.warning(f"V2 response missing v1 keys: {missing_keys}")
        
        # Add missing keys with default values
        for key in missing_keys:
            v2_data[key] = v1_data[key]
    
    return v2_data


# Example usage documentation
"""
Example 1: Simple versioning with URL paths
-------------------------------------------

# Create v1 router
from backend.api.versioning import create_versioned_router

router_v1 = create_versioned_router("1.0", prefix="/api/v1")

@router_v1.get("/users")
async def get_users_v1():
    return {"users": [{"id": 1, "name": "John"}]}

# Create v2 router with enhanced response
router_v2 = create_versioned_router("2.0", prefix="/api/v2")

@router_v2.get("/users")
async def get_users_v2():
    return {
        "version": "2.0",
        "data": {"users": [{"id": 1, "name": "John", "email": "john@example.com"}]},
        "metadata": {"count": 1, "timestamp": "2024-10-19T10:00:00Z"}
    }

# Include both routers in main app
app.include_router(router_v1)
app.include_router(router_v2)


Example 2: Header-based versioning
----------------------------------

@router.get("/api/data")
async def get_data(request: Request):
    version = get_api_version(request)
    
    data = {"items": [...]}
    
    if version == "2.0":
        return {
            "version": "2.0",
            "data": data,
            "metadata": {"count": len(data["items"])}
        }
    else:
        return data


Example 3: Version-aware response
---------------------------------

@router.get("/api/stats")
async def get_stats(request: Request):
    stats = calculate_stats()
    
    return VersionedResponse.format(
        request,
        stats,
        v1_formatter=lambda d: d,
        v2_formatter=lambda d: {
            "version": "2.0",
            "data": d,
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "cache_hit": True
            }
        }
    )


Example 4: Deprecation warning
------------------------------

@router.get("/api/old-endpoint")
@deprecated(
    message="Use /api/v2/new-endpoint instead",
    sunset_date="2024-12-31",
    replacement="/api/v2/new-endpoint"
)
async def old_endpoint():
    return {"data": "..."}


Example 5: Minimum version requirement
--------------------------------------

@router.post("/api/advanced-feature")
@versioned_endpoint(min_version="2.0")
async def advanced_feature(request: Request):
    # This endpoint only works with v2.0+
    return {"result": "..."}
"""

