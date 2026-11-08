"""Basis des CRM Multi-Channel-Schemas aus app.db.models.

Ersetzt die nie angewendeten Vorgaengerrevisionen (doppelte Enum-Anlage, Revisions-IDs
laenger als version_num, Abweichung von den Modellen). Eigene Versionstabelle siehe env.py.

Revision ID: crm_multichannel_0001
Revises:
Create Date: 2026-10-26
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "crm_multichannel_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('crm_multichannel_channels',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.String(length=64), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('type', sa.Enum('facebook', 'twitter', 'linkedin', 'instagram', 'website', 'email', 'sms', 'whatsapp', 'telegram', 'shopify', 'woocommerce', 'stripe', 'erp', name='crm_multichannel_channel_type'), nullable=False),
    sa.Column('status', sa.Enum('active', 'inactive', 'error', 'pending', name='crm_multichannel_channel_status'), nullable=False),
    sa.Column('config', sa.JSON(), nullable=False),
    sa.Column('credentials', sa.JSON(), nullable=False),
    sa.Column('external_id', sa.String(length=255), nullable=True),
    sa.Column('webhook_url', sa.String(length=500), nullable=True),
    sa.Column('messages_sent', sa.Integer(), nullable=False),
    sa.Column('messages_received', sa.Integer(), nullable=False),
    sa.Column('last_activity', sa.DateTime(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_by', sa.String(length=64), nullable=True),
    sa.Column('updated_by', sa.String(length=64), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('crm_multichannel_integrations',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.String(length=64), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('type', sa.String(length=64), nullable=False),
    sa.Column('config', sa.JSON(), nullable=False),
    sa.Column('credentials', sa.JSON(), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('last_sync', sa.DateTime(), nullable=True),
    sa.Column('last_error', sa.Text(), nullable=True),
    sa.Column('sync_enabled', sa.Boolean(), nullable=False),
    sa.Column('sync_frequency', sa.Integer(), nullable=False),
    sa.Column('sync_entities', sa.JSON(), nullable=False),
    sa.Column('records_synced', sa.Integer(), nullable=False),
    sa.Column('last_record_count', sa.Integer(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_by', sa.String(length=64), nullable=True),
    sa.Column('updated_by', sa.String(length=64), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('crm_multichannel_webforms',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.String(length=64), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('fields', sa.JSON(), nullable=False),
    sa.Column('settings', sa.JSON(), nullable=False),
    sa.Column('slug', sa.String(length=255), nullable=False),
    sa.Column('is_published', sa.Boolean(), nullable=False),
    sa.Column('published_at', sa.DateTime(), nullable=True),
    sa.Column('lead_source', sa.String(length=64), nullable=True),
    sa.Column('auto_create_lead', sa.Boolean(), nullable=False),
    sa.Column('notification_emails', sa.JSON(), nullable=False),
    sa.Column('view_count', sa.Integer(), nullable=False),
    sa.Column('submission_count', sa.Integer(), nullable=False),
    sa.Column('conversion_rate', sa.Float(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_by', sa.String(length=64), nullable=True),
    sa.Column('updated_by', sa.String(length=64), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('slug')
    )
    op.create_table('crm_multichannel_conversations',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.String(length=64), nullable=False),
    sa.Column('channel_id', sa.UUID(), nullable=False),
    sa.Column('external_id', sa.String(length=255), nullable=False),
    sa.Column('thread_id', sa.String(length=255), nullable=True),
    sa.Column('customer_id', sa.UUID(), nullable=True),
    sa.Column('contact_id', sa.UUID(), nullable=True),
    sa.Column('lead_id', sa.UUID(), nullable=True),
    sa.Column('subject', sa.String(length=500), nullable=True),
    sa.Column('status', sa.Enum('open', 'closed', 'pending', 'escalated', name='crm_multichannel_conversation_status'), nullable=False),
    sa.Column('priority', sa.String(length=16), nullable=False),
    sa.Column('tags', sa.JSON(), nullable=False),
    sa.Column('assigned_to', sa.String(length=64), nullable=True),
    sa.Column('assigned_at', sa.DateTime(), nullable=True),
    sa.Column('started_at', sa.DateTime(), nullable=False),
    sa.Column('last_message_at', sa.DateTime(), nullable=False),
    sa.Column('closed_at', sa.DateTime(), nullable=True),
    sa.Column('message_count', sa.Integer(), nullable=False),
    sa.Column('customer_message_count', sa.Integer(), nullable=False),
    sa.Column('agent_message_count', sa.Integer(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['channel_id'], ['crm_multichannel_channels.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('crm_multichannel_submissions',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.String(length=64), nullable=False),
    sa.Column('form_id', sa.UUID(), nullable=False),
    sa.Column('data', sa.JSON(), nullable=False),
    sa.Column('metadata', sa.JSON(), nullable=False),
    sa.Column('lead_created', sa.Boolean(), nullable=False),
    sa.Column('lead_id', sa.UUID(), nullable=True),
    sa.Column('processed_at', sa.DateTime(), nullable=True),
    sa.Column('processing_status', sa.String(length=32), nullable=False),
    sa.Column('source_url', sa.String(length=500), nullable=True),
    sa.Column('referrer', sa.String(length=500), nullable=True),
    sa.Column('utm_parameters', sa.JSON(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['form_id'], ['crm_multichannel_webforms.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('crm_multichannel_messages',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.String(length=64), nullable=False),
    sa.Column('conversation_id', sa.UUID(), nullable=False),
    sa.Column('external_id', sa.String(length=255), nullable=False),
    sa.Column('external_parent_id', sa.String(length=255), nullable=True),
    sa.Column('direction', sa.Enum('inbound', 'outbound', name='crm_multichannel_message_direction'), nullable=False),
    sa.Column('type', sa.Enum('text', 'image', 'video', 'file', 'link', 'form', 'payment', 'order', name='crm_multichannel_message_type'), nullable=False),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('metadata', sa.JSON(), nullable=False),
    sa.Column('sender_id', sa.String(length=255), nullable=True),
    sa.Column('sender_name', sa.String(length=255), nullable=True),
    sa.Column('sender_type', sa.String(length=32), nullable=False),
    sa.Column('is_read', sa.Boolean(), nullable=False),
    sa.Column('delivered_at', sa.DateTime(), nullable=True),
    sa.Column('read_at', sa.DateTime(), nullable=True),
    sa.Column('handled_by', sa.String(length=64), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['conversation_id'], ['crm_multichannel_conversations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('crm_multichannel_messages')
    op.drop_table('crm_multichannel_submissions')
    op.drop_table('crm_multichannel_conversations')
    op.drop_table('crm_multichannel_webforms')
    op.drop_table('crm_multichannel_integrations')
    op.drop_table('crm_multichannel_channels')
    sa.Enum(name='crm_multichannel_channel_type').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='crm_multichannel_channel_status').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='crm_multichannel_conversation_status').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='crm_multichannel_message_direction').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='crm_multichannel_message_type').drop(op.get_bind(), checkfirst=True)
