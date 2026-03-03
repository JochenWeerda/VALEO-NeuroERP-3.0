"""domain_erp.journal_entries und journal_entry_lines anlegen (GoBD)

Revision ID: e7f8a9b0c1d2
Revises: d7e8f9a0b1c2
Create Date: 2026-03-03

Legt domain_erp.journal_entries und domain_erp.journal_entry_lines an, falls sie
noch nicht existieren (z. B. wenn 001_initial_schema nicht in der Kette liegt).
Fügt GoBD-Spalten hash_prev, hash_current, sequence_number hinzu, falls die
Tabelle bereits existiert.
"""
from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "e7f8a9b0c1d2"
down_revision = "d7e8f9a0b1c2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    op.execute(text("CREATE SCHEMA IF NOT EXISTS domain_erp"))

    je_exists = conn.execute(text("SELECT to_regclass('domain_erp.journal_entries')")).scalar()
    if not je_exists:
        op.execute(text("""
            CREATE TABLE domain_erp.journal_entries (
                id VARCHAR NOT NULL PRIMARY KEY,
                tenant_id VARCHAR NULL REFERENCES domain_shared.tenants(id),
                entry_number VARCHAR(50) NOT NULL,
                entry_date DATE NOT NULL,
                posting_date DATE NOT NULL,
                document_type VARCHAR(50) NULL,
                document_number VARCHAR(100) NULL,
                reference VARCHAR(255) NULL,
                description TEXT NULL,
                total_debit NUMERIC(15,2) NULL DEFAULT 0,
                total_credit NUMERIC(15,2) NULL DEFAULT 0,
                status VARCHAR(50) NULL DEFAULT 'draft',
                posted_by VARCHAR NULL REFERENCES domain_shared.users(id),
                posted_at TIMESTAMP WITH TIME ZONE NULL,
                created_at TIMESTAMP WITH TIME ZONE NULL DEFAULT now(),
                updated_at TIMESTAMP WITH TIME ZONE NULL DEFAULT now(),
                source VARCHAR(50) NULL DEFAULT 'manual',
                reversed_entry_id VARCHAR NULL REFERENCES domain_erp.journal_entries(id),
                hash_prev VARCHAR(255) NULL,
                hash_current VARCHAR(255) NULL,
                sequence_number BIGINT NULL,
                UNIQUE(entry_number)
            )
        """))
    else:
        for col, defn in [
            ("hash_prev", "VARCHAR(255) NULL"),
            ("hash_current", "VARCHAR(255) NULL"),
            ("sequence_number", "BIGINT NULL"),
        ]:
            r = conn.execute(text("""
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'domain_erp' AND table_name = 'journal_entries' AND column_name = :col
            """), {"col": col})
            if r.scalar() is None:
                op.execute(text(f"ALTER TABLE domain_erp.journal_entries ADD COLUMN {col} {defn}"))

    jel_exists = conn.execute(text("SELECT to_regclass('domain_erp.journal_entry_lines')")).scalar()
    coa_exists = conn.execute(text("SELECT to_regclass('domain_erp.chart_of_accounts')")).scalar()
    if not jel_exists and coa_exists:
        op.execute(text("""
            CREATE TABLE domain_erp.journal_entry_lines (
                id VARCHAR NOT NULL PRIMARY KEY,
                journal_entry_id VARCHAR NOT NULL REFERENCES domain_erp.journal_entries(id) ON DELETE CASCADE,
                account_id VARCHAR NOT NULL REFERENCES domain_erp.chart_of_accounts(id),
                description VARCHAR(255) NULL,
                debit NUMERIC(15,2) NULL DEFAULT 0,
                credit NUMERIC(15,2) NULL DEFAULT 0,
                cost_center VARCHAR(100) NULL,
                project VARCHAR(100) NULL,
                line_number INTEGER NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE NULL DEFAULT now()
            )
        """))


def downgrade() -> None:
    # Nur Spalten zurücknehmen, Tabellen nicht löschen (könnten von 001 stammen)
    conn = op.get_bind()
    je_exists = conn.execute(text("SELECT to_regclass('domain_erp.journal_entries')")).scalar()
    if je_exists:
        op.execute(text("ALTER TABLE domain_erp.journal_entries DROP COLUMN IF EXISTS hash_prev"))
        op.execute(text("ALTER TABLE domain_erp.journal_entries DROP COLUMN IF EXISTS hash_current"))
        op.execute(text("ALTER TABLE domain_erp.journal_entries DROP COLUMN IF EXISTS sequence_number"))
