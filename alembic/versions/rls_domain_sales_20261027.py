"""Row-level security for the sales documents (RLS domain slice sales).

Separate policies per command, named like P3/P5/P6 (docs/architecture/rls-domaenen-entscheidungsmatrix.md,
§3): offers, orders, delivery notes, credit notes and their positions belong to one tenant; no
shared 'system' rows are readable.

Positions hang under their head over ``(head, tenant_id)``: FK checks bypass RLS, so only the key
stops a position under a document of another tenant, also when re-parenting, and a document with
positions cannot change tenant. Delivery note positions and credit note lines had no tenant; they
take it from their head (backfilled, NOT NULL, default from the context). Order items and offer
items (P5) already carry one. ON DELETE behaviour is kept. The article key of delivery note
positions stays single-column: the article master is still deferred (class B, shared catalogue).

``sales_delivery_notes`` (receipt confirmations) had a nullable tenant and becomes NOT NULL.
``domain_inventory.pick_lists`` gets the same policies: its endpoints are tenant-bound since this
slice (before, every write route acted on any tenant's pick list by id).
Rows without a tenant or with a placeholder ('', 'default', 'system') and positions under a head
of another tenant block the migration.
"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "rls_domain_sales_20261027"
down_revision = "rls_domain_ki_20261027"
branch_labels = None
depends_on = None

OFFERS, OFFER_ITEMS = "domain_crm.sales_offers", "domain_crm.sales_offer_items"
ORDERS, ORDER_ITEMS = "domain_crm.sales_orders", "domain_crm.sales_order_items"
NOTES, NOTE_POSITIONS = "domain_sales.delivery_notes", "domain_sales.delivery_note_positions"
CREDITS, CREDIT_LINES = "domain_sales.sales_credit_notes", "domain_sales.sales_credit_note_lines"
RECEIPTS = "domain_sales.sales_delivery_notes"
# Picklisten verweisen auf Auftraege; seit pick_lists.py tokengebunden ist (RLS-DOMAIN-SALES) ohne
# Rueckstellungsgrund. Ihre Kindtabellen (WMS/L3C-Positionen) folgen mit der Domain inventory.
PICK_LISTS = "domain_inventory.pick_lists"

POLICY_TABLES = (OFFERS, ORDERS, ORDER_ITEMS, NOTES, NOTE_POSITIONS, CREDITS, CREDIT_LINES, RECEIPTS, PICK_LISTS)
NEW_TENANT_COLUMN = (NOTE_POSITIONS, CREDIT_LINES)
NULLABLE_TENANT = (RECEIPTS,)
# child, column, parent, ON DELETE
LINKS = (
    (OFFER_ITEMS, "offer_id", OFFERS, "CASCADE"),
    (ORDER_ITEMS, "order_id", ORDERS, "CASCADE"),
    (NOTE_POSITIONS, "delivery_note_id", NOTES, "CASCADE"),
    (CREDIT_LINES, "credit_note_id", CREDITS, "CASCADE"),
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


def _enable(table: str) -> None:
    op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
    for name in POLICIES:
        op.execute(f"DROP POLICY IF EXISTS {name} ON {table}")
    op.execute(f"CREATE POLICY tenant_isolation_select ON {table} FOR SELECT USING ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_insert ON {table} FOR INSERT WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_update ON {table} FOR UPDATE USING ({OWN}) WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_delete ON {table} FOR DELETE USING ({OWN})")


def _disable(table: str) -> None:
    for name in POLICIES:
        op.execute(f"DROP POLICY IF EXISTS {name} ON {table}")
    op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")


def upgrade() -> None:
    bind = op.get_bind()
    links = [l for l in LINKS if _exists(bind, l[0]) and _exists(bind, l[2])]
    present = [t for t in POLICY_TABLES if _exists(bind, t)]
    locked = sorted(set(present) | {l[0] for l in links} | {l[2] for l in links})
    op.execute(f"LOCK TABLE {', '.join(locked)} IN ACCESS EXCLUSIVE MODE")

    for child, column, parent, _ in links:
        if child in NEW_TENANT_COLUMN:
            op.execute(f"ALTER TABLE {child} ADD COLUMN tenant_id character varying")
            op.execute(f"UPDATE {child} c SET tenant_id = p.tenant_id FROM {parent} p WHERE p.id = c.{column}")

    for table in present:
        unclear = bind.execute(sa.text(
            f"SELECT count(*) FROM {table} WHERE tenant_id IS NULL OR tenant_id IN ('', 'default', 'system')"
        )).scalar()
        if unclear:
            raise RuntimeError(
                f"{table}: {unclear} Zeilen ohne eindeutigen Mandanten; Herkunft klaeren, "
                "nicht pauschal zuordnen (rls-domaenen-entscheidungsmatrix.md)"
            )
    for table in NEW_TENANT_COLUMN + NULLABLE_TENANT:
        if table in present:
            op.execute(f"ALTER TABLE {table} ALTER COLUMN tenant_id SET NOT NULL")
    for table in NEW_TENANT_COLUMN:
        if table in present:
            op.execute(f"ALTER TABLE {table} ALTER COLUMN tenant_id SET DEFAULT public.rls_current_tenant()")

    for child, column, parent, on_delete in links:
        foreign = bind.execute(sa.text(
            f"SELECT count(*) FROM {child} c JOIN {parent} p ON p.id = c.{column} "
            "WHERE p.tenant_id IS DISTINCT FROM c.tenant_id")).scalar()
        if foreign:
            raise RuntimeError(f"{child}: {foreign} Positionen haengen an einem Kopf eines anderen Mandanten")
    for parent in sorted({l[2] for l in links}):
        op.execute(f"ALTER TABLE {parent} ADD CONSTRAINT uq_{_name(parent)}_id_tenant UNIQUE (id, tenant_id)")
    for child, column, parent, on_delete in links:
        old = _single_fk(bind, child, column, parent)
        if old:
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
            _disable(table)
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
    for table in NEW_TENANT_COLUMN:
        if _exists(bind, table):
            op.execute(f"ALTER TABLE {table} DROP COLUMN IF EXISTS tenant_id")
    for table in NULLABLE_TENANT:
        if _exists(bind, table):
            op.execute(f"ALTER TABLE {table} ALTER COLUMN tenant_id DROP NOT NULL")
