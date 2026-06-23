"""DOM-SALES-004: sales_ab_status_log, lieferschein_close_log, sales_preisabweichungen

Revision ID: sales_ab_preisabweichung_20260623
Revises: finance_sepa_ratenzahlung_20260623
Create Date: 2026-06-23
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "sales_ab_preisabweichung_20260623"
down_revision = "finance_sepa_ratenzahlung_20260623"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_sales")

    op.create_table(
        "sales_ab_status_log",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("auftrag_id", sa.String(36), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("old_status", sa.String(30)),
        sa.Column("new_status", sa.String(30)),
        sa.Column("operator", sa.String(100)),
        sa.Column("reason", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        schema="domain_sales",
    )
    op.create_index("ix_ab_status_log_auftrag", "sales_ab_status_log", ["auftrag_id"], schema="domain_sales")

    op.create_table(
        "sales_lieferschein_close_log",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("lieferschein_id", sa.String(36), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("aktion", sa.String(30), nullable=False),
        sa.Column("operator", sa.String(100)),
        sa.Column("zeitstempel", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        schema="domain_sales",
    )
    op.create_index(
        "ix_ls_close_log_lieferschein",
        "sales_lieferschein_close_log",
        ["lieferschein_id"],
        schema="domain_sales",
    )

    op.create_table(
        "sales_preisabweichungen",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("auftrag_id", sa.String(36), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("artikel_id", sa.String(64), nullable=False),
        sa.Column("angebots_preis", sa.Numeric(14, 4)),
        sa.Column("rechnungs_preis", sa.Numeric(14, 4)),
        sa.Column("abweichung_pct", sa.Numeric(10, 4)),
        sa.Column("status", sa.String(30), server_default="ESKALIERT"),
        sa.Column("freigabe_operator", sa.String(100), nullable=True),
        sa.Column("freigabe_grund", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.UniqueConstraint("auftrag_id", "artikel_id", "tenant_id", name="uq_preisabweichung_auftrag_artikel"),
        schema="domain_sales",
    )
    op.create_index("ix_preisabweichungen_auftrag", "sales_preisabweichungen", ["auftrag_id"], schema="domain_sales")

    # add quittiert_am / quittiert_von to existing delivery_notes if not present
    op.execute("""
        ALTER TABLE domain_sales.sales_delivery_notes
        ADD COLUMN IF NOT EXISTS quittiert_am TIMESTAMPTZ,
        ADD COLUMN IF NOT EXISTS quittiert_von VARCHAR(100)
    """)


def downgrade() -> None:
    op.drop_table("sales_preisabweichungen", schema="domain_sales")
    op.drop_table("sales_lieferschein_close_log", schema="domain_sales")
    op.drop_table("sales_ab_status_log", schema="domain_sales")
