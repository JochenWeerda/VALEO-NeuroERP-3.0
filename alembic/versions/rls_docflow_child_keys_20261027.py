"""Tenant-bound keys for the children of the document backbone (P5 tables).

Links between documents and positions, postings, return cases, POS receipt checks and
regulatory notices referenced their parent by id only. FK checks bypass row-level security,
so a row could point at a header, position, artifact or TSE device of another tenant (also by
re-pointing it). Each such key becomes a key over ``(parent, tenant_id)``.

The ON DELETE behaviour is kept. Keys that set the reference to NULL use PostgreSQL 15's
``ON DELETE SET NULL (column)``: only the reference is cleared, ``tenant_id`` stays.
Parents get ``UNIQUE (id, tenant_id)`` where it does not exist yet (headers since
rls_domain_docflow_20261027). The policies of the child tables (P5) are unchanged.

Rows that point at a parent of another tenant block the migration.
"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "rls_docflow_child_keys_20261027"
down_revision = "rls_domain_docflow_20261027"
branch_labels = None
depends_on = None

S = "domain_docflow"
HEADERS, ITEMS, ARTIFACTS, TSE = (f"{S}.{t}" for t in (
    "document_headers", "document_items", "document_artifacts", "pos_tse_devices"))
NEW_UNIQUES = (ITEMS, ARTIFACTS, TSE)
# child, column, parent, ON DELETE (None = NO ACTION, "SET NULL" = only the reference)
LINKS = (
    (f"{S}.document_header_links", "from_header_id", HEADERS, "CASCADE"),
    (f"{S}.document_header_links", "to_header_id", HEADERS, "CASCADE"),
    (f"{S}.document_links", "from_header_id", HEADERS, "CASCADE"),
    (f"{S}.document_links", "to_header_id", HEADERS, "CASCADE"),
    (f"{S}.document_links", "from_item_id", ITEMS, "SET NULL"),
    (f"{S}.document_links", "to_item_id", ITEMS, "SET NULL"),
    (f"{S}.document_postings", "header_id", HEADERS, "CASCADE"),
    (f"{S}.document_return_cases", "header_id", HEADERS, None),
    (f"{S}.document_return_cases", "artifact_id", ARTIFACTS, None),
    (f"{S}.pos_receipt_compliance", "header_id", HEADERS, "CASCADE"),
    (f"{S}.pos_receipt_compliance", "original_header_id", HEADERS, "SET NULL"),
    (f"{S}.pos_regulatory_notices", "tse_device_id", TSE, "SET NULL"),
)


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


def _on_delete(action: str | None, column: str) -> str:
    if action is None:
        return ""
    if action == "SET NULL":
        return f" ON DELETE SET NULL ({column})"
    return f" ON DELETE {action}"


def upgrade() -> None:
    bind = op.get_bind()
    links = [l for l in LINKS if _exists(bind, l[0]) and _exists(bind, l[2])]
    tables = sorted({l[0] for l in links} | {l[2] for l in links})
    op.execute(f"LOCK TABLE {', '.join(tables)} IN ACCESS EXCLUSIVE MODE")
    for child, column, parent, _action in links:
        foreign = bind.execute(sa.text(
            f"SELECT count(*) FROM {child} c JOIN {parent} p ON p.id = c.{column} "
            "WHERE p.tenant_id IS DISTINCT FROM c.tenant_id")).scalar()
        if foreign:
            raise RuntimeError(f"{child}.{column}: {foreign} Zeilen verweisen auf einen Elternsatz eines anderen Mandanten")
    for parent in NEW_UNIQUES:
        if _exists(bind, parent):
            op.execute(f"ALTER TABLE {parent} ADD CONSTRAINT uq_{_name(parent)}_id_tenant UNIQUE (id, tenant_id)")
    for child, column, parent, action in links:
        old = _single_fk(bind, child, column, parent)
        if old:
            op.execute(f"ALTER TABLE {child} DROP CONSTRAINT {old}")
        op.execute(
            f"ALTER TABLE {child} ADD CONSTRAINT fk_{_name(child)}_{column}_tenant FOREIGN KEY ({column}, tenant_id) "
            f"REFERENCES {parent} (id, tenant_id){_on_delete(action, column)}"
        )


def downgrade() -> None:
    bind = op.get_bind()
    for child, column, parent, action in LINKS:
        if not (_exists(bind, child) and _exists(bind, parent)):
            continue
        op.execute(f"ALTER TABLE {child} DROP CONSTRAINT IF EXISTS fk_{_name(child)}_{column}_tenant")
        on_delete = "" if action is None else f" ON DELETE {action}"
        op.execute(
            f"ALTER TABLE {child} ADD CONSTRAINT {_name(child)}_{column}_fkey FOREIGN KEY ({column}) "
            f"REFERENCES {parent} (id){on_delete}"
        )
    for parent in NEW_UNIQUES:
        if _exists(bind, parent):
            op.execute(f"ALTER TABLE {parent} DROP CONSTRAINT IF EXISTS uq_{_name(parent)}_id_tenant")
