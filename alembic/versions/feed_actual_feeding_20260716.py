"""Component actual feeding records (FEED-ACT-029).

Revision ID: feed_actual_feeding_20260716
Revises: feed_supply_handoffs_20260716
"""
from alembic import op

revision = "feed_actual_feeding_20260716"
down_revision = "feed_supply_handoffs_20260716"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.feeding_actual_records (
      id VARCHAR PRIMARY KEY,
      tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      plan_version_id VARCHAR NOT NULL REFERENCES domain_agrar.feeding_plan_versions(id),
      group_id VARCHAR NOT NULL REFERENCES domain_agrar.feeding_groups(id),
      feeding_at TIMESTAMPTZ NOT NULL,
      source VARCHAR(30) NOT NULL CHECK (source IN ('manual','mixing_wagon','import')),
      source_ref VARCHAR(200) NOT NULL,
      cause_class VARCHAR(40) NOT NULL CHECK (cause_class IN
        ('normal','stock_substitution','dosing_error','feed_quality','animal_intake','technical','other')),
      comment VARCHAR(2000),
      context JSONB NOT NULL DEFAULT '{}'::jsonb,
      supersedes_id VARCHAR REFERENCES domain_agrar.feeding_actual_records(id),
      idempotency_key VARCHAR(160) NOT NULL,
      request_hash VARCHAR(64) NOT NULL,
      recorded_by VARCHAR(160) NOT NULL,
      recorded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      UNIQUE (tenant_id,idempotency_key)
    )""")
    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.feeding_actual_components (
      id VARCHAR PRIMARY KEY,
      tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      actual_record_id VARCHAR NOT NULL REFERENCES domain_agrar.feeding_actual_records(id),
      instruction_id VARCHAR NOT NULL REFERENCES domain_agrar.feeding_mixing_instructions(id),
      feed_id VARCHAR NOT NULL,
      feed_name VARCHAR,
      target_kg NUMERIC(18,6) NOT NULL,
      actual_kg NUMERIC(18,6) NOT NULL,
      delta_kg NUMERIC(18,6) NOT NULL,
      delta_pct NUMERIC(18,6),
      value_consequences JSONB NOT NULL,
      UNIQUE (actual_record_id,instruction_id)
    )""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_feeding_actual_plan_time
      ON domain_agrar.feeding_actual_records (tenant_id,plan_version_id,feeding_at DESC)""")
    op.execute("""CREATE OR REPLACE FUNCTION domain_agrar.guard_immutable_feeding_actual()
      RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'feeding actual records are append-only'; END; $$""")
    for table_name in ("feeding_actual_records", "feeding_actual_components"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_immutable_{table_name} ON domain_agrar.{table_name}")  # noqa: S608
        op.execute(f"""CREATE TRIGGER trg_immutable_{table_name} BEFORE UPDATE OR DELETE
          ON domain_agrar.{table_name} FOR EACH ROW
          EXECUTE FUNCTION domain_agrar.guard_immutable_feeding_actual()""")  # noqa: S608


def downgrade() -> None:
    for table_name in ("feeding_actual_components", "feeding_actual_records"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_immutable_{table_name} ON domain_agrar.{table_name}")  # noqa: S608
    op.execute("DROP FUNCTION IF EXISTS domain_agrar.guard_immutable_feeding_actual()")
    op.execute("DROP TABLE IF EXISTS domain_agrar.feeding_actual_components")
    op.execute("DROP TABLE IF EXISTS domain_agrar.feeding_actual_records")
