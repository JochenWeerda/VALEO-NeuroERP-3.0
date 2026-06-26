"""Merge Alembic heads: einkauf_ls_opportunities_repair + merge_log_agent.

Revision ID: merge_einkauf_log_agent_20260626
Revises: einkauf_ls_opportunities_repair_20260626, merge_log_agent_20260626
Create Date: 2026-06-26
"""

from __future__ import annotations

revision = "merge_einkauf_log_agent_20260626"
down_revision = (
    "einkauf_ls_opportunities_repair_20260626",
    "merge_log_agent_20260626",
)
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
