"""Row-level security pilot: domain_finance and the posting journal (RLS plan P3).

Every table listed below gets ``ENABLE ROW LEVEL SECURITY`` and one policy
``tenant_isolation``:

- USING: the row belongs to the transaction's tenant (``app.tenant_id``, set by
  app/core/rls_session.py), or it is a shared ``system`` row and a tenant is set at all.
- WITH CHECK: written rows belong to the transaction's tenant.

Without a tenant (empty setting) no row is visible or writable: fail-closed.
``FORCE ROW LEVEL SECURITY`` is deliberately not set: the owner role (valeo_owner, i.e.
migrations) keeps full access; applications connect as valeo_app/valeo_agent and never as
owner (plan, section 2.4).

``public.rls_current_tenant()`` is the single definition of "current tenant" for all
policies; ``NULLIF`` turns the empty setting into NULL so that no comparison matches.

journal_entry_lines.tenant_id is nullable; rows without tenant take it from their entry
(two rows on the grown database at the time of writing) before the policy applies. Retention
placeholders seeded as 'SYSTEM' become 'system', the shared tenant of the policies.
Tables missing on a database (two L3 tables exist only on fresh installations) are skipped.
"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "rls_pilot_finance_20261026"
down_revision = "inventory_service_shape_20261026"
branch_labels = None
depends_on = None

PILOT_TABLES = (
    "domain_erp.journal_entries",
    "domain_erp.journal_entry_lines",
    "domain_finance.aufbewahrungsfristen",
    "domain_finance.billing_batch_audit",
    "domain_finance.billing_batch_lines",
    "domain_finance.billing_batches",
    "domain_finance.dispute_records",
    "domain_finance.ebilanz_exports",
    "domain_finance.finance_mahnstufen_audit",
    "domain_finance.finance_ratenzahlungsplaene",
    "domain_finance.finance_ratenzahlungsraten",
    "domain_finance.finance_sepa_batches",
    "domain_finance.finance_sepa_mandate",
    "domain_finance.fixed_assets",
    "domain_finance.kostenarten",
    "domain_finance.kostenstellen",
    "domain_finance.kostenstellen_buchungen",
    "domain_finance.kostenstellen_umlagen",
    "domain_finance.period_closure",
    "domain_finance.sales_order",
    "domain_finance.self_billing_invoices",
    "domain_finance.ustva_voranmeldungen",
)

CURRENT_TENANT_FUNCTION = """
CREATE OR REPLACE FUNCTION public.rls_current_tenant() RETURNS text
LANGUAGE sql STABLE PARALLEL SAFE
AS $$ SELECT NULLIF(current_setting('app.tenant_id', true), '') $$
"""


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
    op.execute(CURRENT_TENANT_FUNCTION)
    op.execute(
        "UPDATE domain_erp.journal_entry_lines l SET tenant_id = e.tenant_id "
        "FROM domain_erp.journal_entries e "
        "WHERE l.journal_entry_id = e.id AND l.tenant_id IS NULL"
    )
    # gobd_aufbewahrungsfristen_20260301 seeded its placeholders as 'SYSTEM'; the shared tenant
    # of the policies is 'system' (user decision 2026-10-26). The code reads per tenant only.
    op.execute(
        "UPDATE domain_finance.aufbewahrungsfristen SET tenant_id = 'system' WHERE tenant_id = 'SYSTEM'"
    )
    for table in PILOT_TABLES:
        enable_tenant_isolation(bind, table)


def downgrade() -> None:
    bind = op.get_bind()
    for table in PILOT_TABLES:
        disable_tenant_isolation(bind, table)
    op.execute("DROP FUNCTION IF EXISTS public.rls_current_tenant()")
