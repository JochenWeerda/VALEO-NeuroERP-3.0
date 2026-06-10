"""Bring runtime models that predate Alembic under the migration contract.

Revision ID: repair_runtime_schema_20260610
Revises: merge_crm_owner_prod_20260610
"""

from alembic import op
from sqlalchemy import text


revision = "repair_runtime_schema_20260610"
down_revision = "merge_crm_owner_prod_20260610"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        text(
            """
            ALTER TABLE domain_shared.users
              ADD COLUMN IF NOT EXISTS last_login TIMESTAMPTZ,
              ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ,
              ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

            CREATE TABLE IF NOT EXISTS domain_shared.knowledge_objects (
              knowledge_id VARCHAR PRIMARY KEY,
              tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
              titel VARCHAR(255) NOT NULL,
              typ VARCHAR(64) NOT NULL,
              status VARCHAR(32) NOT NULL,
              beschreibung TEXT NOT NULL DEFAULT '',
              tags JSONB NOT NULL DEFAULT '[]'::jsonb,
              zielrollen JSONB NOT NULL DEFAULT '[]'::jsonb,
              agentenfreigabe BOOLEAN NOT NULL DEFAULT TRUE,
              created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
              updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS domain_shared.knowledge_versions (
              id VARCHAR PRIMARY KEY,
              knowledge_id VARCHAR NOT NULL REFERENCES domain_shared.knowledge_objects(knowledge_id) ON DELETE CASCADE,
              version INTEGER NOT NULL,
              format VARCHAR(32) NOT NULL,
              inhalt TEXT NOT NULL,
              strukturierte_daten JSONB NOT NULL DEFAULT '{}'::jsonb,
              quelle VARCHAR(255) NOT NULL DEFAULT 'system',
              erstellt_am TIMESTAMPTZ NOT NULL DEFAULT NOW(),
              CONSTRAINT uq_knowledge_object_version UNIQUE (knowledge_id, version)
            );
            CREATE TABLE IF NOT EXISTS domain_shared.knowledge_improvement_proposals (
              proposal_id VARCHAR PRIMARY KEY,
              tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
              target_knowledge_id VARCHAR REFERENCES domain_shared.knowledge_objects(knowledge_id) ON DELETE SET NULL,
              titel VARCHAR(255) NOT NULL,
              typ VARCHAR(64) NOT NULL,
              status VARCHAR(32) NOT NULL DEFAULT 'EINGEREICHT',
              beschreibung TEXT NOT NULL DEFAULT '',
              tags JSONB NOT NULL DEFAULT '[]'::jsonb,
              zielrollen JSONB NOT NULL DEFAULT '[]'::jsonb,
              format VARCHAR(32) NOT NULL,
              inhalt TEXT NOT NULL,
              strukturierte_daten JSONB NOT NULL DEFAULT '{}'::jsonb,
              quelle VARCHAR(255) NOT NULL DEFAULT 'improvement-workflow',
              vorgeschlagen_von_typ VARCHAR(32) NOT NULL DEFAULT 'human',
              vorgeschlagen_von_ref VARCHAR(255) NOT NULL DEFAULT 'unknown',
              vorgeschlagen_von_rolle VARCHAR(128),
              kanal VARCHAR(32),
              begruendung TEXT NOT NULL DEFAULT '',
              reviewer_ref VARCHAR(255),
              reviewer_rolle VARCHAR(128),
              review_notiz TEXT,
              reviewed_at TIMESTAMPTZ,
              applied_knowledge_id VARCHAR,
              applied_version INTEGER,
              created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
              updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS domain_shared.channel_process_threads (
              thread_id VARCHAR PRIMARY KEY,
              kanal VARCHAR(32) NOT NULL,
              tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
              process_definition_key VARCHAR(120) NOT NULL,
              command_name VARCHAR(120) NOT NULL,
              aggregate_type VARCHAR(120) NOT NULL,
              aggregate_id VARCHAR(120) NOT NULL,
              rolle VARCHAR(120) NOT NULL,
              issuer_type VARCHAR(32) NOT NULL,
              employee_ref VARCHAR(120),
              channel_user_id VARCHAR(120),
              request_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
              status VARCHAR(40) NOT NULL,
              execution JSONB NOT NULL DEFAULT '{}'::jsonb,
              approval_requirement JSONB,
              approval_record JSONB,
              message TEXT NOT NULL DEFAULT '',
              is_active BOOLEAN NOT NULL DEFAULT TRUE,
              created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
              updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS domain_shared.channel_thread_audit_items (
              id BIGSERIAL PRIMARY KEY,
              thread_id VARCHAR NOT NULL REFERENCES domain_shared.channel_process_threads(thread_id) ON DELETE CASCADE,
              position INTEGER NOT NULL DEFAULT 0,
              audit_type VARCHAR(80) NOT NULL,
              payload JSONB NOT NULL DEFAULT '{}'::jsonb,
              recorded_at VARCHAR(64) NOT NULL,
              created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );

            CREATE INDEX IF NOT EXISTS idx_knowledge_objects_tenant ON domain_shared.knowledge_objects(tenant_id);
            CREATE INDEX IF NOT EXISTS idx_knowledge_versions_lookup ON domain_shared.knowledge_versions(knowledge_id, version DESC);
            CREATE INDEX IF NOT EXISTS idx_knowledge_improvement_proposals_tenant ON domain_shared.knowledge_improvement_proposals(tenant_id);
            CREATE INDEX IF NOT EXISTS idx_channel_process_threads_tenant ON domain_shared.channel_process_threads(tenant_id, created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_channel_process_threads_status ON domain_shared.channel_process_threads(status, is_active);
            CREATE INDEX IF NOT EXISTS idx_channel_thread_audit_items_thread ON domain_shared.channel_thread_audit_items(thread_id, position);
            """
        )
    )


def downgrade() -> None:
    # Repair migrations deliberately preserve production data.
    pass
