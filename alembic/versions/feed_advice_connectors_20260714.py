"""Herd-data connector configuration, observations and delta-sync journal.

Revision ID: feed_advice_connectors_20260714
Revises: feldbuch_acker_waves_20260713
"""
from alembic import op

revision = "feed_advice_connectors_20260714"
down_revision = "feldbuch_acker_waves_20260713"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.herd_data_connections (
      id VARCHAR PRIMARY KEY, tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      provider VARCHAR(32) NOT NULL DEFAULT 'ddw', herd_id VARCHAR(160) NOT NULL,
      base_url TEXT NOT NULL, endpoint_templates JSONB NOT NULL DEFAULT '{}'::jsonb,
      query_parameters JSONB NOT NULL DEFAULT '{}'::jsonb,
      credential_env_key VARCHAR(80) NOT NULL DEFAULT 'DDW_HERD_DATA_TOKEN',
      contract_ref VARCHAR(160) NOT NULL, consent_ref VARCHAR(160) NOT NULL,
      enabled BOOLEAN NOT NULL DEFAULT FALSE, live_enabled BOOLEAN NOT NULL DEFAULT FALSE,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now(), updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      CONSTRAINT uq_herd_data_connection UNIQUE (tenant_id,provider,herd_id)
    )""")
    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.herd_data_sync_runs (
      id VARCHAR PRIMARY KEY, tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      connection_id VARCHAR NOT NULL REFERENCES domain_agrar.herd_data_connections(id) ON DELETE CASCADE,
      status VARCHAR(20) NOT NULL, cursor_from TIMESTAMPTZ, cursor_to TIMESTAMPTZ,
      imported_count INTEGER NOT NULL DEFAULT 0, error TEXT,
      started_at TIMESTAMPTZ NOT NULL DEFAULT now(), finished_at TIMESTAMPTZ
    )""")
    op.execute("CREATE INDEX IF NOT EXISTS ix_herd_data_sync_runs ON domain_agrar.herd_data_sync_runs (tenant_id,connection_id,started_at DESC)")
    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.herd_data_observations (
      id VARCHAR PRIMARY KEY, tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      connection_id VARCHAR NOT NULL REFERENCES domain_agrar.herd_data_connections(id) ON DELETE CASCADE,
      provider VARCHAR(32) NOT NULL, herd_id VARCHAR(160) NOT NULL, kind VARCHAR(32) NOT NULL,
      entity_id VARCHAR(200) NOT NULL, effective_at TIMESTAMPTZ NOT NULL,
      provider_updated_at TIMESTAMPTZ NOT NULL, group_id VARCHAR(160), previous_group_id VARCHAR(160),
      is_deleted BOOLEAN NOT NULL DEFAULT FALSE, payload JSONB NOT NULL, payload_hash VARCHAR(64) NOT NULL,
      imported_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      CONSTRAINT uq_herd_data_observation UNIQUE (tenant_id,provider,herd_id,kind,entity_id,effective_at)
    )""")
    op.execute("CREATE INDEX IF NOT EXISTS ix_herd_data_observation_series ON domain_agrar.herd_data_observations (tenant_id,herd_id,kind,effective_at DESC)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS domain_agrar.ix_herd_data_observation_series")
    op.execute("DROP TABLE IF EXISTS domain_agrar.herd_data_observations")
    op.execute("DROP INDEX IF EXISTS domain_agrar.ix_herd_data_sync_runs")
    op.execute("DROP TABLE IF EXISTS domain_agrar.herd_data_sync_runs")
    op.execute("DROP TABLE IF EXISTS domain_agrar.herd_data_connections")
