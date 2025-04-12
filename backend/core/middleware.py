# # core/middleware.py
# from fastapi import Request, Response
# from starlette.middleware.base import BaseHTTPMiddleware
# from backend.db.models import Log, get_db
# import json
# import time

# class LogMiddleware(BaseHTTPMiddleware):
#     """
#     Middleware to log all requests and responses
#     """
    
#     async def dispatch(self, request: Request, call_next):
#         # Start timer
#         start_time = time.time()
        
#         # Get request details
#         path = request.url.path
#         method = request.method
#         client_ip = request.client.host
#         user_agent = request.headers.get("user-agent", "")
        
#         # Try to get request body
#         try:
#             request_body = await request.body()
#             request_body_str = request_body.decode("utf-8")
#         except Exception:
#             request_body_str = None
            
#         # Get response
#         response = await call_next(request)
        
#         # Calculate process time
#         process_time = time.time() - start_time
        
#         # Skip logging for health checks or static files
#         if path.startswith("/health") or path.startswith("/static"):
#             return response
            
#         # Log the request/response
#         try:
#             # Get DB session
#             db = next(get_db())
            
#             # Create log entry
#             log_entry = Log(
#                 request_path=path,
#                 request_method=method,
#                 request_body=request_body_str if request_body_str else None,
#                 response_status=response.status_code,
#                 client_ip=client_ip,
#                 user_agent=user_agent,
#                 metadata={
#                     "process_time_ms": round(process_time * 1000),
#                 }
#             )
            
#             # Add to DB
#             db.add(log_entry)
#             db.commit()
            
#         except Exception as e:
#             print(f"Error logging request: {str(e)}")
            
#         return response
# core/middleware.py
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from backend.db.models import Log, get_db
from backend.config.settings import settings
from jose import JWTError, jwt
import json
import time
import logging
from datetime import datetime
import traceback

# Thiết lập logger
logger = logging.getLogger("middleware")
logger.setLevel(logging.INFO)

if settings.LOG_TO_FILE:
    handler = logging.FileHandler(settings.LOG_FILENAME)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
else:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)

class LogMiddleware(BaseHTTPMiddleware):
    """
    Middleware để ghi log tất cả các requests và responses (phiên bản không dùng DB)
    """
    
    async def dispatch(self, request: Request, call_next):
        # Đánh dấu thời gian bắt đầu
        start_time = time.time()
        
        # Lấy thông tin request
        path = request.url.path
        method = request.method
        
        # Thực hiện request và bắt lỗi
        exception_info = None
        try:
            response = await call_next(request)
        except Exception as e:
            exception_info = {
                "type": str(type(e).__name__),
                "message": str(e)
            }
            # Trả về lỗi 500 khi có exception
            response = JSONResponse(
                status_code=500,
                content={"detail": "Internal Server Error"}
            )
            # Log lỗi
            logger.error(f"Exception during request processing: {str(e)}")
        
        # Tính thời gian xử lý
        process_time = time.time() - start_time
        
        # Bỏ qua logging cho health checks và static files
        if path.startswith("/health") or path.startswith("/static") or path.startswith("/docs") or path.startswith("/redoc") or path.startswith("/openapi.json"):
            return response
        
        # Thêm X-Process-Time header
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log ra file hoặc console thay vì database
        logger.info(f"{method} {path} - Status: {response.status_code} - Time: {process_time:.4f}s")
        
        return response
class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware kiểm soát giới hạn tốc độ request
    """
    
    async def dispatch(self, request: Request, call_next):
        # Kiểm tra nếu rate limiting được bật
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)
        
        # Bỏ qua rate limiting cho một số endpoints
        path = request.url.path
        if path.startswith("/health") or path.startswith("/static") or path.startswith("/docs") or path.startswith("/redoc"):
            return await call_next(request)
        
        # Lấy client IP
        client_ip = None
        try:
            # Xử lý an toàn hơn để tránh lỗi
            if hasattr(request, 'headers'):
                client_ip = request.headers.get("x-forwarded-for")
            
            if not client_ip and hasattr(request, 'client') and request.client:
                client_ip = request.client.host
                
            if not client_ip:
                client_ip = "unknown"
                
            if client_ip and "," in client_ip:
                client_ip = client_ip.split(",")[0].strip()
        except Exception as e:
            logger.error(f"Lỗi khi lấy client IP: {e}")
            client_ip = "unknown"
        
        # Kiểm tra nếu IP là localhost
        if client_ip in ["127.0.0.1", "::1"]:
            return await call_next(request)
            
        # Điều này sẽ tránh gọi database operations
        # Trong môi trường thực tế, bạn sẽ cần sửa backend.utils.rate_limiter
        return await call_next(request)

class CORSMiddleware(BaseHTTPMiddleware):
    """
    Middleware xử lý CORS
    """
    
    async def dispatch(self, request: Request, call_next):
        # Xử lý preflight request
        if request.method == "OPTIONS":
            response = Response()
        else:
            response = await call_next(request)
        
        # Thêm CORS headers
        origin = request.headers.get("origin")
        
        # Kiểm tra origin có hợp lệ không
        allowed_origin = "*"
        if origin:
            for allowed in settings.CORS_ORIGINS:
                if allowed == "*":
                    allowed_origin = origin
                    break
                elif origin == allowed:
                    allowed_origin = origin
                    break
                elif allowed.endswith("*"):
                    prefix = allowed[:-1]
                    if origin.startswith(prefix):
                        allowed_origin = origin
                        break
        
        response.headers["Access-Control-Allow-Origin"] = allowed_origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, X-API-Key"
        
        return response

class ExceptionMiddleware(BaseHTTPMiddleware):
    """
    Middleware bắt và xử lý các exception
    """
    
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            # Log exception
            logger.error(f"Unhandled exception: {str(e)}\n{traceback.format_exc()}")
            
            # Trả về lỗi 500
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Đã xảy ra lỗi server",
                    "error": str(e) if settings.DEBUG else "Internal Server Error"
                }
            )