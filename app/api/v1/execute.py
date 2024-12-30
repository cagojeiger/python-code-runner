from fastapi import APIRouter

from app.schemas.execution import CodeRequest, ExecuteResponse
from app.services.code_execution import execute_user_code

router = APIRouter(tags=["Execution"])


@router.post(
    "/execute", response_model=ExecuteResponse, summary="Run user code securely"
)
def run_code(req: CodeRequest) -> ExecuteResponse:
    result = execute_user_code(req.code)
    return ExecuteResponse(result=result)
