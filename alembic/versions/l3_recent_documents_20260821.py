"""Personal authorized recent-document projection.

Revision ID: l3_recent_documents_20260821
Revises: l3_report_catalog_20260821
"""

from alembic import op

revision = "l3_recent_documents_20260821"
down_revision = "l3_report_catalog_20260821"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
      CREATE SCHEMA IF NOT EXISTS domain_ops;
      CREATE TABLE IF NOT EXISTS domain_ops.recent_documents (
        id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, user_id TEXT NOT NULL,
        screen_id TEXT NOT NULL, document_id TEXT NOT NULL,
        document_type TEXT NOT NULL, document_number TEXT NOT NULL,
        partner_id TEXT, partner_name TEXT, title TEXT NOT NULL,
        route TEXT NOT NULL, required_role TEXT NOT NULL,
        opened_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        expires_at TIMESTAMPTZ NOT NULL,
        UNIQUE (tenant_id,user_id,screen_id,document_id)
      );
      CREATE INDEX IF NOT EXISTS ix_recent_documents_personal
        ON domain_ops.recent_documents (tenant_id,user_id,opened_at DESC);
      CREATE INDEX IF NOT EXISTS ix_recent_documents_expiry
        ON domain_ops.recent_documents (expires_at);
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_ops.recent_documents;")
