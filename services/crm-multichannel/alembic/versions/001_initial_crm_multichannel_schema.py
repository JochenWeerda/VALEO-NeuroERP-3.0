"""Initial CRM Multi-Channel schema.

Revision ID: 001_initial_crm_multichannel_schema
Revises:
Create Date: 2025-11-15 12:08:00.000000

"""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "001_initial_crm_multichannel_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create CRM Multi-Channel tables."""
    # Create enums
    op.execute("CREATE TYPE crm_multichannel_channel_type AS ENUM ('facebook', 'twitter', 'linkedin', 'instagram', 'website', 'email', 'sms', 'whatsapp', 'telegram', 'shopify', 'woocommerce', 'stripe', 'erp')")
    op.execute("CREATE TYPE crm_multichannel_channel_status AS ENUM ('active', 'inactive', 'error', 'pending')")
    op.execute("CREATE TYPE crm_multichannel_message_direction AS ENUM ('inbound', 'outbound')")
    op.execute("CREATE TYPE crm_multichannel_message_type AS ENUM ('text', 'image', 'video', 'file', 'link', 'form', 'payment', 'order')")
    op.execute("CREATE TYPE crm_multichannel_conversation_status AS ENUM ('open', 'closed', 'pending', 'escalated')")
    op.execute("CREATE TYPE crm_multichannel_form_field_type AS ENUM ('text', 'email', 'phone', 'number', 'date', 'select', 'multiselect', 'checkbox', 'radio', 'textarea', 'file')")

    # Channels table
    op.create_table(
        "crm_multichannel_channels",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("type", postgresql.ENUM('facebook', 'twitter', 'linkedin', 'instagram', 'website', 'email', 'sms', 'whatsapp', 'telegram', 'shopify', 'woocommerce', 'stripe', 'erp', name='crm_multichannel_channel_type'), nullable=False),
        sa.Column("status", postgresql.ENUM('active', 'inactive', 'error', 'pending', name='crm_multichannel_channel_status'), nullable=False, server_default='pending'),
        sa.Column("config", postgresql.JSONB, default=dict),
        sa.Column("credentials", postgresql.JSONB, default=dict),
        sa.Column("external_id", sa.String(255)),
        sa.Column("webhook_url", sa.String(500)),
        sa.Column("messages_sent", sa.Integer, nullable=False, server_default='0'),
        sa.Column("messages_received", sa.Integer, nullable=False, server_default='0'),
        sa.Column("last_activity", sa.DateTime),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default='true'),
        sa.Column("created_by", sa.String(64)),
        sa.Column("updated_by", sa.String(64)),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Conversations table
    op.create_table(
        "crm_multichannel_conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("channel_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_multichannel_channels.id"), nullable=False),
        sa.Column("external_id", sa.String(255), nullable=False),
        sa.Column("thread_id", sa.String(255)),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True)),
        sa.Column("contact_id", postgresql.UUID(as_uuid=True)),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True)),
        sa.Column("subject", sa.String(500)),
        sa.Column("status", postgresql.ENUM('open', 'closed', 'pending', 'escalated', name='crm_multichannel_conversation_status'), nullable=False, server_default='open'),
        sa.Column("priority", sa.String(16), server_default='normal'),
        sa.Column("tags", postgresql.JSONB, default=list),
        sa.Column("assigned_to", sa.String(64)),
        sa.Column("assigned_at", sa.DateTime),
        sa.Column("started_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("last_message_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("closed_at", sa.DateTime),
        sa.Column("message_count", sa.Integer, nullable=False, server_default='0'),
        sa.Column("customer_message_count", sa.Integer, nullable=False, server_default='0'),
        sa.Column("agent_message_count", sa.Integer, nullable=False, server_default='0'),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default='true'),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Messages table
    op.create_table(
        "crm_multichannel_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_multichannel_conversations.id"), nullable=False),
        sa.Column("external_id", sa.String(255), nullable=False),
        sa.Column("external_parent_id", sa.String(255)),
        sa.Column("direction", postgresql.ENUM('inbound', 'outbound', name='crm_multichannel_message_direction'), nullable=False),
        sa.Column("type", postgresql.ENUM('text', 'image', 'video', 'file', 'link', 'form', 'payment', 'order', name='crm_multichannel_message_type'), nullable=False, server_default='text'),
        sa.Column("content", sa.Text),
        sa.Column("metadata", postgresql.JSONB, default=dict),
        sa.Column("sender_id", sa.String(255)),
        sa.Column("sender_name", sa.String(255)),
        sa.Column("sender_type", sa.String(32), server_default='customer'),
        sa.Column("is_read", sa.Boolean, nullable=False, server_default='false'),
        sa.Column("delivered_at", sa.DateTime),
        sa.Column("read_at", sa.DateTime),
        sa.Column("handled_by", sa.String(64)),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    # Web Forms table
    op.create_table(
        "crm_multichannel_webforms",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("fields", postgresql.JSONB, nullable=False),
        sa.Column("settings", postgresql.JSONB, default=dict),
        sa.Column("slug", sa.String(255), unique=True),
        sa.Column("lead_source", sa.String(64)),
        sa.Column("auto_create_lead", sa.Boolean, nullable=False, server_default='true'),
        sa.Column("notification_emails", postgresql.JSONB, default=list),
        sa.Column("is_published", sa.Boolean, nullable=False, server_default='false'),
        sa.Column("published_at", sa.DateTime),
        sa.Column("view_count", sa.Integer, nullable=False, server_default='0'),
        sa.Column("submission_count", sa.Integer, nullable=False, server_default='0'),
        sa.Column("conversion_rate", sa.Float),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default='true'),
        sa.Column("created_by", sa.String(64)),
        sa.Column("updated_by", sa.String(64)),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Form Submissions table
    op.create_table(
        "crm_multichannel_submissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("form_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_multichannel_webforms.id"), nullable=False),
        sa.Column("data", postgresql.JSONB, nullable=False),
        sa.Column("metadata", postgresql.JSONB, default=dict),
        sa.Column("lead_created", sa.Boolean, nullable=False, server_default='false'),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True)),
        sa.Column("processed_at", sa.DateTime),
        sa.Column("processing_status", sa.String(32), server_default='pending'),
        sa.Column("source_url", sa.String(500)),
        sa.Column("referrer", sa.String(500)),
        sa.Column("utm_parameters", postgresql.JSONB, default=dict),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    # Integrations table
    op.create_table(
        "crm_multichannel_integrations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("type", sa.String(64), nullable=False),
        sa.Column("config", postgresql.JSONB, default=dict),
        sa.Column("credentials", postgresql.JSONB, default=dict),
        sa.Column("sync_enabled", sa.Boolean, nullable=False, server_default='true'),
        sa.Column("sync_frequency", sa.Integer, nullable=False, server_default='3600'),
        sa.Column("sync_entities", postgresql.JSONB, default=list),
        sa.Column("status", sa.String(32), server_default='disconnected'),
        sa.Column("last_sync", sa.DateTime),
        sa.Column("last_error", sa.Text),
        sa.Column("records_synced", sa.Integer, nullable=False, server_default='0'),
        sa.Column("last_record_count", sa.Integer, nullable=False, server_default='0'),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default='true'),
        sa.Column("created_by", sa.String(64)),
        sa.Column("updated_by", sa.String(64)),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Seed initial data
    _seed_initial_data()


def downgrade() -> None:
    """Drop CRM Multi-Channel tables."""
    op.drop_table("crm_multichannel_integrations")
    op.drop_table("crm_multichannel_submissions")
    op.drop_table("crm_multichannel_webforms")
    op.drop_table("crm_multichannel_messages")
    op.drop_table("crm_multichannel_conversations")
    op.drop_table("crm_multichannel_channels")

    op.execute("DROP TYPE crm_multichannel_form_field_type")
    op.execute("DROP TYPE crm_multichannel_conversation_status")
    op.execute("DROP TYPE crm_multichannel_message_type")
    op.execute("DROP TYPE crm_multichannel_message_direction")
    op.execute("DROP TYPE crm_multichannel_channel_status")
    op.execute("DROP TYPE crm_multichannel_channel_type")


def _seed_initial_data():
    """Seed initial demo multi-channel data."""
    # This will be populated when the service starts and finds existing data
    pass