"""Immutable feeding plan versions (FEED-PLAN-026).

Revision ID: feed_plan_versions_20260716
Revises: feed_editor_templates_20260716
"""
from alembic import op

revision = "feed_plan_versions_20260716"
down_revision = "feed_editor_templates_20260716"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.feeding_plans (
      id VARCHAR PRIMARY KEY, tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      group_id VARCHAR NOT NULL REFERENCES domain_agrar.feeding_groups(id), name VARCHAR(240) NOT NULL,
      created_by VARCHAR(160) NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      UNIQUE (tenant_id, group_id)
    )""")
    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.feeding_plan_versions (
      id VARCHAR PRIMARY KEY, tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      plan_id VARCHAR NOT NULL REFERENCES domain_agrar.feeding_plans(id), version_no INTEGER NOT NULL CHECK (version_no>0),
      source_ration_version_id VARCHAR NOT NULL REFERENCES domain_agrar.ration_versions(id),
      animal_count INTEGER NOT NULL CHECK (animal_count>0), dosing_step_kg NUMERIC(16,6) NOT NULL CHECK (dosing_step_kg>0),
      rounding_mode VARCHAR(12) NOT NULL CHECK (rounding_mode IN ('nearest','up','down')),
      valid_from DATE NOT NULL, valid_until DATE, reason VARCHAR(2000) NOT NULL,
      idempotency_key VARCHAR(160) NOT NULL, request_hash VARCHAR(64) NOT NULL,
      published_by VARCHAR(160) NOT NULL, published_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      UNIQUE (tenant_id, plan_id, version_no), UNIQUE (tenant_id, idempotency_key),
      CHECK (valid_until IS NULL OR valid_until >= valid_from)
    )""")
    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.feeding_mixing_instructions (
      id VARCHAR PRIMARY KEY, tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      plan_version_id VARCHAR NOT NULL REFERENCES domain_agrar.feeding_plan_versions(id),
      sequence INTEGER NOT NULL CHECK (sequence>0), feed_id VARCHAR NOT NULL, feed_name VARCHAR(240),
      kg_fm_per_animal NUMERIC(16,6), raw_batch_kg NUMERIC(16,6), target_batch_kg NUMERIC(16,6),
      rounding_delta_kg NUMERIC(16,6), UNIQUE (tenant_id, plan_version_id, sequence)
    )""")
    op.execute("CREATE INDEX IF NOT EXISTS ix_feeding_plan_versions_source ON domain_agrar.feeding_plan_versions (tenant_id,source_ration_version_id)")
    op.execute("""CREATE OR REPLACE FUNCTION domain_agrar.guard_immutable_feeding_plan_version()
      RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'feeding plan versions are immutable'; END; $$""")
    for table in ("feeding_plan_versions", "feeding_mixing_instructions"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_immutable_{table} ON domain_agrar.{table}")
        op.execute(f"CREATE TRIGGER trg_immutable_{table} BEFORE UPDATE OR DELETE ON domain_agrar.{table} FOR EACH ROW EXECUTE FUNCTION domain_agrar.guard_immutable_feeding_plan_version()")


def downgrade() -> None:
    for table in ("feeding_mixing_instructions", "feeding_plan_versions"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_immutable_{table} ON domain_agrar.{table}")
    op.execute("DROP FUNCTION IF EXISTS domain_agrar.guard_immutable_feeding_plan_version()")
    op.execute("DROP TABLE IF EXISTS domain_agrar.feeding_mixing_instructions")
    op.execute("DROP TABLE IF EXISTS domain_agrar.feeding_plan_versions")
    op.execute("DROP TABLE IF EXISTS domain_agrar.feeding_plans")
