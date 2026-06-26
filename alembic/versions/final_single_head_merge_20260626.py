"""Final single-head merge: alle Repair-Wellen in einen Head zusammenführen.

Revision ID: final_single_head_merge_20260626
Revises: finance_hr_einkauf_repair_20260626, merge_finance_warehouse_20260626
Create Date: 2026-06-26
"""

from __future__ import annotations

from alembic import op


revision = "final_single_head_merge_20260626"
down_revision = (
    "finance_hr_einkauf_repair_20260626",
    "merge_finance_warehouse_20260626",
)
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
