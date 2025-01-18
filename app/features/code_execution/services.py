# app/features/code_execution/services.py
import asyncio
import io
import os
import sys
import tempfile
from typing import Dict

from app.core.exceptions import SandboxRuntimeError
from app.core.security import check_forbidden_patterns


async def execute_user_code(code: str) -> str:
    """
    사용자가 전달한 code를 임시 파일에 저장한 뒤,
    asyncio.create_subprocess_exec로 별도 프로세스에서 비동기로 실행합니다.
    """
    # 1) 코드 보안 검사(AST)
    check_forbidden_patterns(code)

    # 2) 샌드박스용 전용 디렉터리 생성 (권한 최소화)
    sandbox_dir = tempfile.mkdtemp(prefix="sandbox_")
    #   - mkdtemp()은 디렉터리를 0700 권한으로 생성합니다 (오너만 rwx).

    try:
        # 3) 디렉터리 내에 임시 파일 생성
        file_path = os.path.join(sandbox_dir, "user_code.py")
        with open(file_path, "w") as f:
            f.write(code)

        # 4) 비동기 서브프로세스 생성
        process = await asyncio.create_subprocess_exec(
            "python",
            file_path,
            cwd=sandbox_dir,  # 작업 디렉터리를 sandbox_dir로 고정
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        # 5) 결과 수집 (타임아웃 예: 5초)
        try:
            stdout_data, stderr_data = await asyncio.wait_for(
                process.communicate(), timeout=5.0
            )
        except asyncio.TimeoutError:
            # 타임아웃 시, 프로세스 강제 종료 후 예외
            process.kill()
            stdout_data, stderr_data = await process.communicate()
            raise SandboxRuntimeError("Execution timed out.")

        # 6) 출력 정리
        stdout_str = stdout_data.decode()
        stderr_str = stderr_data.decode() if stderr_data else ""

        return stdout_str + (f"\n{stderr_str}" if stderr_str else "")

    except Exception as e:
        raise SandboxRuntimeError(f"Subprocess execution error: {e}")

    finally:
        # 7) 실행 후 디렉터리/파일 삭제
        if os.path.exists(sandbox_dir):
            # 안전하게 전체 디렉터리 삭제
            import shutil

            shutil.rmtree(sandbox_dir)
