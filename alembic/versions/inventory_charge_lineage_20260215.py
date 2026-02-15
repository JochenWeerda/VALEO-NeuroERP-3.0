"""inventory charge lineage links

Revision ID: inventory_charge_lineage_20260215
Revises: docflow_pos_admin_dsfinvk_20260215
Create Date: 2026-02-15
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "inventory_charge_lineage_20260215"
down_revision = "docflow_pos_admin_dsfinvk_20260215"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "charge_lineage_links",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column("article_id", sa.String(length=64), nullable=False),
        sa.Column("from_charge", sa.String(length=64), nullable=False),
        sa.Column("to_charge", sa.String(length=64), nullable=False),
        sa.Column("process_type", sa.String(length=20), nullable=False, server_default="mix"),
        sa.Column("quantity_share", sa.Numeric(14, 3), nullable=False),
        sa.Column("share_percent", sa.Numeric(7, 3), nullable=True),
        sa.Column("source_movement_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("target_movement_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["source_movement_id"], ["domain_inventory.inventory_stock_movements.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["target_movement_id"], ["domain_inventory.inventory_stock_movements.id"], ondelete="SET NULL"
        ),
        sa.CheckConstraint(
            "process_type IN ('mix','withdrawal','split','transfer')",
            name="chk_charge_lineage_process_type",
        ),
        sa.CheckConstraint("quantity_share > 0", name="chk_charge_lineage_qty_positive"),
        sa.CheckConstraint(
            "share_percent IS NULL OR (share_percent >= 0 AND share_percent <= 100)",
            name="chk_charge_lineage_share_range",
        ),
        schema="domain_inventory",
    )
    op.create_index(
        "ix_charge_lineage_tenant_to_charge",
        "charge_lineage_links",
        ["tenant_id", "to_charge"],
        unique=False,
        schema="domain_inventory",
    )
    op.create_index(
        "ix_charge_lineage_tenant_from_charge",
        "charge_lineage_links",
        ["tenant_id", "from_charge"],
        unique=False,
        schema="domain_inventory",
    )


def downgrade() -> None:
    op.drop_index("ix_charge_lineage_tenant_from_charge", table_name="charge_lineage_links", schema="domain_inventory")
    op.drop_index("ix_charge_lineage_tenant_to_charge", table_name="charge_lineage_links", schema="domain_inventory")
    op.drop_table("charge_lineage_links", schema="domain_inventory")
