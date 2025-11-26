"""Initial CRM Workflow schema.

Revision ID: 001_initial_crm_workflow_schema
Revises:
Create Date: 2025-11-15 11:05:00.000000

"""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "001_initial_crm_workflow_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create CRM Workflow tables."""
    # Create enums
    op.execute("CREATE TYPE crm_workflow_status AS ENUM ('active', 'inactive', 'draft')")
    op.execute("CREATE TYPE crm_workflow_trigger_type AS ENUM ('event', 'schedule', 'manual')")
    op.execute("CREATE TYPE crm_workflow_action_type AS ENUM ('notification', 'update_record', 'create_task', 'escalate', 'webhook')")
    op.execute("CREATE TYPE crm_workflow_notification_type AS ENUM ('email', 'in_app', 'sms', 'webhook')")
    op.execute("CREATE TYPE crm_workflow_execution_status AS ENUM ('pending', 'running', 'completed', 'failed', 'cancelled')")

    # Workflows table
    op.create_table(
        "crm_workflow_workflows",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("status", postgresql.ENUM('active', 'inactive', 'draft', name='crm_workflow_status'), nullable=False, server_default='draft'),
        sa.Column("trigger_conditions", postgresql.JSONB, nullable=False),
        sa.Column("actions", postgresql.JSONB, nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default='true'),
        sa.Column("created_by", sa.String(64)),
        sa.Column("updated_by", sa.String(64)),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Triggers table
    op.create_table(
        "crm_workflow_triggers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("trigger_type", postgresql.ENUM('event', 'schedule', 'manual', name='crm_workflow_trigger_type'), nullable=False),
        sa.Column("event_type", sa.String(128)),
        sa.Column("schedule_cron", sa.String(128)),
        sa.Column("conditions", postgresql.JSONB, nullable=False),
        sa.Column("workflow_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_workflow_workflows.id"), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default='true'),
        sa.Column("created_by", sa.String(64)),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    # Workflow executions table
    op.create_table(
        "crm_workflow_executions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("workflow_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_workflow_workflows.id"), nullable=False),
        sa.Column("status", postgresql.ENUM('pending', 'running', 'completed', 'failed', 'cancelled', name='crm_workflow_execution_status'), nullable=False, server_default='pending'),
        sa.Column("trigger_event", postgresql.JSONB, nullable=False),
        sa.Column("execution_context", postgresql.JSONB, nullable=False),
        sa.Column("started_at", sa.DateTime),
        sa.Column("completed_at", sa.DateTime),
        sa.Column("error_message", sa.Text),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    # Notifications table
    op.create_table(
        "crm_workflow_notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("notification_type", postgresql.ENUM('email', 'in_app', 'sms', 'webhook', name='crm_workflow_notification_type'), nullable=False),
        sa.Column("recipient", sa.String(255), nullable=False),
        sa.Column("subject", sa.String(255), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default='pending'),
        sa.Column("sent_at", sa.DateTime),
        sa.Column("error_message", sa.Text),
        sa.Column("workflow_execution_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_workflow_executions.id")),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    # Seed initial data
    _seed_initial_data()


def downgrade() -> None:
    """Drop CRM Workflow tables."""
    op.drop_table("crm_workflow_notifications")
    op.drop_table("crm_workflow_executions")
    op.drop_table("crm_workflow_triggers")
    op.drop_table("crm_workflow_workflows")

    op.execute("DROP TYPE crm_workflow_execution_status")
    op.execute("DROP TYPE crm_workflow_notification_type")
    op.execute("DROP TYPE crm_workflow_action_type")
    op.execute("DROP TYPE crm_workflow_trigger_type")
    op.execute("DROP TYPE crm_workflow_status")


def _seed_initial_data():
    """Seed initial demo workflows."""
    # This will be populated when the service starts and finds existing workflows
    pass