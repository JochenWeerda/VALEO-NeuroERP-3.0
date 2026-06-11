"""Reine Logik-Tests ERS-Gutschriftsverfahren (DOM-PROC-004.5) — ohne DB/Mocks.

Persistenz und API werden in tests/test_procurement_match_integration.py abgedeckt.
"""

from __future__ import annotations

import pytest

from app.services.procurement_match_service import calculate_ers_credit

pytestmark = pytest.mark.unit


def test_ers_ueberlieferung():
    preview = calculate_ers_credit([
        {
            "pos_nr": 1,
            "artikel_nr": "RAPS-00",
            "status": "ueberliefert",
            "offen": -2.0,
            "einzelpreis": 480.0,
        },
    ])
    assert preview["berechtigt"] is True
    assert preview["betrag_netto"] == 960.0
    assert preview["anzahl_zeilen"] == 1


def test_ers_rechnungsueberzahlung():
    preview = calculate_ers_credit(
        [{"pos_nr": 1, "status": "vollstaendig", "offen": 0, "einzelpreis": 100}],
        {"status": "wertabweichung", "abweichung": True, "differenz": 500.0, "bezug": 1000, "fakturiert": 1500},
    )
    assert preview["berechtigt"] is True
    assert preview["betrag_netto"] == 500.0


def test_ers_nicht_berechtigt():
    preview = calculate_ers_credit([
        {"pos_nr": 1, "status": "vollstaendig", "offen": 0, "einzelpreis": 100},
    ])
    assert preview["berechtigt"] is False
    assert preview["betrag_netto"] == 0.0
