"""Initial segment schema

Revision ID: 001_initial_segment
Revises: 
Create Date: 2025-01-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_segment'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create segments table
    op.create_table(
        'crm_marketing_segments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', sa.String(64), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.Enum('dynamic', 'static', 'hybrid', name='segmenttype'), nullable=False),
        sa.Column('status', sa.Enum('active', 'inactive', 'archived', name='segmentstatus'), nullable=False),
        sa.Column('rules', postgresql.JSONB(), nullable=True),
        sa.Column('member_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_calculated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('created_by', sa.String(255), nullable=True),
        sa.Column('updated_by', sa.String(255), nullable=True),
    )
    op.create_index('ix_crm_marketing_segments_tenant_id', 'crm_marketing_segments', ['tenant_id'])

    # Create segment_rules table
    op.create_table(
        'crm_marketing_segment_rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('segment_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('field', sa.String(255), nullable=False),
        sa.Column('operator', sa.Enum(
            'equals', 'not_equals', 'contains', 'not_contains', 'starts_with', 'ends_with',
            'greater_than', 'less_than', 'greater_equal', 'less_equal', 'in', 'not_in',
            'is_null', 'is_not_null', 'between', name='ruleoperator'
        ), nullable=False),
        sa.Column('value', postgresql.JSONB(), nullable=False),
        sa.Column('logical_operator', sa.Enum('AND', 'OR', name='logicaloperator'), nullable=True),
        sa.Column('order', sa.Integer(), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['segment_id'], ['crm_marketing_segments.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_crm_marketing_segment_rules_segment_id', 'crm_marketing_segment_rules', ['segment_id'])

    # Create segment_members table
    op.create_table(
        'crm_marketing_segment_members',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('segment_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('contact_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('added_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('added_by', sa.String(255), nullable=True),
        sa.Column('removed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('removed_by', sa.String(255), nullable=True),
        sa.ForeignKeyConstraint(['segment_id'], ['crm_marketing_segments.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_crm_marketing_segment_members_segment_id', 'crm_marketing_segment_members', ['segment_id'])
    op.create_index('ix_crm_marketing_segment_members_contact_id', 'crm_marketing_segment_members', ['contact_id'])

    # Create segment_performance table
    op.create_table(
        'crm_marketing_segment_performance',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('segment_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('period_type', sa.String(20), nullable=False, server_default='daily'),
        sa.Column('member_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('active_members', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('campaign_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('conversion_rate', sa.Numeric(5, 2), nullable=True),
        sa.Column('revenue', sa.Numeric(12, 2), nullable=True),
        sa.ForeignKeyConstraint(['segment_id'], ['crm_marketing_segments.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_crm_marketing_segment_performance_segment_id', 'crm_marketing_segment_performance', ['segment_id'])
    op.create_index('ix_crm_marketing_segment_performance_date', 'crm_marketing_segment_performance', ['date'])


def downgrade() -> None:
    op.drop_index('ix_crm_marketing_segment_performance_date', table_name='crm_marketing_segment_performance')
    op.drop_index('ix_crm_marketing_segment_performance_segment_id', table_name='crm_marketing_segment_performance')
    op.drop_table('crm_marketing_segment_performance')
    
    op.drop_index('ix_crm_marketing_segment_members_contact_id', table_name='crm_marketing_segment_members')
    op.drop_index('ix_crm_marketing_segment_members_segment_id', table_name='crm_marketing_segment_members')
    op.drop_table('crm_marketing_segment_members')
    
    op.drop_index('ix_crm_marketing_segment_rules_segment_id', table_name='crm_marketing_segment_rules')
    op.drop_table('crm_marketing_segment_rules')
    
    op.drop_index('ix_crm_marketing_segments_tenant_id', table_name='crm_marketing_segments')
    op.drop_table('crm_marketing_segments')
    
    # Drop enums
    sa.Enum(name='segmenttype').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='segmentstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='ruleoperator').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='logicaloperator').drop(op.get_bind(), checkfirst=True)

