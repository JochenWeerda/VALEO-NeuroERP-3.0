"""add_finance_tables

Revision ID: 2012a7987e7f
Revises: fc82677c98b4
Create Date: 2025-11-19 21:58:42.138500

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2012a7987e7f'
down_revision: Union[str, None] = 'fc82677c98b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create offene_posten table
    op.create_table('offene_posten',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('tenant_id', sa.String(36), nullable=False),
        sa.Column('rechnungsnr', sa.String(50), nullable=False),
        sa.Column('datum', sa.Date(), nullable=False),
        sa.Column('faelligkeit', sa.Date(), nullable=False),
        sa.Column('betrag', sa.Numeric(10, 2), nullable=False),
        sa.Column('offen', sa.Numeric(10, 2), nullable=False),
        sa.Column('kunde_id', sa.String(36), nullable=True),
        sa.Column('kunde_name', sa.String(100), nullable=True),
        sa.Column('lieferant_id', sa.String(36), nullable=True),
        sa.Column('lieferant_name', sa.String(100), nullable=True),
        sa.Column('skonto_prozent', sa.Numeric(5, 2), nullable=True),
        sa.Column('skonto_bis', sa.Date(), nullable=True),
        sa.Column('mahn_stufe', sa.Integer(), nullable=True, default=0),
        sa.Column('zahlbar', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_offene_posten_tenant_id', 'tenant_id'),
        sa.Index('ix_offene_posten_rechnungsnr', 'rechnungsnr')
    )

    # Create buchungen table
    op.create_table('buchungen',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('tenant_id', sa.String(36), nullable=False),
        sa.Column('belegnr', sa.String(50), nullable=False),
        sa.Column('datum', sa.Date(), nullable=False),
        sa.Column('soll_konto', sa.String(10), nullable=False),
        sa.Column('haben_konto', sa.String(10), nullable=False),
        sa.Column('betrag', sa.Numeric(10, 2), nullable=False),
        sa.Column('text', sa.String(200), nullable=False),
        sa.Column('belegart', sa.String(10), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_buchungen_tenant_id', 'tenant_id'),
        sa.Index('ix_buchungen_belegnr', 'belegnr')
    )

    # Create konten table
    op.create_table('konten',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('tenant_id', sa.String(36), nullable=False),
        sa.Column('kontonummer', sa.String(10), nullable=False),
        sa.Column('bezeichnung', sa.String(100), nullable=False),
        sa.Column('kontoart', sa.String(50), nullable=False),
        sa.Column('typ', sa.String(20), nullable=False),
        sa.Column('saldo', sa.Numeric(10, 2), nullable=True, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_konten_tenant_id', 'tenant_id'),
        sa.Index('ix_konten_kontonummer', 'kontonummer', unique=True)
    )

    # Create anlagen table
    op.create_table('anlagen',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('tenant_id', sa.String(36), nullable=False),
        sa.Column('anlagennr', sa.String(20), nullable=False),
        sa.Column('bezeichnung', sa.String(200), nullable=False),
        sa.Column('anschaffung', sa.Date(), nullable=False),
        sa.Column('anschaffungswert', sa.Numeric(10, 2), nullable=False),
        sa.Column('nutzungsdauer', sa.Integer(), nullable=False),
        sa.Column('afa_satz', sa.Numeric(5, 2), nullable=False),
        sa.Column('kumulierte_afa', sa.Numeric(10, 2), nullable=True, default=0),
        sa.Column('buchwert', sa.Numeric(10, 2), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_anlagen_tenant_id', 'tenant_id'),
        sa.Index('ix_anlagen_anlagennr', 'anlagennr', unique=True)
    )


def downgrade() -> None:
    # Drop tables in reverse order (due to potential foreign keys)
    op.drop_table('anlagen')
    op.drop_table('konten')
    op.drop_table('buchungen')
    op.drop_table('offene_posten')
