"""Merge Alembic heads: log_frachtbriefe + merge_agent_job_runner.

Revision ID: merge_log_agent_20260626
Revises: log_frachtbriefe_20260626, merge_agent_job_runner_20260626
Create Date: 2026-06-26
"""

from __future__ import annotations

revision = "merge_log_agent_20260626"
down_revision = ("log_frachtbriefe_20260626", "merge_agent_job_runner_20260626")
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
