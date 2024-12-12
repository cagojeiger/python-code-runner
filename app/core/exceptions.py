from typing import Optional


class SandboxError(Exception):
    """Base class for sandbox-related errors."""

    pass


class SandboxSecurityError(SandboxError):
    def __init__(self, message: str, forbidden_item: Optional[str] = None) -> None:
        super().__init__(message)
        self.forbidden_item = forbidden_item


class SandboxSyntaxError(SandboxError):
    pass


class SandboxRuntimeError(SandboxError):
    pass
