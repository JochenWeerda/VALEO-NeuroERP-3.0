"""Unit-Tests ERS-Gutschriftsverfahren (DOM-PROC-004.5)."""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.services.procurement_match_service import (
    ProcurementMatchService,
    calculate_ers_credit,
)

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


def test_create_ers_rejects_without_basis():
    svc = ProcurementMatchService(MagicMock(), "tenant-demo")
    svc.match_three_way = MagicMock(return_value={
        "found": True,
        "bestellnummer": "DEMO-PO-001",
        "positionen": [{"status": "vollstaendig", "offen": 0}],
        "three_way": {"status": "abgeglichen", "abweichung": False},
        "ausnahmen": [],
    })
    with pytest.raises(ValueError, match="Keine ERS-Gutschrift berechtigt"):
        svc.create_ers_credit(bestellnummer="DEMO-PO-001")
