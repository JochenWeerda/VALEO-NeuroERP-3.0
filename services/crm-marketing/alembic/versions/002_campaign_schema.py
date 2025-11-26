"""Campaign schema

Revision ID: 002_campaign
Revises: 001_initial_segment
Create Date: 2025-01-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002_campaign'
down_revision: Union[str, None] = '001_initial_segment'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create campaign_templates table
    op.create_table(
        'crm_marketing_campaign_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', sa.String(64), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.Enum('email', 'sms', 'push', 'other', name='campaigntype'), nullable=False),
        sa.Column('subject_template', sa.String(500), nullable=True),
        sa.Column('body_template', sa.Text(), nullable=False),
        sa.Column('variables', postgresql.JSONB(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('created_by', sa.String(255), nullable=True),
        sa.Column('updated_by', sa.String(255), nullable=True),
    )
    op.create_index('ix_crm_marketing_campaign_templates_tenant_id', 'crm_marketing_campaign_templates', ['tenant_id'])

    # Create campaigns table
    op.create_table(
        'crm_marketing_campaigns',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', sa.String(64), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.Enum('email', 'sms', 'push', 'other', name='campaigntype'), nullable=False),
        sa.Column('status', sa.Enum('draft', 'scheduled', 'running', 'paused', 'completed', 'cancelled', name='campaignstatus'), nullable=False),
        sa.Column('segment_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sender_name', sa.String(255), nullable=True),
        sa.Column('sender_email', sa.String(255), nullable=True),
        sa.Column('subject', sa.String(500), nullable=True),
        sa.Column('settings', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('created_by', sa.String(255), nullable=True),
        sa.Column('updated_by', sa.String(255), nullable=True),
        sa.ForeignKeyConstraint(['segment_id'], ['crm_marketing_segments.id']),
        sa.ForeignKeyConstraint(['template_id'], ['crm_marketing_campaign_templates.id']),
    )
    op.create_index('ix_crm_marketing_campaigns_tenant_id', 'crm_marketing_campaigns', ['tenant_id'])
    op.create_index('ix_crm_marketing_campaigns_segment_id', 'crm_marketing_campaigns', ['segment_id'])
    op.create_index('ix_crm_marketing_campaigns_template_id', 'crm_marketing_campaigns', ['template_id'])

    # Create campaign_recipients table
    op.create_table(
        'crm_marketing_campaign_recipients',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('contact_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('status', sa.Enum('pending', 'sent', 'delivered', 'bounced', 'failed', name='recipientstatus'), nullable=False, server_default='pending'),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('bounce_reason', sa.Text(), nullable=True),
        sa.Column('variant', sa.String(10), nullable=True),
        sa.ForeignKeyConstraint(['campaign_id'], ['crm_marketing_campaigns.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_crm_marketing_campaign_recipients_campaign_id', 'crm_marketing_campaign_recipients', ['campaign_id'])
    op.create_index('ix_crm_marketing_campaign_recipients_contact_id', 'crm_marketing_campaign_recipients', ['contact_id'])
    op.create_index('ix_crm_marketing_campaign_recipients_email', 'crm_marketing_campaign_recipients', ['email'])

    # Create campaign_events table
    op.create_table(
        'crm_marketing_campaign_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('recipient_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('event_type', sa.Enum('sent', 'delivered', 'opened', 'clicked', 'converted', 'bounced', 'unsubscribed', name='campaigneventtype'), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('details', postgresql.JSONB(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.ForeignKeyConstraint(['campaign_id'], ['crm_marketing_campaigns.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['recipient_id'], ['crm_marketing_campaign_recipients.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_crm_marketing_campaign_events_campaign_id', 'crm_marketing_campaign_events', ['campaign_id'])
    op.create_index('ix_crm_marketing_campaign_events_recipient_id', 'crm_marketing_campaign_events', ['recipient_id'])
    op.create_index('ix_crm_marketing_campaign_events_timestamp', 'crm_marketing_campaign_events', ['timestamp'])

    # Create campaign_ab_tests table
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
    op.drop_index('ix_crm_marketing_campaign_ab_tests_campaign_id', table_name='crm_marketing_campaign_ab_tests')
    op.drop_table('crm_marketing_campaign_ab_tests')
    
    op.drop_index('ix_crm_marketing_campaign_events_timestamp', table_name='crm_marketing_campaign_events')
    op.drop_index('ix_crm_marketing_campaign_events_recipient_id', table_name='crm_marketing_campaign_events')
    op.drop_index('ix_crm_marketing_campaign_events_campaign_id', table_name='crm_marketing_campaign_events')
    op.drop_table('crm_marketing_campaign_events')
    
    op.drop_index('ix_crm_marketing_campaign_recipients_email', table_name='crm_marketing_campaign_recipients')
    op.drop_index('ix_crm_marketing_campaign_recipients_contact_id', table_name='crm_marketing_campaign_recipients')
    op.drop_index('ix_crm_marketing_campaign_recipients_campaign_id', table_name='crm_marketing_campaign_recipients')
    op.drop_table('crm_marketing_campaign_recipients')
    
    op.drop_index('ix_crm_marketing_campaigns_template_id', table_name='crm_marketing_campaigns')
    op.drop_index('ix_crm_marketing_campaigns_segment_id', table_name='crm_marketing_campaigns')
    op.drop_index('ix_crm_marketing_campaigns_tenant_id', table_name='crm_marketing_campaigns')
    op.drop_table('crm_marketing_campaigns')
    
    op.drop_index('ix_crm_marketing_campaign_templates_tenant_id', table_name='crm_marketing_campaign_templates')
    op.drop_table('crm_marketing_campaign_templates')
    
    # Drop enums
    sa.Enum(name='campaigntype').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='campaignstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='recipientstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='campaigneventtype').drop(op.get_bind(), checkfirst=True)

