from typing import Any, Dict, Optional

class HeimdallException(Exception):
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class AuthError(HeimdallException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="AUTHENTICATION_FAILED",
            status_code=401,
            details=details
        )

class PermissionDeniedError(HeimdallException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="PERMISSION_DENIED",
            status_code=403,
            details=details
        )

class NotFoundError(HeimdallException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="RESOURCE_NOT_FOUND",
            status_code=404,
            details=details
        )

class ValidationError(HeimdallException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=422,
            details=details
        )

class LLMAPIError(HeimdallException):
    def __init__(self, message: str, provider: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="LLM_API_ERROR",
            status_code=502,
            details={"provider": provider, **(details or {})}
        )
