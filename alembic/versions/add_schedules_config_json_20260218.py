"""add_schedules_config_json_20260218

Revision ID: add_sched_cfg_20260218
Revises: add_config_jobs_20260218
Create Date: 2026-02-18 16:00:00.000000

Add config_json to schedules for Meldewesen frontend (reportType, connectorId, cadence, etc.).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "add_sched_cfg_20260218"
down_revision: Union[str, None] = "add_config_jobs_20260218"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "schedules",
        sa.Column("config_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment="reportType, connectorId, cadence, dayOfMonth, jobParamsJson, etc."),
        schema="domain_shared",
    )


def downgrade() -> None:
    op.drop_column("schedules", "config_json", schema="domain_shared")
