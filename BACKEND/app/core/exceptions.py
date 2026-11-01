"""Custom application exceptions and consistent error handlers.

Keeping error responses in a single format (``ErrorResponse``) makes the API
predictable for the frontend and avoids leaking internal tracebacks to users.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas.common import ErrorResponse

logger = logging.getLogger("krishidrishti.errors")


class AppError(Exception):
    """Base class for expected application errors.

    Raise with an ``error_code`` and a user-safe ``detail`` message.
    """

    def __init__(
        self,
        detail: str,
        *,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_code: str | None = None,
    ):
        self.detail = detail
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(detail)


class NotFoundError(AppError):
    def __init__(self, detail: str = "Resource not found", error_code: str | None = None):
        super().__init__(detail, status_code=status.HTTP_404_NOT_FOUND, error_code=error_code)


class ForbiddenError(AppError):
    def __init__(self, detail: str = "You do not have permission to access this resource", error_code: str | None = None):
        super().__init__(detail, status_code=status.HTTP_403_FORBIDDEN, error_code=error_code)


class ConflictError(AppError):
    def __init__(self, detail: str = "Conflict with existing resource", error_code: str | None = None):
        super().__init__(detail, status_code=status.HTTP_409_CONFLICT, error_code=error_code)


def register_exception_handlers(app: FastAPI) -> None:
    """Register all error handlers on the FastAPI app."""

    @app.exception_handler(AppError)
    async def _app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(detail=exc.detail, error_code=exc.error_code).model_dump(exclude_none=True),
        )

    @app.exception_handler(RequestValidationError)
    async def _validation_error_handler(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        # Keep the validation details but in a clean format.  We log the full
        # detail for debugging but only return a concise message.
        logger.debug("Validation error: %s", exc.errors())
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse(
                detail="Request validation failed. Please check the submitted data.",
                error_code="validation_error",
            ).model_dump(exclude_none=True),
        )

    @app.exception_handler(HTTPException)
    async def _http_error_handler(_request: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(detail=str(exc.detail)).model_dump(exclude_none=True),
        )

    @app.exception_handler(Exception)
    async def _unhandled_error_handler(_request: Request, exc: Exception) -> JSONResponse:
        # Log the full traceback internally, return a generic message to the user.
        logger.exception("Unhandled exception: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                detail="An internal server error occurred. Please try again later.",
                error_code="internal_error",
            ).model_dump(exclude_none=True),
        )
