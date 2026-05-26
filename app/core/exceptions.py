"""Domain exception hierarchy with automatic FastAPI HTTP mapping.

Error responses follow RFC 7807 Problem Details (https://tools.ietf.org/html/rfc7807):
  {
    "type":     "https://valeo-erp.de/errors/<code>",
    "title":    "<Human-readable title>",
    "status":   <HTTP status code>,
    "detail":   "<Specific error detail>",
    "instance": "<Request URL path>"
  }

Backward-compatibility: the legacy "error" and "detail" fields are also included
so existing clients don't break during the migration period.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

_BASE_URI = "https://valeo-erp.de/errors"

_TITLES: dict[str, str] = {
    "DOMAIN_ERROR": "Interner Fehler",
    "NOT_FOUND": "Nicht gefunden",
    "TENANT_MISMATCH": "Mandanten-Konflikt",
    "VALIDATION_FAILED": "Validierungsfehler",
    "CONFLICT": "Konflikt",
    "PERMISSION_DENIED": "Zugriff verweigert",
}


def _problem(
    status: int,
    code: str,
    detail: str,
    instance: str,
) -> dict:
    """Build RFC 7807 Problem Details body with backward-compat fields."""
    return {
        # RFC 7807 fields
        "type": f"{_BASE_URI}/{code.lower().replace('_', '-')}",
        "title": _TITLES.get(code, code),
        "status": status,
        "detail": detail,
        "instance": instance,
        # Backward-compat (clients that already use "error" / "detail")
        "error": code,
    }


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
    """Wire domain exceptions → RFC 7807 JSON HTTP responses."""

    @app.exception_handler(DomainError)
    async def _handle_domain(request: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.http_status,
            content=_problem(
                status=exc.http_status,
                code=exc.error_code,
                detail=exc.detail,
                instance=str(request.url.path),
            ),
            media_type="application/problem+json",
        )
