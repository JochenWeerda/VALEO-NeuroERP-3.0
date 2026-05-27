"""Performance indexes for high-frequency query patterns.

Revision ID: performance_indexes_20260526
Revises: agribusiness_farmers_table_20260525
Create Date: 2026-05-26

Wave C2: DB-Index-Strategie — adds missing indexes on tenant_id + status/date
composite columns for the most frequently queried tables. These are all
non-unique, concurrent-safe indexes that won't block reads during creation.
"""

from alembic import op

revision = "performance_indexes_20260526"
down_revision = "agribusiness_farmers_table_20260525"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Harvest acceptance — heaviest read table during harvest campaign
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS
            idx_harvest_acceptance_tenant_date
        ON harvest_acceptance(tenant_id, created_at DESC)
    """)
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS
            idx_harvest_acceptance_tenant_status
        ON harvest_acceptance(tenant_id, status)
    """)

    # Invoices — core finance query: open invoices per tenant
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS
            idx_invoices_tenant_status_due
        ON invoices(tenant_id, status, due_date)
    """)
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS
            idx_invoices_tenant_created
        ON invoices(tenant_id, created_at DESC)
    """)

    # Articles — master data, filtered by active flag on every product list
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS
            idx_articles_tenant_active
        ON articles(tenant_id, active)
        WHERE active = true
    """)
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS
            idx_articles_tenant_number
        ON articles(tenant_id, article_number)
    """)

    # Business partners — CRM/Einkauf partner lookups
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS
            idx_business_partners_tenant_type
        ON business_partners(tenant_id, partner_type)
    """)
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS
            idx_business_partners_tenant_number
        ON business_partners(tenant_id, partner_number)
    """)

    # Sales orders — order management hot path
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS
            idx_sales_orders_tenant_status
        ON sales_orders(tenant_id, status)
    """)
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS
            idx_sales_orders_tenant_date
        ON sales_orders(tenant_id, order_date DESC)
    """)

    # Journal entries — FIBU, GoBD compliance queries
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS
            idx_journal_entries_tenant_period
        ON journal_entries(tenant_id, accounting_period, booking_date)
    """)
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS
            idx_journal_entries_tenant_account
        ON journal_entries(tenant_id, account_id)
    """)

    # Agrar contracts — allocation queries per harvest year
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS
            idx_agrar_contracts_tenant_year
        ON agrar_contracts(tenant_id, harvest_year, status)
    """)

    # Agrar settlements — settlement queries
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS
            idx_agrar_settlements_tenant_status
        ON agrar_settlements(tenant_id, status)
    """)

    # Purchase orders — Einkauf
    op.execute("""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS
            idx_purchase_orders_tenant_status
        ON purchase_orders(tenant_id, status)
    """)


def downgrade() -> None:
    for idx in [
        "idx_harvest_acceptance_tenant_date",
        "idx_harvest_acceptance_tenant_status",
        "idx_invoices_tenant_status_due",
        "idx_invoices_tenant_created",
        "idx_articles_tenant_active",
        "idx_articles_tenant_number",
        "idx_business_partners_tenant_type",
        "idx_business_partners_tenant_number",
        "idx_sales_orders_tenant_status",
        "idx_sales_orders_tenant_date",
        "idx_journal_entries_tenant_period",
        "idx_journal_entries_tenant_account",
        "idx_agrar_contracts_tenant_year",
        "idx_agrar_settlements_tenant_status",
        "idx_purchase_orders_tenant_status",
    ]:
        op.execute(f"DROP INDEX CONCURRENTLY IF EXISTS {idx}")
