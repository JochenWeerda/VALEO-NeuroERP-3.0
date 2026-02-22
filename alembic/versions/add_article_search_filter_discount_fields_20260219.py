"""Add article search filter and discount fields.

Revision ID: add_article_search_filter_discount_fields_20260219
Revises: add_article_suppliers_documents_20260219
Create Date: 2026-02-19 12:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_article_search_filter_discount_fields_20260219'
down_revision: Union[str, None] = 'add_article_suppliers_documents_20260219'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add search filter fields
    op.add_column('articles', sa.Column('ean_code', sa.String(length=50), nullable=True), schema='domain_inventory')
    op.add_column('articles', sa.Column('alt_ean_code', sa.String(length=50), nullable=True), schema='domain_inventory')
    op.add_column('articles', sa.Column('lieferanten_artikelnummer', sa.String(length=50), nullable=True), schema='domain_inventory')
    op.add_column('articles', sa.Column('kunden_artikelnummer', sa.String(length=50), nullable=True), schema='domain_inventory')
    op.add_column('articles', sa.Column('verwendungszweck', sa.String(length=255), nullable=True), schema='domain_inventory')
    op.add_column('articles', sa.Column('nachhaltige_biomasse', sa.Boolean(), nullable=True, server_default='false'), schema='domain_inventory')
    op.add_column('articles', sa.Column('pool_artikel', sa.Boolean(), nullable=True, server_default='false'), schema='domain_inventory')
    
    # Add discount/surcharge fields
    op.add_column('articles', sa.Column('rabatt_auftrag_rechnung', sa.DECIMAL(precision=5, scale=2), nullable=True), schema='domain_inventory')
    op.add_column('articles', sa.Column('rabatt_lose', sa.DECIMAL(precision=5, scale=2), nullable=True), schema='domain_inventory')
    op.add_column('articles', sa.Column('rabatt_selbstabholer', sa.DECIMAL(precision=5, scale=2), nullable=True), schema='domain_inventory')
    op.add_column('articles', sa.Column('zu_abschlag_1_code', sa.String(length=50), nullable=True), schema='domain_inventory')
    op.add_column('articles', sa.Column('zu_abschlag_1_prozent', sa.DECIMAL(precision=5, scale=2), nullable=True), schema='domain_inventory')
    op.add_column('articles', sa.Column('zu_abschlag_2_code', sa.String(length=50), nullable=True), schema='domain_inventory')
    op.add_column('articles', sa.Column('zu_abschlag_2_prozent', sa.DECIMAL(precision=5, scale=2), nullable=True), schema='domain_inventory')
    op.add_column('articles', sa.Column('berechne_zu_abschlag_auf_netto', sa.Boolean(), nullable=True, server_default='false'), schema='domain_inventory')
    op.add_column('articles', sa.Column('einfuegen_summe_nach_zu_abschlag', sa.Boolean(), nullable=True, server_default='false'), schema='domain_inventory')
    
    # Add discount flags
    op.add_column('articles', sa.Column('skontofaehig', sa.Boolean(), nullable=True, server_default='true'), schema='domain_inventory')
    op.add_column('articles', sa.Column('warenrueckverguetung', sa.Boolean(), nullable=True, server_default='false'), schema='domain_inventory')
    op.add_column('articles', sa.Column('bonus_faehig', sa.Boolean(), nullable=True, server_default='false'), schema='domain_inventory')
    op.add_column('articles', sa.Column('rabattfaehig', sa.Boolean(), nullable=True, server_default='true'), schema='domain_inventory')


def downgrade() -> None:
    # Remove discount flags
    op.drop_column('articles', 'rabattfaehig', schema='domain_inventory')
    op.drop_column('articles', 'bonus_faehig', schema='domain_inventory')
    op.drop_column('articles', 'warenrueckverguetung', schema='domain_inventory')
    op.drop_column('articles', 'skontofaehig', schema='domain_inventory')
    
    # Remove discount/surcharge fields
    op.drop_column('articles', 'einfuegen_summe_nach_zu_abschlag', schema='domain_inventory')
    op.drop_column('articles', 'berechne_zu_abschlag_auf_netto', schema='domain_inventory')
    op.drop_column('articles', 'zu_abschlag_2_prozent', schema='domain_inventory')
    op.drop_column('articles', 'zu_abschlag_2_code', schema='domain_inventory')
    op.drop_column('articles', 'zu_abschlag_1_prozent', schema='domain_inventory')
    op.drop_column('articles', 'zu_abschlag_1_code', schema='domain_inventory')
    op.drop_column('articles', 'rabatt_selbstabholer', schema='domain_inventory')
    op.drop_column('articles', 'rabatt_lose', schema='domain_inventory')
    op.drop_column('articles', 'rabatt_auftrag_rechnung', schema='domain_inventory')
    
    # Remove search filter fields
    op.drop_column('articles', 'pool_artikel', schema='domain_inventory')
    op.drop_column('articles', 'nachhaltige_biomasse', schema='domain_inventory')
    op.drop_column('articles', 'verwendungszweck', schema='domain_inventory')
    op.drop_column('articles', 'kunden_artikelnummer', schema='domain_inventory')
    op.drop_column('articles', 'lieferanten_artikelnummer', schema='domain_inventory')
    op.drop_column('articles', 'alt_ean_code', schema='domain_inventory')
    op.drop_column('articles', 'ean_code', schema='domain_inventory')
