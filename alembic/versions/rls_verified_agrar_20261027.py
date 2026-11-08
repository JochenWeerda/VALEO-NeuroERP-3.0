"""RLS for two Agrar tables whose API tenant fallbacks have been removed.

Prerequisite: verified-tenant Biostimulanz adapters and tenant-bound allocation references.
The former heuristic blockers disappeared through the accompanying API corrections.
Operation-specific policies isolate these business rows; no shared read is justified.
"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "rls_verified_agrar_20261027"
down_revision = "rls_docflow_child_keys_20261027"
branch_labels = None
depends_on = None

VERIFIED_AGRAR_TABLES = (
    "domain_agrar.agrar_biostimulanzien",
    "domain_inventory.agrar_contract_allocations",
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
    # SELECT may expose shared reference data. A permissive ALL policy would also
    # authorize DELETE and allow UPDATE to take ownership of a visible system row.
    owned = f"{column} = public.rls_current_tenant()"
    readable = owned
    for suffix in ("", "_select", "_insert", "_update", "_delete"):
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation{suffix} ON {table}")
    op.execute(f"CREATE POLICY tenant_isolation_select ON {table} FOR SELECT USING ({readable})")
    op.execute(f"CREATE POLICY tenant_isolation_insert ON {table} FOR INSERT WITH CHECK ({owned})")
    op.execute(f"CREATE POLICY tenant_isolation_update ON {table} FOR UPDATE USING ({owned}) WITH CHECK ({owned})")
    op.execute(f"CREATE POLICY tenant_isolation_delete ON {table} FOR DELETE USING ({owned})")
    return True


def disable_tenant_isolation(bind, table: str) -> None:
    if bind.execute(sa.text("SELECT to_regclass(:t)"), {"t": table}).scalar() is None:
        return
    for suffix in ("", "_select", "_insert", "_update", "_delete"):
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation{suffix} ON {table}")
    op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")


def upgrade() -> None:
    bind = op.get_bind()
    for table in VERIFIED_AGRAR_TABLES:
        enable_tenant_isolation(bind, table)


def downgrade() -> None:
    bind = op.get_bind()
    for table in VERIFIED_AGRAR_TABLES:
        disable_tenant_isolation(bind, table)
