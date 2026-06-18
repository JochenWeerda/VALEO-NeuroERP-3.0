"""WM-AGRI-SILO-001: silo_cells layout_x/y + updated_at (Hofplan + Transfer)

Revision ID: agri_silo_cells_layout_20260619
Revises: wave3_wf_trigger_log_20260618
Create Date: 2026-06-19
"""

from __future__ import annotations

from alembic import op

revision = "agri_silo_cells_layout_20260619"
down_revision = "wave3_wf_trigger_log_20260618"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE domain_inventory.silo_cells
        ADD COLUMN IF NOT EXISTS layout_x NUMERIC(12, 3),
        ADD COLUMN IF NOT EXISTS layout_y NUMERIC(12, 3),
        ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW()
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE domain_inventory.silo_cells
        DROP COLUMN IF EXISTS updated_at,
        DROP COLUMN IF EXISTS layout_y,
        DROP COLUMN IF EXISTS layout_x
    """)
