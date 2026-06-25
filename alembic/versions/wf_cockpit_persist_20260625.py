"""WF-COCKPIT-PERSIST-001: Persistente Workflow-Cockpit-Tabellen.

Revision ID: wf_cockpit_persist_20260625
Revises: external_mock_sessions_20260623
Create Date: 2026-06-25

Schema: domain_workflow
Tabellen: wf_cockpit_instances, wf_cockpit_events, wf_cockpit_blockers
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "wf_cockpit_persist_20260625"
down_revision = "external_mock_sessions_20260623"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_workflow")

    op.create_table(
        "wf_cockpit_instances",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(100), nullable=False, index=True),
        sa.Column("process_key", sa.String(200), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, index=True),
        sa.Column("correlation_id", sa.String(200), nullable=False),
        sa.Column("idempotency_key", sa.String(200), nullable=True),
        sa.Column("business_object_ref", sa.String(500), nullable=True),
        sa.Column("current_step", sa.String(200), nullable=True),
        sa.Column("audit_ref", sa.String(200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()"), onupdate=sa.text("now()")),
        sa.Column("active_blocker_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("replayable", sa.Boolean, nullable=False, server_default="false"),
        schema="domain_workflow",
    )
    op.create_index(
        "ix_wf_cockpit_instances_tenant_status",
        "wf_cockpit_instances",
        ["tenant_id", "status"],
        schema="domain_workflow",
    )
    op.create_index(
        "ix_wf_cockpit_instances_tenant_process_key",
        "wf_cockpit_instances",
        ["tenant_id", "process_key"],
        schema="domain_workflow",
    )

    op.create_table(
        "wf_cockpit_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("process_instance_id", sa.String(36), nullable=False, index=True),
        sa.Column("tenant_id", sa.String(100), nullable=False, index=True),
        sa.Column("kind", sa.String(50), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("source", sa.String(200), nullable=False, server_default="workflow-cockpit"),
        sa.Column("payload", postgresql.JSONB, nullable=True, server_default="{}"),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(
            ["process_instance_id"],
            ["domain_workflow.wf_cockpit_instances.id"],
            ondelete="CASCADE",
        ),
        schema="domain_workflow",
    )
    op.create_index(
        "ix_wf_cockpit_events_process_occurred",
        "wf_cockpit_events",
        ["process_instance_id", "occurred_at"],
        schema="domain_workflow",
    )

    op.create_table(
        "wf_cockpit_blockers",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("process_instance_id", sa.String(36), nullable=False, index=True),
        sa.Column("tenant_id", sa.String(100), nullable=False, index=True),
        sa.Column("blocker_type", sa.String(100), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("external_system", sa.String(200), nullable=True),
        sa.Column("retryable", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("resolved", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("since", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["process_instance_id"],
            ["domain_workflow.wf_cockpit_instances.id"],
            ondelete="CASCADE",
        ),
        schema="domain_workflow",
    )
    op.create_index(
        "ix_wf_cockpit_blockers_process_resolved",
        "wf_cockpit_blockers",
        ["process_instance_id", "resolved"],
        schema="domain_workflow",
    )


def downgrade() -> None:
    op.drop_table("wf_cockpit_blockers", schema="domain_workflow")
    op.drop_table("wf_cockpit_events", schema="domain_workflow")
    op.drop_table("wf_cockpit_instances", schema="domain_workflow")
    op.execute("DROP SCHEMA IF EXISTS domain_workflow CASCADE")
