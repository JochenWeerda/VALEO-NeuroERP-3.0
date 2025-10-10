"""add workflow tables

Revision ID: 002
Revises: 001
Create Date: 2025-10-09

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # workflow_status
    op.create_table(
        'workflow_status',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('domain', sa.String(length=50), nullable=False),
        sa.Column('doc_number', sa.String(length=50), nullable=False),
        sa.Column('state', sa.String(length=20), nullable=False, server_default='draft'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_by', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('domain', 'doc_number', name='uq_workflow_domain_number')
    )
    op.create_index('ix_workflow_domain_number', 'workflow_status', ['domain', 'doc_number'])

    # workflow_audit
    op.create_table(
        'workflow_audit',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('domain', sa.String(length=50), nullable=False),
        sa.Column('doc_number', sa.String(length=50), nullable=False),
        sa.Column('ts', sa.Integer(), nullable=False),
        sa.Column('from_state', sa.String(length=20), nullable=False),
        sa.Column('to_state', sa.String(length=20), nullable=False),
        sa.Column('action', sa.String(length=20), nullable=False),
        sa.Column('user', sa.String(length=100), nullable=True),
        sa.Column('reason', sa.String(length=500), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_workflow_audit_doc', 'workflow_audit', ['domain', 'doc_number'])
    op.create_index('ix_workflow_audit_ts', 'workflow_audit', ['ts'])


def downgrade() -> None:
    op.drop_index('ix_workflow_audit_ts', table_name='workflow_audit')
    op.drop_index('ix_workflow_audit_doc', table_name='workflow_audit')
    op.drop_table('workflow_audit')
    op.drop_index('ix_workflow_domain_number', table_name='workflow_status')
    op.drop_table('workflow_status')

