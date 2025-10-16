"""Add sales_offers table

Revision ID: 69a59fde9295
Revises: ff7b1a7899b4
Create Date: 2025-10-16 06:38:59.465712

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '69a59fde9295'
down_revision: Union[str, None] = 'eca81651f8ba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create sales_offers table
    op.create_table('sales_offers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('customer_inquiry_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('offer_number', sa.String(), nullable=False),
        sa.Column('subject', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('total_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, default='EUR'),
        sa.Column('valid_until', postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('status', sa.String(), nullable=False, default='ENTWURF'),
        sa.Column('contact_person', sa.String(), nullable=True),
        sa.Column('delivery_date', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('payment_terms', sa.String(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False, default=1),
        sa.ForeignKeyConstraint(['tenant_id'], ['domain_shared.tenants.id'], ),
        sa.ForeignKeyConstraint(['customer_inquiry_id'], ['domain_crm.customer_inquiries.id'], ),
        sa.ForeignKeyConstraint(['customer_id'], ['domain_crm.customers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('offer_number'),
        schema='domain_crm'
    )


def downgrade() -> None:
    # Drop sales_offers table
    op.drop_table('sales_offers', schema='domain_crm')
