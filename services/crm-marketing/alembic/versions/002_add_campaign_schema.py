"""Add campaign tables

Revision ID: 002_add_campaign_schema
Revises: 001_initial_segment_schema
Create Date: 2025-01-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002_add_campaign_schema'
down_revision: Union[str, None] = '001_initial_segment_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    op.execute("""
        CREATE TYPE crm_marketing_campaign_type AS ENUM ('email', 'sms', 'push', 'social');
    """)
    
    op.execute("""
        CREATE TYPE crm_marketing_campaign_status AS ENUM ('draft', 'scheduled', 'running', 'paused', 'completed', 'cancelled');
    """)
    
    op.execute("""
        CREATE TYPE crm_marketing_recipient_status AS ENUM ('pending', 'sent', 'delivered', 'bounced', 'failed');
    """)
    
    op.execute("""
        CREATE TYPE crm_marketing_campaign_event_type AS ENUM ('sent', 'delivered', 'opened', 'clicked', 'bounced', 'converted');
    """)
    
    # Campaign Templates
    op.create_table(
        'crm_marketing_campaign_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', sa.String(64), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', postgresql.ENUM('email', 'sms', 'push', 'social', name='crm_marketing_campaign_type'), nullable=False),
        sa.Column('subject', sa.String(500), nullable=True),
        sa.Column('body_html', sa.Text(), nullable=True),
        sa.Column('body_text', sa.Text(), nullable=True),
        sa.Column('variables', postgresql.JSONB(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('created_by', sa.String(255), nullable=True),
        sa.Column('updated_by', sa.String(255), nullable=True),
    )
    op.create_index('ix_crm_marketing_campaign_templates_tenant_id', 'crm_marketing_campaign_templates', ['tenant_id'])
    
    # Campaigns
    op.create_table(
        'crm_marketing_campaigns',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', sa.String(64), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', postgresql.ENUM('email', 'sms', 'push', 'social', name='crm_marketing_campaign_type'), nullable=False),
        sa.Column('status', postgresql.ENUM('draft', 'scheduled', 'running', 'paused', 'completed', 'cancelled', name='crm_marketing_campaign_status'), nullable=False, server_default='draft'),
        sa.Column('segment_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sender_name', sa.String(255), nullable=True),
        sa.Column('sender_email', sa.String(255), nullable=True),
        sa.Column('subject', sa.String(500), nullable=True),
        sa.Column('budget', sa.Numeric(12, 2), nullable=True),
        sa.Column('spent', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('target_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('sent_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('delivered_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('open_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('click_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('conversion_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('settings', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('created_by', sa.String(255), nullable=True),
        sa.Column('updated_by', sa.String(255), nullable=True),
        sa.ForeignKeyConstraint(['segment_id'], ['crm_marketing_segments.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['template_id'], ['crm_marketing_campaign_templates.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_crm_marketing_campaigns_tenant_id', 'crm_marketing_campaigns', ['tenant_id'])
    op.create_index('ix_crm_marketing_campaigns_segment_id', 'crm_marketing_campaigns', ['segment_id'])
    op.create_index('ix_crm_marketing_campaigns_template_id', 'crm_marketing_campaigns', ['template_id'])
    
    # Campaign Variants (for A/B Testing)
    op.create_table(
        'crm_marketing_campaign_variants',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('variant_type', sa.String(10), nullable=False),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('target_percentage', sa.Integer(), nullable=False, server_default='50'),
        sa.Column('sent_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('open_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('click_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('conversion_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('winner', sa.Boolean(), nullable=False, server_default='false'),
        sa.ForeignKeyConstraint(['campaign_id'], ['crm_marketing_campaigns.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['template_id'], ['crm_marketing_campaign_templates.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_crm_marketing_campaign_variants_campaign_id', 'crm_marketing_campaign_variants', ['campaign_id'])
    
    # Campaign Recipients
    op.create_table(
        'crm_marketing_campaign_recipients',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('contact_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('variant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('status', postgresql.ENUM('pending', 'sent', 'delivered', 'bounced', 'failed', name='crm_marketing_recipient_status'), nullable=False, server_default='pending'),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('opened_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('clicked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('converted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('open_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('click_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('bounce_reason', sa.Text(), nullable=True),
        sa.Column('failure_reason', sa.Text(), nullable=True),
        sa.Column('variant', sa.String(10), nullable=True),
        sa.ForeignKeyConstraint(['campaign_id'], ['crm_marketing_campaigns.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['variant_id'], ['crm_marketing_campaign_variants.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_crm_marketing_campaign_recipients_campaign_id', 'crm_marketing_campaign_recipients', ['campaign_id'])
    op.create_index('ix_crm_marketing_campaign_recipients_contact_id', 'crm_marketing_campaign_recipients', ['contact_id'])
    op.create_index('ix_crm_marketing_campaign_recipients_variant_id', 'crm_marketing_campaign_recipients', ['variant_id'])
    op.create_index('ix_crm_marketing_campaign_recipients_email', 'crm_marketing_campaign_recipients', ['email'])
    
    # Campaign Events
    op.create_table(
        'crm_marketing_campaign_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('recipient_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('event_type', postgresql.ENUM('sent', 'delivered', 'opened', 'clicked', 'bounced', 'converted', name='crm_marketing_campaign_event_type'), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.ForeignKeyConstraint(['campaign_id'], ['crm_marketing_campaigns.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['recipient_id'], ['crm_marketing_campaign_recipients.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_crm_marketing_campaign_events_campaign_id', 'crm_marketing_campaign_events', ['campaign_id'])
    op.create_index('ix_crm_marketing_campaign_events_recipient_id', 'crm_marketing_campaign_events', ['recipient_id'])
    op.create_index('ix_crm_marketing_campaign_events_timestamp', 'crm_marketing_campaign_events', ['timestamp'])
    
    # Campaign Performance
    op.create_table(
        'crm_marketing_campaign_performance',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('sent_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('delivered_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('open_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('click_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('conversion_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('open_rate', sa.Numeric(5, 2), nullable=True),
        sa.Column('click_rate', sa.Numeric(5, 2), nullable=True),
        sa.Column('conversion_rate', sa.Numeric(5, 2), nullable=True),
        sa.Column('revenue', sa.Numeric(12, 2), nullable=True),
        sa.Column('roi', sa.Numeric(5, 2), nullable=True),
        sa.ForeignKeyConstraint(['campaign_id'], ['crm_marketing_campaigns.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_crm_marketing_campaign_performance_campaign_id', 'crm_marketing_campaign_performance', ['campaign_id'])
    op.create_index('ix_crm_marketing_campaign_performance_date', 'crm_marketing_campaign_performance', ['date'])
    
    # Campaign AB Tests
    op.create_table(
        'crm_marketing_campaign_ab_tests',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('variant_name', sa.String(10), nullable=False),
        sa.Column('subject', sa.String(500), nullable=True),
        sa.Column('body_template', sa.Text(), nullable=True),
        sa.Column('recipient_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('open_rate', sa.Numeric(5, 2), nullable=True),
        sa.Column('click_rate', sa.Numeric(5, 2), nullable=True),
        sa.Column('conversion_rate', sa.Numeric(5, 2), nullable=True),
        sa.ForeignKeyConstraint(['campaign_id'], ['crm_marketing_campaigns.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_crm_marketing_campaign_ab_tests_campaign_id', 'crm_marketing_campaign_ab_tests', ['campaign_id'])


def downgrade() -> None:
    op.drop_table('crm_marketing_campaign_ab_tests')
    op.drop_table('crm_marketing_campaign_performance')
    op.drop_table('crm_marketing_campaign_events')
    op.drop_table('crm_marketing_campaign_recipients')
    op.drop_table('crm_marketing_campaign_variants')
    op.drop_table('crm_marketing_campaigns')
    op.drop_table('crm_marketing_campaign_templates')
    
    op.execute("DROP TYPE IF EXISTS crm_marketing_campaign_event_type")
    op.execute("DROP TYPE IF EXISTS crm_marketing_recipient_status")
    op.execute("DROP TYPE IF EXISTS crm_marketing_campaign_status")
    op.execute("DROP TYPE IF EXISTS crm_marketing_campaign_type")

