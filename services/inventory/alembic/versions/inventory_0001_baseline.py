"""Basis des Inventory-Schemas aus app.db.models.

Ersetzt die nie angewendeten Vorgaengerrevisionen (doppelte Enum-Anlage, Revisions-IDs
laenger als version_num, Abweichung von den Modellen). Eigene Versionstabelle siehe env.py.

Revision ID: inventory_0001
Revises:
Create Date: 2026-10-26
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "inventory_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('inventory_goods_receipts',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.String(length=64), nullable=False),
    sa.Column('gr_number', sa.String(length=64), nullable=False),
    sa.Column('po_number', sa.String(length=64), nullable=False),
    sa.Column('po_id', sa.UUID(), nullable=True),
    sa.Column('supplier_id', sa.UUID(), nullable=True),
    sa.Column('supplier_name', sa.String(length=256), nullable=False),
    sa.Column('delivery_note_number', sa.String(length=64), nullable=True),
    sa.Column('receipt_date', sa.DateTime(), nullable=False),
    sa.Column('status', sa.Enum('DRAFT', 'POSTED', 'CANCELLED', name='goods_receipt_status'), nullable=False),
    sa.Column('notes', sa.Text(), nullable=False),
    sa.Column('created_by', sa.String(length=128), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_inventory_goods_receipts_gr_number'), 'inventory_goods_receipts', ['gr_number'], unique=True)
    op.create_index(op.f('ix_inventory_goods_receipts_po_number'), 'inventory_goods_receipts', ['po_number'], unique=False)
    op.create_index(op.f('ix_inventory_goods_receipts_tenant_id'), 'inventory_goods_receipts', ['tenant_id'], unique=False)
    op.create_table('inventory_lots',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('sku', sa.String(length=64), nullable=False),
    sa.Column('lot_number', sa.String(length=64), nullable=False),
    sa.Column('production_date', sa.DateTime(), nullable=True),
    sa.Column('expiry_date', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('inventory_warehouses',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('code', sa.String(length=32), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('address', sa.Text(), nullable=True),
    sa.Column('tenant_id', sa.String(length=64), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_inventory_warehouses_code'), 'inventory_warehouses', ['code'], unique=True)
    op.create_table('inventory_epcis_events',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.String(length=64), nullable=False),
    sa.Column('event_key', sa.String(length=128), nullable=True),
    sa.Column('event_type', sa.Enum('OBJECT', 'AGGREGATION', 'TRANSFORMATION', 'TRANSACTION', name='epcis_event_type'), nullable=False),
    sa.Column('event_time', sa.DateTime(), nullable=False),
    sa.Column('biz_step', sa.String(length=128), nullable=True),
    sa.Column('read_point', sa.String(length=128), nullable=True),
    sa.Column('lot_id', sa.UUID(), nullable=True),
    sa.Column('sku', sa.String(length=64), nullable=True),
    sa.Column('quantity', sa.Numeric(precision=16, scale=3), nullable=True),
    sa.Column('extensions', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['lot_id'], ['inventory_lots.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_inventory_epcis_events_event_key'), 'inventory_epcis_events', ['event_key'], unique=True)
    op.create_index(op.f('ix_inventory_epcis_events_event_time'), 'inventory_epcis_events', ['event_time'], unique=False)
    op.create_index(op.f('ix_inventory_epcis_events_tenant_id'), 'inventory_epcis_events', ['tenant_id'], unique=False)
    op.create_table('inventory_locations',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('warehouse_id', sa.UUID(), nullable=False),
    sa.Column('code', sa.String(length=32), nullable=False),
    sa.Column('location_type', sa.String(length=32), nullable=False),
    sa.Column('capacity_units', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['warehouse_id'], ['inventory_warehouses.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_inventory_locations_warehouse_id'), 'inventory_locations', ['warehouse_id'], unique=False)
    op.create_table('inventory_goods_receipt_lines',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('goods_receipt_id', sa.UUID(), nullable=False),
    sa.Column('po_line_number', sa.Integer(), nullable=False),
    sa.Column('sku', sa.String(length=64), nullable=False),
    sa.Column('description', sa.String(length=256), nullable=False),
    sa.Column('ordered_quantity', sa.Numeric(precision=16, scale=3), nullable=False),
    sa.Column('received_quantity', sa.Numeric(precision=16, scale=3), nullable=False),
    sa.Column('unit', sa.String(length=16), nullable=False),
    sa.Column('lot_number', sa.String(length=64), nullable=True),
    sa.Column('warehouse_id', sa.UUID(), nullable=False),
    sa.Column('location_id', sa.UUID(), nullable=False),
    sa.Column('quality_status', sa.String(length=32), nullable=False),
    sa.Column('notes', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['goods_receipt_id'], ['inventory_goods_receipts.id'], ),
    sa.ForeignKeyConstraint(['location_id'], ['inventory_locations.id'], ),
    sa.ForeignKeyConstraint(['warehouse_id'], ['inventory_warehouses.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_inventory_goods_receipt_lines_goods_receipt_id'), 'inventory_goods_receipt_lines', ['goods_receipt_id'], unique=False)
    op.create_table('inventory_stock_items',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('warehouse_id', sa.UUID(), nullable=False),
    sa.Column('location_id', sa.UUID(), nullable=False),
    sa.Column('lot_id', sa.UUID(), nullable=False),
    sa.Column('quantity', sa.Numeric(precision=16, scale=3), nullable=False),
    sa.Column('reserved_quantity', sa.Numeric(precision=16, scale=3), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['location_id'], ['inventory_locations.id'], ),
    sa.ForeignKeyConstraint(['lot_id'], ['inventory_lots.id'], ),
    sa.ForeignKeyConstraint(['warehouse_id'], ['inventory_warehouses.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_inventory_stock_items_location_id'), 'inventory_stock_items', ['location_id'], unique=False)
    op.create_index(op.f('ix_inventory_stock_items_lot_id'), 'inventory_stock_items', ['lot_id'], unique=False)
    op.create_index(op.f('ix_inventory_stock_items_warehouse_id'), 'inventory_stock_items', ['warehouse_id'], unique=False)
    op.create_table('inventory_transactions',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('stock_item_id', sa.UUID(), nullable=False),
    sa.Column('transaction_type', sa.Enum('RECEIPT', 'TRANSFER', 'ADJUSTMENT', name='inventory_transaction_type'), nullable=False),
    sa.Column('quantity', sa.Numeric(precision=16, scale=3), nullable=False),
    sa.Column('reference', sa.String(length=128), nullable=True),
    sa.Column('from_location_id', sa.UUID(), nullable=True),
    sa.Column('to_location_id', sa.UUID(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['from_location_id'], ['inventory_locations.id'], ),
    sa.ForeignKeyConstraint(['stock_item_id'], ['inventory_stock_items.id'], ),
    sa.ForeignKeyConstraint(['to_location_id'], ['inventory_locations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_inventory_transactions_stock_item_id'), 'inventory_transactions', ['stock_item_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_inventory_transactions_stock_item_id'), table_name='inventory_transactions')
    op.drop_table('inventory_transactions')
    op.drop_index(op.f('ix_inventory_stock_items_warehouse_id'), table_name='inventory_stock_items')
    op.drop_index(op.f('ix_inventory_stock_items_lot_id'), table_name='inventory_stock_items')
    op.drop_index(op.f('ix_inventory_stock_items_location_id'), table_name='inventory_stock_items')
    op.drop_table('inventory_stock_items')
    op.drop_index(op.f('ix_inventory_goods_receipt_lines_goods_receipt_id'), table_name='inventory_goods_receipt_lines')
    op.drop_table('inventory_goods_receipt_lines')
    op.drop_index(op.f('ix_inventory_locations_warehouse_id'), table_name='inventory_locations')
    op.drop_table('inventory_locations')
    op.drop_index(op.f('ix_inventory_epcis_events_tenant_id'), table_name='inventory_epcis_events')
    op.drop_index(op.f('ix_inventory_epcis_events_event_time'), table_name='inventory_epcis_events')
    op.drop_index(op.f('ix_inventory_epcis_events_event_key'), table_name='inventory_epcis_events')
    op.drop_table('inventory_epcis_events')
    op.drop_index(op.f('ix_inventory_warehouses_code'), table_name='inventory_warehouses')
    op.drop_table('inventory_warehouses')
    op.drop_table('inventory_lots')
    op.drop_index(op.f('ix_inventory_goods_receipts_tenant_id'), table_name='inventory_goods_receipts')
    op.drop_index(op.f('ix_inventory_goods_receipts_po_number'), table_name='inventory_goods_receipts')
    op.drop_index(op.f('ix_inventory_goods_receipts_gr_number'), table_name='inventory_goods_receipts')
    op.drop_table('inventory_goods_receipts')
    sa.Enum(name='goods_receipt_status').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='epcis_event_type').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='inventory_transaction_type').drop(op.get_bind(), checkfirst=True)
