"""Tenant registry for background work (RLS plan P1).

Workers do not discover tenants by ``SELECT DISTINCT tenant_id`` over business tables: under
row-level security those reads see only the current tenant. ``domain_shared.tenants`` carries
no tenant column (class D in docs/admin/rls-inventory.json) and stays readable; it is the one
list of tenants. The work itself runs per tenant inside ``tenant_scope``.
"""

from __future__ import annotations

import logging
from typing import Callable, TypeVar

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.tenant_context import tenant_scope

logger = logging.getLogger(__name__)

T = TypeVar("T")


def active_tenant_ids(db: Session) -> list[str]:
    return list(
        db.execute(text("SELECT id FROM domain_shared.tenants WHERE is_active ORDER BY id")).scalars()
    )


def for_each_tenant(reason: str, work: Callable[[str], T]) -> dict[str, T | Exception]:
    """Run ``work(tenant_id)`` once per active tenant, each in its own ``tenant_scope``.

    A failing tenant does not stop the others; its exception is returned in the result map.
    """
    from app.core.database import SessionLocal

    registry = SessionLocal()
    try:
        tenants = active_tenant_ids(registry)
    finally:
        registry.close()

    results: dict[str, T | Exception] = {}
    for tenant_id in tenants:
        with tenant_scope(tenant_id, reason):
            try:
                results[tenant_id] = work(tenant_id)
            except Exception as exc:  # tenant isolation: one tenant must not block the rest
                logger.error("%s: Mandant %s fehlgeschlagen: %s", reason, tenant_id, exc)
                results[tenant_id] = exc
    return results
