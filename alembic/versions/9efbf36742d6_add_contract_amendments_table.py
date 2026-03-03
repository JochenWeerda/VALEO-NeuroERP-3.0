"""add_contract_amendments_table

Revision ID: 9efbf36742d6
Revises: journal_entries_unify_20260301
Create Date: 2026-03-03 08:43:19.027303

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '9efbf36742d6'
down_revision: Union[str, None] = 'journal_entries_unify_20260301'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'contract_amendments',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('contract_id', sa.String(length=64), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='pending'),
        sa.Column('changes', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('created_by', sa.String(length=255), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['domain_shared.tenants.id'], name='contract_amendments_tenant_id_fkey'),
        sa.PrimaryKeyConstraint('id', name='contract_amendments_pkey'),
        schema='domain_shared',
    )
    op.create_index('ix_contract_amendments_contract_id', 'contract_amendments', ['contract_id'], unique=False, schema='domain_shared')


def downgrade() -> None:
    op.drop_index('ix_contract_amendments_contract_id', table_name='contract_amendments', schema='domain_shared')
    op.drop_table('contract_amendments', schema='domain_shared')
