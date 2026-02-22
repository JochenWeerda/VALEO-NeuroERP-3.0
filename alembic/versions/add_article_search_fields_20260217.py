"""Add missing article search fields for ArtikelSuchDialog.

Revision ID: add_article_search_fields_20260217
Revises: add_customer_chefanweisung_20260217
Create Date: 2026-02-17 12:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_article_search_fields_20260217'
down_revision: Union[str, Sequence[str], None] = 'add_customer_chefanweisung_20260217'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add missing fields for article search dialog
    op.add_column(
        'articles',
        sa.Column(
            'description2',
            sa.Text(),
            nullable=True,
            comment='Zweite Bezeichnung (Extended description)'
        ),
        schema='domain_inventory'
    )
    
    op.add_column(
        'articles',
        sa.Column(
            'short_description',
            sa.String(length=200),
            nullable=True,
            comment='Kurzbezeichnung (Short description)'
        ),
        schema='domain_inventory'
    )
    
    op.add_column(
        'articles',
        sa.Column(
            'matchcode2',
            sa.String(length=100),
            nullable=True,
            comment='Zweiter Matchcode (Alternative search term)'
        ),
        schema='domain_inventory'
    )
    
    op.add_column(
        'articles',
        sa.Column(
            'customer_article_number',
            sa.String(length=50),
            nullable=True,
            comment='Kunden-Artikel-Nummer (Customer-specific article number)'
        ),
        schema='domain_inventory'
    )
    
    # Create indexes for better search performance
    op.create_index(
        'ix_articles_description2',
        'articles',
        ['description2'],
        unique=False,
        schema='domain_inventory'
    )
    
    op.create_index(
        'ix_articles_short_description',
        'articles',
        ['short_description'],
        unique=False,
        schema='domain_inventory'
    )
    
    op.create_index(
        'ix_articles_matchcode2',
        'articles',
        ['matchcode2'],
        unique=False,
        schema='domain_inventory'
    )
    
    op.create_index(
        'ix_articles_customer_article_number',
        'articles',
        ['customer_article_number'],
        unique=False,
        schema='domain_inventory'
    )


def downgrade() -> None:
    # Drop indexes first
    op.drop_index('ix_articles_customer_article_number', table_name='articles', schema='domain_inventory')
    op.drop_index('ix_articles_matchcode2', table_name='articles', schema='domain_inventory')
    op.drop_index('ix_articles_short_description', table_name='articles', schema='domain_inventory')
    op.drop_index('ix_articles_description2', table_name='articles', schema='domain_inventory')
    
    # Drop columns
    op.drop_column('articles', 'customer_article_number', schema='domain_inventory')
    op.drop_column('articles', 'matchcode2', schema='domain_inventory')
    op.drop_column('articles', 'short_description', schema='domain_inventory')
    op.drop_column('articles', 'description2', schema='domain_inventory')

