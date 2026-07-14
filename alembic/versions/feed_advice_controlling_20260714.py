"""Daily feeding controlling observations.

Revision ID: feed_advice_controlling_20260714
Revises: feed_advice_lifecycle_20260714
"""
from alembic import op

revision = "feed_advice_controlling_20260714"
down_revision = "feed_advice_lifecycle_20260714"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.feeding_controlling_daily (
      id VARCHAR PRIMARY KEY, tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      group_id VARCHAR NOT NULL REFERENCES domain_agrar.feeding_groups(id),
      ration_version_id VARCHAR REFERENCES domain_agrar.ration_versions(id),
      observation_date DATE NOT NULL, source VARCHAR(32) NOT NULL,
      source_ref VARCHAR(200) NOT NULL, cow_count INTEGER,
      target_dmi_kg_cow NUMERIC(12,4), actual_dmi_kg_cow NUMERIC(12,4),
      target_cost_eur_cow NUMERIC(12,4), actual_cost_eur_cow NUMERIC(12,4),
      target_milk_kg_cow NUMERIC(12,4), actual_milk_kg_cow NUMERIC(12,4),
      actual_fat_pct NUMERIC(8,4), actual_protein_pct NUMERIC(8,4), actual_ecm_kg_cow NUMERIC(12,4),
      feed_n_kg_cow NUMERIC(12,5), nitrogen_efficiency_pct NUMERIC(10,4),
      target_methane_kg_cow NUMERIC(12,5), actual_methane_kg_cow NUMERIC(12,5),
      methane_estimated BOOLEAN NOT NULL DEFAULT FALSE,
      payload JSONB NOT NULL DEFAULT '{}'::jsonb,
      recorded_by VARCHAR(160) NOT NULL, recorded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      CONSTRAINT uq_feeding_controlling_source UNIQUE (tenant_id,group_id,observation_date,source,source_ref)
    )""")
    op.execute("CREATE INDEX IF NOT EXISTS ix_feeding_controlling_series ON domain_agrar.feeding_controlling_daily (tenant_id,group_id,observation_date DESC)")

def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS domain_agrar.ix_feeding_controlling_series")
    op.execute("DROP TABLE IF EXISTS domain_agrar.feeding_controlling_daily")
