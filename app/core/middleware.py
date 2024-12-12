import time
import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        log = structlog.get_logger()
        request_id = str(uuid.uuid4())  # 실제로는 X-Request-ID 헤더에서 가져올 수 있음
        user_id = "unknown"  # JWT에서 추출 가능
        start = time.time()

        request_log = log.bind(request_id=request_id, user_id=user_id)

        request_log.info("request_start", path=request.url.path, method=request.method)

        response = await call_next(request)

        duration_ms = int((time.time() - start) * 1000)
        success = response.status_code < 400

        request_log.info(
            "request_end",
            path=request.url.path,
            method=request.method,
            status_code=response.status_code,
            execution_time_ms=duration_ms,
            success=success,
        )

        return response
