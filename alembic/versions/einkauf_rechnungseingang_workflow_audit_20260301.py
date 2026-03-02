"""Add workflow audit columns to einkauf_rechnungseingaenge (Prüfen/Freigeben/Verbuchen)

Revision ID: einkauf_re_workflow_20260301
Revises: einkauf_domain_tables_20260227
Create Date: 2025-03-01

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = 'einkauf_re_workflow_20260301'
down_revision = 'einkauf_domain_tables_20260227'
branch_labels = None
depends_on = None


def _table_exists(conn, table_name: str, schema: str | None = "public") -> bool:
    insp = inspect(conn)
    return table_name in insp.get_table_names(schema=schema)


def upgrade() -> None:
    conn = op.get_bind()
    if not _table_exists(conn, "einkauf_rechnungseingaenge"):
        return
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
    conn = op.get_bind()
    if not _table_exists(conn, "einkauf_rechnungseingaenge"):
        return
    op.drop_column('einkauf_rechnungseingaenge', 'posted_at')
    op.drop_column('einkauf_rechnungseingaenge', 'posted_by')
    op.drop_column('einkauf_rechnungseingaenge', 'approved_at')
    op.drop_column('einkauf_rechnungseingaenge', 'approved_by')
    op.drop_column('einkauf_rechnungseingaenge', 'checked_at')
    op.drop_column('einkauf_rechnungseingaenge', 'checked_by')
