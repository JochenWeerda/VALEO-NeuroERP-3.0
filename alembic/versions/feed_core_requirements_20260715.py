"""Evaluation systems, requirement profiles and optimization runs (FEED-CORE-020).

Revision ID: feed_core_requirements_20260715
Revises: feed_core_feed_analyses_20260715
"""

from alembic import op

revision = "feed_core_requirements_20260715"
down_revision = "feed_core_feed_analyses_20260715"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Globale Referenzdaten (wie DLG-Tabellen): Registrierung der Normsysteme;
    # die Formeln selbst bleiben versionierter Code (module_ref).
    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.evaluation_systems (
      id VARCHAR(40) PRIMARY KEY,
      name VARCHAR(160) NOT NULL,
      description TEXT,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    )""")

    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.evaluation_system_versions (
      id VARCHAR PRIMARY KEY,
      system_id VARCHAR(40) NOT NULL REFERENCES domain_agrar.evaluation_systems(id),
      version_label VARCHAR(40) NOT NULL,
      module_ref VARCHAR(240) NOT NULL,
      is_current BOOLEAN NOT NULL DEFAULT FALSE,
      valid_from TIMESTAMPTZ NOT NULL DEFAULT now(),
      created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      CONSTRAINT uq_eval_system_version UNIQUE (system_id, version_label)
    )""")
    op.execute("""CREATE UNIQUE INDEX IF NOT EXISTS uq_eval_system_current
      ON domain_agrar.evaluation_system_versions (system_id) WHERE is_current""")

    # Append-only Bedarfsprofile je Fuetterungsgruppe (kein Update-/Delete-Pfad).
    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.requirement_profiles (
      id VARCHAR PRIMARY KEY,
      tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      group_id VARCHAR NOT NULL REFERENCES domain_agrar.feeding_groups(id),
      system_version_id VARCHAR NOT NULL REFERENCES domain_agrar.evaluation_system_versions(id),
      inputs JSONB NOT NULL,
      estimated_inputs JSONB NOT NULL DEFAULT '[]'::jsonb,
      requirements JSONB NOT NULL,
      created_by VARCHAR(160) NOT NULL,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    )""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_requirement_profiles_group
      ON domain_agrar.requirement_profiles (tenant_id, group_id, created_at DESC)""")
    op.execute("""CREATE OR REPLACE FUNCTION domain_agrar.guard_immutable_requirement_profile()
      RETURNS trigger LANGUAGE plpgsql AS $$
      BEGIN
        RAISE EXCEPTION 'requirement_profiles are append-only; create a new profile';
      END;
      $$""")
    op.execute("DROP TRIGGER IF EXISTS trg_immutable_requirement_profile ON domain_agrar.requirement_profiles")
    op.execute("""CREATE TRIGGER trg_immutable_requirement_profile
      BEFORE UPDATE OR DELETE ON domain_agrar.requirement_profiles
      FOR EACH ROW EXECUTE FUNCTION domain_agrar.guard_immutable_requirement_profile()""")

    # Reproduzierbare Solverlauf-Dokumentation mit Pflichtbezug auf eine Version.
    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.optimization_runs (
      id VARCHAR PRIMARY KEY,
      tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      ration_id VARCHAR NOT NULL REFERENCES domain_agrar.rations(id),
      ration_version_id VARCHAR NOT NULL REFERENCES domain_agrar.ration_versions(id),
      solver_version VARCHAR(80) NOT NULL,
      objective VARCHAR(60) NOT NULL,
      status VARCHAR(24) NOT NULL
        CHECK (status IN ('optimal','infeasible','unbounded','error','timeout')),
      duration_ms INTEGER,
      parameters JSONB NOT NULL DEFAULT '{}'::jsonb,
      created_by VARCHAR(160) NOT NULL,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    )""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_optimization_runs_ration
      ON domain_agrar.optimization_runs (tenant_id, ration_id, created_at DESC)""")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS domain_agrar.ix_optimization_runs_ration")
    op.execute("DROP TABLE IF EXISTS domain_agrar.optimization_runs")
    op.execute("DROP TRIGGER IF EXISTS trg_immutable_requirement_profile ON domain_agrar.requirement_profiles")
    op.execute("DROP FUNCTION IF EXISTS domain_agrar.guard_immutable_requirement_profile()")
    op.execute("DROP INDEX IF EXISTS domain_agrar.ix_requirement_profiles_group")
    op.execute("DROP TABLE IF EXISTS domain_agrar.requirement_profiles")
    op.execute("DROP INDEX IF EXISTS domain_agrar.uq_eval_system_current")
    op.execute("DROP TABLE IF EXISTS domain_agrar.evaluation_system_versions")
    op.execute("DROP TABLE IF EXISTS domain_agrar.evaluation_systems")
