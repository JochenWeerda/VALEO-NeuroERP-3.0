"""add numbering table

Revision ID: 004
Revises: 003
Create Date: 2025-10-09

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'number_series',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('domain', sa.String(length=50), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=True, server_default='default'),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('prefix', sa.String(length=20), nullable=False),
        sa.Column('counter', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('width', sa.Integer(), nullable=False, server_default='5'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('domain', 'tenant_id', 'year', name='uq_numbering_domain_tenant_year')
    )
    op.create_index('ix_numbering_domain', 'number_series', ['domain'])


def downgrade() -> None:
    op.drop_index('ix_numbering_domain', table_name='number_series')
    op.drop_table('number_series')

