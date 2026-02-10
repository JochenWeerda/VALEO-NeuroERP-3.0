"""add_documents_json_table

Revision ID: add_documents_json
Revises: fc82677c98b4
Create Date: 2025-01-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

***REMOVED*** revision identifiers, used by Alembic.
revision: str = 'add_documents_json'
down_revision: Union[str, None] = '59b4fa8420f2'  ***REMOVED*** Current head: Add CRM sub-service seed tables
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    ***REMOVED*** Create documents table for JSON-based document storage
    op.create_table('documents',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('doc_type', sa.String(50), nullable=False),
        sa.Column('doc_number', sa.String(50), nullable=False, unique=True),
        sa.Column('data', postgresql.JSONB, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Index('idx_documents_type', 'doc_type'),
        sa.Index('idx_documents_number', 'doc_number'),
        sa.Index('idx_documents_created', 'created_at'),
    )
    
    ***REMOVED*** Index strategy:
    ***REMOVED*** - GIN on JSONB column for containment queries (`data @> ...`)
    ***REMOVED*** - btree expression indexes for equality filters on extracted text fields
    op.execute("CREATE INDEX idx_documents_data_gin ON documents USING GIN (data);")
    op.execute("CREATE INDEX idx_documents_data_status ON documents ((data->>'status'));")
    op.execute("CREATE INDEX idx_documents_data_customer ON documents ((data->>'customerId'));")
    op.execute("CREATE INDEX idx_documents_data_supplier ON documents ((data->>'supplierId'));")


def downgrade() -> None:
    op.drop_index('idx_documents_data_supplier', table_name='documents')
    op.drop_index('idx_documents_data_customer', table_name='documents')
    op.drop_index('idx_documents_data_status', table_name='documents')
    op.drop_index('idx_documents_data_gin', table_name='documents')
    op.drop_table('documents')

