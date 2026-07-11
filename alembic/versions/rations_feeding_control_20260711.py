"""Persisted feeding-control logs (DLG 01|2025 F1).

Revision ID: rations_feeding_control_20260711
Revises: esg_charge_footprint_uix082
"""
from alembic import op
revision = "rations_feeding_control_20260711"
down_revision = "esg_charge_footprint_uix082"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_agrar")
    op.execute("""
      CREATE TABLE IF NOT EXISTS domain_agrar.feeding_logs (
        id VARCHAR PRIMARY KEY,
        tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
        group_id VARCHAR(96) NOT NULL,
        feeding_date DATE NOT NULL,
        ration_ref VARCHAR(128),
        payload JSONB NOT NULL,
        control_result JSONB NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        CONSTRAINT uq_feeding_log_tenant_group_date UNIQUE (tenant_id, group_id, feeding_date)
      )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_feeding_logs_series ON domain_agrar.feeding_logs (tenant_id, group_id, feeding_date DESC)")

def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS domain_agrar.ix_feeding_logs_series")
    op.execute("DROP TABLE IF EXISTS domain_agrar.feeding_logs")