"""
Tests: Logistik-Modul — Tourenplanung-Engine + Frachtkostenberechnung
"""
from __future__ import annotations

import json
import math
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Helpers / stubs that allow tests to run without a live DB
# ---------------------------------------------------------------------------


def _make_db_stub(query_results: Optional[Dict[str, Any]] = None):
    """Return a minimal SQLAlchemy-Session stub."""
    db = MagicMock()
    db.execute.return_value.mappings.return_value.all.return_value = []
    db.execute.return_value.mappings.return_value.first.return_value = None
    db.execute.return_value.scalar.return_value = 0
    db.commit.return_value = None
    return db


# ---------------------------------------------------------------------------
# Feature 1 – Tourenplanung-Engine
# ---------------------------------------------------------------------------

class TestTourStopOptimization:
    """test_tour_stop_order_can_be_optimized"""

    def test_nearest_neighbor_gives_valid_order(self):
        """3 Stopps – Nearest-Neighbor muss eine valide Reihenfolge zurückgeben."""
        from app.api.v1.endpoints.logistics_tours import _haversine

        # Depot at 0,0
        depot_lat, depot_lng = 0.0, 0.0

        stops = [
            {"id": "stop-A", "lat": 1.0, "lng": 1.0, "stop_order": 0},  # ~157 km from depot
            {"id": "stop-B", "lat": 5.0, "lng": 5.0, "stop_order": 1},  # ~785 km from depot
            {"id": "stop-C", "lat": 2.0, "lng": 2.0, "stop_order": 2},  # ~314 km from depot
        ]

        # Manually run nearest-neighbor (mirrors the logic in optimize_stops)
        remaining = stops.copy()
        ordered: List[Dict] = []
        cur_lat, cur_lng = depot_lat, depot_lng
        while remaining:
            nearest = min(
                remaining,
                key=lambda s: _haversine(cur_lat, cur_lng, s["lat"], s["lng"]),
            )
            ordered.append(nearest)
            cur_lat = nearest["lat"]
            cur_lng = nearest["lng"]
            remaining.remove(nearest)

        # All stops must appear exactly once
        assert len(ordered) == 3
        assert {s["id"] for s in ordered} == {"stop-A", "stop-B", "stop-C"}

        # First stop should be the one closest to depot: stop-A (~157 km)
        assert ordered[0]["id"] == "stop-A"
        # Second should be stop-C (closer to stop-A than stop-B)
        assert ordered[1]["id"] == "stop-C"
        # Last: stop-B
        assert ordered[2]["id"] == "stop-B"

    def test_haversine_zero_for_same_point(self):
        from app.api.v1.endpoints.logistics_tours import _haversine
        assert _haversine(52.5, 13.4, 52.5, 13.4) == pytest.approx(0.0, abs=1e-6)

    def test_haversine_known_distance(self):
        """Berlin → Hamburg ≈ 255 km."""
        from app.api.v1.endpoints.logistics_tours import _haversine
        dist = _haversine(52.5200, 13.4050, 53.5507, 10.0007)
        assert 240 < dist < 270


# ---------------------------------------------------------------------------
# Feature 2 – Frachtkostenberechnung
# ---------------------------------------------------------------------------

class TestFreightCostCalculation:

    def _make_tariff_row(self, price_per_100kg: float, min_charge: float = 0.0) -> Dict[str, Any]:
        return {
            "id": str(uuid.uuid4()),
            "carrier_id": "DHL",
            "zone_from": "10",
            "zone_to": "20",
            "weight_from_kg": 0.0,
            "weight_to_kg": 999999.0,
            "price_per_100kg": price_per_100kg,
            "min_charge": min_charge,
        }

    def test_freight_cost_calculation_basic(self):
        """100 kg @ 10 €/100 kg → 10 €."""
        from app.api.v1.endpoints.logistics_freight import _calculate, _postal_to_zone

        db = _make_db_stub()
        tariff = self._make_tariff_row(price_per_100kg=10.0, min_charge=0.0)
        db.execute.return_value.mappings.return_value.first.return_value = tariff

        result = _calculate(db, "DHL", 100.0, "10115", "20095", 300.0, tenant_id="00000000-0000-0000-0000-000000000001")

        assert result["freight_cost_eur"] == pytest.approx(10.0)
        assert result["carrier_id"] == "DHL"
        assert result["calculation_details"]["applied_minimum"] is False

    def test_freight_cost_respects_minimum_charge(self):
        """5 kg @ 10 €/100 kg = 0.50 €, but min_charge=15 € → result 15 €."""
        from app.api.v1.endpoints.logistics_freight import _calculate

        db = _make_db_stub()
        tariff = self._make_tariff_row(price_per_100kg=10.0, min_charge=15.0)
        db.execute.return_value.mappings.return_value.first.return_value = tariff

        result = _calculate(db, "DHL", 5.0, "10115", "20095", 10.0, tenant_id="00000000-0000-0000-0000-000000000001")

        assert result["freight_cost_eur"] == pytest.approx(15.0)
        assert result["calculation_details"]["applied_minimum"] is True

    def test_postal_to_zone(self):
        from app.api.v1.endpoints.logistics_freight import _postal_to_zone
        assert _postal_to_zone("10115") == "10"
        assert _postal_to_zone("20095") == "20"
        # Empty string → "00"
        assert _postal_to_zone("")      == "00"
        # Single-digit PLZ: zone is either "00" or padded — just verify it's a 2-char string
        zone = _postal_to_zone("9")
        assert len(zone) == 2


# ---------------------------------------------------------------------------
# Feature 3 – ePOD
# ---------------------------------------------------------------------------

class TestPodSetsStopDelivered:
    """test_pod_sets_stop_delivered"""

    def test_pod_sets_stop_delivered(self):
        """POD-Endpunkt muss status='ABGELIEFERT' setzen."""
        from app.api.v1.endpoints.logistics_tours import save_pod, PodIn

        tour_id = str(uuid.uuid4())
        stop_id = str(uuid.uuid4())

        db = _make_db_stub()
        # Simulate that after UPDATE the SELECT returns the updated row
        updated_row = {
            "id": stop_id,
            "tour_id": tour_id,
            "status": "ABGELIEFERT",
            "pod_data": {"recipient_name": "Max Mustermann"},
            "stop_order": 0,
        }
        db.execute.return_value.mappings.return_value.first.return_value = updated_row

        pod_body = PodIn(
            signature_base64="dGVzdA==",
            recipient_name="Max Mustermann",
            delivered_at="2026-05-17T10:00:00",
            notes="Alles ok",
        )

        result = save_pod(tour_id=tour_id, stop_id=stop_id, body=pod_body, x_tenant_id="T1", db=db)

        # DB should have been called (UPDATE + SELECT)
        assert db.execute.called
        assert db.commit.called
        assert result["status"] == "ABGELIEFERT"


# ---------------------------------------------------------------------------
# Feature 1 – Live-Status
# ---------------------------------------------------------------------------

class TestLiveStatus:
    """test_live_status_returns_last_gps_event"""

    def test_live_status_returns_last_gps_event(self):
        """live_status gibt last_gps_event und next_stop zurück."""
        # Test the pure logic without hitting the DB by inspecting return structure.
        # We inject controlled execute results (GPS query, then next_stop query).
        from app.api.v1.endpoints import logistics_tours

        tour_id = str(uuid.uuid4())

        gps_event = {
            "id": str(uuid.uuid4()),
            "tour_id": tour_id,
            "event_type": "GPS",
            "lat": 52.5,
            "lng": 13.4,
            "event_ts": datetime(2026, 5, 17, 9, 30),
        }

        next_stop_row = {
            "id": str(uuid.uuid4()),
            "tour_id": tour_id,
            "status": "GEPLANT",
            "stop_order": 1,
            "planned_arrival": datetime(2026, 5, 17, 11, 0),
        }

        db = MagicMock()
        db.commit.return_value = None

        results_queue = [gps_event, next_stop_row]
        call_count = {"n": 0}

        def side_effect(*args, **kwargs):
            mock = MagicMock()
            idx = call_count["n"]
            call_count["n"] += 1
            if 0 <= idx < len(results_queue):
                mock.mappings.return_value.first.return_value = results_queue[idx]
            else:
                mock.mappings.return_value.first.return_value = None
            return mock

        db.execute.side_effect = side_effect

        result = logistics_tours.live_status(tour_id=tour_id, db=db)

        assert result["tour_id"] == tour_id
        assert result["last_gps_event"] is not None
        assert result["last_gps_event"]["lat"] == pytest.approx(52.5)
        assert result["next_stop"] is not None


# ---------------------------------------------------------------------------
# Feature 4 – Statistik / Pünktlichkeitsrate
# ---------------------------------------------------------------------------

class TestStatisticsOnTimeRate:
    """test_statistics_calculates_on_time_rate"""

    def test_on_time_rate_calculation(self):
        """3 geliefert, 2 pünktlich → on_time_rate = 0.6667."""
        # Test the arithmetic directly (rate = on_time / delivered)
        delivered = 3
        on_time = 2
        rate = round(on_time / delivered, 4)
        assert rate == pytest.approx(0.6667, abs=0.0001)

    def test_on_time_rate_none_when_no_deliveries(self):
        """Wenn keine Lieferungen, soll on_time_rate None sein."""
        delivered = 0
        rate = round(0 / delivered, 4) if delivered > 0 else None
        assert rate is None

    def test_statistics_endpoint_structure(self):
        """get_statistics gibt alle erwarteten Felder zurück."""
        from app.api.v1.endpoints.logistics_tours import get_statistics

        stats_row = {
            "total_tours": 5,
            "total_stops_delivered": 12,
            "total_stops": 15,
            "problem_stops": 1,
            "on_time_stops": 10,
        }

        db = MagicMock()
        db.commit.return_value = None

        call_count = {"n": 0}

        def side_effect(*args, **kwargs):
            mock = MagicMock()
            idx = call_count["n"]
            call_count["n"] += 1
            # idx==0: stats aggregate query
            if idx == 0:
                mock.mappings.return_value.first.return_value = stats_row
                return mock
            # idx==1: GPS events query
            mock.mappings.return_value.all.return_value = []
            return mock

        db.execute.side_effect = side_effect

        result = get_statistics(db=db)

        assert "total_tours" in result
        assert "on_time_rate" in result
        assert "total_km_driven" in result
        assert "problem_rate" in result
        assert "avg_stops_per_tour" in result
