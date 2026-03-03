"""GoBD Hash-Chain: Trigger für journal_entries (sequence_number, hash_prev, hash_current)

Revision ID: a9b0c1d2e3f4
Revises: f8a9b0c1d2e3
Create Date: 2026-03-03

Trigger befüllt bei INSERT in domain_erp.journal_entries die GoBD-Felder
sequence_number, hash_prev, hash_current, falls NULL – damit alle Buchungspfade
automatisch in die Hash-Kette aufgenommen werden.
"""
from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "a9b0c1d2e3f4"
down_revision = "f8a9b0c1d2e3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(text("""
        CREATE OR REPLACE FUNCTION domain_erp.journal_entries_hash_chain()
        RETURNS TRIGGER AS $$
        DECLARE
            last_seq BIGINT;
            last_hash VARCHAR(255);
            payload TEXT;
        BEGIN
            IF NEW.sequence_number IS NULL OR NEW.hash_current IS NULL THEN
                SELECT sequence_number, hash_current INTO last_seq, last_hash
                FROM domain_erp.journal_entries
                WHERE tenant_id IS NOT DISTINCT FROM NEW.tenant_id
                ORDER BY sequence_number DESC NULLS LAST
                LIMIT 1;

                NEW.sequence_number := COALESCE(last_seq, 0) + 1;
                NEW.hash_prev := last_hash;

                payload := CONCAT(
                    COALESCE(NEW.id, ''),
                    '|', COALESCE(NEW.entry_number, ''),
                    '|', COALESCE(NEW.entry_date::TEXT, ''),
                    '|', COALESCE(NEW.posting_date::TEXT, ''),
                    '|', COALESCE(NEW.total_debit::TEXT, '0'),
                    '|', COALESCE(NEW.total_credit::TEXT, '0'),
                    '|', NEW.sequence_number::TEXT,
                    '|', COALESCE(NEW.created_at::TEXT, NOW()::TEXT)
                );
                NEW.hash_current := encode(sha256(payload::bytea), 'hex');
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
    """))
    op.execute(text("""
        DROP TRIGGER IF EXISTS trg_journal_entries_hash_chain ON domain_erp.journal_entries
    """))
    op.execute(text("""
        CREATE TRIGGER trg_journal_entries_hash_chain
        BEFORE INSERT ON domain_erp.journal_entries
        FOR EACH ROW
        EXECUTE FUNCTION domain_erp.journal_entries_hash_chain()
    """))


def downgrade() -> None:
    op.execute(text("DROP TRIGGER IF EXISTS trg_journal_entries_hash_chain ON domain_erp.journal_entries"))
    op.execute(text("DROP FUNCTION IF EXISTS domain_erp.journal_entries_hash_chain()"))
