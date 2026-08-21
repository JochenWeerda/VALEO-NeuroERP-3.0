"""Governed L3 Standard and Unimet adapter contracts.

Revision ID: l3_legacy_interfaces_20260821
Revises: l3_recent_documents_20260821
"""

from alembic import op

revision = "l3_legacy_interfaces_20260821"
down_revision = "l3_recent_documents_20260821"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
      CREATE SCHEMA IF NOT EXISTS domain_integration;
      CREATE TABLE IF NOT EXISTS domain_integration.legacy_adapter_profiles (
        id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, profile_key TEXT NOT NULL,
        format_version TEXT NOT NULL, mapping_version TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'inactive', format_contract JSONB NOT NULL,
        field_mapping JSONB NOT NULL, approved_by TEXT, approved_at TIMESTAMPTZ,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE (tenant_id,profile_key)
      );
      CREATE TABLE IF NOT EXISTS domain_integration.legacy_adapter_batches (
        id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, profile_key TEXT NOT NULL,
        external_id TEXT NOT NULL, payload_hash TEXT NOT NULL, raw_payload JSONB NOT NULL,
        mapping_version TEXT, status TEXT NOT NULL, record_count INTEGER NOT NULL DEFAULT 0,
        staged_count INTEGER NOT NULL DEFAULT 0, mismatch_count INTEGER NOT NULL DEFAULT 0,
        error_code TEXT, error_message TEXT, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE (tenant_id,profile_key,external_id)
      );
      CREATE INDEX IF NOT EXISTS ix_legacy_adapter_batches_monitor
        ON domain_integration.legacy_adapter_batches (tenant_id,status,created_at DESC);
      CREATE TABLE IF NOT EXISTS domain_integration.legacy_adapter_staging (
        id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, batch_id TEXT NOT NULL,
        line_no INTEGER NOT NULL, record_type TEXT, source_ref TEXT,
        canonical_payload JSONB NOT NULL, validation_status TEXT NOT NULL,
        error_message TEXT, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE (tenant_id,batch_id,line_no)
      );
      CREATE TABLE IF NOT EXISTS domain_integration.legacy_adapter_audit (
        id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, profile_key TEXT NOT NULL,
        batch_id TEXT, action TEXT NOT NULL, actor TEXT NOT NULL, reason TEXT NOT NULL,
        details JSONB NOT NULL DEFAULT '{}'::jsonb, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
      );
    """)


def downgrade() -> None:
    op.execute("""
      DROP TABLE IF EXISTS domain_integration.legacy_adapter_audit;
      DROP TABLE IF EXISTS domain_integration.legacy_adapter_staging;
      DROP TABLE IF EXISTS domain_integration.legacy_adapter_batches;
      DROP TABLE IF EXISTS domain_integration.legacy_adapter_profiles;
    """)
