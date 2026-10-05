"""Revision-safe feeding reports (FEED-REP-039).

Revision ID: feed_reports_20260716
Revises: feed_perf_mlp_20260716
"""

from alembic import op

revision = "feed_reports_20260716"
down_revision = "feed_perf_mlp_20260716"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.feeding_reports (
      id VARCHAR PRIMARY KEY,
      tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      report_type VARCHAR(40) NOT NULL CHECK (report_type IN ('feeding_plan')),
      profile VARCHAR(16) NOT NULL CHECK (profile IN ('farmer','advisor','feeder')),
      source_ref VARCHAR(80) NOT NULL,
      content JSONB NOT NULL,
      content_hash VARCHAR(64) NOT NULL,
      dms_document_ref VARCHAR(200),
      created_by VARCHAR(160) NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      CONSTRAINT uq_feeding_report_identity
        UNIQUE (tenant_id, report_type, source_ref, profile, content_hash)
    )""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_feeding_reports_source
      ON domain_agrar.feeding_reports (tenant_id, source_ref, created_at DESC)""")
    op.execute("""CREATE OR REPLACE FUNCTION domain_agrar.guard_immutable_feeding_report()
      RETURNS trigger LANGUAGE plpgsql AS $$
      BEGIN
        RAISE EXCEPTION 'feeding_reports are append-only';
      END;
      $$""")
    op.execute("DROP TRIGGER IF EXISTS trg_immutable_feeding_report ON domain_agrar.feeding_reports")
    op.execute("""CREATE TRIGGER trg_immutable_feeding_report
      BEFORE UPDATE OR DELETE ON domain_agrar.feeding_reports
      FOR EACH ROW EXECUTE FUNCTION domain_agrar.guard_immutable_feeding_report()""")


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_immutable_feeding_report ON domain_agrar.feeding_reports")
    op.execute("DROP FUNCTION IF EXISTS domain_agrar.guard_immutable_feeding_report()")
    op.execute("DROP INDEX IF EXISTS domain_agrar.ix_feeding_reports_source")
    op.execute("DROP TABLE IF EXISTS domain_agrar.feeding_reports")
