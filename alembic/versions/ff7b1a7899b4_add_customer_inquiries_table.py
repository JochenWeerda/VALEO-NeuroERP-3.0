"""add_customer_inquiries_table

Revision ID: ff7b1a7899b4
Revises: eca81651f8ba
Create Date: 2025-10-16 07:16:15.939116

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'ff7b1a7899b4'
down_revision: Union[str, None] = 'eca81651f8ba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create customer_inquiries table
    op.create_table('customer_inquiries',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('inquiry_number', sa.String(), nullable=False),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('subject', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('priority', sa.String(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, default='EUR'),
        sa.Column('status', sa.String(), nullable=False, default='EINGEGANGEN'),
        sa.Column('contact_person', sa.String(), nullable=True),
        sa.Column('requested_delivery_date', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('budget', sa.Numeric(15, 2), nullable=True),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False, default=1),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['domain_shared.tenants.id'], ),
        sa.ForeignKeyConstraint(['customer_id'], ['domain_crm.customers.id'], ),
        sa.ForeignKeyConstraint(['assigned_to'], ['domain_shared.users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('inquiry_number'),
        schema='domain_crm'
    )


def downgrade() -> None:
    # Drop customer_inquiries table
    op.drop_table('customer_inquiries', schema='domain_crm')
