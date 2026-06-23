"""Merge log_disposition and agri_silo_lot_link heads (DOM-INV-004 pre-step).

Revision ID: merge_log_agri_heads_20260623
Revises: log_disposition_20260623, agri_silo_lot_link_20260619
Create Date: 2026-06-23
"""

from __future__ import annotations

from alembic import op

revision = "merge_log_agri_heads_20260623"
down_revision = ("log_disposition_20260623", "agri_silo_lot_link_20260619")
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
