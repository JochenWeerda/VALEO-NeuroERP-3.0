"""add tenant_id to EPCIS events

Revision ID: 20251116_03
Revises: 20251116_02
Create Date: 2025-11-16
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20251116_03"
down_revision = "20251116_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("inventory_epcis_events", sa.Column("tenant_id", sa.String(length=64), nullable=False, server_default="default"))
    op.create_index(op.f("ix_inventory_epcis_events_tenant_id"), "inventory_epcis_events", ["tenant_id"], unique=False)
    # Remove server_default after backfill
    op.alter_column("inventory_epcis_events", "tenant_id", server_default=None)


def downgrade() -> None:
    op.drop_index(op.f("ix_inventory_epcis_events_tenant_id"), table_name="inventory_epcis_events")
    op.drop_column("inventory_epcis_events", "tenant_id")

