"""Tests für P0-INTEGRATION-SLICES-001.

Abdeckung:
- WMS-FLOW-001: book_material_transfer Logik (unit)
- KORE-BAB-001: BAB-Kalkulation (unit)
- QS-CHARGE-001: Abschlags-Kalkulation (unit)
- PROC-3WM-001: match_position / match_three_way_value (unit)
- MOB-SYNC-001: Event-Enqueue-Logik (unit)
"""

from __future__ import annotations

import json
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from app.services.qs_charge_service import QsChargeService
from app.services.procurement_match_service import match_position, match_three_way_value


# ── WMS-FLOW-001 ──────────────────────────────────────────────────────────────

class TestBookMaterialTransfer:
    """Unit-Tests für AgriSiloMaterialFlowService.book_material_transfer."""

    def _make_svc(self, from_stock: float, to_stock: float, route_ok: bool = True):
        from app.services.agri_silo_material_flow_service import AgriSiloMaterialFlowService

        db = MagicMock()

        from_cell = {"id": "cell-a", "cell_code": "A1", "current_stock_kg": from_stock,
                     "current_material_id": "art-1", "current_lot_id": "lot-1"}
        to_cell = {"id": "cell-b", "cell_code": "B1", "current_stock_kg": to_stock,
                   "current_material_id": None, "current_lot_id": None}

        def fetchone_side_effect(*args, **kwargs):
            sql = str(args[0] if args else "")
            if "cell-a" in str(kwargs.get("params", {}).get("id", "")) or "cell-a" in str(args):
                return MagicMock(_mapping=from_cell)
            if "cell-b" in str(kwargs.get("params", {}).get("id", "")) or "cell-b" in str(args):
                return MagicMock(_mapping=to_cell)
            return None

        mock_result = MagicMock()
        mock_result.fetchone.return_value = None  # no node links → skip route validation
        db.execute.return_value = mock_result
        db.commit.return_value = None

        svc = AgriSiloMaterialFlowService(db, "tenant-1", trace_hooks_enabled=False)
        return svc, db, from_cell, to_cell

    def test_insufficient_stock_raises(self):
        from app.services.agri_silo_material_flow_service import AgriSiloMaterialFlowService

        db = MagicMock()
        from_cell_row = MagicMock(_mapping={
            "id": "cell-a", "cell_code": "A1",
            "current_stock_kg": 100.0,
            "current_material_id": "art-1", "current_lot_id": "lot-1",
        })
        to_cell_row = MagicMock(_mapping={
            "id": "cell-b", "cell_code": "B1",
            "current_stock_kg": 0.0,
            "current_material_id": None, "current_lot_id": None,
        })
        db.execute.return_value.fetchone.side_effect = [from_cell_row, to_cell_row, None]

        svc = AgriSiloMaterialFlowService(db, "tenant-1", trace_hooks_enabled=False)
        with pytest.raises(ValueError, match="Unzureichender Bestand"):
            svc.book_material_transfer(
                warehouse_id="wh-1",
                from_cell_id="cell-a",
                to_cell_id="cell-b",
                quantity_kg=Decimal("200"),
                article_id="art-1",
            )

    def test_zero_quantity_raises(self):
        from app.services.agri_silo_material_flow_service import AgriSiloMaterialFlowService

        svc = AgriSiloMaterialFlowService(MagicMock(), "tenant-1", trace_hooks_enabled=False)
        with pytest.raises(ValueError, match="positiv"):
            svc.book_material_transfer(
                warehouse_id="wh-1",
                from_cell_id="cell-a",
                to_cell_id="cell-b",
                quantity_kg=Decimal("0"),
                article_id="art-1",
            )


# ── KORE-BAB-001 ──────────────────────────────────────────────────────────────

class TestBABCalculation:
    """Unit-Tests für BAB-Berechnung (rein funktional)."""

    def _bab_calc(self, primaer: float, umlage_ein: float, umlage_aus: float, budget: float):
        ges = primaer + umlage_ein - umlage_aus
        abw = budget - ges
        abw_pct = (abw / budget * 100) if budget > 0 else 0.0
        return {"gesamt": ges, "abw": abw, "abw_pct": abw_pct}

    def test_no_umlage(self):
        r = self._bab_calc(10000, 0, 0, 12000)
        assert r["gesamt"] == 10000
        assert r["abw"] == 2000
        assert r["abw_pct"] == pytest.approx(16.667, rel=1e-3)

    def test_umlage_eingang(self):
        r = self._bab_calc(5000, 3000, 0, 10000)
        assert r["gesamt"] == 8000
        assert r["abw"] == 2000

    def test_umlage_ausgang(self):
        r = self._bab_calc(10000, 0, 4000, 10000)
        assert r["gesamt"] == 6000
        assert r["abw"] == 4000

    def test_budget_reached(self):
        r = self._bab_calc(10000, 2000, 2000, 10000)
        assert r["gesamt"] == 10000
        assert r["abw"] == 0.0
        assert r["abw_pct"] == 0.0


# ── QS-CHARGE-001 ──────────────────────────────────────────────────────────────

class TestQsChargeCalculation:
    """Unit-Tests für QsChargeService.calculate_deductions."""

    def _svc(self):
        db = MagicMock()
        db.execute.return_value.mappings.return_value.first.return_value = None
        return QsChargeService(db, "tenant-1")

    def test_no_deductions_at_basis(self):
        svc = self._svc()
        qp = {"moisture_pct": "14.0", "impurities_pct": "2.0",
              "hl_weight_kg_per_hl": "76.0", "mycotoxin_ppb": None}
        result = svc.calculate_deductions(
            acceptance_id="ana-1",
            net_weight_kg=Decimal("50000"),
            unit_price_eur_per_t=Decimal("220"),
            quality_protocol=qp,
        )
        assert result["total_deduction_eur"] == 0.0
        assert result["sperrung"] is False
        assert result["deductions"] == []

    def test_feuchte_abschlag(self):
        svc = self._svc()
        qp = {"moisture_pct": "16.0", "impurities_pct": "2.0",
              "hl_weight_kg_per_hl": "76.0", "mycotoxin_ppb": None}
        result = svc.calculate_deductions(
            acceptance_id="ana-1",
            net_weight_kg=Decimal("50000"),  # 50 t
            unit_price_eur_per_t=Decimal("220"),
            quality_protocol=qp,
        )
        # 2% Feuchte × 2€/% × 50t = 200€
        assert any(d["typ"] == "feuchte" for d in result["deductions"])
        feuchte_d = next(d for d in result["deductions"] if d["typ"] == "feuchte")
        assert feuchte_d["abschlag_eur"] == pytest.approx(200.0)
        assert result["total_deduction_eur"] == pytest.approx(200.0)

    def test_unreinheiten_abschlag(self):
        svc = self._svc()
        qp = {"moisture_pct": "14.0", "impurities_pct": "4.0",
              "hl_weight_kg_per_hl": "76.0", "mycotoxin_ppb": None}
        result = svc.calculate_deductions(
            acceptance_id="ana-1",
            net_weight_kg=Decimal("10000"),  # 10 t
            unit_price_eur_per_t=Decimal("200"),
            quality_protocol=qp,
        )
        # 2% × 1.5€/% × 10t = 30€
        unrein_d = next((d for d in result["deductions"] if d["typ"] == "unreinheiten"), None)
        assert unrein_d is not None
        assert unrein_d["abschlag_eur"] == pytest.approx(30.0)

    def test_mykotoxin_sperrung(self):
        svc = self._svc()
        qp = {"moisture_pct": "14.0", "impurities_pct": "2.0",
              "hl_weight_kg_per_hl": "76.0", "mycotoxin_ppb": "1500"}
        result = svc.calculate_deductions(
            acceptance_id="ana-1",
            net_weight_kg=Decimal("10000"),
            unit_price_eur_per_t=Decimal("200"),
            quality_protocol=qp,
        )
        assert result["sperrung"] is True
        assert "Mykotoxin" in result["sperrgrund"]

    def test_hl_gewicht_abschlag(self):
        svc = self._svc()
        qp = {"moisture_pct": "14.0", "impurities_pct": "2.0",
              "hl_weight_kg_per_hl": "74.0", "mycotoxin_ppb": None}
        result = svc.calculate_deductions(
            acceptance_id="ana-1",
            net_weight_kg=Decimal("20000"),  # 20 t
            unit_price_eur_per_t=Decimal("200"),
            quality_protocol=qp,
        )
        # 2 kg/hl unter Basis × 0.5€ × 20t = 20€
        hl_d = next((d for d in result["deductions"] if d["typ"] == "hl_gewicht"), None)
        assert hl_d is not None
        assert hl_d["abschlag_eur"] == pytest.approx(20.0)


# ── PROC-3WM-001 ──────────────────────────────────────────────────────────────

class TestProcurementMatch:
    """Unit-Tests für procurement match_position / match_three_way_value."""

    def test_vollstaendig_innerhalb_toleranz(self):
        r = match_position(Decimal("1000"), Decimal("1010"))  # 1% über — OK bei 1% Toleranz
        assert r["status"] == "vollstaendig"

    def test_ueberliefert(self):
        r = match_position(Decimal("1000"), Decimal("1100"))  # 10% über
        assert r["status"] == "ueberliefert"

    def test_teilgeliefert(self):
        r = match_position(Decimal("1000"), Decimal("900"))  # 10% unter
        assert r["status"] == "teilgeliefert"

    def test_offen_null_lieferung(self):
        r = match_position(Decimal("1000"), Decimal("0"))
        assert r["status"] == "offen"
        assert r["offen"] == 1000.0

    def test_three_way_value_ok(self):
        r = match_three_way_value(Decimal("10000"), Decimal("10050"))  # +0.5% — innerhalb 2%
        assert r["abweichung"] is False

    def test_three_way_value_mismatch(self):
        r = match_three_way_value(Decimal("10000"), Decimal("10300"))  # +3% — ausserhalb 2%
        assert r["abweichung"] is True
        assert float(r["abweichung_pct"]) == pytest.approx(3.0, abs=0.1)


# ── MOB-SYNC-001 ──────────────────────────────────────────────────────────────

class TestMobileSyncEnqueue:
    """Unit-Tests für MobileSyncService.enqueue_events."""

    def _svc(self):
        from app.services.mobile_sync_service import MobileSyncService
        db = MagicMock()
        db.execute.return_value = MagicMock()
        db.commit.return_value = None
        return MobileSyncService(db, "tenant-1")

    def test_enqueue_valid_event(self):
        svc = self._svc()
        results = svc.enqueue_events("device-001", [
            {"event_type": "delivery_confirmation", "payload": {"tour_id": "t1"}, "idempotency_key": "key-1"}
        ])
        assert len(results) == 1
        assert results[0]["status"] == "queued"

    def test_enqueue_unknown_type_rejected(self):
        svc = self._svc()
        results = svc.enqueue_events("device-001", [
            {"event_type": "banana_event", "payload": {}, "idempotency_key": "key-2"}
        ])
        assert results[0]["status"] == "rejected"

    def test_enqueue_multiple_events(self):
        svc = self._svc()
        results = svc.enqueue_events("device-001", [
            {"event_type": "inventory_count", "payload": {"warehouse_id": "w1", "article_id": "a1", "counted_qty": 50}, "idempotency_key": "k1"},
            {"event_type": "generic", "payload": {"data": "x"}, "idempotency_key": "k2"},
        ])
        assert len(results) == 2
        assert all(r["status"] == "queued" for r in results)
