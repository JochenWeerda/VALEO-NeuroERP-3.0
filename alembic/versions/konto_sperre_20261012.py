"""Kontosperre: ein gesperrtes Konto nimmt keine neue Buchungszeile an.

Revision ID: konto_sperre_20261012
Revises: audit_urheber_20261011

Ein bebuchtes Konto bleibt erhalten — es wird weder geloescht noch deaktiviert. Soll es nicht mehr
benutzt werden, sperrt man es. Bis zum 12.10.2026 gab es dafuer kein Feld: ``allow_manual_entries``
stand in Schema und Maske, aber nicht in der Tabelle.

Durchgesetzt wird die Sperre an einer Stelle, der Tabelle der Buchungszeilen. Rund zwanzig Wege
schreiben dorthin (Journal, Vorlagen, Import, Eingangsrechnung, Wareneingang, Lagergeld, Gutschrift,
Ausgleich); eine Pruefung je Weg haette den naechsten neuen Weg wieder vergessen.

Bestehende Zeilen bleiben unberuehrt: Der Trigger prueft nur neue Zeilen und einen Wechsel des Kontos.
"""

from alembic import op

revision = "konto_sperre_20261012"
down_revision = "audit_urheber_20261011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE domain_erp.chart_of_accounts "
        "ADD COLUMN IF NOT EXISTS posting_blocked BOOLEAN NOT NULL DEFAULT false"
    )
    op.execute(
        """
        CREATE OR REPLACE FUNCTION domain_erp.journal_entry_lines_konto_sperre()
        RETURNS TRIGGER AS $$
        DECLARE
            nummer VARCHAR;
        BEGIN
            SELECT account_number INTO nummer
            FROM domain_erp.chart_of_accounts
            WHERE id = NEW.account_id AND posting_blocked;
            IF FOUND THEN
                RAISE EXCEPTION 'Konto % ist fuer Buchungen gesperrt', nummer
                    USING ERRCODE = 'check_violation', CONSTRAINT = 'konto_sperre';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
        """
    )
    op.execute("DROP TRIGGER IF EXISTS trg_journal_entry_lines_konto_sperre ON domain_erp.journal_entry_lines")
    op.execute(
        """
        CREATE TRIGGER trg_journal_entry_lines_konto_sperre
        BEFORE INSERT OR UPDATE OF account_id ON domain_erp.journal_entry_lines
        FOR EACH ROW EXECUTE FUNCTION domain_erp.journal_entry_lines_konto_sperre()
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_journal_entry_lines_konto_sperre ON domain_erp.journal_entry_lines")
    op.execute("DROP FUNCTION IF EXISTS domain_erp.journal_entry_lines_konto_sperre()")
    op.execute("ALTER TABLE domain_erp.chart_of_accounts DROP COLUMN IF EXISTS posting_blocked")
