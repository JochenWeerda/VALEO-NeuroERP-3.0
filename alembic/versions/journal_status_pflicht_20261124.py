"""Journalstatus ist Pflicht: Vorgabe draft, NOT NULL, nur die vier Status des Buchungsdienstes (24.11.2026).

Revision ID: journal_status_pflicht_20261124
Revises: bestandsbuchung_schluessel_20261124

``domain_erp.journal_entries.status`` war auf frischer Installation nullbar, ohne Vorgabe und ohne Pruefbedingung.
Bilanz, GuV und BWA zaehlten einen Eintrag ohne Status als gebucht (behoben in PR #195). Der Buchungsdienst
(``FinanceTransactionService.VALID_STATUSES``) kennt genau draft, posted, cancelled, reversed - die Datenbank jetzt auch.

Eintraege ohne Status werden nicht pauschal eingeordnet (Nutzervorgabe 24.11.2026). Eindeutig ist nur ein belegter
Buchungsstand: ``posted_at`` oder ``posted_by`` (setzt nur das Buchen; der GoBD-Stempel entsteht schon beim Anlegen) ->
``posted``; verweist zusaetzlich eine Gegenbuchung per ``reversed_entry_id`` darauf -> ``reversed``. Bleiben danach
Eintraege ohne Status, bricht die Migration ab und nennt sie - sie werden fachlich entschieden, nicht geraten.
Im gewachsenen Bestand 24.11.2026: keiner.
"""
from __future__ import annotations

from alembic import op

revision = "journal_status_pflicht_20261124"
down_revision = "bestandsbuchung_schluessel_20261124"
branch_labels = None
depends_on = None

TABELLE = "domain_erp.journal_entries"


#: Belegter Buchungsstand: posted_at/posted_by setzt nur das Buchen. Der GoBD-Stempel hash_current zaehlt nicht -
#: trg_journal_entries_hash_chain stempelt schon beim Anlegen, auch Entwuerfe.
BELEGT_GEBUCHT = "(posted_at IS NOT NULL OR NULLIF(posted_by, '') IS NOT NULL)"


def upgrade() -> None:
    bind = op.get_bind()
    # Eindeutig storniert: gebucht belegt und von einer Gegenbuchung referenziert.
    bind.exec_driver_sql(  # nosec B608 - feste Namen
        f"UPDATE {TABELLE} o SET status = 'reversed' WHERE o.status IS NULL AND {BELEGT_GEBUCHT} "
        f"AND EXISTS (SELECT 1 FROM {TABELLE} g WHERE g.tenant_id = o.tenant_id AND g.reversed_entry_id = o.id)")
    bind.exec_driver_sql(f"UPDATE {TABELLE} SET status = 'posted' WHERE status IS NULL AND {BELEGT_GEBUCHT}")  # nosec B608
    offen = bind.exec_driver_sql(  # nosec B608 - feste Namen
        f"SELECT tenant_id, id FROM {TABELLE} WHERE status IS NULL ORDER BY tenant_id, id LIMIT 21").fetchall()
    if offen:
        liste = ", ".join(f"{t}/{i}" for t, i in offen[:20])
        raise RuntimeError(f"Journal: Eintraege ohne Status und ohne belegten Buchungsstand - fachlich entscheiden "
                           f"(draft oder cancelled setzen), dann erneut migrieren: {liste}"
                           + (" ..." if len(offen) > 20 else ""))
    op.execute(f"ALTER TABLE {TABELLE} ALTER COLUMN status SET DEFAULT 'draft'")
    op.execute(f"ALTER TABLE {TABELLE} ALTER COLUMN status SET NOT NULL")
    op.execute(f"ALTER TABLE {TABELLE} ADD CONSTRAINT ck_journal_entries_status "
               "CHECK (status IN ('draft', 'posted', 'cancelled', 'reversed'))")


def downgrade() -> None:
    op.execute(f"ALTER TABLE {TABELLE} DROP CONSTRAINT IF EXISTS ck_journal_entries_status")
    op.execute(f"ALTER TABLE {TABELLE} ALTER COLUMN status DROP NOT NULL")
    op.execute(f"ALTER TABLE {TABELLE} ALTER COLUMN status DROP DEFAULT")
