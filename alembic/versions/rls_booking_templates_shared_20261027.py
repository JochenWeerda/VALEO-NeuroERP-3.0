"""Shared booking templates: 'system' templates readable for every tenant.

User decision 27.10.2026: the booking templates of the shared tenant 'system' (70 on the
grown database) are available to all tenants. ``tenant_isolation_select`` on
``domain_erp.booking_templates`` reads own rows and 'system' rows; insert, update and delete
stay own-only, so a shared template can be read and applied but not changed, deleted or
taken over by a tenant (app/api/v1/endpoints/booking_templates.py answers 403). New shared
templates come only through valeo_system. Reason recorded in docs/admin/rls-exceptions.json
-> system_lesbar.
"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "rls_booking_templates_shared_20261027"
down_revision = "rls_system_read_justified_20261027"
branch_labels = None
depends_on = None

TABLE = "domain_erp.booking_templates"
OWN = "tenant_id = public.rls_current_tenant()"
SHARED = f"{OWN} OR (tenant_id = 'system' AND public.rls_current_tenant() IS NOT NULL)"


def _select(using: str) -> None:
    if op.get_bind().execute(sa.text("SELECT to_regclass(:t)"), {"t": TABLE}).scalar() is None:
        return
    op.execute(f"DROP POLICY IF EXISTS tenant_isolation_select ON {TABLE}")
    op.execute(f"CREATE POLICY tenant_isolation_select ON {TABLE} FOR SELECT USING ({using})")


def upgrade() -> None:
    _select(SHARED)


def downgrade() -> None:
    _select(OWN)
