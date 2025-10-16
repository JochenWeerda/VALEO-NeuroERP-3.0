"""Add inventory entities: stock movements and inventory counts

Revision ID: add_inv_ent
Revises: 1368e3f15650
Create Date: 2025-10-14 09:05:30.335000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_inv_ent'
down_revision: Union[str, None] = '1368e3f15650'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create stock movements table
    op.create_table('inventory_stock_movements',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('article_id', sa.String(), nullable=False),
        sa.Column('warehouse_id', sa.String(), nullable=False),
        sa.Column('movement_type', sa.String(length=20), nullable=False),
        sa.Column('quantity', sa.DECIMAL(10, 2), nullable=False),
        sa.Column('unit_cost', sa.DECIMAL(10, 2), nullable=True),
        sa.Column('reference_number', sa.String(length=50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('previous_stock', sa.DECIMAL(10, 2), nullable=False),
        sa.Column('new_stock', sa.DECIMAL(10, 2), nullable=False),
        sa.Column('total_cost', sa.DECIMAL(12, 2), nullable=True),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['article_id'], ['domain_inventory.articles.id'], ),
        sa.ForeignKeyConstraint(['warehouse_id'], ['domain_inventory.warehouses.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['domain_shared.tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='domain_inventory'
    )

    # Create inventory counts table
    op.create_table('inventory_counts',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('warehouse_id', sa.String(), nullable=False),
        sa.Column('count_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('counted_by', sa.String(), nullable=False),
        sa.Column('status', sa.String(length=20), server_default='draft', nullable=True),
        sa.Column('total_items', sa.Integer(), server_default='0', nullable=True),
        sa.Column('discrepancies_found', sa.Integer(), server_default='0', nullable=True),
        sa.Column('approved_by', sa.String(), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['approved_by'], ['domain_shared.users.id'], ),
        sa.ForeignKeyConstraint(['counted_by'], ['domain_shared.users.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['domain_shared.tenants.id'], ),
        sa.ForeignKeyConstraint(['warehouse_id'], ['domain_inventory.warehouses.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='domain_inventory'
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('inventory_counts', schema='domain_inventory')
    op.drop_table('inventory_stock_movements', schema='domain_inventory')