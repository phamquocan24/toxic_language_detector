import time
from starlette.requests import Request
from starlette.responses import JSONResponse

# Simple in-memory rate limiter
RATE_LIMIT = 5  # max requests
TIME_WINDOW = 60  # in seconds

# Dictionary to store client IP and request timestamps
request_log = {}

def get_client_ip(request: Request):
    return request.client.host

def check_rate_limit(request: Request) -> bool:
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

def get_retry_after(request: Request) -> int:
    ip = get_client_ip(request)
    now = time.time()

    if ip not in request_log or not request_log[ip]:
        return 0

    earliest_request = min(request_log[ip])
    retry_after = TIME_WINDOW - (now - earliest_request)
    return max(1, int(retry_after))
