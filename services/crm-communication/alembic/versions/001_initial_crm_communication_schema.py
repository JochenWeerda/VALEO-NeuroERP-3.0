"""Initial CRM Communication schema.

Revision ID: 001_initial_crm_communication_schema
Revises:
Create Date: 2025-11-15 11:49:00.000000

"""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "001_initial_crm_communication_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create CRM Communication tables."""
    # Create enums
    op.execute("CREATE TYPE crm_communication_email_status AS ENUM ('draft', 'queued', 'sent', 'delivered', 'opened', 'clicked', 'bounced', 'complaint', 'unsubscribed')")
    op.execute("CREATE TYPE crm_communication_email_direction AS ENUM ('inbound', 'outbound')")
    op.execute("CREATE TYPE crm_communication_template_type AS ENUM ('email', 'sms', 'letter')")
    op.execute("CREATE TYPE crm_communication_campaign_status AS ENUM ('draft', 'scheduled', 'running', 'paused', 'completed', 'cancelled')")

    # Emails table
    op.create_table(
        "crm_communication_emails",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("message_id", sa.String(255), unique=True),
        sa.Column("thread_id", sa.String(255), index=True),
        sa.Column("direction", postgresql.ENUM('inbound', 'outbound', name='crm_communication_email_direction'), nullable=False),
        sa.Column("from_address", sa.String(255), nullable=False),
        sa.Column("to_addresses", postgresql.JSONB, nullable=False),
        sa.Column("cc_addresses", postgresql.JSONB),
        sa.Column("bcc_addresses", postgresql.JSONB),
        sa.Column("subject", sa.String(500), nullable=False),
        sa.Column("body_html", sa.Text),
        sa.Column("body_text", sa.Text),
        sa.Column("status", postgresql.ENUM('draft', 'queued', 'sent', 'delivered', 'opened', 'clicked', 'bounced', 'complaint', 'unsubscribed', name='crm_communication_email_status'), nullable=False, server_default='draft'),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), index=True),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), index=True),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), index=True),
        sa.Column("opportunity_id", postgresql.UUID(as_uuid=True), index=True),
        sa.Column("template_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_communication_templates.id")),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_communication_campaigns.id")),
        sa.Column("sent_at", sa.DateTime),
        sa.Column("delivered_at", sa.DateTime),
        sa.Column("opened_at", sa.DateTime),
        sa.Column("clicked_at", sa.DateTime),
        sa.Column("priority", sa.String(16), server_default='normal'),
        sa.Column("tags", postgresql.JSONB, default=list),
        sa.Column("metadata", postgresql.JSONB, default=dict),
        sa.Column("created_by", sa.String(64)),
        sa.Column("updated_by", sa.String(64)),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Templates table
    op.create_table(
        "crm_communication_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("type", postgresql.ENUM('email', 'sms', 'letter', name='crm_communication_template_type'), nullable=False),
        sa.Column("subject_template", sa.String(500)),
        sa.Column("body_template", sa.Text, nullable=False),
        sa.Column("variables", postgresql.JSONB, default=dict),
        sa.Column("sample_data", postgresql.JSONB, default=dict),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default='true'),
        sa.Column("is_default", sa.Boolean, nullable=False, server_default='false'),
        sa.Column("category", sa.String(100)),
        sa.Column("tags", postgresql.JSONB, default=list),
        sa.Column("created_by", sa.String(64)),
        sa.Column("updated_by", sa.String(64)),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Campaigns table
    op.create_table(
        "crm_communication_campaigns",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("template_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_communication_templates.id"), nullable=False),
        sa.Column("status", postgresql.ENUM('draft', 'scheduled', 'running', 'paused', 'completed', 'cancelled', name='crm_communication_campaign_status'), nullable=False, server_default='draft'),
        sa.Column("target_filters", postgresql.JSONB, default=dict),
        sa.Column("target_count", sa.Integer),
        sa.Column("scheduled_at", sa.DateTime),
        sa.Column("started_at", sa.DateTime),
        sa.Column("completed_at", sa.DateTime),
        sa.Column("sent_count", sa.Integer, nullable=False, server_default='0'),
        sa.Column("delivered_count", sa.Integer, nullable=False, server_default='0'),
        sa.Column("opened_count", sa.Integer, nullable=False, server_default='0'),
        sa.Column("clicked_count", sa.Integer, nullable=False, server_default='0'),
        sa.Column("bounced_count", sa.Integer, nullable=False, server_default='0'),
        sa.Column("unsubscribed_count", sa.Integer, nullable=False, server_default='0'),
        sa.Column("created_by", sa.String(64)),
        sa.Column("updated_by", sa.String(64)),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Attachments table
    op.create_table(
        "crm_communication_attachments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("email_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_communication_emails.id"), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("content_type", sa.String(100), nullable=False),
        sa.Column("size", sa.Integer, nullable=False),
        sa.Column("content", sa.LargeBinary, nullable=False),
        sa.Column("inline", sa.Boolean, nullable=False, server_default='false'),
        sa.Column("content_id", sa.String(255)),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    # Automations table
    op.create_table(
        "crm_communication_automations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("trigger_conditions", postgresql.JSONB, nullable=False),
        sa.Column("actions", postgresql.JSONB, nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default='true'),
        sa.Column("priority", sa.Integer, nullable=False, server_default='0'),
        sa.Column("trigger_count", sa.Integer, nullable=False, server_default='0'),
        sa.Column("success_count", sa.Integer, nullable=False, server_default='0'),
        sa.Column("failure_count", sa.Integer, nullable=False, server_default='0'),
        sa.Column("created_by", sa.String(64)),
        sa.Column("updated_by", sa.String(64)),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Seed initial data
    _seed_initial_data()


def downgrade() -> None:
    """Drop CRM Communication tables."""
    op.drop_table("crm_communication_automations")
    op.drop_table("crm_communication_attachments")
    op.drop_table("crm_communication_campaigns")
    op.drop_table("crm_communication_templates")
    op.drop_table("crm_communication_emails")

    op.execute("DROP TYPE crm_communication_campaign_status")
    op.execute("DROP TYPE crm_communication_template_type")
    op.execute("DROP TYPE crm_communication_email_direction")
    op.execute("DROP TYPE crm_communication_email_status")


def _seed_initial_data():
    """Seed initial demo communication data."""
    # This will be populated when the service starts and finds existing data
    pass