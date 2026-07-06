"""SPEC-P1-08: Chargen-Tiefenmodell — Herkunft, Sperrgrund, QS-Status, received_at.

Revision ID: inv_lot_depth_spec_p1_08
Revises: runtime_sweep_repair_20260702
"""
from __future__ import annotations

from alembic import op

revision = "inv_lot_depth_spec_p1_08"
down_revision = "runtime_sweep_repair_20260702"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE domain_inventory.inventory_lots
        ADD COLUMN IF NOT EXISTS herkunft VARCHAR(120)
    """)
    op.execute("""
        ALTER TABLE domain_inventory.inventory_lots
        ADD COLUMN IF NOT EXISTS sperrgrund VARCHAR(255)
    """)
    op.execute("""
        ALTER TABLE domain_inventory.inventory_lots
        ADD COLUMN IF NOT EXISTS qs_status VARCHAR(30) DEFAULT 'pending'
    """)
    op.execute("""
        ALTER TABLE domain_inventory.inventory_lots
        ADD COLUMN IF NOT EXISTS received_at DATE
    """)
    op.execute("""
        UPDATE domain_inventory.inventory_lots
        SET received_at = created_at::date
        WHERE received_at IS NULL AND created_at IS NOT NULL
    """)


def downgrade() -> None:
    op.execute("ALTER TABLE domain_inventory.inventory_lots DROP COLUMN IF EXISTS received_at")
    op.execute("ALTER TABLE domain_inventory.inventory_lots DROP COLUMN IF EXISTS qs_status")
    op.execute("ALTER TABLE domain_inventory.inventory_lots DROP COLUMN IF EXISTS sperrgrund")
    op.execute("ALTER TABLE domain_inventory.inventory_lots DROP COLUMN IF EXISTS herkunft")
