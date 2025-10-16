"""add_crm_activities_and_farm_profiles

Revision ID: 7f8529f27eb0
Revises: a489a6a4a212
Create Date: 2025-10-13 18:50:40.776106

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '7f8529f27eb0'
down_revision: Union[str, None] = 'a489a6a4a212'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create activities table
    op.create_table(
        'activities',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('type', sa.String(length=20), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('customer', sa.String(length=100), nullable=False),
        sa.Column('contact_person', sa.String(length=100), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('assigned_to', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['domain_shared.tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='domain_crm'
    )

    # Create farm_profiles table
    op.create_table(
        'farm_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('farm_name', sa.String(length=200), nullable=False),
        sa.Column('owner', sa.String(length=100), nullable=False),
        sa.Column('total_area', sa.Float(), nullable=False),
        sa.Column('crops', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('livestock', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('location', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('certifications', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['domain_shared.tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='domain_crm'
    )


def downgrade() -> None:
    op.drop_table('farm_profiles', schema='domain_crm')
    op.drop_table('activities', schema='domain_crm')
