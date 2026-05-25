"""gdpr_requests_table

Revision ID: c137c1d3ba3a
Revises: 4e8447ad429a
Create Date: 2026-05-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'c137c1d3ba3a'
down_revision: Union[str, None] = '4e8447ad429a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'gdpr_requests',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), nullable=False),
        sa.Column('subject_id', sa.String(36), nullable=False),
        sa.Column('subject_email', sa.String(255), nullable=False),
        sa.Column('request_type', sa.String(40), nullable=False),
        sa.Column('status', sa.String(40), nullable=False, server_default='PENDING'),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('rejection_reason', sa.Text, nullable=True),
        sa.Column('export_payload', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.String(36), nullable=True),
    )
    op.create_index('ix_gdpr_requests_tenant_id', 'gdpr_requests', ['tenant_id'])

    op.create_table(
        'gdpr_request_history',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('request_id', sa.String(36), nullable=False),
        sa.Column('tenant_id', sa.String(36), nullable=False),
        sa.Column('old_status', sa.String(40), nullable=True),
        sa.Column('new_status', sa.String(40), nullable=False),
        sa.Column('changed_by', sa.String(36), nullable=True),
        sa.Column('note', sa.Text, nullable=True),
        sa.Column('changed_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_gdpr_request_history_request_id', 'gdpr_request_history', ['request_id'])
    op.create_index('ix_gdpr_request_history_tenant_id', 'gdpr_request_history', ['tenant_id'])


def downgrade() -> None:
    op.drop_index('ix_gdpr_request_history_tenant_id', table_name='gdpr_request_history')
    op.drop_index('ix_gdpr_request_history_request_id', table_name='gdpr_request_history')
    op.drop_table('gdpr_request_history')
    op.drop_index('ix_gdpr_requests_tenant_id', table_name='gdpr_requests')
    op.drop_table('gdpr_requests')
