# VALEO-NeuroERP Initial Schema Migration
# This migration creates the complete database schema for clean architecture

"""initial_schema

Revision ID: 001
Revises:
Create Date: 2025-09-26 17:50:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create schemas
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_crm")
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_erp")
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_inventory")
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_shared")
    op.execute("CREATE SCHEMA IF NOT EXISTS infrastructure")

    # Create shared tables
    op.create_table('tenants',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('domain', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('settings', postgresql.JSONB(astext_type=sa.Text()), nullable=True, default='{}'),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='domain_shared'
    )

    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('keycloak_id', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=255), nullable=True),
        sa.Column('last_name', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('roles', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('preferences', postgresql.JSONB(astext_type=sa.Text()), nullable=True, default='{}'),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['domain_shared.tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('keycloak_id'),
        sa.UniqueConstraint('username'),
        schema='domain_shared'
    )

    # Create CRM tables
    op.create_table('customers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('customer_number', sa.String(length=50), nullable=False),
        sa.Column('company_name', sa.String(length=255), nullable=True),
        sa.Column('contact_person', sa.String(length=255), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('address', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('customer_type', sa.String(length=50), nullable=True, default='business'),
        sa.Column('credit_limit', sa.Numeric(precision=15, scale=2), nullable=True, default=0),
        sa.Column('payment_terms', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['domain_shared.users.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['domain_shared.tenants.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['domain_shared.users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('customer_number'),
        schema='domain_crm'
    )

    op.create_table('leads',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('lead_source', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True, default='new'),
        sa.Column('estimated_value', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('probability', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('expected_close_date', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['assigned_to'], ['domain_shared.users.id'], ),
        sa.ForeignKeyConstraint(['customer_id'], ['domain_crm.customers.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['domain_shared.tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='domain_crm'
    )

    # Create ERP tables
    op.create_table('chart_of_accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('account_number', sa.String(length=20), nullable=False),
        sa.Column('account_name', sa.String(length=255), nullable=False),
        sa.Column('account_type', sa.String(length=50), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['domain_shared.tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('account_number'),
        schema='domain_erp'
    )

    op.create_table('bank_accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('account_number', sa.String(length=50), nullable=False),
        sa.Column('bank_name', sa.String(length=255), nullable=False),
        sa.Column('iban', sa.String(length=34), nullable=True),
        sa.Column('bic', sa.String(length=11), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=True, default='EUR'),
        sa.Column('balance', sa.Numeric(precision=15, scale=2), nullable=True, default=0),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['domain_shared.tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('account_number'),
        schema='domain_erp'
    )

    op.create_table('journal_entries',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('entry_number', sa.String(length=50), nullable=False),
        sa.Column('entry_date', sa.Date(), nullable=False),
        sa.Column('posting_date', sa.Date(), nullable=False),
        sa.Column('document_type', sa.String(length=50), nullable=True),
        sa.Column('document_number', sa.String(length=100), nullable=True),
        sa.Column('reference', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('total_debit', sa.Numeric(precision=15, scale=2), nullable=True, default=0),
        sa.Column('total_credit', sa.Numeric(precision=15, scale=2), nullable=True, default=0),
        sa.Column('status', sa.String(length=50), nullable=True, default='draft'),
        sa.Column('posted_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('posted_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['posted_by'], ['domain_shared.users.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['domain_shared.tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('entry_number'),
        schema='domain_erp'
    )

    op.create_table('journal_entry_lines',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('journal_entry_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('debit', sa.Numeric(precision=15, scale=2), nullable=True, default=0),
        sa.Column('credit', sa.Numeric(precision=15, scale=2), nullable=True, default=0),
        sa.Column('cost_center', sa.String(length=100), nullable=True),
        sa.Column('project', sa.String(length=100), nullable=True),
        sa.Column('line_number', sa.Integer(), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['account_id'], ['domain_erp.chart_of_accounts.id'], ),
        sa.ForeignKeyConstraint(['journal_entry_id'], ['domain_erp.journal_entries.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='domain_erp'
    )

    op.create_table('debitors',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('debitor_number', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('address', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('payment_terms', sa.String(length=100), nullable=True, default='30_days'),
        sa.Column('credit_limit', sa.Numeric(precision=15, scale=2), nullable=True, default=0),
        sa.Column('current_balance', sa.Numeric(precision=15, scale=2), nullable=True, default=0),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['domain_crm.customers.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['domain_shared.tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('debitor_number'),
        schema='domain_erp'
    )

    op.create_table('creditors',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('creditor_number', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('address', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('payment_terms', sa.String(length=100), nullable=True, default='30_days'),
        sa.Column('current_balance', sa.Numeric(precision=15, scale=2), nullable=True, default=0),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['domain_shared.tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('creditor_number'),
        schema='domain_erp'
    )

    # Create Inventory tables
    op.create_table('warehouses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('warehouse_code', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('address', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['domain_shared.tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('warehouse_code'),
        schema='domain_inventory'
    )

    op.create_table('articles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('article_number', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('unit', sa.String(length=20), nullable=True, default='pcs'),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('purchase_price', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('sales_price', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('minimum_stock', sa.Integer(), nullable=True, default=0),
        sa.Column('maximum_stock', sa.Integer(), nullable=True),
        sa.Column('current_stock', sa.Integer(), nullable=True, default=0),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['domain_shared.tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('article_number'),
        schema='domain_inventory'
    )

    op.create_table('stock_locations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('warehouse_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('location_code', sa.String(length=50), nullable=False),
        sa.Column('location_type', sa.String(length=50), nullable=True, default='shelf'),
        sa.Column('capacity', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.ForeignKeyConstraint(['warehouse_id'], ['domain_inventory.warehouses.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('warehouse_id', 'location_code', name='uq_warehouse_location'),
        schema='domain_inventory'
    )

    op.create_table('stock_movements',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('article_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('warehouse_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('location_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('movement_type', sa.String(length=50), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('reference_document', sa.String(length=100), nullable=True),
        sa.Column('reason', sa.String(length=255), nullable=True),
        sa.Column('performed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('movement_date', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['article_id'], ['domain_inventory.articles.id'], ),
        sa.ForeignKeyConstraint(['location_id'], ['domain_inventory.stock_locations.id'], ),
        sa.ForeignKeyConstraint(['performed_by'], ['domain_shared.users.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['domain_shared.tenants.id'], ),
        sa.ForeignKeyConstraint(['warehouse_id'], ['domain_inventory.warehouses.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='domain_inventory'
    )

    # Create Infrastructure tables
    op.create_table('event_store',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('aggregate_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('aggregate_type', sa.String(length=255), nullable=False),
        sa.Column('event_type', sa.String(length=255), nullable=False),
        sa.Column('event_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('event_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True, default='{}'),
        sa.Column('event_version', sa.Integer(), nullable=False),
        sa.Column('occurred_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('processed_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='infrastructure'
    )

    op.create_table('outbox',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_type', sa.String(length=255), nullable=False),
        sa.Column('event_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('event_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True, default='{}'),
        sa.Column('status', sa.String(length=50), nullable=True, default='pending'),
        sa.Column('published_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=True, default=0),
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='infrastructure'
    )

    op.create_table('policy_rules',
        sa.Column('id', sa.String(length=255), nullable=False),
        sa.Column('tenant_id', sa.String(length=255), nullable=True),
        sa.Column('when_kpi_id', sa.String(length=255), nullable=False),
        sa.Column('when_severity', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('action', sa.String(length=255), nullable=False),
        sa.Column('params', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('limits', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('window', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('approval', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('auto_execute', sa.Boolean(), nullable=True, server_default=sa.text('false')),
        sa.Column('auto_suggest', sa.Boolean(), nullable=True, server_default=sa.text('true')),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('audit_log',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=100), nullable=False),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('old_values', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('new_values', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('timestamp', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['domain_shared.users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='infrastructure'
    )

    # Create indexes
    op.create_index('idx_customers_tenant', 'customers', ['tenant_id'], schema='domain_crm')
    op.create_index('idx_customers_number', 'customers', ['customer_number'], schema='domain_crm')
    op.create_index('idx_leads_customer', 'leads', ['customer_id'], schema='domain_crm')
    op.create_index('idx_leads_status', 'leads', ['status'], schema='domain_crm')

    op.create_index('idx_accounts_number', 'chart_of_accounts', ['account_number'], schema='domain_erp')
    op.create_index('idx_accounts_type', 'chart_of_accounts', ['account_type'], schema='domain_erp')
    op.create_index('idx_journal_entries_date', 'journal_entries', ['entry_date'], schema='domain_erp')
    op.create_index('idx_journal_entries_status', 'journal_entries', ['status'], schema='domain_erp')
    op.create_index('idx_journal_lines_entry', 'journal_entry_lines', ['journal_entry_id'], schema='domain_erp')
    op.create_index('idx_debitors_customer', 'debitors', ['customer_id'], schema='domain_erp')
    op.create_index('idx_creditors_number', 'creditors', ['creditor_number'], schema='domain_erp')

    op.create_index('idx_articles_number', 'articles', ['article_number'], schema='domain_inventory')
    op.create_index('idx_articles_category', 'articles', ['category'], schema='domain_inventory')
    op.create_index('idx_stock_movements_article', 'stock_movements', ['article_id'], schema='domain_inventory')
    op.create_index('idx_stock_movements_date', 'stock_movements', ['movement_date'], schema='domain_inventory')

    op.create_index('idx_event_store_aggregate', 'event_store', ['aggregate_id', 'aggregate_type'], schema='infrastructure')
    op.create_index('idx_outbox_status', 'outbox', ['status'], schema='infrastructure')
    op.create_index('idx_audit_log_timestamp', 'audit_log', ['timestamp'], schema='infrastructure')
    op.create_index('idx_audit_log_user', 'audit_log', ['user_id'], schema='infrastructure')

    # Create functions and triggers
    op.execute("""
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)

    # Apply triggers
    op.execute("CREATE TRIGGER update_customers_updated_at BEFORE UPDATE ON domain_crm.customers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();")
    op.execute("CREATE TRIGGER update_leads_updated_at BEFORE UPDATE ON domain_crm.leads FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();")
    op.execute("CREATE TRIGGER update_journal_entries_updated_at BEFORE UPDATE ON domain_erp.journal_entries FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();")
    op.execute("CREATE TRIGGER update_debitors_updated_at BEFORE UPDATE ON domain_erp.debitors FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();")
    op.execute("CREATE TRIGGER update_creditors_updated_at BEFORE UPDATE ON domain_erp.creditors FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();")
    op.execute("CREATE TRIGGER update_articles_updated_at BEFORE UPDATE ON domain_inventory.articles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();")
    op.execute("CREATE TRIGGER update_warehouses_updated_at BEFORE UPDATE ON domain_inventory.warehouses FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();")
    op.execute("CREATE TRIGGER update_outbox_updated_at BEFORE UPDATE ON infrastructure.outbox FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();")


def downgrade():
    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS update_customers_updated_at ON domain_crm.customers;")
    op.execute("DROP TRIGGER IF EXISTS update_leads_updated_at ON domain_crm.leads;")
    op.execute("DROP TRIGGER IF EXISTS update_journal_entries_updated_at ON domain_erp.journal_entries;")
    op.execute("DROP TRIGGER IF EXISTS update_debitors_updated_at ON domain_erp.debitors;")
    op.execute("DROP TRIGGER IF EXISTS update_creditors_updated_at ON domain_erp.creditors;")
    op.execute("DROP TRIGGER IF EXISTS update_articles_updated_at ON domain_inventory.articles;")
    op.execute("DROP TRIGGER IF EXISTS update_warehouses_updated_at ON domain_inventory.warehouses;")
    op.execute("DROP TRIGGER IF EXISTS update_outbox_updated_at ON infrastructure.outbox;")

    # Drop functions
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")

    # Drop indexes
    op.drop_index('idx_audit_log_user', schema='infrastructure')
    op.drop_index('idx_audit_log_timestamp', schema='infrastructure')
    op.drop_index('idx_outbox_status', schema='infrastructure')
    op.drop_index('idx_event_store_aggregate', schema='infrastructure')
    op.drop_index('idx_stock_movements_date', schema='domain_inventory')
    op.drop_index('idx_stock_movements_article', schema='domain_inventory')
    op.drop_index('idx_articles_category', schema='domain_inventory')
    op.drop_index('idx_articles_number', schema='domain_inventory')
    op.drop_index('idx_creditors_number', schema='domain_erp')
    op.drop_index('idx_debitors_customer', schema='domain_erp')
    op.drop_index('idx_journal_lines_entry', schema='domain_erp')
    op.drop_index('idx_journal_entries_status', schema='domain_erp')
    op.drop_index('idx_journal_entries_date', schema='domain_erp')
    op.drop_index('idx_accounts_type', schema='domain_erp')
    op.drop_index('idx_accounts_number', schema='domain_erp')
    op.drop_index('idx_leads_status', schema='domain_crm')
    op.drop_index('idx_leads_customer', schema='domain_crm')
    op.drop_index('idx_customers_number', schema='domain_crm')
    op.drop_index('idx_customers_tenant', schema='domain_crm')

    # Drop tables
    op.drop_table('policy_rules')
    op.drop_table('audit_log', schema='infrastructure')
    op.drop_table('outbox', schema='infrastructure')
    op.drop_table('event_store', schema='infrastructure')
    op.drop_table('stock_movements', schema='domain_inventory')
    op.drop_table('stock_locations', schema='domain_inventory')
    op.drop_table('articles', schema='domain_inventory')
    op.drop_table('warehouses', schema='domain_inventory')
    op.drop_table('creditors', schema='domain_erp')
    op.drop_table('debitors', schema='domain_erp')
    op.drop_table('journal_entry_lines', schema='domain_erp')
    op.drop_table('journal_entries', schema='domain_erp')
    op.drop_table('bank_accounts', schema='domain_erp')
    op.drop_table('chart_of_accounts', schema='domain_erp')
    op.drop_table('leads', schema='domain_crm')
    op.drop_table('customers', schema='domain_crm')
    op.drop_table('users', schema='domain_shared')
    op.drop_table('tenants', schema='domain_shared')

    # Drop schemas
    op.execute("DROP SCHEMA IF EXISTS infrastructure CASCADE;")
    op.execute("DROP SCHEMA IF EXISTS domain_inventory CASCADE;")
    op.execute("DROP SCHEMA IF EXISTS domain_erp CASCADE;")
    op.execute("DROP SCHEMA IF EXISTS domain_crm CASCADE;")
    op.execute("DROP SCHEMA IF EXISTS domain_shared CASCADE;")
