"""Row-level security for domain_erp part 1 (bank accounts, creditors, debitors, dunning notices, gift cards,
open items, connector run items).

Revision ID: rls_domain_erp_20261028
Revises: rls_nutrient_compositions_20261028

All seven tables belong to one tenant: separate policies per command, no shared 'system' rows (live: 0 rows in
each). ``tenant_id`` becomes NOT NULL with the context tenant as default.

- Creditor and debitor numbers were unique across all tenants (``UNIQUE (creditor_number)``): a second tenant could
  not use number 10001. They are unique per tenant now. The grown database had lost both constraints; the migration
  looks them up by definition, not by name.
- ``fibu_connector_run_items`` had no tenant at all; it takes the tenant of its run and hangs under it over
  ``(run_id, tenant_id)``. FK checks bypass RLS, so only the key stops an item pointing at a run of another tenant.
- ``debitors.customer_id`` points at the customer over ``(customer_id, tenant_id)``; SET NULL clears only the
  reference column.

Not here (part 2): ``offene_posten`` (30 writers, live rows), ``chart_of_accounts`` and ``policy_rules``.
"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "rls_domain_erp_20261028"
down_revision = "rls_nutrient_compositions_20261028"
branch_labels = None
depends_on = None

ERP = "domain_erp"
RUNS, ITEMS = f"{ERP}.fibu_connector_runs", f"{ERP}.fibu_connector_run_items"
DEBITORS, CUSTOMERS = f"{ERP}.debitors", "domain_crm.customers"
POLICY_TABLES = (
    f"{ERP}.bank_accounts", f"{ERP}.creditors", DEBITORS, f"{ERP}.dunning_notices", f"{ERP}.gift_cards",
    f"{ERP}.open_items", ITEMS,
)
# table, number column: unique per tenant instead of system-wide
NUMBERS = ((f"{ERP}.creditors", "creditor_number"), (DEBITORS, "debitor_number"))
OWN = "tenant_id = public.rls_current_tenant()"
POLICIES = tuple(f"tenant_isolation_{kind}" for kind in ("select", "insert", "update", "delete"))
UNCLEAR = "tenant_id IS NULL OR tenant_id IN ('', 'default', 'system', 'legacy-unassigned')"


def _exists(bind, table: str) -> bool:
    return bind.execute(sa.text("SELECT to_regclass(:t)"), {"t": table}).scalar() is not None


def _has_column(bind, table: str, column: str) -> bool:
    return bind.execute(sa.text(
        "SELECT 1 FROM pg_attribute WHERE attrelid = to_regclass(:t) AND attname = :c AND NOT attisdropped"),
        {"t": table, "c": column}).scalar() is not None


def _constraints(bind, table: str, kind: str, columns: list[str], referenced: str | None = None) -> list[str]:
    """Names of constraints of ``kind`` on exactly ``columns`` (optionally referencing ``referenced``)."""
    rows = bind.execute(sa.text(
        "SELECT k.conname FROM pg_constraint k WHERE k.conrelid = to_regclass(:t) AND k.contype = :kind "
        "AND (CAST(:r AS text) IS NULL OR k.confrelid = to_regclass(:r)) "
        "AND (SELECT array_agg(a.attname::text ORDER BY a.attname) FROM pg_attribute a "
        "     WHERE a.attrelid = k.conrelid AND a.attnum = ANY(k.conkey)) = CAST(:cols AS text[])"),
        {"t": table, "kind": kind, "r": referenced, "cols": sorted(columns)}).scalars().all()
    return list(rows)


def _unique_indexes(bind, table: str, columns: list[str]) -> list[tuple[str, str | None]]:
    """(index, owning constraint or None) of unique indexes on exactly ``columns``; the grown database has both forms."""
    rows = bind.execute(sa.text(
        "SELECT i.indexrelid::regclass::text, k.conname FROM pg_index i "
        "LEFT JOIN pg_constraint k ON k.conindid = i.indexrelid AND k.conrelid = i.indrelid "
        "WHERE i.indrelid = to_regclass(:t) AND i.indisunique AND NOT i.indisprimary AND i.indpred IS NULL "
        "AND (SELECT array_agg(a.attname::text ORDER BY a.attname) FROM pg_attribute a "
        "     WHERE a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)) = CAST(:cols AS text[])"),
        {"t": table, "cols": sorted(columns)}).all()
    return [(r[0], r[1]) for r in rows]


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
    if not present:
        return
    locked = present + [t for t in (RUNS, CUSTOMERS) if _exists(bind, t)]
    op.execute(f"LOCK TABLE {', '.join(locked)} IN ACCESS EXCLUSIVE MODE")

    if ITEMS in present:
        if not _has_column(bind, ITEMS, "tenant_id"):
            op.execute(f"ALTER TABLE {ITEMS} ADD COLUMN tenant_id character varying(36)")
        op.execute(f"UPDATE {ITEMS} i SET tenant_id = r.tenant_id FROM {RUNS} r WHERE r.id = i.run_id AND i.tenant_id IS NULL")

    for table in present:
        unclear = bind.execute(sa.text(f"SELECT count(*) FROM {table} WHERE {UNCLEAR}")).scalar()  # nosec B608
        if unclear:
            raise RuntimeError(f"{table}: {unclear} Zeilen ohne eindeutigen Mandanten; Herkunft klaeren, nicht pauschal zuordnen")
    for table, column in NUMBERS:
        if table in present:
            doubled = bind.execute(sa.text(
                f"SELECT count(*) FROM (SELECT 1 FROM {table} GROUP BY tenant_id, {column} HAVING count(*) > 1) d"
            )).scalar()  # nosec B608
            if doubled:
                raise RuntimeError(f"{table}.{column}: {doubled} Nummern mehrfach im selben Mandanten")
    if ITEMS in present:
        foreign = bind.execute(sa.text(
            f"SELECT count(*) FROM {ITEMS} i JOIN {RUNS} r ON r.id = i.run_id WHERE r.tenant_id IS DISTINCT FROM i.tenant_id"
        )).scalar()  # nosec B608
        if foreign:
            raise RuntimeError(f"{ITEMS}: {foreign} Positionen auf einen Lauf eines anderen Mandanten")
    if DEBITORS in present and _exists(bind, CUSTOMERS):
        foreign = bind.execute(sa.text(
            f"SELECT count(*) FROM {DEBITORS} d JOIN {CUSTOMERS} c ON c.id = d.customer_id "
            "WHERE c.tenant_id IS DISTINCT FROM d.tenant_id")).scalar()  # nosec B608
        orphans = bind.execute(sa.text(
            f"SELECT count(*) FROM {DEBITORS} d WHERE d.customer_id IS NOT NULL "
            f"AND NOT EXISTS (SELECT 1 FROM {CUSTOMERS} c WHERE c.id = d.customer_id)")).scalar()  # nosec B608
        if foreign or orphans:
            raise RuntimeError(f"{DEBITORS}.customer_id: {orphans} ohne Kunde, {foreign} auf einen Kunden eines anderen Mandanten")

    for table in present:
        op.execute(f"ALTER TABLE {table} ALTER COLUMN tenant_id SET NOT NULL")
        op.execute(f"ALTER TABLE {table} ALTER COLUMN tenant_id SET DEFAULT public.rls_current_tenant()")

    for table, column in NUMBERS:
        if table not in present:
            continue
        name = table.split(".")[1]
        for index, constraint in _unique_indexes(bind, table, [column]):
            if constraint:
                op.execute(f"ALTER TABLE {table} DROP CONSTRAINT {constraint}")
            else:
                op.execute(f"DROP INDEX {index}")
        if not _unique_indexes(bind, table, [column, "tenant_id"]):
            op.execute(f"ALTER TABLE {table} ADD CONSTRAINT uq_{name}_tenant_{column} UNIQUE (tenant_id, {column})")

    if ITEMS in present:
        if not _unique_indexes(bind, RUNS, ["id", "tenant_id"]):
            op.execute(f"ALTER TABLE {RUNS} ADD CONSTRAINT uq_fibu_connector_runs_id_tenant UNIQUE (id, tenant_id)")
        for old in _constraints(bind, ITEMS, "f", ["run_id"], RUNS):
            op.execute(f"ALTER TABLE {ITEMS} DROP CONSTRAINT {old}")
        op.execute(
            f"ALTER TABLE {ITEMS} ADD CONSTRAINT fk_fibu_connector_run_items_run_id_tenant FOREIGN KEY (run_id, tenant_id) "
            f"REFERENCES {RUNS} (id, tenant_id) ON DELETE CASCADE"
        )

    if DEBITORS in present and _exists(bind, CUSTOMERS):
        if not _unique_indexes(bind, CUSTOMERS, ["id", "tenant_id"]):
            op.execute(f"ALTER TABLE {CUSTOMERS} ADD CONSTRAINT uq_customers_id_tenant UNIQUE (id, tenant_id)")
        for old in _constraints(bind, DEBITORS, "f", ["customer_id"], CUSTOMERS):
            op.execute(f"ALTER TABLE {DEBITORS} DROP CONSTRAINT {old}")
        op.execute(
            f"ALTER TABLE {DEBITORS} ADD CONSTRAINT fk_debitors_customer_id_tenant FOREIGN KEY (customer_id, tenant_id) "
            f"REFERENCES {CUSTOMERS} (id, tenant_id) ON DELETE SET NULL (customer_id)"
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
    if _exists(bind, DEBITORS):
        op.execute(f"ALTER TABLE {DEBITORS} DROP CONSTRAINT IF EXISTS fk_debitors_customer_id_tenant")
        if _exists(bind, CUSTOMERS):
            op.execute(f"ALTER TABLE {DEBITORS} ADD CONSTRAINT debitors_customer_id_fkey "
                       f"FOREIGN KEY (customer_id) REFERENCES {CUSTOMERS} (id)")
    if _exists(bind, CUSTOMERS):
        op.execute(f"ALTER TABLE {CUSTOMERS} DROP CONSTRAINT IF EXISTS uq_customers_id_tenant")
    if _exists(bind, ITEMS):
        op.execute(f"ALTER TABLE {ITEMS} DROP CONSTRAINT IF EXISTS fk_fibu_connector_run_items_run_id_tenant")
        op.execute(f"ALTER TABLE {ITEMS} ADD CONSTRAINT fibu_connector_run_items_run_id_fkey "
                   f"FOREIGN KEY (run_id) REFERENCES {RUNS} (id) ON DELETE CASCADE")
        op.execute(f"ALTER TABLE {ITEMS} DROP COLUMN IF EXISTS tenant_id")
    if _exists(bind, RUNS):
        op.execute(f"ALTER TABLE {RUNS} DROP CONSTRAINT IF EXISTS uq_fibu_connector_runs_id_tenant")
    for table, column in NUMBERS:
        if _exists(bind, table):
            name = table.split(".")[1]
            op.execute(f"ALTER TABLE {table} DROP CONSTRAINT IF EXISTS uq_{name}_tenant_{column}")
            op.execute(f"ALTER TABLE {table} ADD CONSTRAINT {name}_{column}_key UNIQUE ({column})")
            # A per-tenant unique index that existed before (ensure_creditors_table_20260304) stays.
    for table in POLICY_TABLES:
        if _exists(bind, table) and table != ITEMS:
            op.execute(f"ALTER TABLE {table} ALTER COLUMN tenant_id DROP DEFAULT")
            if table not in (f"{ERP}.dunning_notices", f"{ERP}.gift_cards", f"{ERP}.open_items"):
                op.execute(f"ALTER TABLE {table} ALTER COLUMN tenant_id DROP NOT NULL")
