"""Domain exception hierarchy with automatic FastAPI HTTP mapping."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class DomainError(Exception):
    """Base for all domain-level errors."""
    http_status: int = 500
    error_code: str = "DOMAIN_ERROR"

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


class EntityNotFoundError(DomainError):
    http_status = 404
    error_code = "NOT_FOUND"

    def __init__(self, entity: str, id: str) -> None:
        super().__init__(f"{entity} '{id}' not found")
        self.entity = entity
        self.id = id


class TenantMismatchError(DomainError):
    http_status = 403
    error_code = "TENANT_MISMATCH"

    def __init__(self, entity: str, id: str) -> None:
        super().__init__(f"{entity} '{id}' does not belong to this tenant")


class ValidationFailedError(DomainError):
    http_status = 422
    error_code = "VALIDATION_FAILED"


class ConflictError(DomainError):
    http_status = 409
    error_code = "CONFLICT"


class PermissionDeniedError(DomainError):
    http_status = 403
    error_code = "PERMISSION_DENIED"


def register_domain_exception_handlers(app: FastAPI) -> None:
    """Wire domain exceptions → structured JSON HTTP responses."""

    @app.exception_handler(DomainError)
    async def _handle(request: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.http_status,
            content={"error": exc.error_code, "detail": exc.detail},
        )
