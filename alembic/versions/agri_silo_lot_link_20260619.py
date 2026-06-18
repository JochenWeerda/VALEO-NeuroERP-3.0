"""WM-AGRI-LOT-LINK: silo_cells.legacy_silo_id → domain_inventory.silos

Revision ID: agri_silo_lot_link_20260619
Revises: agri_silo_cells_layout_20260619
Create Date: 2026-06-19
"""

from __future__ import annotations

from alembic import op

revision = "agri_silo_lot_link_20260619"
down_revision = "agri_silo_cells_layout_20260619"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE domain_inventory.silo_cells
        ADD COLUMN IF NOT EXISTS legacy_silo_id VARCHAR
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_silo_cells_legacy_silo
        ON domain_inventory.silo_cells (legacy_silo_id)
        WHERE legacy_silo_id IS NOT NULL
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS domain_inventory.idx_silo_cells_legacy_silo")
    op.execute("""
        ALTER TABLE domain_inventory.silo_cells
        DROP COLUMN IF EXISTS legacy_silo_id
    """)
