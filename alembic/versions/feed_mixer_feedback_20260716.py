"""Mixer feedback on feeding plan versions (FEED-INT-035).

Revision ID: feed_mixer_feedback_20260716
Revises: feed_import_jobs_20260716
"""

from alembic import op

revision = "feed_mixer_feedback_20260716"
down_revision = "feed_import_jobs_20260716"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.feeding_mixer_feedback (
      id VARCHAR PRIMARY KEY,
      tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      plan_version_id VARCHAR NOT NULL REFERENCES domain_agrar.feeding_plan_versions(id),
      client_ref VARCHAR(120) NOT NULL,
      lines JSONB NOT NULL,
      residual_kg NUMERIC(12,3),
      accuracy_pct NUMERIC(6,2),
      created_by VARCHAR(160) NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      CONSTRAINT uq_mixer_feedback_client UNIQUE (tenant_id, plan_version_id, client_ref)
    )""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_mixer_feedback_plan
      ON domain_agrar.feeding_mixer_feedback (tenant_id, plan_version_id, created_at DESC)""")
    op.execute("""CREATE OR REPLACE FUNCTION domain_agrar.guard_immutable_mixer_feedback()
      RETURNS trigger LANGUAGE plpgsql AS $$
      BEGIN
        RAISE EXCEPTION 'feeding_mixer_feedback is append-only';
      END;
      $$""")
    op.execute("DROP TRIGGER IF EXISTS trg_immutable_mixer_feedback ON domain_agrar.feeding_mixer_feedback")
    op.execute("""CREATE TRIGGER trg_immutable_mixer_feedback
      BEFORE UPDATE OR DELETE ON domain_agrar.feeding_mixer_feedback
      FOR EACH ROW EXECUTE FUNCTION domain_agrar.guard_immutable_mixer_feedback()""")


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_immutable_mixer_feedback ON domain_agrar.feeding_mixer_feedback")
    op.execute("DROP FUNCTION IF EXISTS domain_agrar.guard_immutable_mixer_feedback()")
    op.execute("DROP INDEX IF EXISTS domain_agrar.ix_mixer_feedback_plan")
    op.execute("DROP TABLE IF EXISTS domain_agrar.feeding_mixer_feedback")
