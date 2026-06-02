"""Performance indexes for high-frequency query patterns.

Revision ID: performance_indexes_20260526
Revises: agribusiness_farmers_table_20260525
Create Date: 2026-05-26

Wave C2: DB-Index-Strategie — adds missing indexes on tenant_id + status/date
composite columns for the most frequently queried tables. These are all
non-unique, concurrent-safe indexes that won't block reads during creation.

Korrektur 2026-06-02: Die Index-Definitionen sind jetzt **schema-qualifiziert**
(domain_inventory/domain_crm/domain_erp) und auf die **tatsächlich vorhandenen
Spaltennamen** abgebildet (z. B. articles.is_active statt active,
sales_orders.created_at statt order_date, journal_entries.period/posting_date
statt accounting_period/booking_date, business_partners.is_customer statt
partner_type). Tabellen, die in einer Umgebung (noch) nicht existieren, werden
über einen to_regclass-Guard sauber übersprungen. Die kanonische Index-Liste
(PERF_INDEXES / PERF_INDEX_DROPS) wird von der Catch-up-Migration
perf_indexes_apply_20260602 wiederverwendet (Single Source of Truth).
"""

from alembic import op

revision = "performance_indexes_20260526"
down_revision = "agribusiness_farmers_table_20260525"
branch_labels = None
depends_on = None


# (schema-qualifizierte Zieltabelle, CREATE-Statement) — Single Source of Truth.
PERF_INDEXES = [
    ("domain_inventory.articles",
     "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_articles_tenant_active "
     "ON domain_inventory.articles (tenant_id, is_active) WHERE is_active = true"),
    ("domain_inventory.articles",
     "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_articles_tenant_number "
     "ON domain_inventory.articles (tenant_id, article_number)"),
    ("domain_crm.business_partners",
     "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_business_partners_tenant_customer "
     "ON domain_crm.business_partners (tenant_id, is_customer) WHERE is_customer = true"),
    ("domain_crm.business_partners",
     "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_business_partners_tenant_number "
     "ON domain_crm.business_partners (tenant_id, partner_number)"),
    ("domain_crm.sales_orders",
     "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sales_orders_tenant_status "
     "ON domain_crm.sales_orders (tenant_id, status)"),
    ("domain_crm.sales_orders",
     "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sales_orders_tenant_date "
     "ON domain_crm.sales_orders (tenant_id, created_at DESC)"),
    ("domain_erp.journal_entries",
     "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_journal_entries_tenant_period "
     "ON domain_erp.journal_entries (tenant_id, period, posting_date)"),
    ("domain_erp.journal_entries",
     "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_journal_entries_tenant_status "
     "ON domain_erp.journal_entries (tenant_id, status)"),
    ("domain_inventory.agrar_contracts",
     "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_agrar_contracts_tenant_year "
     "ON domain_inventory.agrar_contracts (tenant_id, harvest_year, status)"),
    ("domain_inventory.agrar_settlements",
     "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_agrar_settlements_tenant_status "
     "ON domain_inventory.agrar_settlements (tenant_id, status)"),
    # Tabellen, die in dieser Umgebung (noch) nicht existieren — Guard überspringt
    # sie. Schema ist Best-Guess für künftige Umgebungen; Spalten sind Standard.
    ("domain_agrar.harvest_acceptance",
     "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_harvest_acceptance_tenant_date "
     "ON domain_agrar.harvest_acceptance (tenant_id, created_at DESC)"),
    ("domain_agrar.harvest_acceptance",
     "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_harvest_acceptance_tenant_status "
     "ON domain_agrar.harvest_acceptance (tenant_id, status)"),
    ("domain_erp.invoices",
     "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_invoices_tenant_status_due "
     "ON domain_erp.invoices (tenant_id, status, due_date)"),
    ("domain_erp.invoices",
     "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_invoices_tenant_created "
     "ON domain_erp.invoices (tenant_id, created_at DESC)"),
    ("domain_einkauf.purchase_orders",
     "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_purchase_orders_tenant_status "
     "ON domain_einkauf.purchase_orders (tenant_id, status)"),
]

# Schema-qualifizierte Indexnamen für DROP (Index liegt im Schema seiner Tabelle).
PERF_INDEX_DROPS = [
    "domain_inventory.idx_articles_tenant_active",
    "domain_inventory.idx_articles_tenant_number",
    "domain_crm.idx_business_partners_tenant_customer",
    "domain_crm.idx_business_partners_tenant_number",
    "domain_crm.idx_sales_orders_tenant_status",
    "domain_crm.idx_sales_orders_tenant_date",
    "domain_erp.idx_journal_entries_tenant_period",
    "domain_erp.idx_journal_entries_tenant_status",
    "domain_inventory.idx_agrar_contracts_tenant_year",
    "domain_inventory.idx_agrar_settlements_tenant_status",
    "domain_agrar.idx_harvest_acceptance_tenant_date",
    "domain_agrar.idx_harvest_acceptance_tenant_status",
    "domain_erp.idx_invoices_tenant_status_due",
    "domain_erp.idx_invoices_tenant_created",
    "domain_einkauf.idx_purchase_orders_tenant_status",
]


def apply_indexes() -> None:
    """Legt alle PERF_INDEXES an; überspringt Tabellen, die nicht auflösbar sind.

    Muss innerhalb eines autocommit_block laufen (CREATE INDEX CONCURRENTLY darf
    nicht in einer Transaktion stehen).
    """
    from sqlalchemy import text as _sa_text

    conn = op.get_bind()
    for table, sql in PERF_INDEXES:
        if conn.execute(_sa_text("SELECT to_regclass(:t)"), {"t": table}).scalar() is None:
            continue  # Tabelle in dieser Umgebung nicht vorhanden → Index überspringen
        op.execute(sql)


def remove_indexes() -> None:
    """Entfernt alle PERF_INDEXES (idempotent). Innerhalb autocommit_block."""
    for idx in PERF_INDEX_DROPS:
        op.execute(f"DROP INDEX CONCURRENTLY IF EXISTS {idx}")


def upgrade() -> None:
    # CREATE INDEX CONCURRENTLY darf nicht innerhalb eines Transaktionsblocks laufen
    # (Postgres). autocommit_block führt die Index-Erstellung außerhalb der
    # Migrations-Transaktion aus.
    with op.get_context().autocommit_block():
        apply_indexes()


def downgrade() -> None:
    # DROP INDEX CONCURRENTLY ebenfalls außerhalb der Transaktion.
    with op.get_context().autocommit_block():
        remove_indexes()
