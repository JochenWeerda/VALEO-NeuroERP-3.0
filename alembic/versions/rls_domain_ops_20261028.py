"""Row-level security for domain_ops, part 1 (schema only, no data change).

Revision ID: rls_domain_ops_20261028
Revises: service_anfragen_20261027

* ``kon_contract`` and ``ops_pcn_meldungen`` get separate policies per command (their children already have them).
* Columns defaulting ``tenant_id`` to ``'default'`` or ``'legacy-unassigned'`` default to the tenant of the context.
  Existing rows are not touched (live: one flow-spine instance and 31 EDI messages carry ``'default'``; they are a data
  decision).
* Numbers that are unique per tenant were unique system-wide: tank stock per article, insurance contract number, EDI
  partner GLN, EDI message id. A second tenant with the same article failed at the database.
* Children hang under their parent over ``(parent key, tenant_id)``: FK checks bypass RLS, so only the key stops a row
  under or pointing at a parent of another tenant, also when re-pointing.

Not here (part 2): the 21 domain_ops tables without any tenant column. Rows of the policy tables without a tenant or
with a placeholder and rows pointing at a parent of another tenant block the migration.
"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "rls_domain_ops_20261028"
down_revision = "service_anfragen_20261027"
branch_labels = None
depends_on = None

OPS = "domain_ops"
POLICY_TABLES = (f"{OPS}.kon_contract", f"{OPS}.ops_pcn_meldungen")
DEFAULT_TO_CONTEXT = {
    "'default'::character varying": (
        f"{OPS}.edi_nachrichten", f"{OPS}.ops_flow_spine_instances", f"{OPS}.ops_flow_spine_instance_events",
        f"{OPS}.ops_flow_spine_instance_documents", f"{OPS}.ops_projekte", f"{OPS}.ops_projekt_aufgaben",
        f"{OPS}.ops_tank_bestand", f"{OPS}.ops_verladungen", f"{OPS}.ops_versicherungen", f"{OPS}.ops_wartung_anlagen",
        f"{OPS}.ops_wartungs_protokolle", f"{OPS}.ops_zapfungen", f"{OPS}.ops_pcn_meldungen",
    ),
    "'legacy-unassigned'::character varying": (
        f"{OPS}.ops_fahrzeuge", f"{OPS}.ops_fuhrpark_ausgehende_dokumente", f"{OPS}.ops_fuhrpark_rechnungen",
        f"{OPS}.ops_fuhrpark_terminarten",
    ),
}
# table, column: unique per tenant instead of system-wide
PER_TENANT_UNIQUE = (
    (f"{OPS}.ops_tank_bestand", "artikel"),
    (f"{OPS}.ops_versicherungen", "vertragsnummer"),
    (f"{OPS}.edi_partner", "gln"),
    (f"{OPS}.edi_nachrichten", "nachricht_id"),
)
# child, column, parent, parent key, ON DELETE
LINKS = (
    (f"{OPS}.kon_contract_line", "contract_id", f"{OPS}.kon_contract", "contract_id", "CASCADE"),
    (f"{OPS}.kon_contract_movement", "contract_id", f"{OPS}.kon_contract", "contract_id", "CASCADE"),
    (f"{OPS}.kon_contract_movement", "line_id", f"{OPS}.kon_contract_line", "line_id", "SET NULL"),
    (f"{OPS}.ops_projekt_aufgaben", "projekt_id", f"{OPS}.ops_projekte", "id", "CASCADE"),
    (f"{OPS}.ops_wartungs_protokolle", "anlage_id", f"{OPS}.ops_wartung_anlagen", "id", "CASCADE"),
    (f"{OPS}.ops_flow_spine_instance_documents", "instance_id", f"{OPS}.ops_flow_spine_instances", "id", "CASCADE"),
    (f"{OPS}.ops_flow_spine_instance_events", "instance_id", f"{OPS}.ops_flow_spine_instances", "id", "CASCADE"),
    (f"{OPS}.ops_fuhrpark_rechnungen", "fahrzeug_id", f"{OPS}.ops_fahrzeuge", "id", "SET NULL"),
)
OWN = "tenant_id = public.rls_current_tenant()"
POLICIES = tuple(f"tenant_isolation_{kind}" for kind in ("select", "insert", "update", "delete"))


def _exists(bind, table: str) -> bool:
    return bind.execute(sa.text("SELECT to_regclass(:t)"), {"t": table}).scalar() is not None


def _name(table: str) -> str:
    return table.split(".")[1]


def _default(bind, table: str) -> str | None:
    return bind.execute(sa.text(
        "SELECT pg_get_expr(d.adbin, d.adrelid) FROM pg_attribute a JOIN pg_attrdef d ON d.adrelid = a.attrelid "
        "AND d.adnum = a.attnum WHERE a.attrelid = to_regclass(:t) AND a.attname = 'tenant_id'"), {"t": table}).scalar()


def _single_constraint(bind, table: str, column: str, kind: str, parent: str | None = None) -> str | None:
    return bind.execute(sa.text(
        "SELECT k.conname FROM pg_constraint k JOIN pg_attribute a ON a.attrelid = k.conrelid AND a.attnum = k.conkey[1] "
        "WHERE k.contype = :kind AND k.conrelid = to_regclass(:t) AND cardinality(k.conkey) = 1 AND a.attname = :col "
        "AND (:p IS NULL OR k.confrelid = to_regclass(:p))"),
        {"kind": kind, "t": table, "col": column, "p": parent}).scalar()


def _has_unique(bind, parent: str, key: str) -> bool:
    return bind.execute(sa.text(
        "SELECT 1 FROM pg_constraint k WHERE k.conrelid = to_regclass(:p) AND k.contype IN ('u', 'p') "
        "AND (SELECT array_agg(a.attname::text ORDER BY a.attname) FROM pg_attribute a "
        "     WHERE a.attrelid = k.conrelid AND a.attnum = ANY(k.conkey)) = ARRAY[:k, 'tenant_id']::text[]"),
        {"p": parent, "k": key}).scalar() is not None


def _on_delete(column: str, on_delete: str) -> str:
    # Ein Verbund-FK mit SET NULL leert sonst auch tenant_id (NOT NULL); PG15 leert nur die Verweisspalte.
    return f"SET NULL ({column})" if on_delete == "SET NULL" else on_delete


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
    links = [link for link in LINKS if _exists(bind, link[0]) and _exists(bind, link[2])]
    present = [t for t in POLICY_TABLES if _exists(bind, t)]
    defaults = [(t, old) for old, tables in DEFAULT_TO_CONTEXT.items() for t in tables if _exists(bind, t)]
    uniques = [(t, c) for t, c in PER_TENANT_UNIQUE if _exists(bind, t)]
    locked = sorted(set(present) | {t for t, _ in defaults} | {t for t, _ in uniques}
                    | {link[0] for link in links} | {link[2] for link in links})
    op.execute(f"LOCK TABLE {', '.join(locked)} IN ACCESS EXCLUSIVE MODE")

    for table in present:
        unclear = bind.execute(sa.text(
            f"SELECT count(*) FROM {table} WHERE tenant_id IS NULL "
            "OR tenant_id IN ('', 'default', 'system', 'legacy-unassigned')")).scalar()
        if unclear:
            raise RuntimeError(f"{table}: {unclear} Zeilen ohne eindeutigen Mandanten; Herkunft klaeren, nicht pauschal zuordnen")
    for table, old in defaults:
        if _default(bind, table) == old:
            op.execute(f"ALTER TABLE {table} ALTER COLUMN tenant_id SET DEFAULT public.rls_current_tenant()")

    for table, column in uniques:
        old = _single_constraint(bind, table, column, "u")
        if old:
            op.execute(f"ALTER TABLE {table} DROP CONSTRAINT {old}")
        op.execute(f"ALTER TABLE {table} ADD CONSTRAINT uq_{_name(table)}_tenant_{column} UNIQUE (tenant_id, {column})")

    for child, column, parent, key, _ in links:
        foreign = bind.execute(sa.text(
            f"SELECT count(*) FROM {child} c JOIN {parent} p ON p.{key} = c.{column} "
            "WHERE p.tenant_id IS DISTINCT FROM c.tenant_id")).scalar()
        if foreign:
            raise RuntimeError(f"{child}.{column}: {foreign} Zeilen verweisen auf {parent} eines anderen Mandanten")
    for parent, key in sorted({(link[2], link[3]) for link in links}):
        if not _has_unique(bind, parent, key):
            op.execute(f"ALTER TABLE {parent} ADD CONSTRAINT uq_{_name(parent)}_{key}_tenant UNIQUE ({key}, tenant_id)")
    for child, column, parent, key, on_delete in links:
        old = _single_constraint(bind, child, column, "f", parent)
        if old:
            op.execute(f"ALTER TABLE {child} DROP CONSTRAINT {old}")
        op.execute(
            f"ALTER TABLE {child} ADD CONSTRAINT fk_{_name(child)}_{column}_tenant FOREIGN KEY ({column}, tenant_id) "
            f"REFERENCES {parent} ({key}, tenant_id) ON DELETE {_on_delete(column, on_delete)}"
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
    for child, column, parent, key, on_delete in LINKS:
        if not (_exists(bind, child) and _exists(bind, parent)):
            continue
        op.execute(f"ALTER TABLE {child} DROP CONSTRAINT IF EXISTS fk_{_name(child)}_{column}_tenant")
        op.execute(f"ALTER TABLE {child} ADD CONSTRAINT {_name(child)}_{column}_fkey FOREIGN KEY ({column}) "
                   f"REFERENCES {parent} ({key}) ON DELETE {on_delete}")
    for parent, key in sorted({(link[2], link[3]) for link in LINKS}):
        if _exists(bind, parent):
            op.execute(f"ALTER TABLE {parent} DROP CONSTRAINT IF EXISTS uq_{_name(parent)}_{key}_tenant")
    for table, column in PER_TENANT_UNIQUE:
        if _exists(bind, table):
            op.execute(f"ALTER TABLE {table} DROP CONSTRAINT IF EXISTS uq_{_name(table)}_tenant_{column}")
            op.execute(f"ALTER TABLE {table} ADD CONSTRAINT {_name(table)}_{column}_key UNIQUE ({column})")
    for old, tables in DEFAULT_TO_CONTEXT.items():
        for table in tables:
            if _exists(bind, table):
                op.execute(f"ALTER TABLE {table} ALTER COLUMN tenant_id SET DEFAULT {old}")
