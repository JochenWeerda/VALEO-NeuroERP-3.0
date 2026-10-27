"""Row-level security for tables freed by the valeo_system connection (RLS plan P6).

Cross-tenant workers now connect as valeo_system (BYPASSRLS) through
``app.core.database.system_session()``. Tables that waited only because such workers read
them across tenants (reason ``uebergreifend`` in docs/admin/rls-rollout.json) get the same
policy as the pilot.
"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "rls_system_role_20261026"
down_revision = "rls_rollout_20261026"
branch_labels = None
depends_on = None

SYSTEM_ROLE_TABLES = (
    "domain_erp.business_partners",
)


def _tenant_expr(bind, table: str) -> str | None:
    schema, name = table.split(".")
    data_type = bind.execute(
        sa.text(
            "SELECT data_type FROM information_schema.columns "
            "WHERE table_schema = :s AND table_name = :n AND column_name = 'tenant_id'"
        ),
        {"s": schema, "n": name},
    ).scalar()
    if data_type is None:
        return None
    return "tenant_id::text" if data_type == "uuid" else "tenant_id"


def enable_tenant_isolation(bind, table: str) -> bool:
    if bind.execute(sa.text("SELECT to_regclass(:t)"), {"t": table}).scalar() is None:
        return False
    column = _tenant_expr(bind, table)
    if column is None:
        raise RuntimeError(f"{table} hat keine Spalte tenant_id")
    op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
    op.execute(f"DROP POLICY IF EXISTS tenant_isolation ON {table}")
    op.execute(
        f"CREATE POLICY tenant_isolation ON {table} "
        f"USING ({column} = public.rls_current_tenant() "
        f"OR ({column} = 'system' AND public.rls_current_tenant() IS NOT NULL)) "
        f"WITH CHECK ({column} = public.rls_current_tenant())"
    )
    return True


def disable_tenant_isolation(bind, table: str) -> None:
    if bind.execute(sa.text("SELECT to_regclass(:t)"), {"t": table}).scalar() is None:
        return
    op.execute(f"DROP POLICY IF EXISTS tenant_isolation ON {table}")
    op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")


def upgrade() -> None:
    bind = op.get_bind()
    for table in SYSTEM_ROLE_TABLES:
        enable_tenant_isolation(bind, table)


def downgrade() -> None:
    bind = op.get_bind()
    for table in SYSTEM_ROLE_TABLES:
        disable_tenant_isolation(bind, table)
