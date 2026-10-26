"""Basis des CRM Communication-Schemas aus app.db.models.

Ersetzt die nie angewendeten Vorgaengerrevisionen (doppelte Enum-Anlage, Revisions-IDs
laenger als version_num, Abweichung von den Modellen). Eigene Versionstabelle siehe env.py.

Revision ID: crm_communication_0001
Revises:
Create Date: 2026-10-26
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "crm_communication_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('crm_communication_automations',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.String(length=64), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('trigger_conditions', sa.JSON(), nullable=False),
    sa.Column('actions', sa.JSON(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('priority', sa.Integer(), nullable=False),
    sa.Column('trigger_count', sa.Integer(), nullable=False),
    sa.Column('success_count', sa.Integer(), nullable=False),
    sa.Column('failure_count', sa.Integer(), nullable=False),
    sa.Column('created_by', sa.String(length=64), nullable=True),
    sa.Column('updated_by', sa.String(length=64), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('crm_communication_templates',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.String(length=64), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('type', sa.Enum('email', 'sms', 'letter', name='crm_communication_template_type'), nullable=False),
    sa.Column('subject_template', sa.String(length=500), nullable=True),
    sa.Column('body_template', sa.Text(), nullable=False),
    sa.Column('variables', sa.JSON(), nullable=False),
    sa.Column('sample_data', sa.JSON(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_default', sa.Boolean(), nullable=False),
    sa.Column('category', sa.String(length=100), nullable=True),
    sa.Column('tags', sa.JSON(), nullable=False),
    sa.Column('created_by', sa.String(length=64), nullable=True),
    sa.Column('updated_by', sa.String(length=64), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('crm_communication_campaigns',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.String(length=64), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('template_id', sa.UUID(), nullable=False),
    sa.Column('status', sa.Enum('draft', 'scheduled', 'running', 'paused', 'completed', 'cancelled', name='crm_communication_campaign_status'), nullable=False),
    sa.Column('target_filters', sa.JSON(), nullable=False),
    sa.Column('target_count', sa.Integer(), nullable=True),
    sa.Column('scheduled_at', sa.DateTime(), nullable=True),
    sa.Column('started_at', sa.DateTime(), nullable=True),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.Column('sent_count', sa.Integer(), nullable=False),
    sa.Column('delivered_count', sa.Integer(), nullable=False),
    sa.Column('opened_count', sa.Integer(), nullable=False),
    sa.Column('clicked_count', sa.Integer(), nullable=False),
    sa.Column('bounced_count', sa.Integer(), nullable=False),
    sa.Column('unsubscribed_count', sa.Integer(), nullable=False),
    sa.Column('created_by', sa.String(length=64), nullable=True),
    sa.Column('updated_by', sa.String(length=64), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['template_id'], ['crm_communication_templates.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('crm_communication_emails',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.String(length=64), nullable=False),
    sa.Column('message_id', sa.String(length=255), nullable=False),
    sa.Column('thread_id', sa.String(length=255), nullable=False),
    sa.Column('direction', sa.Enum('inbound', 'outbound', name='crm_communication_email_direction'), nullable=False),
    sa.Column('from_address', sa.String(length=255), nullable=False),
    sa.Column('to_addresses', sa.JSON(), nullable=False),
    sa.Column('cc_addresses', sa.JSON(), nullable=True),
    sa.Column('bcc_addresses', sa.JSON(), nullable=True),
    sa.Column('subject', sa.String(length=500), nullable=False),
    sa.Column('body_html', sa.Text(), nullable=True),
    sa.Column('body_text', sa.Text(), nullable=True),
    sa.Column('status', sa.Enum('draft', 'queued', 'sent', 'delivered', 'opened', 'clicked', 'bounced', 'complaint', 'unsubscribed', name='crm_communication_email_status'), nullable=False),
    sa.Column('customer_id', sa.UUID(), nullable=True),
    sa.Column('lead_id', sa.UUID(), nullable=True),
    sa.Column('case_id', sa.UUID(), nullable=True),
    sa.Column('opportunity_id', sa.UUID(), nullable=True),
    sa.Column('template_id', sa.UUID(), nullable=True),
    sa.Column('campaign_id', sa.UUID(), nullable=True),
    sa.Column('sent_at', sa.DateTime(), nullable=True),
    sa.Column('delivered_at', sa.DateTime(), nullable=True),
    sa.Column('opened_at', sa.DateTime(), nullable=True),
    sa.Column('clicked_at', sa.DateTime(), nullable=True),
    sa.Column('priority', sa.String(length=16), nullable=False),
    sa.Column('tags', sa.JSON(), nullable=False),
    sa.Column('metadata', sa.JSON(), nullable=False),
    sa.Column('created_by', sa.String(length=64), nullable=True),
    sa.Column('updated_by', sa.String(length=64), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['campaign_id'], ['crm_communication_campaigns.id'], ),
    sa.ForeignKeyConstraint(['template_id'], ['crm_communication_templates.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('message_id')
    )
    op.create_index(op.f('ix_crm_communication_emails_case_id'), 'crm_communication_emails', ['case_id'], unique=False)
    op.create_index(op.f('ix_crm_communication_emails_customer_id'), 'crm_communication_emails', ['customer_id'], unique=False)
    op.create_index(op.f('ix_crm_communication_emails_lead_id'), 'crm_communication_emails', ['lead_id'], unique=False)
    op.create_index(op.f('ix_crm_communication_emails_opportunity_id'), 'crm_communication_emails', ['opportunity_id'], unique=False)
    op.create_index(op.f('ix_crm_communication_emails_thread_id'), 'crm_communication_emails', ['thread_id'], unique=False)
    op.create_table('crm_communication_attachments',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('email_id', sa.UUID(), nullable=False),
    sa.Column('filename', sa.String(length=255), nullable=False),
    sa.Column('content_type', sa.String(length=100), nullable=False),
    sa.Column('size', sa.Integer(), nullable=False),
    sa.Column('content', sa.LargeBinary(), nullable=False),
    sa.Column('inline', sa.Boolean(), nullable=False),
    sa.Column('content_id', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['email_id'], ['crm_communication_emails.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('crm_communication_attachments')
    op.drop_index(op.f('ix_crm_communication_emails_thread_id'), table_name='crm_communication_emails')
    op.drop_index(op.f('ix_crm_communication_emails_opportunity_id'), table_name='crm_communication_emails')
    op.drop_index(op.f('ix_crm_communication_emails_lead_id'), table_name='crm_communication_emails')
    op.drop_index(op.f('ix_crm_communication_emails_customer_id'), table_name='crm_communication_emails')
    op.drop_index(op.f('ix_crm_communication_emails_case_id'), table_name='crm_communication_emails')
    op.drop_table('crm_communication_emails')
    op.drop_table('crm_communication_campaigns')
    op.drop_table('crm_communication_templates')
    op.drop_table('crm_communication_automations')
    sa.Enum(name='crm_communication_template_type').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='crm_communication_campaign_status').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='crm_communication_email_direction').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='crm_communication_email_status').drop(op.get_bind(), checkfirst=True)
