import time
import json
from typing import Callable, Dict, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.base import async_session
from backend.db.models.log import Log
from backend.core.security import get_current_user

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests and responses"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Any]
    ) -> Response:
        # Skip logging for some endpoints
        if (
            request.url.path.startswith("/docs") 
            or request.url.path.startswith("/redoc") 
            or request.url.path.startswith("/openapi.json")
        ):
            return await call_next(request)
        
        # Get request data for logging
        request_time = time.time()
        
        # Process the request
        response = await call_next(request)
        
        # Calculate request processing time
        process_time = time.time() - request_time
        
        # Add processing time header
        response.headers["X-Process-Time"] = str(process_time)
        
        # Try to log the request if authentication is present
        try:
            # Only log authenticated requests that modify data
            if (
                request.method in ["POST", "PUT", "DELETE", "PATCH"] 
                and "authorization" in request.headers
            ):
                # Get the current user (if authenticated)
                user = await get_current_user(
                    request.headers.get("authorization", "").replace("Bearer ", ""), 
                )
                
                # Create a log entry
                async with async_session() as db:
                    # Try to parse request body
                    try:
                        body = await request.json()
                        # Remove sensitive data like passwords
                        if isinstance(body, dict):
                            if "password" in body:
                                body["password"] = "***REDACTED***"
                            if "current_password" in body:
                                body["current_password"] = "***REDACTED***"
                            if "new_password" in body:
                                body["new_password"] = "***REDACTED***"
                    except:
                        body = {}
                    
                    # Create log entry
                    log = Log(
                        user_id=user.id,
                        action=f"{request.method}_{request.url.path}",
                        endpoint=request.url.path,
                        request_data=body,
                        response_data={"status_code": response.status_code},
                        ip_address=request.client.host,
                        user_agent=request.headers.get("user-agent", ""),
                        status_code=response.status_code,
                        details=f"{request.method} {request.url.path} - {response.status_code}"
                    )
                    db.add(log)
                    await db.commit()
        except Exception as e:
            # If logging fails, just continue without logging
            print(f"Logging error: {str(e)}")
        
        return response