"""
Vertragstests fuer die Buchungsherkunft ``domain_erp.journal_entries.source``
(Slice L3-JOURNAL-SOURCE-20260910).

Hintergrund: der Schreib-Whitelist-Validator sass auf ``JournalEntryBase`` und
wurde dadurch von ``JournalEntry`` — dem *Response*-Model der Journal-Liste —
mitgeerbt. Eine einzige gespeicherte Buchung mit einer nicht gelisteten
Herkunft (real: ``produktion_mischfutter``) liess damit
``GET /api/v1/journal-entries/`` komplett mit HTTP 500 fehlschlagen.

Der Vertrag lautet seitdem:

* **Leseweg** (``JournalEntry``) gibt gespeicherte Herkunft unveraendert
  zurueck und prueft sie nicht — vorhandene Buchungen duerfen nie aus dem
  Journal verschwinden.
* **Schreibweg** (``JournalEntryCreate``) nimmt nur belegte Herkunft an;
  unbekannte Eingaben werden weiterhin abgewiesen.

Die Tests kommen ohne Datenbank und ohne Netzwerk aus.
"""

import pytest
from decimal import Decimal
from datetime import datetime
from pydantic import ValidationError

from app.api.v1.schemas.finance import (
    JOURNAL_ENTRY_WRITE_SOURCES,
    JournalEntry,
    JournalEntryBase,
    JournalEntryCreate,
    JournalEntryLineCreate,
)


# Herkunft, die am 2026-09-10 in der lokalen Buchungstabelle real vorlag.
# ``produktion_mischfutter`` ist der Wert, an dem der API-Sweep gescheitert ist.
GESPEICHERTE_HERKUNFT = [
    "manual",
    "produktion_mischfutter",
    "reversal",
    "sales_invoice",
    "bulk_import",
]


def _lines():
    return [
        JournalEntryLineCreate(
            account_id="1000", debit_amount=Decimal("100.00"),
            credit_amount=Decimal("0.00"), line_number=1,
        ),
        JournalEntryLineCreate(
            account_id="1200", debit_amount=Decimal("0.00"),
            credit_amount=Decimal("100.00"), line_number=2,
        ),
    ]


def _gespeicherte_zeile(source):
    """Eine Zeile so, wie sie aus ``domain_erp.journal_entries`` gelesen wird."""
    now = datetime(2026, 9, 10, 12, 0, 0)
    return {
        "id": "je-1",
        "tenant_id": "test-tenant",
        "entry_number": "JE-2026-0001",
        "entry_date": now,
        "posting_date": now,
        "description": "Produktionsabschluss",
        "reference": "REF-1",
        "source": source,
        "status": "posted",
        "total_debit": Decimal("100.00"),
        "total_credit": Decimal("100.00"),
    }


# ═══════════════════════════════════════════════════════════════════════════
# Leseweg: vorhandene Herkunft unveraendert lesbar
# ═══════════════════════════════════════════════════════════════════════════

class TestLeseweg:
    @pytest.mark.parametrize("source", GESPEICHERTE_HERKUNFT)
    def test_gespeicherte_herkunft_wird_unveraendert_gelesen(self, source):
        entry = JournalEntry.model_validate(_gespeicherte_zeile(source))
        assert entry.source == source

    def test_regression_sweep_wert_produktion_mischfutter(self):
        """Der konkrete Wert aus dem 500er des Sweeps vom 2026-09-10."""
        entry = JournalEntry.model_validate(
            _gespeicherte_zeile("produktion_mischfutter")
        )
        assert entry.source == "produktion_mischfutter"

    def test_leere_herkunft_bricht_das_lesen_nicht(self):
        """Die Spalte ist nullable; storage_fees und finance_closing_service
        schreiben sie gar nicht."""
        entry = JournalEntry.model_validate(_gespeicherte_zeile(None))
        assert entry.source is None

    def test_unbekannte_historische_herkunft_wird_nicht_umgedeutet(self):
        """Kein Fallback auf ``manual``/``system``: unbekannte Herkunft bleibt
        stehen, damit sie fachlich geklaert statt still ueberschrieben wird."""
        entry = JournalEntry.model_validate(
            _gespeicherte_zeile("nicht_im_schreibvertrag")
        )
        assert entry.source == "nicht_im_schreibvertrag"

    def test_leseweg_traegt_keinen_schreibvalidator(self):
        """Strukturschutz gegen die Ursache: der Whitelist-Validator darf nicht
        erneut ueber die Basisklasse in das Response-Model wandern."""
        assert not hasattr(JournalEntryBase, "validate_source")
        JournalEntry.model_validate(_gespeicherte_zeile("beliebiger_neuer_wert"))


# ═══════════════════════════════════════════════════════════════════════════
# Schreibweg: ungueltige Eingaben weiterhin abgewiesen
# ═══════════════════════════════════════════════════════════════════════════

class TestSchreibweg:
    @pytest.mark.parametrize("source", sorted(JOURNAL_ENTRY_WRITE_SOURCES))
    def test_belegte_herkunft_wird_angenommen(self, source):
        now = datetime(2026, 9, 10, 12, 0, 0)
        entry = JournalEntryCreate(
            entry_number="BUC-001", entry_date=now, posting_date=now,
            description="Test", tenant_id="t", source=source, lines=_lines(),
        )
        assert entry.source == source

    @pytest.mark.parametrize(
        "source", ["unknown", "", "MANUAL", "nicht_im_schreibvertrag", "drop table"]
    )
    def test_unbelegte_herkunft_wird_abgewiesen(self, source):
        now = datetime(2026, 9, 10, 12, 0, 0)
        with pytest.raises(ValidationError, match="Source must be one of"):
            JournalEntryCreate(
                entry_number="BUC-001", entry_date=now, posting_date=now,
                description="Test", tenant_id="t", source=source, lines=_lines(),
            )

    def test_default_bleibt_manual(self):
        now = datetime(2026, 9, 10, 12, 0, 0)
        entry = JournalEntryCreate(
            entry_number="BUC-001", entry_date=now, posting_date=now,
            description="Test", tenant_id="t", lines=_lines(),
        )
        assert entry.source == "manual"


# ═══════════════════════════════════════════════════════════════════════════
# Der Schreibvertrag muss die real geschriebene Herkunft abdecken
# ═══════════════════════════════════════════════════════════════════════════

class TestVertragsdeckung:
    @pytest.mark.parametrize("source", GESPEICHERTE_HERKUNFT)
    def test_reale_herkunft_ist_im_schreibvertrag(self, source):
        """Wer eine Herkunft schreibt, muss sie auch ueber die API buchen
        koennen — sonst faellt der Vertrag wieder auseinander."""
        assert source in JOURNAL_ENTRY_WRITE_SOURCES
