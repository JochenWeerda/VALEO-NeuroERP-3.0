"""Reine Logik-Tests des Supply-Chain-Traceability-Service (ohne DB).

Deckt Mengen-Konsistenz (Schwund/Differenz über Toleranz) und Lücken-Erkennung ab.
"""

from __future__ import annotations

import pytest

from app.services.supply_chain_trace_service import SupplyChainTraceService

pytestmark = pytest.mark.unit


def _svc() -> SupplyChainTraceService:
    # db wird in den getesteten reinen Methoden nicht benutzt.
    return SupplyChainTraceService(db=None, tenant_id="t")  # type: ignore[arg-type]


def test_mengen_check_innerhalb_toleranz():
    nodes = [
        {"label": "Wiegung", "menge_kg": 25000.0},
        {"label": "Lager (Silo-Lot)", "menge_kg": 25000.0},
    ]
    checks = _svc()._mengen_check(nodes)
    assert len(checks) == 1
    assert checks[0]["abweichung"] is False
    assert checks[0]["differenz_pct"] == 0.0


def test_mengen_check_schwund_ueber_toleranz():
    nodes = [
        {"label": "Wiegung", "menge_kg": 25000.0},
        {"label": "Lager (Silo-Lot)", "menge_kg": 23000.0},  # -8 % > 2 %
    ]
    checks = _svc()._mengen_check(nodes)
    assert checks[0]["abweichung"] is True
    assert checks[0]["differenz_kg"] == -2000.0
    assert checks[0]["differenz_pct"] < 0


def test_mengen_check_ignoriert_stufen_ohne_menge():
    nodes = [
        {"label": "Wiegung", "menge_kg": 25000.0},
        {"label": "Annahme", "menge_kg": None},   # wird übersprungen
        {"label": "Lager (Silo-Lot)", "menge_kg": 25000.0},
    ]
    checks = _svc()._mengen_check(nodes)
    # Nur Wiegung↔Lager vergleichbar (Annahme hat keine Menge)
    assert len(checks) == 1
    assert checks[0]["von"] == "Wiegung" and checks[0]["nach"] == "Lager (Silo-Lot)"


def test_luecken_meldet_fehlende_stufen_und_status():
    wiegung = {"facts": {"allokation": "unallocated"}}
    annahmen = [{"ref": "EA-1", "status": "draft"}]
    luecken = _svc()._luecken(wiegung, annahmen, lager=[], abrechnungen=[])
    stufen = {l["stufe"] for l in luecken}
    assert "wiegung" in stufen      # unallocated
    assert "lager" in stufen        # fehlt
    assert "abrechnung" in stufen   # fehlt
    assert any("nicht freigegeben" in l["text"] for l in luecken)


def test_luecken_vollstaendige_kette_nur_minimal():
    wiegung = {"facts": {"allokation": "allocated"}}
    annahmen = [{"ref": "EA-1", "status": "released"}]
    lager = [{"ref": "LOT-1"}]
    abrechnungen = [{"ref": "AB-1"}]
    luecken = _svc()._luecken(wiegung, annahmen, lager, abrechnungen)
    assert luecken == []
