"""Add L3-Connect gap closure tables

Revision ID: l3c_gap_001
Revises: 4b6600ac3926, 59b4fa8420f2
Create Date: 2026-02-10
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'l3c_gap_001'
down_revision: Union[str, None] = ('4b6600ac3926', '59b4fa8420f2')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ensure schemas exist
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_inventory")
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_shared")

    # ── Inventory Count Lines ────────────────────────────────────
    op.create_table(
        'inventory_count_lines',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('inventory_count_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('domain_inventory.inventory_counts.id'), nullable=False),
        sa.Column('article_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('domain_inventory.articles.id'), nullable=False),
        sa.Column('expected_qty', sa.DECIMAL(12, 3), server_default='0'),
        sa.Column('counted_qty', sa.DECIMAL(12, 3), server_default='0'),
        sa.Column('difference', sa.DECIMAL(12, 3), server_default='0'),
        sa.Column('warehouse_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('domain_inventory.warehouses.id'), nullable=True),
        sa.Column('bin_location_id', sa.String(), nullable=True),
        sa.Column('batch_number', sa.String(50), nullable=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('domain_shared.tenants.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        schema='domain_inventory',
    )

    # ── Weighing Tickets ─────────────────────────────────────────
    op.create_table(
        'weighing_tickets',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('ticket_number', sa.String(50), nullable=False),
        sa.Column('scale_id', sa.String(50), nullable=True),
        sa.Column('vehicle_plate', sa.String(20), nullable=True),
        sa.Column('gross_weight', sa.DECIMAL(12, 3), nullable=True),
        sa.Column('tare_weight', sa.DECIMAL(12, 3), nullable=True),
        sa.Column('net_weight', sa.DECIMAL(12, 3), nullable=True),
        sa.Column('weighing_date', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('status', sa.String(20), server_default='open'),
        sa.Column('direction', sa.String(10), server_default='in'),
        sa.Column('reference_doc', sa.String(100), nullable=True),
        sa.Column('tenant_id', sa.String(), sa.ForeignKey('domain_shared.tenants.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        schema='domain_inventory',
    )

    op.create_table(
        'weighing_ticket_lines',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('ticket_id', sa.String(), sa.ForeignKey('domain_inventory.weighing_tickets.id'), nullable=False),
        sa.Column('article_id', sa.String(), sa.ForeignKey('domain_inventory.articles.id'), nullable=False),
        sa.Column('quantity', sa.DECIMAL(12, 3), nullable=False),
        sa.Column('unit', sa.String(10), server_default='kg'),
        sa.Column('tenant_id', sa.String(), sa.ForeignKey('domain_shared.tenants.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema='domain_inventory',
    )

    # ── Warehouse Transfers ──────────────────────────────────────
    op.create_table(
        'warehouse_transfers',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('transfer_number', sa.String(50), nullable=False),
        sa.Column('from_warehouse_id', sa.String(), sa.ForeignKey('domain_inventory.warehouses.id'), nullable=False),
        sa.Column('to_warehouse_id', sa.String(), sa.ForeignKey('domain_inventory.warehouses.id'), nullable=False),
        sa.Column('status', sa.String(20), server_default='draft'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('tenant_id', sa.String(), sa.ForeignKey('domain_shared.tenants.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        schema='domain_inventory',
    )

    op.create_table(
        'warehouse_transfer_lines',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('transfer_id', sa.String(), sa.ForeignKey('domain_inventory.warehouse_transfers.id'), nullable=False),
        sa.Column('article_id', sa.String(), sa.ForeignKey('domain_inventory.articles.id'), nullable=False),
        sa.Column('quantity', sa.DECIMAL(12, 3), nullable=False),
        sa.Column('batch_number', sa.String(50), nullable=True),
        sa.Column('tenant_id', sa.String(), sa.ForeignKey('domain_shared.tenants.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema='domain_inventory',
    )

    # ── Stock Corrections ────────────────────────────────────────
    op.create_table(
        'stock_corrections',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('correction_number', sa.String(50), nullable=False),
        sa.Column('warehouse_id', sa.String(), sa.ForeignKey('domain_inventory.warehouses.id'), nullable=False),
        sa.Column('reason', sa.String(100), nullable=True),
        sa.Column('status', sa.String(20), server_default='draft'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('tenant_id', sa.String(), sa.ForeignKey('domain_shared.tenants.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        schema='domain_inventory',
    )

    op.create_table(
        'stock_correction_lines',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('correction_id', sa.String(), sa.ForeignKey('domain_inventory.stock_corrections.id'), nullable=False),
        sa.Column('article_id', sa.String(), sa.ForeignKey('domain_inventory.articles.id'), nullable=False),
        sa.Column('old_quantity', sa.DECIMAL(12, 3), nullable=False),
        sa.Column('new_quantity', sa.DECIMAL(12, 3), nullable=False),
        sa.Column('difference', sa.DECIMAL(12, 3), nullable=False),
        sa.Column('batch_number', sa.String(50), nullable=True),
        sa.Column('tenant_id', sa.String(), sa.ForeignKey('domain_shared.tenants.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema='domain_inventory',
    )

    # ── Bin Locations ────────────────────────────────────────────
    op.create_table(
        'bin_locations',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('warehouse_id', sa.String(), sa.ForeignKey('domain_inventory.warehouses.id'), nullable=False),
        sa.Column('zone', sa.String(20), nullable=True),
        sa.Column('rack', sa.String(20), nullable=True),
        sa.Column('shelf', sa.String(20), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('tenant_id', sa.String(), sa.ForeignKey('domain_shared.tenants.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema='domain_inventory',
    )

    # ── Preparation Lists ────────────────────────────────────────
    op.create_table(
        'preparation_lists',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('list_number', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), server_default='open'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('warehouse_id', sa.String(), sa.ForeignKey('domain_inventory.warehouses.id'), nullable=True),
        sa.Column('tenant_id', sa.String(), sa.ForeignKey('domain_shared.tenants.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        schema='domain_inventory',
    )

    op.create_table(
        'preparation_list_lines',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('list_id', sa.String(), sa.ForeignKey('domain_inventory.preparation_lists.id'), nullable=False),
        sa.Column('article_id', sa.String(), sa.ForeignKey('domain_inventory.articles.id'), nullable=False),
        sa.Column('required_qty', sa.DECIMAL(12, 3), nullable=False),
        sa.Column('picked_qty', sa.DECIMAL(12, 3), server_default='0'),
        sa.Column('bin_location_id', sa.String(), nullable=True),
        sa.Column('tenant_id', sa.String(), sa.ForeignKey('domain_shared.tenants.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema='domain_inventory',
    )

    # ── Pick Lists ───────────────────────────────────────────────
    op.create_table(
        'pick_lists',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('pick_list_number', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(20), server_default='open'),
        sa.Column('tour_id', sa.String(), nullable=True),
        sa.Column('order_id', sa.String(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('tenant_id', sa.String(), sa.ForeignKey('domain_shared.tenants.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        schema='domain_inventory',
    )

    op.create_table(
        'pick_list_lines',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('pick_list_id', sa.String(), sa.ForeignKey('domain_inventory.pick_lists.id'), nullable=False),
        sa.Column('article_id', sa.String(), sa.ForeignKey('domain_inventory.articles.id'), nullable=False),
        sa.Column('required_qty', sa.DECIMAL(12, 3), nullable=False),
        sa.Column('picked_qty', sa.DECIMAL(12, 3), server_default='0'),
        sa.Column('bin_location_id', sa.String(), nullable=True),
        sa.Column('batch_number', sa.String(50), nullable=True),
        sa.Column('tenant_id', sa.String(), sa.ForeignKey('domain_shared.tenants.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema='domain_inventory',
    )

    # ── Shipping Units (NVE/SSCC) ────────────────────────────────
    op.create_table(
        'shipping_units',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('sscc', sa.String(18), nullable=False, unique=True),
        sa.Column('status', sa.String(20), server_default='created'),
        sa.Column('order_id', sa.String(), nullable=True),
        sa.Column('delivery_note_id', sa.String(), nullable=True),
        sa.Column('weight', sa.DECIMAL(12, 3), nullable=True),
        sa.Column('contents', postgresql.JSONB(), nullable=True),
        sa.Column('tenant_id', sa.String(), sa.ForeignKey('domain_shared.tenants.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        schema='domain_inventory',
    )

    # ── Webhook Registrations ────────────────────────────────────
    op.create_table(
        'webhook_registrations',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('url', sa.String(500), nullable=False),
        sa.Column('event_area', sa.String(50), nullable=False),
        sa.Column('secret', sa.String(200), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('tenant_id', sa.String(), sa.ForeignKey('domain_shared.tenants.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        schema='domain_shared',
    )

    # ── Article Batches ──────────────────────────────────────────
    op.create_table(
        'article_batches',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('article_id', sa.String(), sa.ForeignKey('domain_inventory.articles.id'), nullable=False),
        sa.Column('batch_number', sa.String(50), nullable=False),
        sa.Column('warehouse_id', sa.String(), sa.ForeignKey('domain_inventory.warehouses.id'), nullable=False),
        sa.Column('quantity', sa.DECIMAL(12, 3), server_default='0'),
        sa.Column('expiry_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tenant_id', sa.String(), sa.ForeignKey('domain_shared.tenants.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema='domain_inventory',
    )

    # ── Internal Messages ────────────────────────────────────────
    op.create_table(
        'internal_messages',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('sender_id', sa.String(), sa.ForeignKey('domain_shared.users.id'), nullable=False),
        sa.Column('recipient_id', sa.String(), sa.ForeignKey('domain_shared.users.id'), nullable=False),
        sa.Column('subject', sa.String(200), nullable=False),
        sa.Column('body', sa.Text(), nullable=True),
        sa.Column('is_read', sa.Boolean(), server_default='false'),
        sa.Column('tenant_id', sa.String(), sa.ForeignKey('domain_shared.tenants.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema='domain_shared',
    )

    # ── Master Data Entries ──────────────────────────────────────
    op.create_table(
        'master_data_entries',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('label', sa.String(200), nullable=False),
        sa.Column('extra', postgresql.JSONB(), nullable=True),
        sa.Column('sort_order', sa.Integer(), server_default='0'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('tenant_id', sa.String(), sa.ForeignKey('domain_shared.tenants.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        schema='domain_shared',
    )

    # ── Dispatchers ──────────────────────────────────────────────
    op.create_table(
        'dispatchers',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('code', sa.String(20), nullable=True),
        sa.Column('email', sa.String(100), nullable=True),
        sa.Column('phone', sa.String(30), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('tenant_id', sa.String(), sa.ForeignKey('domain_shared.tenants.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        schema='domain_shared',
    )

    # ── Article Selections ───────────────────────────────────────
    op.create_table(
        'article_selections',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('article_id', sa.String(), sa.ForeignKey('domain_inventory.articles.id'), nullable=False),
        sa.Column('selection_code', sa.String(50), nullable=False),
        sa.Column('label', sa.String(200), nullable=True),
        sa.Column('tenant_id', sa.String(), sa.ForeignKey('domain_shared.tenants.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema='domain_inventory',
    )

    # ── Performance Indices ──────────────────────────────────────
    op.create_index('ix_weighing_tickets_tenant', 'weighing_tickets', ['tenant_id'], schema='domain_inventory')
    op.create_index('ix_warehouse_transfers_tenant', 'warehouse_transfers', ['tenant_id'], schema='domain_inventory')
    op.create_index('ix_stock_corrections_tenant', 'stock_corrections', ['tenant_id'], schema='domain_inventory')
    op.create_index('ix_pick_lists_tenant', 'pick_lists', ['tenant_id'], schema='domain_inventory')
    op.create_index('ix_shipping_units_sscc', 'shipping_units', ['sscc'], schema='domain_inventory', unique=True)
    op.create_index('ix_article_batches_article', 'article_batches', ['article_id'], schema='domain_inventory')
    op.create_index('ix_internal_messages_recipient', 'internal_messages', ['recipient_id'], schema='domain_shared')
    op.create_index('ix_master_data_category', 'master_data_entries', ['category', 'tenant_id'], schema='domain_shared')


def downgrade() -> None:
    # Drop indices
    op.drop_index('ix_master_data_category', table_name='master_data_entries', schema='domain_shared')
    op.drop_index('ix_internal_messages_recipient', table_name='internal_messages', schema='domain_shared')
    op.drop_index('ix_article_batches_article', table_name='article_batches', schema='domain_inventory')
    op.drop_index('ix_shipping_units_sscc', table_name='shipping_units', schema='domain_inventory')
    op.drop_index('ix_pick_lists_tenant', table_name='pick_lists', schema='domain_inventory')
    op.drop_index('ix_stock_corrections_tenant', table_name='stock_corrections', schema='domain_inventory')
    op.drop_index('ix_warehouse_transfers_tenant', table_name='warehouse_transfers', schema='domain_inventory')
    op.drop_index('ix_weighing_tickets_tenant', table_name='weighing_tickets', schema='domain_inventory')

    # Drop tables in reverse order
    op.drop_table('article_selections', schema='domain_inventory')
    op.drop_table('dispatchers', schema='domain_shared')
    op.drop_table('master_data_entries', schema='domain_shared')
    op.drop_table('internal_messages', schema='domain_shared')
    op.drop_table('article_batches', schema='domain_inventory')
    op.drop_table('webhook_registrations', schema='domain_shared')
    op.drop_table('shipping_units', schema='domain_inventory')
    op.drop_table('pick_list_lines', schema='domain_inventory')
    op.drop_table('pick_lists', schema='domain_inventory')
    op.drop_table('preparation_list_lines', schema='domain_inventory')
    op.drop_table('preparation_lists', schema='domain_inventory')
    op.drop_table('bin_locations', schema='domain_inventory')
    op.drop_table('stock_correction_lines', schema='domain_inventory')
    op.drop_table('stock_corrections', schema='domain_inventory')
    op.drop_table('warehouse_transfer_lines', schema='domain_inventory')
    op.drop_table('warehouse_transfers', schema='domain_inventory')
    op.drop_table('weighing_ticket_lines', schema='domain_inventory')
    op.drop_table('weighing_tickets', schema='domain_inventory')
    op.drop_table('inventory_count_lines', schema='domain_inventory')
