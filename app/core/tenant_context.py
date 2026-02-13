"""
Tenant context handling for request-scoped multi-tenancy.
"""

from __future__ import annotations

from contextvars import ContextVar, Token

from app.core.config import settings

_tenant_id_ctx: ContextVar[str] = ContextVar("tenant_id", default=settings.DEFAULT_TENANT_ID)


def get_current_tenant_id() -> str:
    return _tenant_id_ctx.get()


def set_current_tenant_id(tenant_id: str) -> Token[str]:
    effective = (tenant_id or "").strip() or settings.DEFAULT_TENANT_ID
    return _tenant_id_ctx.set(effective)


def reset_current_tenant_id(token: Token[str]) -> None:
    _tenant_id_ctx.reset(token)

