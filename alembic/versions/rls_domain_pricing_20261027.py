"""Row-level security for domain_pricing (RLS domain slice, first after P0-P7).

Separate policies per command (docs/architecture/rls-domaenen-entscheidungsmatrix.md, §3):

- SELECT, UPDATE, DELETE see only rows of the transaction's tenant (``app.tenant_id``);
  INSERT and the result of UPDATE must belong to it. Price lists are commercial data of one
  tenant: no shared 'system' rows are readable here.
- No ALL policy: permissive policies are combined with OR.

price_list_items had no tenant_id; the tenant came only from its price list. It now carries
the tenant of its list (backfilled, NOT NULL, default from the context), and the foreign key
``(price_list_id, tenant_id) -> price_lists(id, tenant_id)`` makes a position under a list of
another tenant structurally impossible, also when re-parenting (FK checks bypass RLS, so the
policy alone would not catch it). A list with positions cannot change its tenant either.

Rows with a placeholder tenant ('', 'default', 'system') block the migration: their origin
has to be settled first, they are never assigned in bulk.
"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "rls_domain_pricing_20261027"
down_revision = "rls_system_role_20261026"
branch_labels = None
depends_on = None

LISTS = "domain_pricing.price_lists"
ITEMS = "domain_pricing.price_list_items"
OWN = "tenant_id = public.rls_current_tenant()"
# Same names as the corrected P3/P5/P6 policies (943ba2bb0); one shape for all RLS tables.
POLICIES = tuple(f"tenant_isolation_{kind}" for kind in ("select", "insert", "update", "delete"))


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
    op.execute(f"LOCK TABLE {LISTS}, {ITEMS} IN ACCESS EXCLUSIVE MODE")
    placeholders = bind.execute(sa.text(
        f"SELECT count(*) FROM {LISTS} WHERE tenant_id IS NULL OR tenant_id IN ('', 'default', 'system')"
    )).scalar()
    if placeholders:
        raise RuntimeError(
            f"{LISTS}: {placeholders} Preislisten ohne eindeutigen Mandanten; Herkunft klaeren, "
            "nicht pauschal zuordnen (rls-domaenen-entscheidungsmatrix.md)"
        )

    op.execute(f"ALTER TABLE {ITEMS} ADD COLUMN tenant_id character varying")
    op.execute(
        f"UPDATE {ITEMS} i SET tenant_id = l.tenant_id FROM {LISTS} l WHERE l.id = i.price_list_id"
    )
    op.execute(f"ALTER TABLE {ITEMS} ALTER COLUMN tenant_id SET NOT NULL")
    op.execute(f"ALTER TABLE {ITEMS} ALTER COLUMN tenant_id SET DEFAULT public.rls_current_tenant()")

    op.execute(f"ALTER TABLE {LISTS} ADD CONSTRAINT uq_price_lists_id_tenant UNIQUE (id, tenant_id)")
    op.execute(f"ALTER TABLE {ITEMS} DROP CONSTRAINT IF EXISTS fk_pli_price_list")
    op.execute(
        f"ALTER TABLE {ITEMS} ADD CONSTRAINT fk_pli_price_list_tenant "
        f"FOREIGN KEY (price_list_id, tenant_id) REFERENCES {LISTS} (id, tenant_id) ON DELETE CASCADE"
    )

    _enable_tenant_policies(LISTS)
    _enable_tenant_policies(ITEMS)


def downgrade() -> None:
    _disable_tenant_policies(ITEMS)
    _disable_tenant_policies(LISTS)
    op.execute(f"ALTER TABLE {ITEMS} DROP CONSTRAINT IF EXISTS fk_pli_price_list_tenant")
    op.execute(
        f"ALTER TABLE {ITEMS} ADD CONSTRAINT fk_pli_price_list "
        f"FOREIGN KEY (price_list_id) REFERENCES {LISTS} (id) ON DELETE CASCADE"
    )
    op.execute(f"ALTER TABLE {LISTS} DROP CONSTRAINT IF EXISTS uq_price_lists_id_tenant")
    op.execute(f"ALTER TABLE {ITEMS} DROP COLUMN IF EXISTS tenant_id")
