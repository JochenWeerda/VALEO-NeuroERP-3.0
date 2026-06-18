"""LOG-FRACHT-001: Spediteur-Rechnungen (carrier_invoices)

Revision ID: log_carrier_invoices_20260618
Revises: prod_fibu_journal_ref_20260618
Create Date: 2026-06-18
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "log_carrier_invoices_20260618"
down_revision = "prod_fibu_journal_ref_20260618"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_logistics")
    op.create_table(
        "carrier_invoices",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("tour_id", sa.String(36), nullable=False),
        sa.Column("carrier_id", sa.String(255), nullable=False),
        sa.Column("invoice_number", sa.String(100), nullable=False),
        sa.Column("invoice_date", sa.Date, nullable=False),
        sa.Column("net_amount_eur", sa.Numeric(14, 2), nullable=False),
        sa.Column("tax_amount_eur", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("gross_amount_eur", sa.Numeric(14, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="EUR"),
        sa.Column("bemerkung", sa.Text, nullable=True),
        sa.Column("fibu_journal_ref", sa.String(128), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="offen"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.UniqueConstraint("tenant_id", "invoice_number", name="uq_carrier_invoice_tenant_nr"),
        schema="domain_logistics",
    )
    op.create_index(
        "ix_carrier_invoices_tenant_tour",
        "carrier_invoices",
        ["tenant_id", "tour_id"],
        schema="domain_logistics",
    )


def downgrade() -> None:
    op.drop_index("ix_carrier_invoices_tenant_tour", table_name="carrier_invoices", schema="domain_logistics")
    op.drop_table("carrier_invoices", schema="domain_logistics")
