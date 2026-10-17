"""Typed HTTP exceptions for the application.

Each subclass owns its status_code, default detail, and error_code so callers
never pass HTTP status literals. The registered HTTP handler reads
``error_code``; untyped ``HTTPException`` still falls back to GENERIC_ERROR.

Raise these instead of ``HTTPException``. Do not add resource-specific
NotFound/BadRequest subclasses — pass ``detail`` and ``error_code`` instead.
"""

from fastapi import HTTPException, status


class AppHTTPException(HTTPException):
    """Shared base so every typed error carries an error_code."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail: str = "An error occurred"
    error_code: str = "GENERIC_ERROR"

    def __init__(self, detail: str | None = None, *, error_code: str | None = None, details: list[dict[str, object]] | None = None) -> None:
        super().__init__(
            status_code=self.status_code,
            detail=self.default_detail if detail is None else detail,
        )
        self.error_code = self.__class__.error_code if error_code is None else error_code
        self.details = details if details is not None else []


class BadRequestException(AppHTTPException):
    """Generic client-error: invalid payload, empty patch, immutable fields."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Bad request"
    error_code = "BAD_REQUEST"


class InvalidSortFieldException(AppHTTPException):
    """List endpoint received a sort field that is not allowed."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid sort field"
    error_code = "INVALID_SORT_FIELD"


class UnauthorizedException(AppHTTPException):
    """Unauthorized access."""

    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Unauthorized"
    error_code = "UNAUTHORIZED"


class ForbiddenException(AppHTTPException):
    """Forbidden access."""

    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Forbidden"
    error_code = "FORBIDDEN"


class ConflictException(AppHTTPException):
    """Resource already exists or conflicts with current state."""

    status_code = status.HTTP_409_CONFLICT
    default_detail = "Conflict"
    error_code = "CONFLICT"


class NotFoundException(AppHTTPException):
    """Requested resource does not exist."""

    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Resource not found"
    error_code = "NOT_FOUND"


class StorageException(AppHTTPException):
    """File storage provider failed."""

    status_code = status.HTTP_502_BAD_GATEWAY
    default_detail = "File storage error"
    error_code = "STORAGE_ERROR"


class DatabaseException(AppHTTPException):
    """Database error."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Database error"
    error_code = "DATABASE_ERROR"
