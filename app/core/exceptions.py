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

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

_BASE_URI = "https://valeo-erp.de/errors"

_TITLES: dict[str, str] = {
    "DOMAIN_ERROR": "Interner Fehler",
    "BAD_REQUEST": "Ungültige Anfrage",
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


class BadRequestError(DomainError):
    http_status = 400
    error_code = "BAD_REQUEST"


class ValidationFailedError(DomainError):
    http_status = 422
    error_code = "VALIDATION_FAILED"


class ConflictError(DomainError):
    http_status = 409
    error_code = "CONFLICT"


class PermissionDeniedError(DomainError):
    http_status = 403
    error_code = "PERMISSION_DENIED"


_HTTP_CODES: dict[int, tuple[str, str]] = {
    400: ("BAD_REQUEST", "Ungültige Anfrage"),
    401: ("UNAUTHORIZED", "Nicht authentifiziert"),
    403: ("FORBIDDEN", "Zugriff verweigert"),
    404: ("NOT_FOUND", "Nicht gefunden"),
    405: ("METHOD_NOT_ALLOWED", "Methode nicht erlaubt"),
    409: ("CONFLICT", "Konflikt"),
    422: ("UNPROCESSABLE_ENTITY", "Validierungsfehler"),
    429: ("TOO_MANY_REQUESTS", "Zu viele Anfragen"),
    503: ("SERVICE_UNAVAILABLE", "Dienst nicht verfügbar"),
}


def register_domain_exception_handlers(app: FastAPI) -> None:
    """Wire all exceptions → RFC 7807 Problem Details (application/problem+json).

    Backward-compat: the ``"detail"`` field is preserved so existing clients
    that already parse ``{"detail": "..."}`` keep working during migration.
    """

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

    @app.exception_handler(HTTPException)
    async def _handle_http(request: Request, exc: HTTPException) -> JSONResponse:
        code, title = _HTTP_CODES.get(exc.status_code, ("HTTP_ERROR", f"HTTP {exc.status_code}"))
        # Preserve the original detail type (str or dict) for backward-compatibility:
        # existing clients may parse structured dict details from HTTPException.
        detail = exc.detail if isinstance(exc.detail, (str, dict, list)) else str(exc.detail)
        body = {
            "type": f"{_BASE_URI}/{code.lower().replace('_', '-')}",
            "title": title,
            "status": exc.status_code,
            "detail": detail,
            "instance": str(request.url.path),
            "error": code,
        }
        headers = getattr(exc, "headers", None) or {}
        return JSONResponse(
            status_code=exc.status_code,
            content=body,
            media_type="application/problem+json",
            headers=headers,
        )

    @app.exception_handler(RequestValidationError)
    async def _handle_validation(request: Request, exc: RequestValidationError) -> JSONResponse:
        # Pydantic v2 errors() may include non-JSON-serializable objects in "ctx"
        # (e.g. ValueError instances). Sanitise by converting ctx values to str.
        raw_errors = exc.errors()
        errors = []
        for e in raw_errors:
            entry = dict(e)
            if "ctx" in entry:
                entry["ctx"] = {k: str(v) for k, v in entry["ctx"].items()}
            errors.append(entry)

        first = errors[0] if errors else {}
        loc = " → ".join(str(p) for p in first.get("loc", []))
        msg = first.get("msg", "Validierungsfehler")
        detail = f"{loc}: {msg}" if loc else str(msg)
        body = {
            "type": f"{_BASE_URI}/validation-failed",
            "title": "Validierungsfehler",
            "status": 422,
            "detail": detail,
            "instance": str(request.url.path),
            "error": "VALIDATION_FAILED",
            "errors": errors,
        }
        return JSONResponse(
            status_code=422,
            content=body,
            media_type="application/problem+json",
        )
