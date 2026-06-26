"""Merge Alembic heads: warehouse_schema_repair + merge_einkauf_log_agent.

Revision ID: merge_warehouse_einkauf_20260626
Revises: warehouse_schema_repair_20260626, merge_einkauf_log_agent_20260626
Create Date: 2026-06-26
"""

from __future__ import annotations

revision = "merge_warehouse_einkauf_20260626"
down_revision = (
    "warehouse_schema_repair_20260626",
    "merge_einkauf_log_agent_20260626",
)
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
