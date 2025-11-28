"""Add portal tables: contracts, prepurchases, orders

Revision ID: portal_001
Revises: ff7b1a7899b4
Create Date: 2024-11-28

Kundenportal-Tabellen für:
- Kundenkontrakte (Rahmenverträge)
- Vorkäufe (bereits bezahlte Ware)
- Kundenbestellungen
- Bestellpositionen
- Bestellhistorie
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'portal_001'
down_revision = 'ff7b1a7899b4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Schema erstellen falls nicht vorhanden
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_portal")
    
    # Enum-Typen erstellen
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE domain_portal.contract_status AS ENUM ('NONE', 'ACTIVE', 'LOW', 'EXHAUSTED');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE domain_portal.order_status AS ENUM (
                'DRAFT', 'SUBMITTED', 'CONFIRMED', 'IN_PROGRESS', 
                'SHIPPED', 'DELIVERED', 'CANCELLED'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Kundenkontrakte
    op.create_table(
        'customer_contracts',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), nullable=False, index=True),
        sa.Column('customer_id', sa.String(36), nullable=False, index=True),
        sa.Column('article_id', sa.String(36), nullable=False, index=True),
        sa.Column('article_number', sa.String(50), nullable=False),
        sa.Column('article_name', sa.String(200), nullable=False),
        sa.Column('contract_number', sa.String(50), nullable=False, unique=True),
        sa.Column('contract_price', sa.Numeric(12, 2), nullable=False),
        sa.Column('list_price', sa.Numeric(12, 2), nullable=False),
        sa.Column('unit', sa.String(20), nullable=False),
        sa.Column('total_quantity', sa.Numeric(12, 2), nullable=False),
        sa.Column('remaining_quantity', sa.Numeric(12, 2), nullable=False),
        sa.Column('status', sa.Enum('NONE', 'ACTIVE', 'LOW', 'EXHAUSTED', name='contract_status', schema='domain_portal'), 
                  nullable=False, server_default='ACTIVE'),
        sa.Column('valid_from', sa.DateTime(timezone=True), nullable=False),
        sa.Column('valid_until', sa.DateTime(timezone=True), nullable=False),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column('created_by', sa.String(36), nullable=True),
        schema='domain_portal'
    )
    
    # Vorkäufe
    op.create_table(
        'customer_pre_purchases',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), nullable=False, index=True),
        sa.Column('customer_id', sa.String(36), nullable=False, index=True),
        sa.Column('article_id', sa.String(36), nullable=False, index=True),
        sa.Column('article_number', sa.String(50), nullable=False),
        sa.Column('article_name', sa.String(200), nullable=False),
        sa.Column('pre_purchase_number', sa.String(50), nullable=False, unique=True),
        sa.Column('pre_purchase_price', sa.Numeric(12, 2), nullable=False),
        sa.Column('current_list_price', sa.Numeric(12, 2), nullable=False),
        sa.Column('unit', sa.String(20), nullable=False),
        sa.Column('total_quantity', sa.Numeric(12, 2), nullable=False),
        sa.Column('remaining_quantity', sa.Numeric(12, 2), nullable=False),
        sa.Column('payment_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('payment_reference', sa.String(100), nullable=True),
        sa.Column('valid_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        schema='domain_portal'
    )
    
    # Kundenbestellungen
    op.create_table(
        'customer_orders',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), nullable=False, index=True),
        sa.Column('customer_id', sa.String(36), nullable=False, index=True),
        sa.Column('customer_number', sa.String(50), nullable=False),
        sa.Column('customer_name', sa.String(200), nullable=False),
        sa.Column('order_number', sa.String(50), nullable=False, unique=True),
        sa.Column('order_date', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('status', sa.Enum('DRAFT', 'SUBMITTED', 'CONFIRMED', 'IN_PROGRESS', 
                                    'SHIPPED', 'DELIVERED', 'CANCELLED', 
                                    name='order_status', schema='domain_portal'),
                  nullable=False, server_default='SUBMITTED'),
        sa.Column('total_net', sa.Numeric(12, 2), server_default='0'),
        sa.Column('total_gross', sa.Numeric(12, 2), server_default='0'),
        sa.Column('delivery_address', sa.Text, nullable=True),
        sa.Column('delivery_date_requested', sa.DateTime(timezone=True), nullable=True),
        sa.Column('customer_notes', sa.Text, nullable=True),
        sa.Column('internal_notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        schema='domain_portal'
    )
    
    # Bestellpositionen
    op.create_table(
        'customer_order_items',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('order_id', sa.String(36), sa.ForeignKey('domain_portal.customer_orders.id'), nullable=False),
        sa.Column('article_id', sa.String(36), nullable=False),
        sa.Column('article_number', sa.String(50), nullable=False),
        sa.Column('article_name', sa.String(200), nullable=False),
        sa.Column('quantity', sa.Numeric(12, 2), nullable=False),
        sa.Column('unit', sa.String(20), nullable=False),
        sa.Column('unit_price', sa.Numeric(12, 2), nullable=False),
        sa.Column('total_price', sa.Numeric(12, 2), nullable=False),
        sa.Column('price_source', sa.String(20), nullable=False),
        sa.Column('contract_id', sa.String(36), nullable=True),
        sa.Column('pre_purchase_id', sa.String(36), nullable=True),
        sa.Column('quantity_from_credit', sa.Numeric(12, 2), server_default='0'),
        sa.Column('quantity_at_list_price', sa.Numeric(12, 2), server_default='0'),
        schema='domain_portal'
    )
    
    # Bestellhistorie
    op.create_table(
        'customer_order_history',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), nullable=False, index=True),
        sa.Column('customer_id', sa.String(36), nullable=False, index=True),
        sa.Column('article_id', sa.String(36), nullable=False, index=True),
        sa.Column('last_order_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_order_quantity', sa.Numeric(12, 2), nullable=False),
        sa.Column('last_order_id', sa.String(36), nullable=False),
        sa.Column('total_orders', sa.Integer, server_default='1'),
        sa.Column('total_quantity', sa.Numeric(12, 2), nullable=False),
        sa.Column('average_quantity', sa.Numeric(12, 2), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        schema='domain_portal'
    )
    
    # Indizes für Performance
    op.create_index('ix_customer_contracts_lookup', 'customer_contracts', 
                    ['tenant_id', 'customer_id', 'article_id'], schema='domain_portal')
    op.create_index('ix_customer_pre_purchases_lookup', 'customer_pre_purchases',
                    ['tenant_id', 'customer_id', 'article_id'], schema='domain_portal')
    op.create_index('ix_customer_orders_date', 'customer_orders',
                    ['tenant_id', 'customer_id', 'order_date'], schema='domain_portal')
    op.create_index('ix_customer_order_history_lookup', 'customer_order_history',
                    ['tenant_id', 'customer_id', 'article_id', 'last_order_date'], schema='domain_portal')


def downgrade() -> None:
    # Indizes entfernen
    op.drop_index('ix_customer_order_history_lookup', table_name='customer_order_history', schema='domain_portal')
    op.drop_index('ix_customer_orders_date', table_name='customer_orders', schema='domain_portal')
    op.drop_index('ix_customer_pre_purchases_lookup', table_name='customer_pre_purchases', schema='domain_portal')
    op.drop_index('ix_customer_contracts_lookup', table_name='customer_contracts', schema='domain_portal')
    
    # Tabellen entfernen
    op.drop_table('customer_order_history', schema='domain_portal')
    op.drop_table('customer_order_items', schema='domain_portal')
    op.drop_table('customer_orders', schema='domain_portal')
    op.drop_table('customer_pre_purchases', schema='domain_portal')
    op.drop_table('customer_contracts', schema='domain_portal')
    
    # Enum-Typen entfernen
    op.execute("DROP TYPE IF EXISTS domain_portal.order_status")
    op.execute("DROP TYPE IF EXISTS domain_portal.contract_status")

