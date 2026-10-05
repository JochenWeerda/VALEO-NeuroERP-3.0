"""
Vertragstests fuer den POS-Buchungsweg (Slice POS-FIBU-CLEANUP-20260910).

Hintergrund: es gab zwei Implementierungen. Der produktive Weg ist
``POST /pos/tagesabschluss`` in ``app/api/v1/endpoints/compat.py``: fiskalisch
abgesichert (TSE/DSFinV-K) und mit den Buchungssaetzen aus
``app/services/pos_accounting_service.build_pos_closing_lines``.

Daneben lag in ``PosCompatService`` eine zweite, nie verdrahtete Fassung mit
kaputtem SQL (nicht existierende Spalten ``source_doc_id``/``account_code``),
fehlenden NOT-NULL-Feldern, ohne ``tenant_id`` und mit drei Zeilen samtlich im
Soll. Sie ist entfernt; diese Tests halten den Zustand fest.

Ohne Datenbank und ohne Netzwerk lauffaehig.
"""

import ast
import io
import pathlib
from decimal import Decimal

import pytest

from app.services.pos_accounting_service import (
    PosClosingAmounts,
    build_pos_closing_lines,
)

REPO = pathlib.Path(__file__).resolve().parents[1]
ZERO = Decimal("0.00")


# ═══════════════════════════════════════════════════════════════════════════
# Genau eine Stelle bucht POS in das Journal
# ═══════════════════════════════════════════════════════════════════════════

class TestEineBuchungsstelle:
    def test_pos_compat_service_bucht_nicht_mehr(self):
        from app.services.pos_compat_service import PosCompatService

        assert not hasattr(PosCompatService, "_write_fibu_entries")
        assert not hasattr(PosCompatService, "create_tagesabschluss")

    def test_pos_compat_service_behaelt_seine_genutzten_methoden(self):
        """Die vom Endpunkt tatsaechlich verwendeten Methoden bleiben."""
        from app.services.pos_compat_service import PosCompatService

        for name in (
            "list_suspended_sales",
            "get_suspended_sale",
            "suspend_sale",
            "resume_sale",
            "delete_suspended_sale",
            "list_tagesabschluesse",
        ):
            assert hasattr(PosCompatService, name), name

    def test_nur_compat_py_schreibt_pos_nach_journal_entries(self):
        """Ein zweiter POS-Schreiber waere wieder eine Buchungsquelle ohne
        Fiskalisierungs-Gate."""
        treffer = []
        for pfad in (REPO / "app").rglob("*.py"):
            quelle = io.open(pfad, encoding="utf-8", errors="ignore").read()
            if "journal_entries" not in quelle:
                continue
            if "pos_tagesabschluss" in quelle.lower() or "'POS'" in quelle:
                if "INSERT INTO domain_erp.journal_entries" in quelle:
                    treffer.append(pfad.relative_to(REPO).as_posix())
        assert treffer == ["app/api/v1/endpoints/compat.py"], treffer

    def test_keine_nicht_existierenden_spalten_mehr(self):
        """``source_doc_id``, ``source_doc_type`` und ``account_code`` gibt es
        in den Buchungstabellen nicht."""
        for pfad in (REPO / "app").rglob("*.py"):
            quelle = io.open(pfad, encoding="utf-8", errors="ignore").read()
            if "INSERT INTO domain_erp.journal_entr" not in quelle:
                continue
            for spalte in ("source_doc_id", "source_doc_type", "account_code"):
                assert spalte not in quelle, f"{pfad.name}: {spalte}"


# ═══════════════════════════════════════════════════════════════════════════
# Die kanonischen Buchungssaetze bleiben ausgeglichen
# ═══════════════════════════════════════════════════════════════════════════

def _amounts(**kw):
    felder = dict(
        cash_sales=ZERO, card_sales=ZERO, paypal_sales=ZERO, b2b_sales=ZERO,
        voucher_redemptions=ZERO, voucher_issues=ZERO,
        cash_withdrawals=ZERO, cash_difference=ZERO,
    )
    felder.update({k: Decimal(str(v)) for k, v in kw.items()})
    return PosClosingAmounts(**felder)


class TestBuchungssaetze:
    @pytest.mark.parametrize(
        "kw",
        [
            {"cash_sales": "100.00"},
            {"card_sales": "250.50"},
            {"cash_sales": "100.00", "card_sales": "50.00", "paypal_sales": "25.00"},
            {"cash_sales": "80.00", "b2b_sales": "120.00"},
            {"cash_sales": "100.00", "voucher_redemptions": "20.00"},
            {"cash_sales": "100.00", "voucher_issues": "30.00"},
            {"cash_sales": "100.00", "cash_withdrawals": "40.00"},
            {"cash_sales": "100.00", "cash_difference": "5.00"},
            {"cash_sales": "100.00", "cash_difference": "-5.00"},
            {
                "cash_sales": "500.00", "card_sales": "300.00", "paypal_sales": "50.00",
                "b2b_sales": "150.00", "voucher_redemptions": "40.00",
                "voucher_issues": "60.00", "cash_withdrawals": "200.00",
                "cash_difference": "-3.50",
            },
        ],
    )
    def test_buchung_ist_ausgeglichen(self, kw):
        lines = build_pos_closing_lines(_amounts(**kw))
        soll = sum((l.debit for l in lines), ZERO)
        haben = sum((l.credit for l in lines), ZERO)
        assert soll == haben, f"Soll={soll} Haben={haben}"

    def test_jede_buchung_hat_beide_seiten(self):
        """Der entfernte Pfad stellte drei Zeilen samtlich ins Soll."""
        lines = build_pos_closing_lines(_amounts(cash_sales="100.00", card_sales="50.00"))
        assert any(l.debit > ZERO for l in lines), "Es fehlt eine Sollseite"
        assert any(l.credit > ZERO for l in lines), "Es fehlt eine Habenseite"

    def test_ausgleichspruefung_ist_vorhanden(self):
        """Die Funktion schuetzt sich selbst gegen unausgeglichene Saetze —
        genau die Zusicherung, die dem entfernten Pfad fehlte."""
        import inspect

        quelle = inspect.getsource(build_pos_closing_lines)
        assert "raise ValueError" in quelle
        assert "nicht ausgeglichen" in quelle

    def test_leerer_abschluss_erzeugt_keine_buchung(self):
        assert build_pos_closing_lines(_amounts()) == []
