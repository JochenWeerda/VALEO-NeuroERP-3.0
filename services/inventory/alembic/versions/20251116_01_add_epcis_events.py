"""add EPCIS events table and enums

Revision ID: 20251116_01
Revises:
Create Date: 2025-11-16
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20251116_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum type for EPCIS event
    epcis_enum = postgresql.ENUM(
        "ObjectEvent", "AggregationEvent", "TransformationEvent", "TransactionEvent", name="epcis_event_type"
    )
    epcis_enum.create(op.get_bind(), checkfirst=True)

    # Create table
    op.create_table(
        "inventory_epcis_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("event_type", sa.Enum(name="epcis_event_type"), nullable=False),
        sa.Column("event_time", sa.DateTime(), nullable=False),
        sa.Column("biz_step", sa.String(length=128), nullable=True),
        sa.Column("read_point", sa.String(length=128), nullable=True),
        sa.Column("lot_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("sku", sa.String(length=64), nullable=True),
        sa.Column("quantity", sa.Numeric(16, 3), nullable=True),
        sa.Column("extensions", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["lot_id"], ["inventory_lots.id"]),
    )
    # Indexes
    op.create_index("ix_epcis_event_time", "inventory_epcis_events", ["event_time"])
    op.create_index("ix_epcis_biz_step", "inventory_epcis_events", ["biz_step"])
    op.create_index("ix_epcis_sku", "inventory_epcis_events", ["sku"])


def downgrade() -> None:
    op.drop_index("ix_epcis_sku", table_name="inventory_epcis_events")
    op.drop_index("ix_epcis_biz_step", table_name="inventory_epcis_events")
    op.drop_index("ix_epcis_event_time", table_name="inventory_epcis_events")
    op.drop_table("inventory_epcis_events")
    # Drop enum
    epcis_enum = postgresql.ENUM(
        "ObjectEvent", "AggregationEvent", "TransformationEvent", "TransactionEvent", name="epcis_event_type"
    )
    epcis_enum.drop(op.get_bind(), checkfirst=True)



