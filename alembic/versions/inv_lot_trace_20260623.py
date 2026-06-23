"""DOM-INV-004.2/.4: inventory_lots + inventory_lot_movements + storno_ref column

Revision ID: inv_lot_trace_20260623
Revises: merge_log_agri_heads_20260623
Create Date: 2026-06-23
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "inv_lot_trace_20260623"
down_revision = "merge_log_agri_heads_20260623"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_inventory")

    op.create_table(
        "inventory_lots",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("article_id", sa.String(64), nullable=False),
        sa.Column("warehouse_id", sa.String(64), nullable=False),
        sa.Column("lot_number", sa.String(100), nullable=False),
        sa.Column("mhd", sa.Date, nullable=True),
        sa.Column("initial_qty", sa.Numeric(14, 3), nullable=False),
        sa.Column("current_qty", sa.Numeric(14, 3), nullable=False),
        sa.Column("unit", sa.String(20), server_default="kg"),
        sa.Column("status", sa.String(20), server_default="AKTIV"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        schema="domain_inventory",
    )
    op.create_index(
        "ix_inventory_lots_tenant_article",
        "inventory_lots",
        ["tenant_id", "article_id"],
        schema="domain_inventory",
    )
    op.create_index(
        "ix_inventory_lots_mhd",
        "inventory_lots",
        ["mhd"],
        schema="domain_inventory",
    )

    op.create_table(
        "inventory_lot_movements",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("lot_id", sa.String(36), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=True),
        sa.Column("movement_type", sa.String(10), nullable=False),
        sa.Column("quantity", sa.Numeric(14, 3), nullable=False),
        sa.Column("reference_id", sa.String(36), nullable=True),
        sa.Column("reference_type", sa.String(50), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        schema="domain_inventory",
    )
    op.create_index(
        "ix_inventory_lot_movements_lot_id",
        "inventory_lot_movements",
        ["lot_id"],
        schema="domain_inventory",
    )

    # add storno_ref column to inventory_stock_movements
    op.execute("""
        ALTER TABLE domain_inventory.inventory_stock_movements
        ADD COLUMN IF NOT EXISTS storno_ref VARCHAR(36)
    """)


def downgrade() -> None:
    op.drop_table("inventory_lot_movements", schema="domain_inventory")
    op.drop_table("inventory_lots", schema="domain_inventory")
    # storno_ref column intentionally not dropped (non-destructive)
