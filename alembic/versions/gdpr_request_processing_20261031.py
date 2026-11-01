"""Explicit CRM subject type and processing receipts; no guessed legacy identity."""
from alembic import op
import sqlalchemy as sa

revision = 'gdpr_request_process_20261031'
down_revision = 'sales_offer_number_tenant_20261031'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('gdpr_requests', sa.Column('data_scope', sa.String(32), nullable=True))
    op.add_column('gdpr_requests', sa.Column('subject_type', sa.String(20), nullable=True))
    op.add_column('gdpr_requests', sa.Column('version', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('gdpr_requests', sa.Column('creation_key', sa.String(128), nullable=True))
    op.add_column('gdpr_requests', sa.Column('creation_digest', sa.String(64), nullable=True))
    op.add_column('gdpr_requests', sa.Column('processing_result', sa.Text(), nullable=True))
    op.create_unique_constraint('uq_gdpr_request_creation_key', 'gdpr_requests', ['tenant_id', 'creation_key'])
    op.create_check_constraint('ck_gdpr_request_subject_type', 'gdpr_requests', "subject_type IS NULL OR subject_type IN ('CUSTOMER','LEAD')")


def downgrade():
    raise RuntimeError('Processing receipts and explicit subject identity must not be removed automatically')
