"""Safe query-center definitions and audit.

Revision ID: query_center_20260821
Revises: foreign_goods_worklist_20260821
"""

from alembic import op

revision = "query_center_20260821"
down_revision = "foreign_goods_worklist_20260821"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
      CREATE SCHEMA IF NOT EXISTS domain_reporting;
      CREATE TABLE IF NOT EXISTS domain_reporting.query_definitions (
        id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, owner_id TEXT NOT NULL,
        name TEXT NOT NULL, data_product_id TEXT NOT NULL,
        selected_fields JSONB NOT NULL DEFAULT '[]'::jsonb,
        filter_spec JSONB NOT NULL DEFAULT '{}'::jsonb,
        aggregations JSONB NOT NULL DEFAULT '[]'::jsonb,
        is_favorite BOOLEAN NOT NULL DEFAULT FALSE,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE (tenant_id, owner_id, name)
      );
      CREATE INDEX IF NOT EXISTS ix_query_definitions_worklist
        ON domain_reporting.query_definitions (tenant_id, owner_id, is_favorite, updated_at);
      CREATE TABLE IF NOT EXISTS domain_reporting.query_center_audit (
        id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, definition_id TEXT,
        action TEXT NOT NULL, actor TEXT NOT NULL, reason TEXT NOT NULL,
        payload_hash TEXT, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
      );
      CREATE INDEX IF NOT EXISTS ix_query_center_audit
        ON domain_reporting.query_center_audit (tenant_id, definition_id, created_at);
    """)


def downgrade() -> None:
    op.execute("""
      DROP TABLE IF EXISTS domain_reporting.query_center_audit;
      DROP TABLE IF EXISTS domain_reporting.query_definitions;
    """)
