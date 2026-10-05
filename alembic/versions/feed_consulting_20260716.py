"""Consulting cases and observations (FEED-CONS-031).

Revision ID: feed_consulting_20260716
Revises: feed_actual_measures_20260716
"""

from alembic import op

revision = "feed_consulting_20260716"
down_revision = "feed_actual_measures_20260716"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.consulting_cases (
      id VARCHAR PRIMARY KEY,
      tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      business_id VARCHAR REFERENCES domain_agrar.feeding_businesses(id),
      group_id VARCHAR REFERENCES domain_agrar.feeding_groups(id),
      case_type VARCHAR(16) NOT NULL CHECK (case_type IN ('visit','remote')),
      title VARCHAR(240) NOT NULL,
      initial_situation TEXT,
      status VARCHAR(16) NOT NULL DEFAULT 'open' CHECK (status IN ('open','closed')),
      closing_summary TEXT,
      closed_by VARCHAR(160), closed_at TIMESTAMPTZ,
      created_by VARCHAR(160) NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
    )""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_consulting_cases_tenant
      ON domain_agrar.consulting_cases (tenant_id, status, created_at DESC)""")

    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.consulting_observations (
      id VARCHAR PRIMARY KEY,
      tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      case_id VARCHAR NOT NULL REFERENCES domain_agrar.consulting_cases(id),
      category VARCHAR(60) NOT NULL,
      text TEXT NOT NULL,
      photo_document_refs JSONB NOT NULL DEFAULT '[]'::jsonb,
      ration_id VARCHAR REFERENCES domain_agrar.rations(id),
      analysis_ref VARCHAR(80),
      observation_date DATE,
      client_ref VARCHAR(120) NOT NULL,
      created_by VARCHAR(160) NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      CONSTRAINT uq_consulting_observation_client UNIQUE (tenant_id, case_id, client_ref)
    )""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_consulting_observations_case
      ON domain_agrar.consulting_observations (tenant_id, case_id, created_at)""")
    op.execute("""CREATE OR REPLACE FUNCTION domain_agrar.guard_immutable_consulting_observation()
      RETURNS trigger LANGUAGE plpgsql AS $$
      BEGIN
        RAISE EXCEPTION 'consulting_observations are append-only';
      END;
      $$""")
    op.execute("DROP TRIGGER IF EXISTS trg_immutable_consulting_observation ON domain_agrar.consulting_observations")
    op.execute("""CREATE TRIGGER trg_immutable_consulting_observation
      BEFORE UPDATE OR DELETE ON domain_agrar.consulting_observations
      FOR EACH ROW EXECUTE FUNCTION domain_agrar.guard_immutable_consulting_observation()""")


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_immutable_consulting_observation ON domain_agrar.consulting_observations")
    op.execute("DROP FUNCTION IF EXISTS domain_agrar.guard_immutable_consulting_observation()")
    op.execute("DROP INDEX IF EXISTS domain_agrar.ix_consulting_observations_case")
    op.execute("DROP TABLE IF EXISTS domain_agrar.consulting_observations")
    op.execute("DROP INDEX IF EXISTS domain_agrar.ix_consulting_cases_tenant")
    op.execute("DROP TABLE IF EXISTS domain_agrar.consulting_cases")
