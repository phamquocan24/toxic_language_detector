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
    Middleware để ghi log tất cả các requests và responses
    """
    
    async def dispatch(self, request: Request, call_next):
        # Đánh dấu thời gian bắt đầu
        start_time = time.time()
        
        # Lấy thông tin request
        path = request.url.path
        query_params = str(request.query_params) if request.query_params else None
        method = request.method
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "")
        
        # Lấy thông tin người dùng từ token (nếu có)
        user_id = None
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
                username = payload.get("sub")
                if username:
                    # Lấy user_id từ database nếu cần
                    # Ở đây chỉ lưu lại username
                    user_id = username
            except JWTError:
                pass
        
        # Lấy request body (nếu không phải upload file)
        request_body_str = None
        if "multipart/form-data" not in request.headers.get("content-type", ""):
            try:
                request_body = await request.body()
                if request_body:
                    request_body_str = request_body.decode("utf-8")
                    # Che dấu thông tin nhạy cảm
                    if "password" in request_body_str:
                        body_json = json.loads(request_body_str)
                        if "password" in body_json:
                            body_json["password"] = "******"
                        if "current_password" in body_json:
                            body_json["current_password"] = "******"
                        if "new_password" in body_json:
                            body_json["new_password"] = "******"
                        request_body_str = json.dumps(body_json)
            except Exception:
                request_body_str = None
        
        # Thực hiện request và bắt lỗi
        exception_info = None
        try:
            response = await call_next(request)
        except Exception as e:
            exception_info = {
                "type": str(type(e).__name__),
                "message": str(e),
                "traceback": traceback.format_exc()
            }
            # Trả về lỗi 500 khi có exception
            response = JSONResponse(
                status_code=500,
                content={"detail": "Internal Server Error"}
            )
            # Log lỗi
            logger.error(f"Exception during request processing: {str(e)}\n{traceback.format_exc()}")
        
        # Tính thời gian xử lý
        process_time = time.time() - start_time
        
        # Bỏ qua logging cho health checks và static files
        if path.startswith("/health") or path.startswith("/static") or path.startswith("/docs") or path.startswith("/redoc") or path.startswith("/openapi.json"):
            return response
        
        # Lấy response body nếu debug mode
        response_body = None
        if settings.DEBUG and isinstance(response, JSONResponse):
            response_body = response.body.decode("utf-8")
        
        # Log request/response
        try:
            # Lấy DB session
            db = next(get_db())
            
            # Tạo log entry
            log_entry = Log(
                request_path=path,
                request_method=method,
                request_query=query_params,
                request_body=request_body_str if request_body_str else None,
                response_status=response.status_code,
                response_body=response_body,
                client_ip=client_ip,
                user_agent=user_agent,
                user_id=user_id,
                timestamp=datetime.utcnow(),
                metadata=json.dumps({
                    "process_time_ms": round(process_time * 1000),
                    "exception": exception_info
                })
            )
            
            # Thêm vào DB
            db.add(log_entry)
            db.commit()
            
        except Exception as e:
            logger.error(f"Error logging request: {str(e)}\n{traceback.format_exc()}")
        
        # Thêm X-Process-Time header
        response.headers["X-Process-Time"] = str(process_time)
        
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
        client_ip = request.headers.get("x-forwarded-for", request.client.host)
        if client_ip and "," in client_ip:
            client_ip = client_ip.split(",")[0].strip()
        
        # Kiểm tra nếu IP là localhost
        if client_ip in ["127.0.0.1", "::1"]:
            return await call_next(request)
        
        # Kiểm tra rate limit
        from backend.utils.rate_limiter import check_rate_limit, get_retry_after
        
        if not check_rate_limit(client_ip):
            retry_after = get_retry_after(client_ip)
            return JSONResponse(
                status_code=429,
                content={"detail": "Quá nhiều yêu cầu, vui lòng thử lại sau"},
                headers={"Retry-After": str(retry_after)}
            )
        
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