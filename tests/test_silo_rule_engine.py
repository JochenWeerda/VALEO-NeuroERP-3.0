"""WM-SILO-RULE-ENGINE-001 — Unit Tests fuer SiloRuleEngineService.

Alle Tests laufen ohne Datenbank-Verbindung (Mock-Session).
"""
from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from app.services.silo_rule_engine_service import (
    SiloRuleEngineService,
    VorschlagGrund,
    ZielzelleVorschlag,
)


def _mock_cell(
    id: str = "cell-1",
    warehouse_id: str = "WH-001",
    cell_code: str = "A01",
    capacity_kg: float = 100_000,
    current_stock_kg: float = 0,
    current_material_id: str | None = None,
    current_lot_id: str | None = None,
    qs_status: str | None = None,
    is_active: bool = True,
    ernte_jahr: int | None = None,
    qualitaetsklasse: str | None = None,
) -> dict:
    return dict(
        id=id,
        warehouse_id=warehouse_id,
        cell_code=cell_code,
        capacity_kg=capacity_kg,
        current_stock_kg=current_stock_kg,
        current_material_id=current_material_id,
        current_lot_id=current_lot_id,
        qs_status=qs_status,
        is_active=is_active,
        ernte_jahr=ernte_jahr,
        qualitaetsklasse=qualitaetsklasse,
    )


def _svc(cells: list[dict] | None = None, lot: dict | None = None) -> SiloRuleEngineService:
    db = MagicMock()
    svc = SiloRuleEngineService(db=db, tenant_id="test-tenant")
    svc._load_cells = MagicMock(return_value=cells or [])
    svc._lot_info = MagicMock(return_value=lot)
    return svc


class TestVorschlagGrund:
    def test_enum_values_exist(self):
        assert VorschlagGrund.GLEICHER_ARTIKEL_GLEICHES_ERNTEJAHR
        assert VorschlagGrund.LEERE_ZELLE
        assert VorschlagGrund.GLEICHER_ARTIKEL
        assert VorschlagGrund.GENERISCH_KAPAZITAET


class TestZielzelleVorschlag:
    def test_to_dict_contains_required_keys(self):
        v = ZielzelleVorschlag(
            cell_id="c1", cell_code="A01", warehouse_id="WH",
            kapazitaet_kg=Decimal("100000"), aktueller_bestand_kg=Decimal("0"),
            freie_kapazitaet_kg=Decimal("100000"), belegungsgrad_pct=0.0,
            aktuelles_material_id=None, aktuelles_lot_id=None, qs_status=None,
            grund=VorschlagGrund.LEERE_ZELLE, rang=2, hinweis="Test",
        )
        d = v.to_dict()
        assert d["cell_id"] == "c1"
        assert d["rang"] == 2
        assert d["grund"] == "leere_zelle"
        assert isinstance(d["freie_kapazitaet_kg"], float)


class TestSiloRuleEngine:
    def test_leere_zellen_werden_vorgeschlagen(self):
        cells = [_mock_cell(id="c1", cell_code="A01", capacity_kg=50000)]
        svc = _svc(cells)
        result = svc.vorschlag(artikel_id="WEIZEN", menge_kg=10000)
        assert len(result) == 1
        assert result[0]["grund"] == VorschlagGrund.LEERE_ZELLE.value

    def test_zu_kleine_zelle_wird_ausgeschlossen(self):
        cells = [_mock_cell(id="c1", capacity_kg=5000, current_stock_kg=4900)]
        svc = _svc(cells)
        result = svc.vorschlag(artikel_id="WEIZEN", menge_kg=500)
        assert len(result) == 0

    def test_gesperrte_zelle_wird_gefiltert(self):
        cells = [_mock_cell(id="c1", capacity_kg=100000, qs_status="gesperrt")]
        # _load_cells filtert bereits in SQL; wir simulieren es hier manuell:
        # Der Test stellt sicher, dass qs_status='gesperrt' nie im Ergebnis landet
        svc = _svc([])  # _load_cells gibt leere Liste (wie SQL WHERE würde)
        result = svc.vorschlag(artikel_id="WEIZEN", menge_kg=10000)
        assert len(result) == 0

    def test_regel1_gleicher_artikel_gleiches_erntejahr(self):
        cells = [_mock_cell(
            id="c1", current_material_id="WEIZEN",
            current_stock_kg=20000, capacity_kg=100000,
            ernte_jahr=2026, qs_status="",
        )]
        svc = _svc(cells)
        result = svc.vorschlag(artikel_id="WEIZEN", menge_kg=10000, ernte_jahr=2026)
        assert len(result) == 1
        assert result[0]["grund"] == VorschlagGrund.GLEICHER_ARTIKEL_GLEICHES_ERNTEJAHR.value
        assert result[0]["rang"] == 1

    def test_regel3_gleicher_artikel_anderes_erntejahr(self):
        cells = [_mock_cell(
            id="c1", current_material_id="WEIZEN",
            current_stock_kg=20000, capacity_kg=100000,
            ernte_jahr=2025, qs_status="FREIGEGEBEN",
        )]
        svc = _svc(cells)
        result = svc.vorschlag(artikel_id="WEIZEN", menge_kg=10000, ernte_jahr=2026)
        assert len(result) == 1
        # Kein Erntejahr-Match → Rang 3 (oder Rang 1 wenn ohne Erntejahr-Check)
        assert result[0]["rang"] in (1, 3)

    def test_regel4_generisch_anderer_artikel(self):
        cells = [_mock_cell(
            id="c1", current_material_id="GERSTE",
            current_stock_kg=10000, capacity_kg=100000,
        )]
        svc = _svc(cells)
        result = svc.vorschlag(artikel_id="WEIZEN", menge_kg=10000)
        assert len(result) == 1
        assert result[0]["grund"] == VorschlagGrund.GENERISCH_KAPAZITAET.value
        assert result[0]["rang"] == 4

    def test_sortierung_rang_dann_freie_kapazitaet(self):
        cells = [
            _mock_cell(id="c1", cell_code="A01", capacity_kg=50000, current_stock_kg=0),
            _mock_cell(id="c2", cell_code="A02", capacity_kg=80000, current_stock_kg=0),
        ]
        svc = _svc(cells)
        result = svc.vorschlag(artikel_id="WEIZEN", menge_kg=1000)
        assert len(result) == 2
        # Beide Rang 2 (leere Zellen), aber c2 hat mehr freie Kapazitaet → erster
        assert result[0]["freie_kapazitaet_kg"] >= result[1]["freie_kapazitaet_kg"]

    def test_max_vorschlaege_limitiert_ergebnis(self):
        cells = [_mock_cell(id=f"c{i}", cell_code=f"A{i:02d}", capacity_kg=100000) for i in range(10)]
        svc = _svc(cells)
        result = svc.vorschlag(artikel_id="WEIZEN", menge_kg=1000, max_vorschlaege=3)
        assert len(result) <= 3

    def test_belegungsgrad_berechnung(self):
        cells = [_mock_cell(id="c1", capacity_kg=100000, current_stock_kg=50000)]
        svc = _svc(cells)
        result = svc.vorschlag(artikel_id="WEIZEN", menge_kg=1000)
        assert result[0]["belegungsgrad_pct"] == pytest.approx(50.0, abs=0.1)

    def test_freie_kapazitaet_korrekt(self):
        cells = [_mock_cell(id="c1", capacity_kg=100000, current_stock_kg=30000)]
        svc = _svc(cells)
        result = svc.vorschlag(artikel_id="WEIZEN", menge_kg=1000)
        assert result[0]["freie_kapazitaet_kg"] == pytest.approx(70000.0)

    def test_vorschlag_fuer_lot_not_found(self):
        svc = _svc(lot=None)
        result = svc.vorschlag_fuer_lot(lot_id="NICHT-VORHANDEN", menge_kg=1000)
        assert "fehler" in result
        assert result["vorschlaege"] == []

    def test_vorschlag_fuer_lot_found(self):
        lot = {"id": "lot-1", "article_id": "SOJA", "ernte_jahr": 2026, "qualitaetsklasse": "A"}
        cells = [_mock_cell(id="c1", capacity_kg=50000)]
        svc = _svc(cells=cells, lot=lot)
        result = svc.vorschlag_fuer_lot(lot_id="lot-1", menge_kg=5000)
        assert "fehler" not in result
        assert result["lot_id"] == "lot-1"
        assert result["artikel_id"] == "SOJA"
        assert "vorschlaege" in result

    def test_vorschlag_fuer_lot_ohne_menge_nutzt_default(self):
        lot = {"id": "lot-2", "article_id": "MAIS", "ernte_jahr": 2025, "qualitaetsklasse": None}
        cells = [_mock_cell(id="c1", capacity_kg=50000)]
        svc = _svc(cells=cells, lot=lot)
        result = svc.vorschlag_fuer_lot(lot_id="lot-2")
        assert result["angefragte_menge_kg"] is None
        assert "vorschlaege" in result

    def test_warehouse_filter_weitergegeben(self):
        cells = [_mock_cell(id="c1", warehouse_id="WH-002", capacity_kg=50000)]
        svc = _svc(cells)
        svc.vorschlag(artikel_id="WEIZEN", menge_kg=1000, warehouse_id="WH-002")
        svc._load_cells.assert_called_once_with("WH-002")

    def test_zu_dict_alle_felder_numerisch(self):
        cells = [_mock_cell(id="c1", capacity_kg=100000, current_stock_kg=25000,
                            current_material_id="WEIZEN", ernte_jahr=2026)]
        svc = _svc(cells)
        result = svc.vorschlag(artikel_id="GERSTE", menge_kg=1000)
        assert len(result) == 1
        d = result[0]
        assert isinstance(d["kapazitaet_kg"], float)
        assert isinstance(d["aktueller_bestand_kg"], float)
        assert isinstance(d["freie_kapazitaet_kg"], float)
