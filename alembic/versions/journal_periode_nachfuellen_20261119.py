"""Buchungsperiode der Journalbuchungen aus dem Buchungsdatum nachfuellen (M3).

Das ORM kannte ``domain_erp.journal_entries.period`` bis 19.11.2026 nicht; jede Buchung ueber den Buchungsdienst
(Ausgangs- und Eingangsrechnungen, Gutschriften, Storno ...) blieb ohne Periode. UStVA (``app/finance/ustva.py``) und
Periodenabschluss filtern auf ``period`` - diese Buchungen fehlten dort. Seit 19.11. setzt der Dienst die Periode;
diese Migration fuellt die Altbuchungen aus ``posting_date`` nach (dieselbe Regel wie der Dienst:
``posting_date`` -> JJJJ-MM).

Die Periode gehoert nicht zur Hash-Kette (tenant, Sequenz, Nummer, Belegdatum, Betrag, Vorgaenger); Betraege und
Kette bleiben bitgleich. Mengenbasiert in einem UPDATE.

Rueckweg: ohne Wirkung. Welche Zeilen vorher leer waren, ist nicht festgehalten, und eine abgeleitete Periode
zurueckzunehmen machte die Buchungen nur wieder unsichtbar.
"""
from alembic import op

revision = "journal_periode_nachfuellen_20261119"
down_revision = "rohware_schema_canonical_20261115"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        UPDATE domain_erp.journal_entries
           SET period = to_char(posting_date, 'YYYY-MM')
         WHERE period IS NULL AND posting_date IS NOT NULL
    """)


def downgrade():
    pass
