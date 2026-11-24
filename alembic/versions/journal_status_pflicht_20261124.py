"""Journalstatus ist Pflicht: Vorgabe draft, NOT NULL, nur die vier Status des Buchungsdienstes (24.11.2026).

Revision ID: journal_status_pflicht_20261124
Revises: bestandsbuchung_schluessel_20261124

``domain_erp.journal_entries.status`` war auf frischer Installation nullbar, ohne Vorgabe und ohne Pruefbedingung.
Bilanz, GuV und BWA zaehlten einen Eintrag ohne Status als gebucht (behoben in PR #195). Der Buchungsdienst
(``FinanceTransactionService.VALID_STATUSES``) kennt genau draft, posted, cancelled, reversed - die Datenbank jetzt auch.

Ein Eintrag ohne Status (im gewachsenen Bestand 24.11.2026: keiner) wird draft: nicht gebucht, wie er bisher gelten
sollte - kein erfundener Buchungsstand.
"""
from __future__ import annotations

from alembic import op

revision = "journal_status_pflicht_20261124"
down_revision = "bestandsbuchung_schluessel_20261124"
branch_labels = None
depends_on = None

TABELLE = "domain_erp.journal_entries"


def upgrade() -> None:
    op.execute(f"UPDATE {TABELLE} SET status = 'draft' WHERE status IS NULL")
    op.execute(f"ALTER TABLE {TABELLE} ALTER COLUMN status SET DEFAULT 'draft'")
    op.execute(f"ALTER TABLE {TABELLE} ALTER COLUMN status SET NOT NULL")
    op.execute(f"ALTER TABLE {TABELLE} ADD CONSTRAINT ck_journal_entries_status "
               "CHECK (status IN ('draft', 'posted', 'cancelled', 'reversed'))")


def downgrade() -> None:
    op.execute(f"ALTER TABLE {TABELLE} DROP CONSTRAINT IF EXISTS ck_journal_entries_status")
    op.execute(f"ALTER TABLE {TABELLE} ALTER COLUMN status DROP NOT NULL")
    op.execute(f"ALTER TABLE {TABELLE} ALTER COLUMN status DROP DEFAULT")
