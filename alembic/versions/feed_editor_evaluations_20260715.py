"""Persisted ration version evaluations (FEED-EDITOR-022).

Revision ID: feed_editor_evaluations_20260715
Revises: feed_core_requirements_20260715
"""

from alembic import op

revision = "feed_editor_evaluations_20260715"
down_revision = "feed_core_requirements_20260715"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Append-only Bewertungshistorie je unveraenderlicher Rationsversion.
    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.ration_evaluations (
      id VARCHAR PRIMARY KEY,
      tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      ration_id VARCHAR NOT NULL REFERENCES domain_agrar.rations(id),
      ration_version_id VARCHAR NOT NULL REFERENCES domain_agrar.ration_versions(id),
      requirement_profile_id VARCHAR NOT NULL REFERENCES domain_agrar.requirement_profiles(id),
      totals JSONB NOT NULL,
      deltas JSONB NOT NULL DEFAULT '[]'::jsonb,
      findings JSONB NOT NULL DEFAULT '[]'::jsonb,
      coverage JSONB NOT NULL DEFAULT '{}'::jsonb,
      evaluated_by VARCHAR(160) NOT NULL,
      evaluated_at TIMESTAMPTZ NOT NULL DEFAULT now()
    )""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_ration_evaluations_version
      ON domain_agrar.ration_evaluations (tenant_id, ration_version_id, evaluated_at DESC)""")
    op.execute("""CREATE OR REPLACE FUNCTION domain_agrar.guard_immutable_ration_evaluation()
      RETURNS trigger LANGUAGE plpgsql AS $$
      BEGIN
        RAISE EXCEPTION 'ration_evaluations are append-only; evaluate again instead';
      END;
      $$""")
    op.execute("DROP TRIGGER IF EXISTS trg_immutable_ration_evaluation ON domain_agrar.ration_evaluations")
    op.execute("""CREATE TRIGGER trg_immutable_ration_evaluation
      BEFORE UPDATE OR DELETE ON domain_agrar.ration_evaluations
      FOR EACH ROW EXECUTE FUNCTION domain_agrar.guard_immutable_ration_evaluation()""")


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_immutable_ration_evaluation ON domain_agrar.ration_evaluations")
    op.execute("DROP FUNCTION IF EXISTS domain_agrar.guard_immutable_ration_evaluation()")
    op.execute("DROP INDEX IF EXISTS domain_agrar.ix_ration_evaluations_version")
    op.execute("DROP TABLE IF EXISTS domain_agrar.ration_evaluations")
