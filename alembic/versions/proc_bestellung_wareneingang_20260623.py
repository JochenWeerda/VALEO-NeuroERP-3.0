"""DOM-PROC-004: proc_bestellung_status_log, proc_wareneingaenge, proc_rechnungspruefungen

Revision ID: proc_bestellung_wareneingang_20260623
Revises: sales_ab_preisabweichung_20260623
Create Date: 2026-06-23
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "proc_bestellung_wareneingang_20260623"
down_revision = "merge_dom004_feed_chain_20260623"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_procurement")

    op.create_table(
        "proc_bestellung_status_log",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("bestellung_id", sa.String(36), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("old_status", sa.String(30)),
        sa.Column("new_status", sa.String(30)),
        sa.Column("operator", sa.String(100)),
        sa.Column("reason", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        schema="domain_procurement",
    )
    op.create_index(
        "ix_bestellung_status_log_bid",
        "proc_bestellung_status_log",
        ["bestellung_id"],
        schema="domain_procurement",
    )

    op.create_table(
        "proc_wareneingaenge",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("bestellung_id", sa.String(36), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("menge_erhalten", sa.Numeric(14, 3), nullable=False),
        sa.Column("einheit", sa.String(20), nullable=False),
        sa.Column("lager_id", sa.String(36)),
        sa.Column("qs_status", sa.String(20), server_default="AUSSTEHEND"),
        sa.Column("gebucht_am", sa.DateTime(timezone=True), nullable=True),
        sa.Column("operator", sa.String(100)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        schema="domain_procurement",
    )
    op.create_index(
        "ix_proc_wareneingaenge_bid",
        "proc_wareneingaenge",
        ["bestellung_id"],
        schema="domain_procurement",
    )

    op.create_table(
        "proc_rechnungspruefungen",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("bestellung_id", sa.String(36), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("rechnungs_nr", sa.String(60), nullable=False),
        sa.Column("bestell_wert_eur", sa.Numeric(14, 2)),
        sa.Column("we_menge", sa.Numeric(14, 3)),
        sa.Column("rechnungs_betrag_eur", sa.Numeric(14, 2)),
        sa.Column("abweichung_pct", sa.Numeric(10, 4)),
        sa.Column("status", sa.String(20), server_default="GESPERRT"),
        sa.Column("freigabe_operator", sa.String(100), nullable=True),
        sa.Column("freigabe_grund", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.UniqueConstraint("bestellung_id", "rechnungs_nr", "tenant_id", name="uq_rechnungspruefung_bid_rnr"),
        schema="domain_procurement",
    )
    op.create_index(
        "ix_proc_rechnungspruefungen_bid",
        "proc_rechnungspruefungen",
        ["bestellung_id"],
        schema="domain_procurement",
    )

    # Empty CI databases may not have the legacy purchase-order table yet.
    # Keep the migration additive so a full bootstrap can reach head.
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_procurement.proc_purchase_orders (
            id VARCHAR(36) PRIMARY KEY,
            tenant_id VARCHAR(36)
        )
    """)

    # add status column to existing purchase orders if not present
    op.execute("""
        ALTER TABLE domain_procurement.proc_purchase_orders
        ADD COLUMN IF NOT EXISTS status VARCHAR(30) DEFAULT 'DRAFT'
    """)


def downgrade() -> None:
    op.drop_table("proc_rechnungspruefungen", schema="domain_procurement")
    op.drop_table("proc_wareneingaenge", schema="domain_procurement")
    op.drop_table("proc_bestellung_status_log", schema="domain_procurement")
