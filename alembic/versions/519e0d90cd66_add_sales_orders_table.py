"""add_sales_orders_table

Revision ID: 519e0d90cd66
Revises: 5ebb49807644
Create Date: 2025-10-16 07:33:53.652295

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '519e0d90cd66'
down_revision: Union[str, None] = '5ebb49807644'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create sales_orders table
    op.create_table('sales_orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sales_offer_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_number', sa.String(), nullable=False),
        sa.Column('subject', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('total_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, default='EUR'),
        sa.Column('status', sa.String(), nullable=False, default='ENTWURF'),
        sa.Column('contact_person', sa.String(), nullable=True),
        sa.Column('delivery_date', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('delivery_address', sa.Text(), nullable=True),
        sa.Column('payment_terms', sa.String(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False, default=1),
        sa.ForeignKeyConstraint(['tenant_id'], ['domain_shared.tenants.id'], ),
        sa.ForeignKeyConstraint(['sales_offer_id'], ['domain_crm.sales_offers.id'], ),
        sa.ForeignKeyConstraint(['customer_id'], ['domain_crm.customers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_number'),
        schema='domain_crm'
    )


def downgrade() -> None:
    # Drop sales_orders table
    op.drop_table('sales_orders', schema='domain_crm')
