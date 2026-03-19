"""Gap 011: workflow_version in workflow_status (versionierte Workflow Engine)

Revision ID: workflow_version_20260307
Revises: audit_hash_20260306
Create Date: 2026-03-07

Adds workflow_version column to workflow_status. Existing rows default to '1'.
"""
from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "workflow_version_20260307"
down_revision = "audit_hash_20260306"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    r = conn.execute(
        text(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_schema = 'public' AND table_name = 'workflow_status' "
            "AND column_name = 'workflow_version'"
        )
    )
    if r.scalar() is not None:
        return
    op.execute(
        text(
            "ALTER TABLE workflow_status ADD COLUMN workflow_version VARCHAR(20) DEFAULT '1'"
        )
    )
    op.execute(text("UPDATE workflow_status SET workflow_version = '1' WHERE workflow_version IS NULL"))


def downgrade() -> None:
    op.execute(text("ALTER TABLE workflow_status DROP COLUMN IF EXISTS workflow_version"))
