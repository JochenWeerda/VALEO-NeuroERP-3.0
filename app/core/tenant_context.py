"""
Tenant context handling for request-scoped multi-tenancy.

Fail-closed (RLS plan P1, docs/architecture/rls-mandantenkernel-plan.md): without a tenant
there is no silent fallback to ``DEFAULT_TENANT_ID``. Requests get their tenant from the
middleware, which the token binding (``app.core.tenant_binding``) holds equal to the verified
token tenant. Code outside a request states its context explicitly:

- ``tenant_scope(tenant_id, reason)`` for work on behalf of one tenant (workers per tenant),
- ``cross_tenant_scope(reason)`` for reads across tenants (tenant lists, outbox delivery).

Under row-level security a cross-tenant scope sees nothing through the application role; it
is the marker for the ``valeo_system`` connection (plan P6).
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from contextvars import ContextVar, Token
from typing import Iterator, Optional

logger = logging.getLogger(__name__)

_tenant_id_ctx: ContextVar[Optional[str]] = ContextVar("tenant_id", default=None)
_cross_tenant_ctx: ContextVar[Optional[str]] = ContextVar("cross_tenant_reason", default=None)


class TenantContextMissing(RuntimeError):
    """Tenant-bound work was attempted without a tenant context."""


def get_current_tenant_id() -> str:
    tenant_id = _tenant_id_ctx.get()
    if not tenant_id:
        raise TenantContextMissing(
            "Kein Mandantenkontext: Request ohne Mandant oder Hintergrundarbeit ohne tenant_scope()"
        )
    return tenant_id


def current_tenant_or_none() -> Optional[str]:
    """Tenant of the current context, ``None`` if there is none (never a default)."""
    return _tenant_id_ctx.get() or None


def cross_tenant_reason() -> Optional[str]:
    return _cross_tenant_ctx.get()


def set_current_tenant_id(tenant_id: str) -> Token:
    effective = (tenant_id or "").strip()
    if not effective:
        raise TenantContextMissing("Leerer Mandant wird nicht gesetzt")
    return _tenant_id_ctx.set(effective)


def reset_current_tenant_id(token: Token) -> None:
    _tenant_id_ctx.reset(token)


@contextmanager
def tenant_scope(tenant_id: str, reason: str) -> Iterator[str]:
    """Run the block for exactly one tenant, e.g. one pass of a worker loop."""
    if not reason:
        raise ValueError("tenant_scope braucht einen Grund")
    token = set_current_tenant_id(tenant_id)
    cross = _cross_tenant_ctx.set(None)
    logger.debug("tenant_scope tenant=%s reason=%s", tenant_id, reason)
    try:
        yield tenant_id
    finally:
        _cross_tenant_ctx.reset(cross)
        reset_current_tenant_id(token)


@contextmanager
def cross_tenant_scope(reason: str) -> Iterator[None]:
    """Mark deliberate cross-tenant work; clears any tenant so nothing is attributed by accident."""
    if not reason:
        raise ValueError("cross_tenant_scope braucht einen Grund")
    token = _tenant_id_ctx.set(None)
    cross = _cross_tenant_ctx.set(reason)
    logger.info("cross_tenant_scope reason=%s", reason)
    try:
        yield
    finally:
        _cross_tenant_ctx.reset(cross)
        _tenant_id_ctx.reset(token)
