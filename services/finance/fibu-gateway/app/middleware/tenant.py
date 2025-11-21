"""Middleware für Tenant-Kontext."""

from __future__ import annotations

from typing import Callable

from fastapi import Request, Response

from app.config import settings

TENANT_HEADER = "x-tenant-id"


async def tenant_middleware(request: Request, call_next: Callable) -> Response:
    tenant = request.headers.get(TENANT_HEADER, settings.DEFAULT_TENANT).strip() or settings.DEFAULT_TENANT
    request.state.tenant_id = tenant
    response = await call_next(request)
    response.headers[TENANT_HEADER] = tenant
    return response

