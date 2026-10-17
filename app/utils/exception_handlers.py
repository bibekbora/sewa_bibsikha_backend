from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.conf.logger_config import api_logger


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Flatten request validation errors into {field, message} pairs."""
    errors: list[dict[str, str]] = []

    for error in exc.errors():
        column_name = error["loc"][-1]  # Extract the last element as the column name
        detail = {"field": str(column_name), "message": error["msg"]}
        errors.append(detail)

    api_logger.warning("Validation error for request %s: %s", request.url.path, errors)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=jsonable_encoder(
            {
                "message": "Validation error",
                "error_code": "VALIDATION_ERROR",
                "details": errors,
            }
        ),
    )


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    """HTTP exception handler."""
    error_code = getattr(exc, "error_code", "GENERIC_ERROR")

    # 4xx are client mistakes; only 5xx indicate a server fault worth alerting on.
    log = api_logger.error if exc.status_code >= status.HTTP_500_INTERNAL_SERVER_ERROR else api_logger.warning
    log("HTTP %s on %s: %s", exc.status_code, request.url.path, exc.detail)

    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(
            {
                "message": exc.detail,
                "error_code": error_code,
                "details": getattr(exc, "details", []),
            }
        ),
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler; never leaks the underlying exception to the client."""
    api_logger.error("Global exception on %s: %s", request.url.path, exc, exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder(
            {
                "message": "Internal server error",
                "error_code": "INTERNAL_SERVER_ERROR",
                "details": [],
            }
        ),
    )
