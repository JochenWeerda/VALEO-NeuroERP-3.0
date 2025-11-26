"""Initial consent schema

Revision ID: 001_initial_consent
Revises: 
Create Date: 2025-01-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_consent'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create consent_consents table
    op.create_table(
        'crm_consent_consents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', sa.String(64), nullable=False),
        sa.Column('contact_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('channel', sa.String(20), nullable=False),  # email, sms, phone, postal
        sa.Column('consent_type', sa.String(20), nullable=False),  # marketing, service, required
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),  # pending, granted, denied, revoked
        sa.Column('granted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('denied_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('double_opt_in_token', postgresql.UUID(as_uuid=True), nullable=True, unique=True),
        sa.Column('double_opt_in_confirmed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('source', sa.String(20), nullable=False, server_default='manual'),  # web_form, api, import, manual
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text, nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('created_by', sa.String(255), nullable=True),
        sa.Column('updated_by', sa.String(255), nullable=True),
    )
    
    # Create indexes
    op.create_index('idx_consent_tenant_id', 'crm_consent_consents', ['tenant_id'])
    op.create_index('idx_consent_contact_id', 'crm_consent_consents', ['contact_id'])
    op.create_index('idx_consent_double_opt_in_token', 'crm_consent_consents', ['double_opt_in_token'], unique=True)
    op.create_index('idx_consent_status', 'crm_consent_consents', ['status'])
    op.create_index('idx_consent_channel', 'crm_consent_consents', ['channel'])
    
    # Create consent_history table
    op.create_table(
        'crm_consent_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('consent_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action', sa.String(20), nullable=False),  # granted, denied, revoked, updated
        sa.Column('old_status', sa.String(20), nullable=True),
        sa.Column('new_status', sa.String(20), nullable=False),
        sa.Column('reason', sa.Text, nullable=True),
        sa.Column('changed_by', sa.String(255), nullable=False),
        sa.Column('changed_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text, nullable=True),
        sa.ForeignKeyConstraint(['consent_id'], ['crm_consent_consents.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for history
    op.create_index('idx_consent_history_consent_id', 'crm_consent_history', ['consent_id'])
    op.create_index('idx_consent_history_changed_at', 'crm_consent_history', ['changed_at'])


def downgrade() -> None:
    op.drop_table('crm_consent_history')
    op.drop_table('crm_consent_consents')

