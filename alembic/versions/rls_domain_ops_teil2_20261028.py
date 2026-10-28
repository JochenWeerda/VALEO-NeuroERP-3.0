"""Row-level security for domain_ops part 2: the ten tables without a tenant column that are empty live.

Revision ID: rls_domain_ops_teil2_20261028
Revises: rls_domain_erp_20261028

Documents and their versions, vehicle fines, damages, status history and trips, framework contracts, scales,
weighings and the drop-shipment freight tariffs had **no tenant at all**; their routes read and wrote across tenants.
Live every one of them is empty, so the column comes in NOT NULL with the context tenant as default and nothing has
to be assigned. A row (on another installation) blocks the migration instead of being assigned blindly.

Children hang under their parent over ``(key, tenant_id)``: FK checks bypass RLS, so only the key stops a row pointing
at a parent of another tenant. ``SET NULL`` clears only the reference column. Framework contract numbers become unique
per tenant instead of system-wide.

Not here: the thirteen tenantless domain_ops tables with live rows (``ops_disposition``, ``ops_labor_auftraege``,
``ops_zertifikate`` ...) - their tenant cannot be derived and is not assigned in bulk. ``ops_fahrzeug_touren.fahrer_id``
keeps its single-column key: ``ops_fahrer`` has no tenant yet (one live row).
"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "rls_domain_ops_teil2_20261028"
down_revision = "rls_domain_erp_20261028"
branch_labels = None
depends_on = None

OPS = "domain_ops"
DOKUMENTE, WAAGEN, FAHRZEUGE = f"{OPS}.ops_dokumente", f"{OPS}.ops_waagen", f"{OPS}.ops_fahrzeuge"
RAHMEN = f"{OPS}.ops_rahmenvertraege"
POLICY_TABLES = (
    DOKUMENTE, f"{OPS}.ops_dokument_versionen", f"{OPS}.ops_fahrzeug_bussgeld", f"{OPS}.ops_fahrzeug_schaeden",
    f"{OPS}.ops_fahrzeug_status_historie", f"{OPS}.ops_fahrzeug_touren", RAHMEN, WAAGEN, f"{OPS}.ops_wiegungen",
    f"{OPS}.strecke_speditionen_frachttarife",
)
# child, column, parent, ON DELETE
LINKS = (
    (f"{OPS}.ops_dokument_versionen", "dokument_id", DOKUMENTE, "CASCADE"),
    (f"{OPS}.ops_fahrzeug_bussgeld", "fahrzeug_id", FAHRZEUGE, "CASCADE"),
    (f"{OPS}.ops_fahrzeug_schaeden", "fahrzeug_id", FAHRZEUGE, "CASCADE"),
    (f"{OPS}.ops_fahrzeug_status_historie", "fahrzeug_id", FAHRZEUGE, "CASCADE"),
    (f"{OPS}.ops_fahrzeug_touren", "fahrzeug_id", FAHRZEUGE, "CASCADE"),
    (f"{OPS}.ops_wiegungen", "waage_id", WAAGEN, "SET NULL (waage_id)"),
)
OWN = "tenant_id = public.rls_current_tenant()"
POLICIES = tuple(f"tenant_isolation_{kind}" for kind in ("select", "insert", "update", "delete"))


def _exists(bind, table: str) -> bool:
    return bind.execute(sa.text("SELECT to_regclass(:t)"), {"t": table}).scalar() is not None


def _has_column(bind, table: str, column: str) -> bool:
    return bind.execute(sa.text(
        "SELECT 1 FROM pg_attribute WHERE attrelid = to_regclass(:t) AND attname = :c AND NOT attisdropped"),
        {"t": table, "c": column}).scalar() is not None


def _name(table: str) -> str:
    return table.split(".")[1]


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


def _foreign_keys(bind, table: str, column: str, parent: str) -> list[str]:
    return list(bind.execute(sa.text(
        "SELECT k.conname FROM pg_constraint k WHERE k.conrelid = to_regclass(:t) AND k.contype = 'f' "
        "AND k.confrelid = to_regclass(:p) AND (SELECT array_agg(a.attname::text) FROM pg_attribute a "
        "WHERE a.attrelid = k.conrelid AND a.attnum = ANY(k.conkey)) = ARRAY[CAST(:c AS text)]"),
        {"t": table, "p": parent, "c": column}).scalars().all())


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
    locked = present + ([FAHRZEUGE] if _exists(bind, FAHRZEUGE) else [])
    op.execute(f"LOCK TABLE {', '.join(locked)} IN ACCESS EXCLUSIVE MODE")

    for table in present:
        rows = bind.execute(sa.text(f"SELECT count(*) FROM {table}")).scalar()  # nosec B608
        if rows and not _has_column(bind, table, "tenant_id"):
            raise RuntimeError(f"{table}: {rows} Zeilen ohne Mandantenspalte; Herkunft klaeren, nicht pauschal zuordnen")
    for table in present:
        if not _has_column(bind, table, "tenant_id"):
            op.execute(f"ALTER TABLE {table} ADD COLUMN tenant_id character varying(120)")
        op.execute(f"ALTER TABLE {table} ALTER COLUMN tenant_id SET DEFAULT public.rls_current_tenant()")
        op.execute(f"ALTER TABLE {table} ALTER COLUMN tenant_id SET NOT NULL")
        op.execute(f"CREATE INDEX IF NOT EXISTS ix_{_name(table)}_tenant_id ON {table} (tenant_id)")

    if RAHMEN in present:
        for index, constraint in _unique_indexes(bind, RAHMEN, ["nummer"]):
            if constraint:
                op.execute(f"ALTER TABLE {RAHMEN} DROP CONSTRAINT {constraint}")
            else:
                op.execute(f"DROP INDEX {index}")
        if not _unique_indexes(bind, RAHMEN, ["nummer", "tenant_id"]):
            op.execute(f"ALTER TABLE {RAHMEN} ADD CONSTRAINT uq_ops_rahmenvertraege_tenant_nummer UNIQUE (tenant_id, nummer)")

    links = [link for link in LINKS if link[0] in present and _exists(bind, link[2])]
    for parent in sorted({link[2] for link in links}):
        if not _unique_indexes(bind, parent, ["id", "tenant_id"]):
            op.execute(f"ALTER TABLE {parent} ADD CONSTRAINT uq_{_name(parent)}_id_tenant UNIQUE (id, tenant_id)")
    for child, column, parent, on_delete in links:
        for old in _foreign_keys(bind, child, column, parent):
            op.execute(f"ALTER TABLE {child} DROP CONSTRAINT {old}")
        op.execute(
            f"ALTER TABLE {child} ADD CONSTRAINT fk_{_name(child)}_{column}_tenant FOREIGN KEY ({column}, tenant_id) "
            f"REFERENCES {parent} (id, tenant_id) ON DELETE {on_delete}"
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
    for child, column, parent, on_delete in LINKS:
        if _exists(bind, child) and _exists(bind, parent):
            op.execute(f"ALTER TABLE {child} DROP CONSTRAINT IF EXISTS fk_{_name(child)}_{column}_tenant")
            plain = "SET NULL" if on_delete.startswith("SET NULL") else on_delete
            op.execute(f"ALTER TABLE {child} ADD CONSTRAINT {_name(child)}_{column}_fkey FOREIGN KEY ({column}) "
                       f"REFERENCES {parent} (id) ON DELETE {plain}")
    for parent in (DOKUMENTE, WAAGEN):
        if _exists(bind, parent):
            op.execute(f"ALTER TABLE {parent} DROP CONSTRAINT IF EXISTS uq_{_name(parent)}_id_tenant")
    if _exists(bind, RAHMEN):
        op.execute(f"ALTER TABLE {RAHMEN} DROP CONSTRAINT IF EXISTS uq_ops_rahmenvertraege_tenant_nummer")
        op.execute(f"ALTER TABLE {RAHMEN} ADD CONSTRAINT ops_rahmenvertraege_nummer_key UNIQUE (nummer)")
    for table in POLICY_TABLES:
        if _exists(bind, table):
            op.execute(f"DROP INDEX IF EXISTS {OPS}.ix_{_name(table)}_tenant_id")
            op.execute(f"ALTER TABLE {table} DROP COLUMN IF EXISTS tenant_id")
