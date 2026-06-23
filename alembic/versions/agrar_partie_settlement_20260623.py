"""DOM-AGRAR-004: agrar_partien, agrar_partie_links, agrar_trocknung_abrechnungen, agrar_selbstabrechnung_status_log

Revision ID: agrar_partie_settlement_20260623
Revises: inv_lot_trace_20260623
Create Date: 2026-06-23
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "agrar_partie_settlement_20260623"
down_revision = "inv_lot_trace_20260623"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_agrar")

    op.create_table(
        "agrar_partien",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("partie_number", sa.String(50), nullable=False, unique=True),
        sa.Column("article_id", sa.String(64), nullable=True),
        sa.Column("campaign_id", sa.String(36), nullable=True),
        sa.Column("total_gross_kg", sa.Numeric(14, 3)),
        sa.Column("total_net_kg", sa.Numeric(14, 3)),
        sa.Column("avg_moisture_pct", sa.Numeric(7, 3)),
        sa.Column("avg_impurity_pct", sa.Numeric(7, 3)),
        sa.Column("status", sa.String(20), server_default="OFFEN"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        schema="domain_agrar",
    )
    op.create_index(
        "ix_agrar_partien_tenant_id",
        "agrar_partien",
        ["tenant_id"],
        schema="domain_agrar",
    )

    op.create_table(
        "agrar_partie_links",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("partie_id", sa.String(36), nullable=False),
        sa.Column("acceptance_id", sa.String(36), nullable=False),
        sa.Column("gross_kg", sa.Numeric(14, 3)),
        sa.Column("net_kg", sa.Numeric(14, 3)),
        sa.Column("tenant_id", sa.String(36)),
        sa.UniqueConstraint("partie_id", "acceptance_id", name="uq_partie_link"),
        schema="domain_agrar",
    )
    op.create_index(
        "ix_agrar_partie_links_partie_id",
        "agrar_partie_links",
        ["partie_id"],
        schema="domain_agrar",
    )

    op.create_table(
        "agrar_trocknung_abrechnungen",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("partie_id", sa.String(36), nullable=False, unique=True),
        sa.Column("tenant_id", sa.String(36)),
        sa.Column("moisture_in_pct", sa.Numeric(7, 3)),
        sa.Column("moisture_out_pct", sa.Numeric(7, 3)),
        sa.Column("brutto_kg", sa.Numeric(14, 3)),
        sa.Column("trocknungsabzug_kg", sa.Numeric(14, 3)),
        sa.Column("trocknungskosten_eur", sa.Numeric(12, 2)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        schema="domain_agrar",
    )

    op.create_table(
        "agrar_selbstabrechnung_status_log",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("rechnung_id", sa.String(36), nullable=False),
        sa.Column("old_status", sa.String(20)),
        sa.Column("new_status", sa.String(20)),
        sa.Column("operator", sa.String(100)),
        sa.Column("reason", sa.Text),
        sa.Column("tenant_id", sa.String(36)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        schema="domain_agrar",
    )
    op.create_index(
        "ix_selbstabrechnung_status_log_rechnung",
        "agrar_selbstabrechnung_status_log",
        ["rechnung_id"],
        schema="domain_agrar",
    )

    # Empty CI databases may not have the legacy settlement table yet. Keep the
    # migration idempotent and additive; domain-specific columns are added by
    # their owning migrations/services when present.
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_agrar.agrar_selbstabrechnungen (
            id VARCHAR(36) PRIMARY KEY,
            tenant_id VARCHAR(36)
        )
    """)

    # add status column to existing agrar_selbstabrechnungen if not present
    op.execute("""
        ALTER TABLE domain_agrar.agrar_selbstabrechnungen
        ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'DRAFT'
    """)


def downgrade() -> None:
    op.drop_table("agrar_selbstabrechnung_status_log", schema="domain_agrar")
    op.drop_table("agrar_trocknung_abrechnungen", schema="domain_agrar")
    op.drop_table("agrar_partie_links", schema="domain_agrar")
    op.drop_table("agrar_partien", schema="domain_agrar")
