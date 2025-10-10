"""add archive table

Revision ID: 003
Revises: 002
Create Date: 2025-10-09

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'archive_index',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('domain', sa.String(length=50), nullable=False),
        sa.Column('doc_number', sa.String(length=50), nullable=False),
        sa.Column('ts', sa.Integer(), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('sha256', sa.String(length=64), nullable=False),
        sa.Column('user', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_archive_doc', 'archive_index', ['domain', 'doc_number'])
    op.create_index('ix_archive_ts', 'archive_index', ['ts'])
    op.create_index('ix_archive_sha256', 'archive_index', ['sha256'])


def downgrade() -> None:
    op.drop_index('ix_archive_sha256', table_name='archive_index')
    op.drop_index('ix_archive_ts', table_name='archive_index')
    op.drop_index('ix_archive_doc', table_name='archive_index')
    op.drop_table('archive_index')

