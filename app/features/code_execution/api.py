# app/features/code_execution/api.py
from fastapi import APIRouter

from app.features.code_execution.schemas import CodeRequest, ExecuteResponse
from app.features.code_execution.services import execute_user_code

router = APIRouter(tags=["Execution"])


@router.post(
    "/execute", response_model=ExecuteResponse, summary="Run user code securely"
)
async def run_code(req: CodeRequest) -> ExecuteResponse:
    result = await execute_user_code(req.code)
    return ExecuteResponse(result=result)
