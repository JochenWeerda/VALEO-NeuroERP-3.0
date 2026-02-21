"""Add article_suppliers and article_documents tables.

Revision ID: add_article_suppliers_documents_20260219
Revises: add_weighing_ticket_article_notes_20260219
Create Date: 2026-02-19 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_article_suppliers_documents_20260219'
down_revision: Union[str, None] = 'add_wt_article_notes_20260219'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create article_suppliers table
    op.create_table(
        'article_suppliers',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('article_id', sa.String(), nullable=False),
        sa.Column('partner_id', sa.String(36), nullable=False),
        sa.Column('supplier_article_number', sa.String(length=50), nullable=True),
        sa.Column('purchase_price', sa.DECIMAL(precision=14, scale=4), nullable=True),
        sa.Column('price_valid_from', sa.Date(), nullable=True),
        sa.Column('price_valid_to', sa.Date(), nullable=True),
        sa.Column('lead_time_days', sa.Integer(), nullable=True),
        sa.Column('min_order_quantity', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('is_preferred', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['article_id'], ['domain_inventory.articles.id']),
        sa.ForeignKeyConstraint(['partner_id'], ['domain_crm.business_partners.partner_id']),
        schema='domain_inventory'
    )
    op.create_index('ix_domain_inventory_article_suppliers_article_id', 'article_suppliers', ['article_id'], schema='domain_inventory')
    op.create_index('ix_domain_inventory_article_suppliers_partner_id', 'article_suppliers', ['partner_id'], schema='domain_inventory')

    # Create article_documents table
    op.create_table(
        'article_documents',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('article_id', sa.String(), nullable=False),
        sa.Column('document_id', sa.String(), nullable=False),
        sa.Column('document_name', sa.String(length=255), nullable=False),
        sa.Column('document_type', sa.String(length=50), nullable=True),
        sa.Column('document_category', sa.String(length=50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['article_id'], ['domain_inventory.articles.id']),
        schema='domain_inventory'
    )
    op.create_index('ix_domain_inventory_article_documents_article_id', 'article_documents', ['article_id'], schema='domain_inventory')
    op.create_index('ix_domain_inventory_article_documents_document_id', 'article_documents', ['document_id'], schema='domain_inventory')


def downgrade() -> None:
    op.drop_index('ix_domain_inventory_article_documents_document_id', table_name='article_documents', schema='domain_inventory')
    op.drop_index('ix_domain_inventory_article_documents_article_id', table_name='article_documents', schema='domain_inventory')
    op.drop_table('article_documents', schema='domain_inventory')
    
    op.drop_index('ix_domain_inventory_article_suppliers_partner_id', table_name='article_suppliers', schema='domain_inventory')
    op.drop_index('ix_domain_inventory_article_suppliers_article_id', table_name='article_suppliers', schema='domain_inventory')
    op.drop_table('article_suppliers', schema='domain_inventory')
