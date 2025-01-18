from fastapi import APIRouter

from app.core.config import ENV, SERVICE, VERSION
from app.features.root.schemas import ServiceInfo

router = APIRouter(tags=["System"])


@router.get(
    "/",
    response_model=ServiceInfo,
    summary="서비스 기본 정보 조회",
    description="서비스의 환경 설정 및 버전 정보를 반환합니다.",
    response_description="서비스 정보가 성공적으로 반환됩니다.",
)
async def get_service_info() -> ServiceInfo:
    """
    서비스의 기본 정보를 조회합니다.

    Returns:
        ServiceInfo: 서비스 정보 객체
            - service (str): 서비스 이름
            - environment (str): 실행 환경 (dev/stage/prod)
            - version (str): 서비스 버전

    Raises:
        HTTPException: 환경 설정 정보를 불러오는데 실패한 경우
    """

    return ServiceInfo(service=SERVICE, environment=ENV, version=VERSION)
