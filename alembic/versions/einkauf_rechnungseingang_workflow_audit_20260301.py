"""Add workflow audit columns to einkauf_rechnungseingaenge (Prüfen/Freigeben/Verbuchen)

Revision ID: einkauf_re_workflow_20260301
Revises: einkauf_domain_tables_20260227
Create Date: 2025-03-01

"""
from alembic import op
import sqlalchemy as sa


revision = 'einkauf_re_workflow_20260301'
down_revision = 'einkauf_domain_tables_20260227'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'einkauf_rechnungseingaenge',
        sa.Column('checked_by', sa.String(255), nullable=True),
    )
    op.add_column(
        'einkauf_rechnungseingaenge',
        sa.Column('checked_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        'einkauf_rechnungseingaenge',
        sa.Column('approved_by', sa.String(255), nullable=True),
    )
    op.add_column(
        'einkauf_rechnungseingaenge',
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        'einkauf_rechnungseingaenge',
        sa.Column('posted_by', sa.String(255), nullable=True),
    )
    op.add_column(
        'einkauf_rechnungseingaenge',
        sa.Column('posted_at', sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('einkauf_rechnungseingaenge', 'posted_at')
    op.drop_column('einkauf_rechnungseingaenge', 'posted_by')
    op.drop_column('einkauf_rechnungseingaenge', 'approved_at')
    op.drop_column('einkauf_rechnungseingaenge', 'approved_by')
    op.drop_column('einkauf_rechnungseingaenge', 'checked_at')
    op.drop_column('einkauf_rechnungseingaenge', 'checked_by')
