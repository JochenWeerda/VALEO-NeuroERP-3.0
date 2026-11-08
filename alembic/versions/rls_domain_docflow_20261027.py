"""Row-level security for the document backbone (RLS domain slice docflow).

Separate policies per command, named like the corrected P3/P5/P6 policies
(docs/architecture/rls-domaenen-entscheidungsmatrix.md, §3): SELECT, UPDATE and DELETE
see only rows of the transaction's tenant, INSERT and the result of UPDATE must belong to
it. Documents are records of one tenant: no shared 'system' rows are readable.

Positions, archived artifacts and stored e-invoice XML hang under a document header, a TSE
device under a POS terminal. Their single-column keys become keys over ``(parent,
tenant_id)``: FK checks bypass RLS, so only the key stops a row under a header or terminal of
another tenant, also when re-parenting, and a header with positions cannot change tenant.
The ON DELETE behaviour of each key is kept. ``pos_terminals`` keeps its P5 policies.

Rows without a tenant or with a placeholder ('', 'default', 'system') and rows under a parent
of another tenant block the migration.
"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "rls_domain_docflow_20261027"
down_revision = "rls_knowledge_objects_shared_20261027"
branch_labels = None
depends_on = None

S = "domain_docflow"
TABLES = tuple(f"{S}.{t}" for t in (
    "document_headers", "document_items", "document_artifacts", "invoice_xml_store", "pos_tse_devices"))
# child, column, parent, ON DELETE
LINKS = (
    (f"{S}.document_items", "header_id", f"{S}.document_headers", "CASCADE"),
    (f"{S}.document_artifacts", "header_id", f"{S}.document_headers", "CASCADE"),
    (f"{S}.invoice_xml_store", "header_id", f"{S}.document_headers", "CASCADE"),
    (f"{S}.pos_tse_devices", "terminal_id", f"{S}.pos_terminals", "CASCADE"),
)
OWN = "tenant_id = public.rls_current_tenant()"
POLICIES = tuple(f"tenant_isolation_{kind}" for kind in ("select", "insert", "update", "delete"))


def _exists(bind, table: str) -> bool:
    return bind.execute(sa.text("SELECT to_regclass(:t)"), {"t": table}).scalar() is not None


def _name(table: str) -> str:
    return table.split(".")[1]


def _single_fk(bind, child: str, column: str, parent: str) -> str | None:
    return bind.execute(sa.text(
        "SELECT k.conname FROM pg_constraint k JOIN pg_attribute a ON a.attrelid = k.conrelid "
        "AND a.attnum = k.conkey[1] WHERE k.contype = 'f' AND k.conrelid = to_regclass(:c) "
        "AND k.confrelid = to_regclass(:p) AND cardinality(k.conkey) = 1 AND a.attname = :col"),
        {"c": child, "p": parent, "col": column}).scalar()


def _enable_tenant_policies(table: str) -> None:
    op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
    for name in POLICIES:
        op.execute(f"DROP POLICY IF EXISTS {name} ON {table}")
    op.execute(f"CREATE POLICY tenant_isolation_select ON {table} FOR SELECT USING ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_insert ON {table} FOR INSERT WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_update ON {table} FOR UPDATE USING ({OWN}) WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_delete ON {table} FOR DELETE USING ({OWN})")


def _disable_tenant_policies(table: str) -> None:
    for name in POLICIES:
        op.execute(f"DROP POLICY IF EXISTS {name} ON {table}")
    op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")


def upgrade() -> None:
    bind = op.get_bind()
    present = [t for t in TABLES if _exists(bind, t)]
    links = [link for link in LINKS if _exists(bind, link[0]) and _exists(bind, link[2])]
    op.execute(f"LOCK TABLE {', '.join(sorted(set(present) | {l[2] for l in links}))} IN ACCESS EXCLUSIVE MODE")

    for table in present:
        unclear = bind.execute(sa.text(
            f"SELECT count(*) FROM {table} WHERE tenant_id IS NULL OR tenant_id IN ('', 'default', 'system')"
        )).scalar()
        if unclear:
            raise RuntimeError(
                f"{table}: {unclear} Zeilen ohne eindeutigen Mandanten; Herkunft klaeren, "
                "nicht pauschal zuordnen (rls-domaenen-entscheidungsmatrix.md)"
            )

    for parent in sorted({l[2] for l in links}):
        op.execute(f"ALTER TABLE {parent} ADD CONSTRAINT uq_{_name(parent)}_id_tenant UNIQUE (id, tenant_id)")
    for child, column, parent, on_delete in links:
        foreign = bind.execute(sa.text(
            f"SELECT count(*) FROM {child} c JOIN {parent} p ON p.id = c.{column} "
            "WHERE p.tenant_id IS DISTINCT FROM c.tenant_id"
        )).scalar()
        if foreign:
            raise RuntimeError(f"{child}: {foreign} Zeilen haengen an einem Elternsatz eines anderen Mandanten")
        old = _single_fk(bind, child, column, parent)
        if old:
            op.execute(f"ALTER TABLE {child} DROP CONSTRAINT {old}")
        op.execute(
            f"ALTER TABLE {child} ADD CONSTRAINT fk_{_name(child)}_{column}_tenant FOREIGN KEY ({column}, tenant_id) "
            f"REFERENCES {parent} (id, tenant_id) ON DELETE {on_delete}"
        )

    for table in present:
        _enable_tenant_policies(table)


def downgrade() -> None:
    bind = op.get_bind()
    for table in TABLES:
        if _exists(bind, table):
            _disable_tenant_policies(table)
    for child, column, parent, on_delete in LINKS:
        if not (_exists(bind, child) and _exists(bind, parent)):
            continue
        op.execute(f"ALTER TABLE {child} DROP CONSTRAINT IF EXISTS fk_{_name(child)}_{column}_tenant")
        op.execute(
            f"ALTER TABLE {child} ADD CONSTRAINT {_name(child)}_{column}_fkey FOREIGN KEY ({column}) "
            f"REFERENCES {parent} (id) ON DELETE {on_delete}"
        )
    for parent in sorted({l[2] for l in LINKS}):
        if _exists(bind, parent):
            op.execute(f"ALTER TABLE {parent} DROP CONSTRAINT IF EXISTS uq_{_name(parent)}_id_tenant")
