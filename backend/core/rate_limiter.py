from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import time

class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 10, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.clients = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if hasattr(request, "client") else "unknown"
        now = time.time()

        request_log = self.clients.get(client_ip, [])
        # Remove expired requests
        request_log = [req for req in request_log if now - req < self.window_seconds]
        request_log.append(now)

        self.clients[client_ip] = request_log

        if len(request_log) > self.max_requests:
            return Response(
                "Too Many Requests", status_code=429
            )

        return await call_next(request)
