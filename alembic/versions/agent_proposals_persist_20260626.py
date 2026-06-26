"""OPERATOR-AGENT-002: Tabelle agent_proposals fuer persistente Agent-Proposals.

Revision ID: agent_proposals_persist_20260626
Revises: wf_cockpit_persist_20260625
Create Date: 2026-06-26
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "agent_proposals_persist_20260626"
down_revision = "wf_cockpit_persist_20260625"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "agent_proposals",
        sa.Column("proposal_id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(128), nullable=False),
        sa.Column("action_type", sa.String(64), nullable=False),
        sa.Column("risk_level", sa.String(16), nullable=False),
        sa.Column("approval_status", sa.String(16), nullable=False, server_default="pending"),
        sa.Column("context_snapshot", sa.JSON, nullable=True),
        sa.Column("rationale", sa.Text, nullable=True),
        sa.Column("idempotency_key", sa.String(128), nullable=True, unique=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_by", sa.String(128), nullable=True),
        sa.Column("execution_result", sa.JSON, nullable=True),
    )
    op.create_index(
        "ix_agent_proposals_tenant_status",
        "agent_proposals",
        ["tenant_id", "approval_status"],
    )
    op.create_index(
        "ix_agent_proposals_tenant_created",
        "agent_proposals",
        ["tenant_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_agent_proposals_tenant_created", table_name="agent_proposals")
    op.drop_index("ix_agent_proposals_tenant_status", table_name="agent_proposals")
    op.drop_table("agent_proposals")
