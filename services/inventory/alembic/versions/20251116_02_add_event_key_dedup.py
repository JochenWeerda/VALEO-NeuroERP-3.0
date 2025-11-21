"""add event_key for EPCIS idempotency

Revision ID: 20251116_02
Revises: 20251116_01
Create Date: 2025-11-16
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20251116_02"
down_revision = "20251116_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("inventory_epcis_events", sa.Column("event_key", sa.String(length=128), nullable=True))
    op.create_index(op.f("ix_inventory_epcis_events_event_key"), "inventory_epcis_events", ["event_key"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_inventory_epcis_events_event_key"), table_name="inventory_epcis_events")
    op.drop_column("inventory_epcis_events", "event_key")
*** End Patch***  #-}
'</json>```' ***!

