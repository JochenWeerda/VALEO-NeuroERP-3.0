"""Feeding import jobs for the integration monitor (FEED-INT-034).

Revision ID: feed_import_jobs_20260716
Revises: feed_consulting_20260716
"""

from alembic import op

revision = "feed_import_jobs_20260716"
down_revision = "feed_consulting_20260716"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.feeding_import_jobs (
      id VARCHAR PRIMARY KEY,
      tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      adapter VARCHAR(40) NOT NULL,
      payload JSONB NOT NULL,
      payload_hash VARCHAR(64) NOT NULL,
      status VARCHAR(16) NOT NULL DEFAULT 'validated'
        CHECK (status IN ('validated','quarantined','accepted','rejected')),
      findings JSONB NOT NULL DEFAULT '[]'::jsonb,
      mapped_excerpt JSONB NOT NULL DEFAULT '{}'::jsonb,
      result_ref VARCHAR(80),
      decision_reason TEXT,
      decided_by VARCHAR(160), decided_at TIMESTAMPTZ,
      created_by VARCHAR(160) NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    )""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_feeding_import_jobs_tenant
      ON domain_agrar.feeding_import_jobs (tenant_id, status, created_at DESC)""")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS domain_agrar.ix_feeding_import_jobs_tenant")
    op.execute("DROP TABLE IF EXISTS domain_agrar.feeding_import_jobs")
