from fastapi import FastAPI

from app.core.handlers import register_exception_handlers
from app.core.logging import configure_logging
from app.core.middleware import RequestLoggingMiddleware
from app.features.code_execution.api import router as code_execution_router
from app.features.root.api import router as root_router

SERVICE = "code-runner"
ENV = "prod"
VERSION = "1.0.0"

# 로깅 설정
configure_logging(service=SERVICE, env=ENV, version=VERSION)

# FastAPI 인스턴스 생성
app = FastAPI(
    title="sandboxed-code-runner",
    description="A sandbox environment for secure code execution.",
    version="0.1.0",
)

# 요청 로깅 미들웨어 등록
app.add_middleware(RequestLoggingMiddleware)

# 루트 라우터 등록: prefix 없이 바로 사용 (ex: GET "/")
app.include_router(root_router)

# Code Execution 기능 라우터 등록
app.include_router(code_execution_router, prefix="/v1")

# 예외 핸들러 등록
register_exception_handlers(app)
