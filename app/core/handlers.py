from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import (SandboxRuntimeError, SandboxSecurityError,
                                 SandboxSyntaxError)
from app.models.schemas import ErrorResponse


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(SandboxSecurityError)
    def security_error_handler(
        request: Request, exc: SandboxSecurityError
    ) -> JSONResponse:
        content = ErrorResponse(
            error_type="security", detail=str(exc), forbidden_item=exc.forbidden_item
        ).dict()
        return JSONResponse(status_code=400, content=content)

    @app.exception_handler(SandboxSyntaxError)
    def syntax_error_handler(request: Request, exc: SandboxSyntaxError) -> JSONResponse:
        content = ErrorResponse(error_type="syntax", detail=str(exc)).dict()
        return JSONResponse(status_code=400, content=content)

    @app.exception_handler(SandboxRuntimeError)
    def runtime_error_handler(
        request: Request, exc: SandboxRuntimeError
    ) -> JSONResponse:
        content = ErrorResponse(error_type="runtime", detail=str(exc)).dict()
        return JSONResponse(status_code=500, content=content)
