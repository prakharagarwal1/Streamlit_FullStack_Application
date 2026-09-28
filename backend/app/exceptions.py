"""Custom exception hierarchy + FastAPI exception handlers."""
from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, OperationalError
from pydantic import ValidationError


class AppException(Exception):
    """Base exception carrying an HTTP status code and detail."""

    def __init__(self, detail: str, status_code: int = 400) -> None:
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


class NotFoundError(AppException):
    def __init__(self, detail: str = "Resource not found") -> None:
        super().__init__(detail, status_code=404)


class UnauthorizedError(AppException):
    def __init__(self, detail: str = "Not authenticated") -> None:
        super().__init__(detail, status_code=401)


class ForbiddenError(AppException):
    def __init__(self, detail: str = "Forbidden") -> None:
        super().__init__(detail, status_code=403)


class ConflictError(AppException):
    def __init__(self, detail: str = "Resource already exists") -> None:
        super().__init__(detail, status_code=409)


class ValidationError(AppException):
    def __init__(self, detail: str = "Validation error") -> None:
        super().__init__(detail, status_code=422)


class RateLimitError(AppException):
    def __init__(self, detail: str = "Too many requests") -> None:
        super().__init__(detail, status_code=429)


def register_exception_handlers(app: FastAPI) -> FastAPI:
    """Attach structured error handlers to a FastAPI app."""

    @app.exception_handler(AppException)
    async def handle_app_exception(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": True, "detail": exc.detail, "path": request.url.path},
        )

    @app.exception_handler(RequestValidationError)
    async def handle_request_validation(request: Request, exc: RequestValidationError):
        errors = exc.errors()
        # Simplify the pydantic error output for clients.
        simplified = [
            {"loc": list(err.get("loc", [])), "msg": err.get("msg", ""), "type": err.get("type", "")}
            for err in errors
        ]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": True,
                "detail": "Validation failed",
                "errors": simplified,
                "path": request.url.path,
            },
        )

    @app.exception_handler(ValidationError)
    async def handle_pydantic_validation(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error": True, "detail": str(exc), "path": request.url.path},
        )

    @app.exception_handler(IntegrityError)
    async def handle_integrity_error(request: Request, exc: IntegrityError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"error": True, "detail": "Database integrity constraint violated", "path": request.url.path},
        )

    @app.exception_handler(OperationalError)
    async def handle_operational_error(request: Request, exc: OperationalError):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"error": True, "detail": "Database unavailable", "path": request.url.path},
        )

    @app.exception_handler(Exception)
    async def handle_generic(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": True,
                "detail": "Internal server error",
                "path": request.url.path,
            },
        )

    return app