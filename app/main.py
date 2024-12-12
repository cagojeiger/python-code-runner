from fastapi import FastAPI

from app.api.v1.execute import router as execute_router
from app.core.handlers import register_exception_handlers
from app.core.logging import configure_logging
from app.core.middleware import RequestLoggingMiddleware

SERVICE = "code-runner"
ENV = "prod"
VERSION = "1.0.0"

configure_logging(service=SERVICE, env=ENV, version=VERSION)


app = FastAPI(
    title="sandboxed-code-runner",
    description="A sandbox environment for secure code execution.",
    version="0.1.0",
)

app.add_middleware(RequestLoggingMiddleware)


app.include_router(execute_router, prefix="/v1")

register_exception_handlers(app)
