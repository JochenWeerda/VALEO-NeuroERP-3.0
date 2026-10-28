"""Row-level security for domain_logistics (tours, stops, events, disposition checks, ePOD settlements, freight
tariffs, carrier invoices).

Revision ID: rls_domain_logistics_20261028
Revises: rls_domain_ops_20261028

All seven tables belong to one tenant: separate policies per command, no shared 'system' rows. Freight tariffs used
``tenant_id IS NULL`` as "global"; live there were none and the API could not create them, so they are not kept as a
shared family (that would need a decision). ``tenant_id`` becomes NOT NULL with the context tenant as default.

There were no foreign keys at all between tours and their stops, events, checks, settlements and carrier invoices.
They hang under their parent over ``(key, tenant_id)``; FK checks bypass RLS, so only the key stops a row pointing at
a tour of another tenant. Rows without a tenant, orphans and rows pointing at a parent of another tenant block the
migration.

Not here: ``domain_log.*`` (loading, owned by LOADING-ATOMIC-ACTOR).
"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "rls_domain_logistics_20261028"
down_revision = "rls_domain_ops_20261028"
branch_labels = None
depends_on = None

LOG = "domain_logistics"
TOURS, STOPS = f"{LOG}.tours", f"{LOG}.tour_stops"
POLICY_TABLES = (
    TOURS, STOPS, f"{LOG}.tour_events", f"{LOG}.tour_disposition_checks", f"{LOG}.epod_settlements",
    f"{LOG}.freight_tariffs", f"{LOG}.carrier_invoices",
)
# child, column, parent, parent key, ON DELETE
LINKS = (
    (STOPS, "tour_id", TOURS, "id", "CASCADE"),
    (f"{LOG}.tour_events", "tour_id", TOURS, "id", "CASCADE"),
    (f"{LOG}.tour_disposition_checks", "tour_id", TOURS, "id", "CASCADE"),
    (f"{LOG}.epod_settlements", "tour_id", TOURS, "id", "NO ACTION"),
    (f"{LOG}.epod_settlements", "stop_id", STOPS, "id", "NO ACTION"),
    (f"{LOG}.carrier_invoices", "tour_id", TOURS, "id", "NO ACTION"),
)
OWN = "tenant_id = public.rls_current_tenant()"
POLICIES = tuple(f"tenant_isolation_{kind}" for kind in ("select", "insert", "update", "delete"))


def _exists(bind, table: str) -> bool:
    return bind.execute(sa.text("SELECT to_regclass(:t)"), {"t": table}).scalar() is not None


def _name(table: str) -> str:
    return table.split(".")[1]


def _has_unique(bind, parent: str, key: str) -> bool:
    return bind.execute(sa.text(
        "SELECT 1 FROM pg_constraint k WHERE k.conrelid = to_regclass(:p) AND k.contype IN ('u', 'p') "
        "AND (SELECT array_agg(a.attname::text ORDER BY a.attname) FROM pg_attribute a "
        "     WHERE a.attrelid = k.conrelid AND a.attnum = ANY(k.conkey)) = ARRAY[:k, 'tenant_id']::text[]"),
        {"p": parent, "k": key}).scalar() is not None


def _enable(table: str) -> None:
    op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
    for name in POLICIES:
        op.execute(f"DROP POLICY IF EXISTS {name} ON {table}")
    op.execute(f"CREATE POLICY tenant_isolation_select ON {table} FOR SELECT USING ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_insert ON {table} FOR INSERT WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_update ON {table} FOR UPDATE USING ({OWN}) WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_delete ON {table} FOR DELETE USING ({OWN})")


def upgrade() -> None:
    bind = op.get_bind()
    present = [t for t in POLICY_TABLES if _exists(bind, t)]
    links = [link for link in LINKS if _exists(bind, link[0]) and _exists(bind, link[2])]
    op.execute(f"LOCK TABLE {', '.join(present)} IN ACCESS EXCLUSIVE MODE")

    for table in present:
        unclear = bind.execute(sa.text(
            f"SELECT count(*) FROM {table} WHERE tenant_id IS NULL "
            "OR tenant_id IN ('', 'default', 'system', 'legacy-unassigned')")).scalar()
        if unclear:
            raise RuntimeError(
                f"{table}: {unclear} Zeilen ohne eindeutigen Mandanten (bei Frachttarifen: 'globale' Tarife); "
                "Herkunft klaeren, nicht pauschal zuordnen")
    for table in present:
        op.execute(f"ALTER TABLE {table} ALTER COLUMN tenant_id SET NOT NULL")
        op.execute(f"ALTER TABLE {table} ALTER COLUMN tenant_id SET DEFAULT public.rls_current_tenant()")

    for child, column, parent, key, _ in links:
        orphans = bind.execute(sa.text(
            f"SELECT count(*) FROM {child} c WHERE c.{column} IS NOT NULL "
            f"AND NOT EXISTS (SELECT 1 FROM {parent} p WHERE p.{key} = c.{column})")).scalar()
        foreign = bind.execute(sa.text(
            f"SELECT count(*) FROM {child} c JOIN {parent} p ON p.{key} = c.{column} "
            "WHERE p.tenant_id IS DISTINCT FROM c.tenant_id")).scalar()
        if orphans or foreign:
            raise RuntimeError(f"{child}.{column}: {orphans} Zeilen ohne {parent}, {foreign} auf einen fremden Mandanten")
    for parent, key in sorted({(link[2], link[3]) for link in links}):
        if not _has_unique(bind, parent, key):
            op.execute(f"ALTER TABLE {parent} ADD CONSTRAINT uq_{_name(parent)}_{key}_tenant UNIQUE ({key}, tenant_id)")
    for child, column, parent, key, on_delete in links:
        op.execute(
            f"ALTER TABLE {child} ADD CONSTRAINT fk_{_name(child)}_{column}_tenant FOREIGN KEY ({column}, tenant_id) "
            f"REFERENCES {parent} ({key}, tenant_id) ON DELETE {on_delete}"
        )

    for table in present:
        _enable(table)


def downgrade() -> None:
    bind = op.get_bind()
    for table in POLICY_TABLES:
        if _exists(bind, table):
            for name in POLICIES:
                op.execute(f"DROP POLICY IF EXISTS {name} ON {table}")
            op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")
    for child, column, _parent, _key, _ in LINKS:
        if _exists(bind, child):
            op.execute(f"ALTER TABLE {child} DROP CONSTRAINT IF EXISTS fk_{_name(child)}_{column}_tenant")
    for parent, key in sorted({(link[2], link[3]) for link in LINKS}):
        if _exists(bind, parent):
            op.execute(f"ALTER TABLE {parent} DROP CONSTRAINT IF EXISTS uq_{_name(parent)}_{key}_tenant")
    for table in POLICY_TABLES:
        if _exists(bind, table):
            op.execute(f"ALTER TABLE {table} ALTER COLUMN tenant_id DROP DEFAULT")
            if table not in (f"{LOG}.carrier_invoices",):
                op.execute(f"ALTER TABLE {table} ALTER COLUMN tenant_id DROP NOT NULL")
