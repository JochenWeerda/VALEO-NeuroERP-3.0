"""Initial GDPR schema

Revision ID: 001_initial_gdpr
Revises: 
Create Date: 2025-01-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_gdpr'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create gdpr_requests table
    op.create_table(
        'crm_gdpr_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', sa.String(64), nullable=False),
        sa.Column('request_type', sa.String(20), nullable=False),  # access, deletion, portability, objection
        sa.Column('contact_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),  # pending, in_progress, completed, rejected, cancelled
        sa.Column('requested_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rejected_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('requested_by', sa.String(255), nullable=False),
        sa.Column('is_self_request', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('verification_method', sa.String(20), nullable=True),  # email, id_card, manual, other
        sa.Column('verification_token', postgresql.UUID(as_uuid=True), nullable=True, unique=True),
        sa.Column('response_data', postgresql.JSONB, nullable=True),
        sa.Column('response_file_path', sa.String(512), nullable=True),
        sa.Column('response_file_format', sa.String(10), nullable=True),  # json, csv, pdf
        sa.Column('rejection_reason', sa.Text, nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('created_by', sa.String(255), nullable=True),
        sa.Column('updated_by', sa.String(255), nullable=True),
    )
    
    # Create indexes
    op.create_index('idx_gdpr_request_tenant_id', 'crm_gdpr_requests', ['tenant_id'])
    op.create_index('idx_gdpr_request_contact_id', 'crm_gdpr_requests', ['contact_id'])
    op.create_index('idx_gdpr_request_status', 'crm_gdpr_requests', ['status'])
    op.create_index('idx_gdpr_request_type', 'crm_gdpr_requests', ['request_type'])
    op.create_index('idx_gdpr_request_verification_token', 'crm_gdpr_requests', ['verification_token'], unique=True)
    
    # Create gdpr_request_history table
    op.create_table(
        'crm_gdpr_request_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('request_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action', sa.String(20), nullable=False),  # created, status_changed, verified, data_exported, data_deleted, rejected, cancelled
        sa.Column('old_status', sa.String(20), nullable=True),
        sa.Column('new_status', sa.String(20), nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('changed_by', sa.String(255), nullable=False),
        sa.Column('changed_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['request_id'], ['crm_gdpr_requests.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for history
    op.create_index('idx_gdpr_request_history_request_id', 'crm_gdpr_request_history', ['request_id'])
    op.create_index('idx_gdpr_request_history_changed_at', 'crm_gdpr_request_history', ['changed_at'])


def downgrade() -> None:
    op.drop_table('crm_gdpr_request_history')
    op.drop_table('crm_gdpr_requests')

