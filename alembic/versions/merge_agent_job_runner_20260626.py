"""Merge Alembic heads: agent_proposals + job_runner_tables_repair.

Revision ID: merge_agent_job_runner_20260626
Revises: agent_proposals_persist_20260626, job_runner_tables_repair_20260625
Create Date: 2026-06-26
"""

from __future__ import annotations

revision = "merge_agent_job_runner_20260626"
down_revision = ("agent_proposals_persist_20260626", "job_runner_tables_repair_20260625")
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
