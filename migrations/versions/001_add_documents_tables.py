"""add documents tables

Revision ID: 001
Revises: 
Create Date: 2025-10-09

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # documents_header
    op.create_table(
        'documents_header',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('number', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='draft'),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('customer_id', sa.String(length=36), nullable=True),
        sa.Column('supplier_id', sa.String(length=36), nullable=True),
        sa.Column('total', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('ref_id', sa.String(length=36), nullable=True),
        sa.Column('next_id', sa.String(length=36), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('type', 'number', name='uq_type_number')
    )
    op.create_index('ix_documents_type_number', 'documents_header', ['type', 'number'])
    op.create_index('ix_documents_customer', 'documents_header', ['customer_id'])
    op.create_index('ix_documents_status', 'documents_header', ['status'])

    # documents_line
    op.create_table(
        'documents_line',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('header_id', sa.String(length=36), nullable=False),
        sa.Column('line_number', sa.Integer(), nullable=False),
        sa.Column('article_id', sa.String(length=50), nullable=True),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('quantity', sa.Numeric(precision=10, scale=3), nullable=False),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('cost', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('vat_rate', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('total', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['header_id'], ['documents_header.id'], ondelete='CASCADE')
    )
    op.create_index('ix_documents_line_header', 'documents_line', ['header_id'])

    # document_flow
    op.create_table(
        'document_flow',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('from_type', sa.String(length=50), nullable=False),
        sa.Column('to_type', sa.String(length=50), nullable=False),
        sa.Column('relation', sa.String(length=20), nullable=False, server_default='creates'),
        sa.Column('copy_fields', sa.JSON(), nullable=True),
        sa.Column('rules', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('from_type', 'to_type', name='uq_flow_types')
    )


def downgrade() -> None:
    op.drop_table('document_flow')
    op.drop_index('ix_documents_line_header', table_name='documents_line')
    op.drop_table('documents_line')
    op.drop_index('ix_documents_status', table_name='documents_header')
    op.drop_index('ix_documents_customer', table_name='documents_header')
    op.drop_index('ix_documents_type_number', table_name='documents_header')
    op.drop_table('documents_header')

