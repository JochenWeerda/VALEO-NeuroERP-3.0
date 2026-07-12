"""Rations integration import journal.
Revision ID: rations_integrations_20260712
Revises: rations_feeding_control_20260711
"""
from alembic import op
revision = "rations_integrations_20260712"
down_revision = "rations_feeding_control_20260711"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_agrar")
    op.execute("""
      CREATE TABLE IF NOT EXISTS domain_agrar.rations_integration_imports (
        id VARCHAR PRIMARY KEY, tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
        adapter VARCHAR(32) NOT NULL, external_id VARCHAR(160) NOT NULL, source_version VARCHAR(64),
        payload_hash VARCHAR(64) NOT NULL, target_model VARCHAR(64) NOT NULL, result JSONB NOT NULL,
        imported_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        CONSTRAINT uq_rations_import UNIQUE (tenant_id, adapter, external_id)
      )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_rations_import_time ON domain_agrar.rations_integration_imports (tenant_id, imported_at DESC)")

def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS domain_agrar.ix_rations_import_time")
    op.execute("DROP TABLE IF EXISTS domain_agrar.rations_integration_imports")