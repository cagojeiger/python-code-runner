from typing import Optional

from pydantic import BaseModel


class CodeRequest(BaseModel):
    code: str


class ExecuteResponse(BaseModel):
    result: str


class ErrorResponse(BaseModel):
    error_type: str
    detail: str
    forbidden_item: Optional[str] = None
