"""add_documents_tables

Revision ID: fc82677c98b4
Revises: f49745206879
Create Date: 2025-11-19 21:52:15.876596

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fc82677c98b4'
down_revision: Union[str, None] = 'f49745206879'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create documents_header table
    op.create_table('documents_header',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('number', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='draft'),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('customer_id', sa.String(36), nullable=True),
        sa.Column('supplier_id', sa.String(36), nullable=True),
        sa.Column('total', sa.Numeric(10, 2), nullable=True),
        sa.Column('ref_id', sa.String(36), nullable=True),
        sa.Column('next_id', sa.String(36), nullable=True),
        sa.Column('created_by', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create documents_line table
    op.create_table('documents_line',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('header_id', sa.String(36), nullable=False),
        sa.Column('line_number', sa.Integer(), nullable=False),
        sa.Column('article_id', sa.String(50), nullable=True),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('quantity', sa.Numeric(10, 3), nullable=False),
        sa.Column('price', sa.Numeric(10, 2), nullable=True),
        sa.Column('cost', sa.Numeric(10, 2), nullable=True),
        sa.Column('vat_rate', sa.Numeric(5, 2), nullable=True),
        sa.Column('total', sa.Numeric(10, 2), nullable=True),
        sa.ForeignKeyConstraint(['header_id'], ['documents_header.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create document_flow table
    op.create_table('document_flow',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('from_type', sa.String(50), nullable=False),
        sa.Column('to_type', sa.String(50), nullable=False),
        sa.Column('relation', sa.String(20), nullable=False, server_default='creates'),
        sa.Column('copy_fields', sa.JSON(), nullable=True),
        sa.Column('rules', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create workflow_status table
    op.create_table('workflow_status',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('domain', sa.String(50), nullable=False),
        sa.Column('doc_number', sa.String(50), nullable=False),
        sa.Column('state', sa.String(20), nullable=False, server_default='draft'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_by', sa.String(100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create workflow_audit table
    op.create_table('workflow_audit',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('domain', sa.String(50), nullable=False),
        sa.Column('doc_number', sa.String(50), nullable=False),
        sa.Column('ts', sa.Integer(), nullable=False),
        sa.Column('from_state', sa.String(20), nullable=False),
        sa.Column('to_state', sa.String(20), nullable=False),
        sa.Column('action', sa.String(20), nullable=False),
        sa.Column('user', sa.String(100), nullable=True),
        sa.Column('reason', sa.String(500), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create archive_index table
    op.create_table('archive_index',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('domain', sa.String(50), nullable=False),
        sa.Column('doc_number', sa.String(50), nullable=False),
        sa.Column('ts', sa.Integer(), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('sha256', sa.String(64), nullable=False),
        sa.Column('user', sa.String(100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create number_series table
    op.create_table('number_series',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('domain', sa.String(50), nullable=False),
        sa.Column('tenant_id', sa.String(36), nullable=True, server_default='default'),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('prefix', sa.String(20), nullable=False),
        sa.Column('counter', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('width', sa.Integer(), nullable=False, server_default='5'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # Drop tables in reverse order (due to foreign keys)
    op.drop_table('number_series')
    op.drop_table('archive_index')
    op.drop_table('workflow_audit')
    op.drop_table('workflow_status')
    op.drop_table('document_flow')
    op.drop_table('documents_line')
    op.drop_table('documents_header')
