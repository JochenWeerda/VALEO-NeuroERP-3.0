"""Gap 010: Hash-Kette für domain_shared.audit_logs (Betriebsprüfungsfest)

Revision ID: audit_hash_20260306
Revises: lkw_queue_20260306
Create Date: 2026-03-06

Adds prev_hash and hash columns to audit_logs. Trigger befüllt bei INSERT
die Hash-Kette pro Tenant – damit alle kritischen Prozessschritte
revisionssicher nachvollziehbar sind.
"""
from __future__ import annotations

from alembic import op
from sqlalchemy import text


revision = "audit_hash_20260306"
down_revision = "lkw_queue_20260306"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # Prüfen ob Spalten bereits existieren
    r = conn.execute(
        text(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_schema = 'domain_shared' AND table_name = 'audit_logs' AND column_name = 'hash'"
        )
    )
    if r.scalar() is not None:
        return

    op.execute(text("""
        ALTER TABLE domain_shared.audit_logs
        ADD COLUMN IF NOT EXISTS prev_hash VARCHAR(64) DEFAULT '',
        ADD COLUMN IF NOT EXISTS hash VARCHAR(64) NULL
    """))

    op.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))

    op.execute(text("""
        CREATE OR REPLACE FUNCTION domain_shared.audit_logs_hash_chain()
        RETURNS TRIGGER AS $$
        DECLARE
            last_hash VARCHAR(64);
            payload TEXT;
        BEGIN
            IF NEW.hash IS NULL OR NEW.hash = '' THEN
                PERFORM pg_advisory_xact_lock(hashtext(COALESCE(NEW.tenant_id, ''))::bigint);

                SELECT COALESCE(hash, '') INTO last_hash
                FROM domain_shared.audit_logs
                WHERE tenant_id IS NOT DISTINCT FROM NEW.tenant_id
                ORDER BY timestamp DESC NULLS LAST, id DESC NULLS LAST
                LIMIT 1;

                NEW.prev_hash := COALESCE(last_hash, '');

                payload := CONCAT(
                    COALESCE(NEW.id, ''),
                    '|', COALESCE(NEW.timestamp::TEXT, ''),
                    '|', COALESCE(NEW.tenant_id, ''),
                    '|', COALESCE(NEW.user_id, ''),
                    '|', COALESCE(NEW.action, ''),
                    '|', COALESCE(NEW.entity_type, ''),
                    '|', COALESCE(NEW.entity_id, ''),
                    '|', COALESCE(NEW.changes::TEXT, '{}'),
                    '|', NEW.prev_hash
                );
                NEW.hash := encode(public.digest(convert_to(payload, 'UTF8'), 'sha256'), 'hex');
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
    """))
    op.execute(text("DROP TRIGGER IF EXISTS trg_audit_logs_hash_chain ON domain_shared.audit_logs"))
    op.execute(text("""
        CREATE TRIGGER trg_audit_logs_hash_chain
        BEFORE INSERT ON domain_shared.audit_logs
        FOR EACH ROW
        EXECUTE PROCEDURE domain_shared.audit_logs_hash_chain()
    """))


def downgrade() -> None:
    op.execute(text("DROP TRIGGER IF EXISTS trg_audit_logs_hash_chain ON domain_shared.audit_logs"))
    op.execute(text("DROP FUNCTION IF EXISTS domain_shared.audit_logs_hash_chain()"))
    op.execute(text("""
        ALTER TABLE domain_shared.audit_logs
        DROP COLUMN IF EXISTS prev_hash,
        DROP COLUMN IF EXISTS hash
    """))
