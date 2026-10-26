"""Basis des CRM Workflow-Schemas aus app.db.models.

Ersetzt die nie angewendeten Vorgaengerrevisionen (doppelte Enum-Anlage, Revisions-IDs
laenger als version_num, Abweichung von den Modellen). Eigene Versionstabelle siehe env.py.

Revision ID: crm_workflow_0001
Revises:
Create Date: 2026-10-26
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "crm_workflow_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('crm_workflow_workflows',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.String(length=64), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('status', sa.Enum('active', 'inactive', 'draft', name='crm_workflow_status'), nullable=False),
    sa.Column('trigger_conditions', sa.JSON(), nullable=False),
    sa.Column('actions', sa.JSON(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_by', sa.String(length=64), nullable=True),
    sa.Column('updated_by', sa.String(length=64), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('crm_workflow_executions',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workflow_id', sa.UUID(), nullable=False),
    sa.Column('status', sa.Enum('pending', 'running', 'completed', 'failed', 'cancelled', name='crm_workflow_execution_status'), nullable=False),
    sa.Column('trigger_event', sa.JSON(), nullable=False),
    sa.Column('execution_context', sa.JSON(), nullable=False),
    sa.Column('started_at', sa.DateTime(), nullable=True),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['workflow_id'], ['crm_workflow_workflows.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('crm_workflow_triggers',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.String(length=64), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('trigger_type', sa.Enum('event', 'schedule', 'manual', name='crm_workflow_trigger_type'), nullable=False),
    sa.Column('event_type', sa.String(length=128), nullable=True),
    sa.Column('schedule_cron', sa.String(length=128), nullable=True),
    sa.Column('conditions', sa.JSON(), nullable=False),
    sa.Column('workflow_id', sa.UUID(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_by', sa.String(length=64), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['workflow_id'], ['crm_workflow_workflows.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('crm_workflow_notifications',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.String(length=64), nullable=False),
    sa.Column('notification_type', sa.Enum('email', 'in_app', 'sms', 'webhook', name='crm_workflow_notification_type'), nullable=False),
    sa.Column('recipient', sa.String(length=255), nullable=False),
    sa.Column('subject', sa.String(length=255), nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('sent_at', sa.DateTime(), nullable=True),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.Column('workflow_execution_id', sa.UUID(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['workflow_execution_id'], ['crm_workflow_executions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('crm_workflow_notifications')
    op.drop_table('crm_workflow_triggers')
    op.drop_table('crm_workflow_executions')
    op.drop_table('crm_workflow_workflows')
    sa.Enum(name='crm_workflow_status').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='crm_workflow_execution_status').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='crm_workflow_trigger_type').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='crm_workflow_notification_type').drop(op.get_bind(), checkfirst=True)
