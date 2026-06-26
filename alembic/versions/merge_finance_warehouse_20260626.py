"""Merge Alembic heads: finance_agrar_sales_repair + merge_warehouse_einkauf.

Revision ID: merge_finance_warehouse_20260626
Revises: finance_agrar_sales_repair_20260626, merge_warehouse_einkauf_20260626
Create Date: 2026-06-26
"""

from __future__ import annotations

revision = "merge_finance_warehouse_20260626"
down_revision = (
    "finance_agrar_sales_repair_20260626",
    "merge_warehouse_einkauf_20260626",
)
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
