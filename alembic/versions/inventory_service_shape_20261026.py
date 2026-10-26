"""Bring the public inventory compatibility tables into the inventory service's shape.

wms_material_flow_stock_link_20260619 created public.inventory_warehouses, _locations,
_goods_receipts and _goods_receipt_lines with TEXT ids so that the procurement match could
read goods receipts. The inventory service owns these tables (user decision 2026-10-26,
INVENTORY-OWNERSHIP-20261026) and models them with uuid ids; on a fresh database the TEXT
tables came first and the service could not start. The backend stays a reader.

Tables already in the service shape (every grown database so far) are left alone. Empty
tables in TEXT shape are replaced by the service shape. TEXT tables holding rows stop the
migration: converting them silently could lose or reinterpret data.

The _create_* functions are copies of services/inventory/alembic/versions/
inventory_0001_baseline.py; tests/test_inventory_service_shape.py keeps them identical.

Downgrade is a no-op: restoring the TEXT shape would break the service again, and the
tables may hold rows the service wrote.
"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "inventory_service_shape_20261026"
down_revision = "runtime_ddl_to_migrations_20261026"
branch_labels = None
depends_on = None


def _create_inventory_warehouses() -> None:
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


def _create_inventory_locations() -> None:
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


def _create_inventory_goods_receipts() -> None:
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


def _create_inventory_goods_receipt_lines() -> None:
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


# Dependency order for creation; drops run in reverse.
_TABLES = (
    ('inventory_warehouses', _create_inventory_warehouses),
    ('inventory_locations', _create_inventory_locations),
    ('inventory_goods_receipts', _create_inventory_goods_receipts),
    ('inventory_goods_receipt_lines', _create_inventory_goods_receipt_lines),
)

# Read paths of app/services/procurement_match_service.py, as in the original migration.
_READ_INDEXES = (
    "CREATE INDEX IF NOT EXISTS ix_inventory_gr_tenant_po "
    "ON inventory_goods_receipts (tenant_id, po_number, po_id)",
    "CREATE INDEX IF NOT EXISTS ix_inventory_gr_lines_receipt "
    "ON inventory_goods_receipt_lines (goods_receipt_id, po_line_number)",
)


def _id_type(bind, table: str) -> str | None:
    return bind.execute(
        sa.text(
            "SELECT data_type FROM information_schema.columns "
            "WHERE table_schema = current_schema() AND table_name = :t AND column_name = 'id'"
        ),
        {"t": table},
    ).scalar()


def upgrade() -> None:
    bind = op.get_bind()
    id_types = {table: _id_type(bind, table) for table, _ in _TABLES}
    if all(id_type == "uuid" for id_type in id_types.values()):
        return

    foreign = [t for t, id_type in id_types.items() if id_type not in (None, "uuid")]
    filled = [
        t for t in foreign
        if bind.execute(sa.text(f'SELECT EXISTS (SELECT 1 FROM "{t}")')).scalar()  # nosec B608 - fixed table names
    ]
    if filled:
        raise RuntimeError(
            "inventory compatibility tables hold rows in TEXT shape, convert them by hand "
            f"before migrating: {', '.join(filled)}"
        )

    for table, _ in reversed(_TABLES):
        if id_types[table] not in (None, "uuid"):
            op.drop_table(table)
    for table, create in _TABLES:
        if id_types[table] != "uuid":
            create()
    for statement in _READ_INDEXES:
        op.execute(statement)


def downgrade() -> None:
    pass
