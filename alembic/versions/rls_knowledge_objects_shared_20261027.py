"""Row-level security for knowledge objects: own objects plus shared product knowledge.

Knowledge objects of the shared tenant 'system' are product knowledge (SOPs, standards)
delivered with the system and maintained centrally; every tenant reads them
(docs/admin/rls-exceptions.json -> system_lesbar). Since SYSTEM-TENANT-FALLBACK-20261027 new
objects belong to the creating tenant (knowledge_api, process kernel) and tenants change only
their own objects (403 on shared ones).

Separate policies per command, named like P3/P5/P6: SELECT own + 'system'; INSERT, UPDATE and
DELETE own only. Placeholder tenants ('', 'default') block the migration; 'system' rows are
the shared objects and stay.
"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "rls_knowledge_objects_shared_20261027"
down_revision = "rls_booking_templates_shared_20261027"
branch_labels = None
depends_on = None

TABLE = "domain_shared.knowledge_objects"
OWN = "tenant_id = public.rls_current_tenant()"
SHARED = f"{OWN} OR (tenant_id = 'system' AND public.rls_current_tenant() IS NOT NULL)"
POLICIES = tuple(f"tenant_isolation_{kind}" for kind in ("select", "insert", "update", "delete"))


def upgrade() -> None:
    bind = op.get_bind()
    if bind.execute(sa.text("SELECT to_regclass(:t)"), {"t": TABLE}).scalar() is None:
        return
    op.execute(f"LOCK TABLE {TABLE} IN ACCESS EXCLUSIVE MODE")
    unclear = bind.execute(sa.text(
        f"SELECT count(*) FROM {TABLE} WHERE tenant_id IS NULL OR tenant_id IN ('', 'default')")).scalar()
    if unclear:
        raise RuntimeError(f"{TABLE}: {unclear} Zeilen ohne eindeutigen Mandanten; Herkunft klaeren")
    op.execute(f"ALTER TABLE {TABLE} ENABLE ROW LEVEL SECURITY")
    for name in POLICIES:
        op.execute(f"DROP POLICY IF EXISTS {name} ON {TABLE}")
    op.execute(f"CREATE POLICY tenant_isolation_select ON {TABLE} FOR SELECT USING ({SHARED})")
    op.execute(f"CREATE POLICY tenant_isolation_insert ON {TABLE} FOR INSERT WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_update ON {TABLE} FOR UPDATE USING ({OWN}) WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_delete ON {TABLE} FOR DELETE USING ({OWN})")


def downgrade() -> None:
    bind = op.get_bind()
    if bind.execute(sa.text("SELECT to_regclass(:t)"), {"t": TABLE}).scalar() is None:
        return
    for name in POLICIES:
        op.execute(f"DROP POLICY IF EXISTS {name} ON {TABLE}")
    op.execute(f"ALTER TABLE {TABLE} DISABLE ROW LEVEL SECURITY")
