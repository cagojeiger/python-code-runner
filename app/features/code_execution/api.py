from fastapi import APIRouter

from app.features.code_execution.schemas import CodeRequest, ExecuteResponse
from app.features.code_execution.services import execute_user_code

router = APIRouter(tags=["Execution"])


@router.post(
    "/execute",
    response_model=ExecuteResponse,
    summary="사용자 코드 실행",
    description="사용자가 제출한 코드를 안전한 환경에서 실행하고 결과를 반환합니다.",
    response_description="코드 실행 결과가 성공적으로 반환됩니다."
)
async def run_code(req: CodeRequest) -> ExecuteResponse:
    """
    사용자가 제출한 코드를 실행합니다.

    Args:
        req (CodeRequest): 실행할 코드 정보
            - code (str): 실행할 파이썬 코드

    Returns:
        ExecuteResponse: 코드 실행 결과 객체
            - result (str): 코드 실행 결과 문자열

    Raises:
        HTTPException: 코드 실행 중 오류가 발생한 경우
    """
    result = await execute_user_code(req.code)
    return ExecuteResponse(result=result)
