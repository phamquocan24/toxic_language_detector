#backend.utils.rate_limiter.pypy
import time
from starlette.requests import Request
from starlette.responses import JSONResponse

# Simple in-memory rate limiter
RATE_LIMIT = 5  # max requests
TIME_WINDOW = 60  # in seconds

# Dictionary to store client IP and request timestamps
request_log = {}

def get_client_ip(request):
    """
    Lấy địa chỉ IP của client từ request
    """
    # Kiểm tra nếu request là string
    if isinstance(request, str):
        return request
    
    # Kiểm tra các headers phổ biến được sử dụng cho proxy
    if hasattr(request, 'headers'):
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
    
    # Nếu không có header, sử dụng client.host
    if hasattr(request, 'client') and request.client:
        return request.client.host
    
    # Fallback nếu không thể xác định
    return "127.0.0.1"

def check_rate_limit(request) -> bool:
    """
    Kiểm tra nếu yêu cầu vượt quá giới hạn tỉ lệ
    """
    try:
        ip = get_client_ip(request)
        now = time.time()

        if ip not in request_log:
            request_log[ip] = []

        # Remove timestamps outside the window
        request_log[ip] = [ts for ts in request_log[ip] if now - ts < TIME_WINDOW]

        if len(request_log[ip]) >= RATE_LIMIT:
            return False  # limit exceeded

        request_log[ip].append(now)
        return True
    except Exception as e:
        # Log lỗi nếu cần
        # print(f"Rate limit check error: {str(e)}")
        return True  # Cho phép yêu cầu nếu có lỗi

def get_retry_after(request) -> int:
    """
    Trả về thời gian (giây) cần đợi trước khi thử lại
    """
    try:
        ip = get_client_ip(request)
        now = time.time()

        if ip not in request_log or not request_log[ip]:
            return 0

        earliest_request = min(request_log[ip])
        retry_after = TIME_WINDOW - (now - earliest_request)
        return max(1, int(retry_after))
    except Exception:
        return 60  # Giá trị mặc định nếu có lỗi