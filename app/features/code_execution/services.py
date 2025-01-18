# app/features/code_execution/services.py
import io
import sys
from typing import Dict

from app.core.exceptions import SandboxRuntimeError
from app.core.security import check_forbidden_patterns


def execute_user_code(code: str) -> str:
    # 코드 보안 검사(AST)
    check_forbidden_patterns(code)

    # 허용할 내장 함수들만 삽입
    allowed_builtins: Dict[str, object] = {"print": print, "range": range, "len": len}
    safe_globals: Dict[str, Dict[str, object]] = {"__builtins__": {}}
    for k, v in allowed_builtins.items():
        safe_globals["__builtins__"][k] = v

    # stdout 캡처
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        exec(code, safe_globals, {})
        output: str = sys.stdout.getvalue()
    except Exception as e:
        raise SandboxRuntimeError(str(e))
    finally:
        sys.stdout = old_stdout

    return output
