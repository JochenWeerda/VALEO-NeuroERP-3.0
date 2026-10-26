"""Basis des CRM Marketing-Schemas aus app.db.models.

Ersetzt die nie angewendeten Vorgaengerrevisionen: sie wichen von den Modellen ab (IDs
varchar statt uuid, Enum-Spalten als varchar, abweichende Tabellen). Indizes, die nur die
Altkette kannte, sind in die Modelle uebernommen. Eigene Versionstabelle siehe env.py.

Revision ID: crm_marketing_0001
Revises:
Create Date: 2026-10-26
"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "crm_marketing_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('crm_marketing_campaign_templates',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.String(length=64), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('type', sa.Enum('EMAIL', 'SMS', 'PUSH', 'SOCIAL', name='campaigntype'), nullable=False),
    sa.Column('subject', sa.String(length=500), nullable=True),
    sa.Column('body_html', sa.Text(), nullable=True),
    sa.Column('body_text', sa.Text(), nullable=True),
    sa.Column('variables', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_crm_marketing_campaign_templates_tenant_id'), 'crm_marketing_campaign_templates', ['tenant_id'], unique=False)
    op.create_table('crm_marketing_segments',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.String(length=64), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('type', sa.Enum('DYNAMIC', 'STATIC', 'HYBRID', name='segmenttype'), nullable=False),
    sa.Column('status', sa.Enum('ACTIVE', 'INACTIVE', 'ARCHIVED', name='segmentstatus'), nullable=False),
    sa.Column('rules', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('member_count', sa.Integer(), nullable=False),
    sa.Column('last_calculated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('created_by', sa.String(length=255), nullable=True),
    sa.Column('updated_by', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_crm_marketing_segments_tenant_id'), 'crm_marketing_segments', ['tenant_id'], unique=False)
    op.create_table('crm_marketing_campaigns',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.String(length=64), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('type', sa.Enum('EMAIL', 'SMS', 'PUSH', 'SOCIAL', name='campaigntype'), nullable=False),
    sa.Column('status', sa.Enum('DRAFT', 'SCHEDULED', 'RUNNING', 'PAUSED', 'COMPLETED', 'CANCELLED', name='campaignstatus'), nullable=False),
    sa.Column('segment_id', sa.UUID(), nullable=True),
    sa.Column('template_id', sa.UUID(), nullable=True),
    sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('budget', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('spent', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('target_count', sa.Integer(), nullable=False),
    sa.Column('sent_count', sa.Integer(), nullable=False),
    sa.Column('delivered_count', sa.Integer(), nullable=False),
    sa.Column('open_count', sa.Integer(), nullable=False),
    sa.Column('click_count', sa.Integer(), nullable=False),
    sa.Column('conversion_count', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('created_by', sa.String(length=255), nullable=True),
    sa.Column('updated_by', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['segment_id'], ['crm_marketing_segments.id'], ),
    sa.ForeignKeyConstraint(['template_id'], ['crm_marketing_campaign_templates.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_crm_marketing_campaigns_segment_id'), 'crm_marketing_campaigns', ['segment_id'], unique=False)
    op.create_index(op.f('ix_crm_marketing_campaigns_template_id'), 'crm_marketing_campaigns', ['template_id'], unique=False)
    op.create_index(op.f('ix_crm_marketing_campaigns_tenant_id'), 'crm_marketing_campaigns', ['tenant_id'], unique=False)
    op.create_table('crm_marketing_segment_members',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('segment_id', sa.UUID(), nullable=False),
    sa.Column('contact_id', sa.UUID(), nullable=False),
    sa.Column('added_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('added_by', sa.String(length=255), nullable=True),
    sa.Column('removed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('removed_by', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['segment_id'], ['crm_marketing_segments.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_crm_marketing_segment_members_contact_id'), 'crm_marketing_segment_members', ['contact_id'], unique=False)
    op.create_index(op.f('ix_crm_marketing_segment_members_segment_id'), 'crm_marketing_segment_members', ['segment_id'], unique=False)
    op.create_table('crm_marketing_segment_performance',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('segment_id', sa.UUID(), nullable=False),
    sa.Column('date', sa.DateTime(timezone=True), nullable=False),
    sa.Column('period_type', sa.String(length=20), nullable=False),
    sa.Column('member_count', sa.Integer(), nullable=False),
    sa.Column('active_members', sa.Integer(), nullable=False),
    sa.Column('campaign_count', sa.Integer(), nullable=False),
    sa.Column('conversion_rate', sa.Numeric(precision=5, scale=2), nullable=True),
    sa.Column('revenue', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.ForeignKeyConstraint(['segment_id'], ['crm_marketing_segments.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_crm_marketing_segment_performance_date'), 'crm_marketing_segment_performance', ['date'], unique=False)
    op.create_index(op.f('ix_crm_marketing_segment_performance_segment_id'), 'crm_marketing_segment_performance', ['segment_id'], unique=False)
    op.create_table('crm_marketing_segment_rules',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('segment_id', sa.UUID(), nullable=False),
    sa.Column('field', sa.String(length=255), nullable=False),
    sa.Column('operator', sa.Enum('EQUALS', 'NOT_EQUALS', 'CONTAINS', 'NOT_CONTAINS', 'STARTS_WITH', 'ENDS_WITH', 'GREATER_THAN', 'LESS_THAN', 'GREATER_EQUAL', 'LESS_EQUAL', 'IN', 'NOT_IN', 'IS_NULL', 'IS_NOT_NULL', 'BETWEEN', name='ruleoperator'), nullable=False),
    sa.Column('value', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('logical_operator', sa.Enum('AND', 'OR', name='logicaloperator'), nullable=True),
    sa.Column('order', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['segment_id'], ['crm_marketing_segments.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_crm_marketing_segment_rules_segment_id'), 'crm_marketing_segment_rules', ['segment_id'], unique=False)
    op.create_table('crm_marketing_campaign_performance',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('campaign_id', sa.UUID(), nullable=False),
    sa.Column('date', sa.DateTime(timezone=True), nullable=False),
    sa.Column('sent_count', sa.Integer(), nullable=False),
    sa.Column('delivered_count', sa.Integer(), nullable=False),
    sa.Column('open_count', sa.Integer(), nullable=False),
    sa.Column('click_count', sa.Integer(), nullable=False),
    sa.Column('conversion_count', sa.Integer(), nullable=False),
    sa.Column('open_rate', sa.Numeric(precision=5, scale=2), nullable=True),
    sa.Column('click_rate', sa.Numeric(precision=5, scale=2), nullable=True),
    sa.Column('conversion_rate', sa.Numeric(precision=5, scale=2), nullable=True),
    sa.Column('revenue', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('roi', sa.Numeric(precision=5, scale=2), nullable=True),
    sa.ForeignKeyConstraint(['campaign_id'], ['crm_marketing_campaigns.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_crm_marketing_campaign_performance_campaign_id'), 'crm_marketing_campaign_performance', ['campaign_id'], unique=False)
    op.create_index(op.f('ix_crm_marketing_campaign_performance_date'), 'crm_marketing_campaign_performance', ['date'], unique=False)
    op.create_table('crm_marketing_campaign_variants',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('campaign_id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('variant_type', sa.String(length=10), nullable=False),
    sa.Column('template_id', sa.UUID(), nullable=True),
    sa.Column('target_percentage', sa.Integer(), nullable=False),
    sa.Column('sent_count', sa.Integer(), nullable=False),
    sa.Column('open_count', sa.Integer(), nullable=False),
    sa.Column('click_count', sa.Integer(), nullable=False),
    sa.Column('conversion_count', sa.Integer(), nullable=False),
    sa.Column('winner', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['campaign_id'], ['crm_marketing_campaigns.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['template_id'], ['crm_marketing_campaign_templates.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_crm_marketing_campaign_variants_campaign_id'), 'crm_marketing_campaign_variants', ['campaign_id'], unique=False)
    op.create_table('crm_marketing_campaign_recipients',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('campaign_id', sa.UUID(), nullable=False),
    sa.Column('contact_id', sa.UUID(), nullable=False),
    sa.Column('variant_id', sa.UUID(), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('phone', sa.String(length=50), nullable=True),
    sa.Column('status', sa.Enum('PENDING', 'SENT', 'DELIVERED', 'BOUNCED', 'FAILED', name='recipientstatus'), nullable=False),
    sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('opened_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('clicked_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('converted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('open_count', sa.Integer(), nullable=False),
    sa.Column('click_count', sa.Integer(), nullable=False),
    sa.Column('bounce_reason', sa.Text(), nullable=True),
    sa.Column('failure_reason', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['campaign_id'], ['crm_marketing_campaigns.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['variant_id'], ['crm_marketing_campaign_variants.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_crm_marketing_campaign_recipients_campaign_id'), 'crm_marketing_campaign_recipients', ['campaign_id'], unique=False)
    op.create_index(op.f('ix_crm_marketing_campaign_recipients_contact_id'), 'crm_marketing_campaign_recipients', ['contact_id'], unique=False)
    op.create_index(op.f('ix_crm_marketing_campaign_recipients_email'), 'crm_marketing_campaign_recipients', ['email'], unique=False)
    op.create_index(op.f('ix_crm_marketing_campaign_recipients_variant_id'), 'crm_marketing_campaign_recipients', ['variant_id'], unique=False)
    op.create_table('crm_marketing_campaign_events',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('campaign_id', sa.UUID(), nullable=False),
    sa.Column('recipient_id', sa.UUID(), nullable=True),
    sa.Column('event_type', sa.Enum('SENT', 'DELIVERED', 'OPENED', 'CLICKED', 'BOUNCED', 'CONVERTED', name='campaigneventtype'), nullable=False),
    sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
    sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.ForeignKeyConstraint(['campaign_id'], ['crm_marketing_campaigns.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['recipient_id'], ['crm_marketing_campaign_recipients.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_crm_marketing_campaign_events_campaign_id'), 'crm_marketing_campaign_events', ['campaign_id'], unique=False)
    op.create_index(op.f('ix_crm_marketing_campaign_events_recipient_id'), 'crm_marketing_campaign_events', ['recipient_id'], unique=False)
    op.create_index(op.f('ix_crm_marketing_campaign_events_timestamp'), 'crm_marketing_campaign_events', ['timestamp'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_crm_marketing_campaign_events_timestamp'), table_name='crm_marketing_campaign_events')
    op.drop_index(op.f('ix_crm_marketing_campaign_events_recipient_id'), table_name='crm_marketing_campaign_events')
    op.drop_index(op.f('ix_crm_marketing_campaign_events_campaign_id'), table_name='crm_marketing_campaign_events')
    op.drop_table('crm_marketing_campaign_events')
    op.drop_index(op.f('ix_crm_marketing_campaign_recipients_variant_id'), table_name='crm_marketing_campaign_recipients')
    op.drop_index(op.f('ix_crm_marketing_campaign_recipients_email'), table_name='crm_marketing_campaign_recipients')
    op.drop_index(op.f('ix_crm_marketing_campaign_recipients_contact_id'), table_name='crm_marketing_campaign_recipients')
    op.drop_index(op.f('ix_crm_marketing_campaign_recipients_campaign_id'), table_name='crm_marketing_campaign_recipients')
    op.drop_table('crm_marketing_campaign_recipients')
    op.drop_index(op.f('ix_crm_marketing_campaign_variants_campaign_id'), table_name='crm_marketing_campaign_variants')
    op.drop_table('crm_marketing_campaign_variants')
    op.drop_index(op.f('ix_crm_marketing_campaign_performance_date'), table_name='crm_marketing_campaign_performance')
    op.drop_index(op.f('ix_crm_marketing_campaign_performance_campaign_id'), table_name='crm_marketing_campaign_performance')
    op.drop_table('crm_marketing_campaign_performance')
    op.drop_index(op.f('ix_crm_marketing_segment_rules_segment_id'), table_name='crm_marketing_segment_rules')
    op.drop_table('crm_marketing_segment_rules')
    op.drop_index(op.f('ix_crm_marketing_segment_performance_segment_id'), table_name='crm_marketing_segment_performance')
    op.drop_index(op.f('ix_crm_marketing_segment_performance_date'), table_name='crm_marketing_segment_performance')
    op.drop_table('crm_marketing_segment_performance')
    op.drop_index(op.f('ix_crm_marketing_segment_members_segment_id'), table_name='crm_marketing_segment_members')
    op.drop_index(op.f('ix_crm_marketing_segment_members_contact_id'), table_name='crm_marketing_segment_members')
    op.drop_table('crm_marketing_segment_members')
    op.drop_index(op.f('ix_crm_marketing_campaigns_tenant_id'), table_name='crm_marketing_campaigns')
    op.drop_index(op.f('ix_crm_marketing_campaigns_template_id'), table_name='crm_marketing_campaigns')
    op.drop_index(op.f('ix_crm_marketing_campaigns_segment_id'), table_name='crm_marketing_campaigns')
    op.drop_table('crm_marketing_campaigns')
    op.drop_index(op.f('ix_crm_marketing_segments_tenant_id'), table_name='crm_marketing_segments')
    op.drop_table('crm_marketing_segments')
    op.drop_index(op.f('ix_crm_marketing_campaign_templates_tenant_id'), table_name='crm_marketing_campaign_templates')
    op.drop_table('crm_marketing_campaign_templates')
    sa.Enum(name='campaigneventtype').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='campaignstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='campaigntype').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='logicaloperator').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='recipientstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='ruleoperator').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='segmentstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='segmenttype').drop(op.get_bind(), checkfirst=True)
