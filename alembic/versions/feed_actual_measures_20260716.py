"""Deviation policies, findings measures and IOFC projection (FEED-ACT-030).

Revision ID: feed_actual_measures_20260716
Revises: feed_actual_feeding_20260716
"""

from alembic import op

revision = "feed_actual_measures_20260716"
down_revision = "feed_actual_feeding_20260716"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.feeding_deviation_policies (
      id VARCHAR PRIMARY KEY, tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      feed_class VARCHAR(30) NOT NULL, version INTEGER NOT NULL CHECK (version>0),
      warning_pct NUMERIC(8,3) NOT NULL, critical_pct NUMERIC(8,3) NOT NULL,
      valid_from DATE NOT NULL, reason VARCHAR(1000) NOT NULL,
      created_by VARCHAR(160) NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      UNIQUE (tenant_id,feed_class,version),
      CHECK (warning_pct>0 AND critical_pct>warning_pct AND critical_pct<=100)
    )""")
    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.feeding_actual_measures (
      id VARCHAR PRIMARY KEY, tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      actual_record_id VARCHAR NOT NULL REFERENCES domain_agrar.feeding_actual_records(id),
      actual_component_id VARCHAR NOT NULL REFERENCES domain_agrar.feeding_actual_components(id),
      group_id VARCHAR NOT NULL REFERENCES domain_agrar.feeding_groups(id),
      finding JSONB NOT NULL, title VARCHAR(240) NOT NULL, owner_subject VARCHAR(160) NOT NULL,
      due_date DATE NOT NULL, version INTEGER NOT NULL DEFAULT 1 CHECK (version>0),
      status VARCHAR(30) NOT NULL DEFAULT 'open' CHECK (status='open'),
      reason VARCHAR(2000) NOT NULL, idempotency_key VARCHAR(160) NOT NULL,
      request_hash VARCHAR(64) NOT NULL, created_by VARCHAR(160) NOT NULL,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now(), UNIQUE (tenant_id,idempotency_key)
    )""")
    op.execute("""ALTER TABLE domain_agrar.feeding_controlling_daily
      ADD COLUMN IF NOT EXISTS feeding_plan_version_id VARCHAR REFERENCES domain_agrar.feeding_plan_versions(id),
      ADD COLUMN IF NOT EXISTS milk_price_eur_kg NUMERIC(12,6),
      ADD COLUMN IF NOT EXISTS milk_revenue_eur_cow NUMERIC(12,4),
      ADD COLUMN IF NOT EXISTS iofc_eur_cow NUMERIC(12,4)""")
    op.execute("""CREATE OR REPLACE FUNCTION domain_agrar.guard_immutable_feeding_measure_config()
      RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'feeding policy and measure records are append-only'; END; $$""")
    for table_name in ("feeding_deviation_policies", "feeding_actual_measures"):
        op.execute(
            f"DROP TRIGGER IF EXISTS trg_immutable_{table_name} ON domain_agrar.{table_name}"
        )  # noqa: S608
        op.execute(f"""CREATE TRIGGER trg_immutable_{table_name} BEFORE UPDATE OR DELETE
          ON domain_agrar.{table_name} FOR EACH ROW
          EXECUTE FUNCTION domain_agrar.guard_immutable_feeding_measure_config()""")  # noqa: S608


def downgrade() -> None:
    op.execute(
        "ALTER TABLE domain_agrar.feeding_controlling_daily DROP COLUMN IF EXISTS iofc_eur_cow, DROP COLUMN IF EXISTS milk_revenue_eur_cow, DROP COLUMN IF EXISTS milk_price_eur_kg, DROP COLUMN IF EXISTS feeding_plan_version_id"
    )
    for table_name in ("feeding_actual_measures", "feeding_deviation_policies"):
        op.execute(
            f"DROP TRIGGER IF EXISTS trg_immutable_{table_name} ON domain_agrar.{table_name}"
        )  # noqa: S608
        op.execute(f"DROP TABLE IF EXISTS domain_agrar.{table_name}")  # noqa: S608
    op.execute(
        "DROP FUNCTION IF EXISTS domain_agrar.guard_immutable_feeding_measure_config()"
    )
