"""perf: add missing database indexes for multi-tenant queries

Revision ID: perf_indexes_20260408
Revises: domain_schemas_baseline_20260409
Create Date: 2026-04-08

Adds indexes on tenant_id columns (critical for multi-tenant query
performance), status/filter columns, and timestamp columns used in
range queries.  All statements use IF NOT EXISTS for idempotency.

Tables that may not yet exist (sales_orders, sales_order_items, contacts
with tenant_id) are wrapped in a PL/pgSQL guard so the migration never
fails regardless of the current schema state.
"""
from alembic import op
from sqlalchemy import text

revision = "perf_indexes_20260408"
down_revision = "domain_schemas_baseline_20260409"
branch_labels = None
depends_on = None


# Helper: wrap a CREATE INDEX in a DO block that silently skips if the
# table or column does not exist.
_SAFE_IDX = """
DO $$ BEGIN
    {stmt};
EXCEPTION WHEN undefined_table OR undefined_column THEN
    RAISE NOTICE 'Skipped index – table or column missing';
END $$;
"""


def _safe(stmt: str):
    """Execute a CREATE INDEX, gracefully skipping if the table/column is absent."""
    op.execute(text(_SAFE_IDX.format(stmt=stmt)))


def upgrade():
    # ── 1. tenant_id indexes (CRITICAL — every query filters by tenant) ──

    # domain_shared
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_audit_logs_tenant_id "
        "ON domain_shared.audit_logs (tenant_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_users_tenant_id "
        "ON domain_shared.users (tenant_id)"
    )

    # domain_erp — journal_entries
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_journal_entries_tenant_id "
        "ON domain_erp.journal_entries (tenant_id)"
    )
    # domain_erp — journal_entry_lines (composite: tenant + parent FK)
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_journal_entry_lines_tenant_je "
        "ON domain_erp.journal_entry_lines (tenant_id, journal_entry_id)"
    )
    # domain_erp — chart_of_accounts (single + composite)
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_coa_tenant_id "
        "ON domain_erp.chart_of_accounts (tenant_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_coa_tenant_account_number "
        "ON domain_erp.chart_of_accounts (tenant_id, account_number)"
    )

    # domain_crm — tables may not exist on all installations
    _safe(
        "CREATE INDEX IF NOT EXISTS ix_sales_orders_tenant_id "
        "ON domain_crm.sales_orders (tenant_id)"
    )
    _safe(
        "CREATE INDEX IF NOT EXISTS ix_sales_order_items_order_tenant "
        "ON domain_crm.sales_order_items (order_id, tenant_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_business_partners_tenant_id "
        "ON domain_crm.business_partners (tenant_id)"
    )
    _safe(
        "CREATE INDEX IF NOT EXISTS ix_contacts_tenant_id "
        "ON domain_crm.contacts (tenant_id)"
    )

    # domain_einkauf
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_bestellungen_tenant_id "
        "ON domain_einkauf.bestellungen (tenant_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_bestellung_positionen_bestellung_id "
        "ON domain_einkauf.bestellung_positionen (bestellung_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_lieferanten_tenant_id "
        "ON domain_einkauf.lieferanten (tenant_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_kontrakte_tenant_id "
        "ON domain_einkauf.kontrakte (tenant_id)"
    )

    # ── 2. Status / filter indexes ──

    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_journal_entries_tenant_status "
        "ON domain_erp.journal_entries (tenant_id, status)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_audit_logs_entity "
        "ON domain_shared.audit_logs (entity_type, entity_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_audit_logs_user_id "
        "ON domain_shared.audit_logs (user_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_blockchain_anchors_tenant_subject "
        "ON domain_shared.blockchain_anchors (tenant_id, subject_type)"
    )

    # ── 3. Timestamp indexes for range queries ──

    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_audit_logs_timestamp "
        "ON domain_shared.audit_logs (timestamp)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_journal_entries_entry_date "
        "ON domain_erp.journal_entries (entry_date)"
    )


def downgrade():
    # Drop in reverse order; IF EXISTS for safety
    op.execute("DROP INDEX IF EXISTS domain_erp.ix_journal_entries_entry_date")
    op.execute("DROP INDEX IF EXISTS domain_shared.ix_audit_logs_timestamp")

    op.execute("DROP INDEX IF EXISTS domain_shared.ix_blockchain_anchors_tenant_subject")
    op.execute("DROP INDEX IF EXISTS domain_shared.ix_audit_logs_user_id")
    op.execute("DROP INDEX IF EXISTS domain_shared.ix_audit_logs_entity")
    op.execute("DROP INDEX IF EXISTS domain_erp.ix_journal_entries_tenant_status")

    op.execute("DROP INDEX IF EXISTS domain_einkauf.ix_kontrakte_tenant_id")
    op.execute("DROP INDEX IF EXISTS domain_einkauf.ix_lieferanten_tenant_id")
    op.execute("DROP INDEX IF EXISTS domain_einkauf.ix_bestellung_positionen_bestellung_id")
    op.execute("DROP INDEX IF EXISTS domain_einkauf.ix_bestellungen_tenant_id")

    op.execute("DROP INDEX IF EXISTS domain_crm.ix_contacts_tenant_id")
    op.execute("DROP INDEX IF EXISTS domain_crm.ix_business_partners_tenant_id")
    op.execute("DROP INDEX IF EXISTS domain_crm.ix_sales_order_items_order_tenant")
    op.execute("DROP INDEX IF EXISTS domain_crm.ix_sales_orders_tenant_id")

    op.execute("DROP INDEX IF EXISTS domain_erp.ix_coa_tenant_account_number")
    op.execute("DROP INDEX IF EXISTS domain_erp.ix_coa_tenant_id")
    op.execute("DROP INDEX IF EXISTS domain_erp.ix_journal_entry_lines_tenant_je")
    op.execute("DROP INDEX IF EXISTS domain_erp.ix_journal_entries_tenant_id")

    op.execute("DROP INDEX IF EXISTS domain_shared.ix_users_tenant_id")
    op.execute("DROP INDEX IF EXISTS domain_shared.ix_audit_logs_tenant_id")
