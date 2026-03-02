"""Journal: Eine Tabelle für List + Connector (domain_erp.journal_entries)

Revision ID: journal_entries_unify_20260301
Revises: fibu_connector_asset_ledger_20260301
Create Date: 2026-03-01

- Fügt Spalte 'source' zu domain_erp.journal_entries hinzu, falls fehlend (ORM/Filter).
- Connector und Liste nutzen dieselbe Tabelle journal_entries (kein finance_journal_entries).
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import text


revision = "journal_entries_unify_20260301"
down_revision = "fibu_connector_asset_ledger_20260301"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    # Existenz per to_regclass (schema-qualified)
    je = conn.execute(text("SELECT to_regclass('domain_erp.journal_entries')")).scalar()
    fje = conn.execute(text("SELECT to_regclass('domain_erp.finance_journal_entries')")).scalar()

    if not je and fje:
        # Umbenennen in Savepoint; bei Fehler Rollback, damit Transaktion nicht abgebrochen bleibt
        conn.execute(text("SAVEPOINT journal_entries_rename"))
        try:
            conn.execute(text("ALTER TABLE domain_erp.finance_journal_entries RENAME TO journal_entries"))
            conn.execute(text("ALTER TABLE domain_erp.finance_journal_entry_lines RENAME TO journal_entry_lines"))
            conn.execute(text("ALTER TABLE domain_erp.journal_entry_lines DROP CONSTRAINT IF EXISTS journal_entry_lines_journal_entry_id_fkey"))
            conn.execute(text("""
                ALTER TABLE domain_erp.journal_entry_lines
                ADD CONSTRAINT journal_entry_lines_journal_entry_id_fkey
                FOREIGN KEY (journal_entry_id) REFERENCES domain_erp.journal_entries(id) ON DELETE CASCADE
            """))
            try:
                conn.execute(text("ALTER TABLE domain_erp.journal_entry_lines DROP CONSTRAINT IF EXISTS journal_entry_lines_account_id_fkey"))
                conn.execute(text("""
                    ALTER TABLE domain_erp.journal_entry_lines
                    ADD CONSTRAINT journal_entry_lines_account_id_fkey
                    FOREIGN KEY (account_id) REFERENCES domain_erp.chart_of_accounts(id)
                """))
            except Exception:
                pass
            conn.execute(text("RELEASE SAVEPOINT journal_entries_rename"))
        except Exception:
            conn.execute(text("ROLLBACK TO SAVEPOINT journal_entries_rename"))

    je_now = conn.execute(text("SELECT to_regclass('domain_erp.journal_entries')")).scalar()
    if not je_now:
        return

    # source für Herkunft (manual, connector, …)
    r = conn.execute(text("""
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'domain_erp' AND table_name = 'journal_entries' AND column_name = 'source'
    """))
    if r.scalar() is None:
        conn.execute(text("""
            ALTER TABLE domain_erp.journal_entries
            ADD COLUMN source VARCHAR(50) NULL DEFAULT 'manual'
        """))
    r2 = conn.execute(text("""
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'domain_erp' AND table_name = 'journal_entries' AND column_name = 'reversed_entry_id'
    """))
    if r2.scalar() is None:
        conn.execute(text("""
            ALTER TABLE domain_erp.journal_entries
            ADD COLUMN reversed_entry_id VARCHAR(36) NULL
            REFERENCES domain_erp.journal_entries(id)
        """))


def downgrade() -> None:
    op.execute("ALTER TABLE domain_erp.journal_entries DROP COLUMN IF EXISTS reversed_entry_id")
    op.execute("ALTER TABLE domain_erp.journal_entries DROP COLUMN IF EXISTS source")
