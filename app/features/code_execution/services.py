# app/features/code_execution/services.py
import asyncio
import tempfile
from pathlib import Path
from typing import Tuple

from app.core.exceptions import SandboxRuntimeError
from app.core.security import check_forbidden_patterns

# 상수 정의
SANDBOX_PREFIX = "sandbox_"
CODE_FILENAME = "user_code.py"
EXECUTION_TIMEOUT = 5.0  # seconds


async def execute_user_code(code: str) -> str:
    """사용자 코드를 안전한 환경에서 실행하고 결과를 반환합니다.

    Args:
        code: 실행할 파이썬 코드 문자열

    Returns:
        str: 실행 결과 (표준 출력 + 표준 에러)

    Raises:
        SandboxRuntimeError: 코드 실행 중 오류 발생시
    """
    check_forbidden_patterns(code)

    # 임시 디렉터리 생성 및 자동 정리
    with tempfile.TemporaryDirectory(prefix=SANDBOX_PREFIX) as sandbox_dir:
        try:
            return await _run_code_in_sandbox(code, sandbox_dir)
        except asyncio.TimeoutError:
            raise SandboxRuntimeError("Execution timed out.")
        except Exception as e:
            raise SandboxRuntimeError(f"Subprocess execution error: {str(e)}")


async def _run_code_in_sandbox(code: str, sandbox_dir: str) -> str:
    """샌드박스 환경에서 코드를 실행합니다.

    Args:
        code: 실행할 파이썬 코드
        sandbox_dir: 샌드박스 디렉터리 경로

    Returns:
        str: 실행 결과
    """
    file_path = Path(sandbox_dir) / CODE_FILENAME

    # 코드를 파일에 작성
    file_path.write_text(code)

    # 프로세스 실행 및 결과 수집
    stdout_str, stderr_str = await _execute_process(file_path, sandbox_dir)

    return stdout_str + (f"\n{stderr_str}" if stderr_str else "")


async def _execute_process(file_path: Path, cwd: str) -> Tuple[str, str]:
    """별도 프로세스에서 파이썬 코드를 실행합니다.

    Args:
        file_path: 실행할 파이썬 파일 경로
        cwd: 작업 디렉터리

    Returns:
        Tuple[str, str]: (표준 출력, 표준 에러) 튜플
    """
    process = await asyncio.create_subprocess_exec(
        "python",
        str(file_path),
        cwd=cwd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout_data, stderr_data = await asyncio.wait_for(
        process.communicate(), 
        timeout=EXECUTION_TIMEOUT
    )

    if process.returncode != 0:
        raise RuntimeError(stderr_data.decode() or "Unknown error from user code")

    return (
        stdout_data.decode(),
        stderr_data.decode() if stderr_data else ""
    )
