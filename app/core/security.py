import ast

from app.core.exceptions import SandboxSecurityError, SandboxSyntaxError

FORBIDDEN_FUNCTIONS = {"exec", "eval", "__import__", "open"}
FORBIDDEN_MODULES = {"os", "sys", "subprocess", "socket"}


def check_forbidden_patterns(code: str) -> None:
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        raise SandboxSyntaxError(f"Syntax error: {e}")

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in FORBIDDEN_MODULES:
                    raise SandboxSecurityError("Forbidden module import", alias.name)
        if isinstance(node, ast.ImportFrom):
            if node.module and node.module.split(".")[0] in FORBIDDEN_MODULES:
                raise SandboxSecurityError("Forbidden module import", node.module)
        if isinstance(node, ast.Call) and hasattr(node.func, "id"):
            func_name = node.func.id
            if func_name in FORBIDDEN_FUNCTIONS:
                raise SandboxSecurityError("Forbidden function usage", func_name)
