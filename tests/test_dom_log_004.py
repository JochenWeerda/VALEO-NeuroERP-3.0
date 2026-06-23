"""DOM-LOG-004 Unit Tests — Disposition-Service (.2) + ePOD-Service (.3)."""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch


def _mock_execute(sql_results: dict):
    """Build a db mock whose execute() dispatches on SQL keywords.

    sql_results maps keyword → return value:
      - list  → .mappings().all() returns it
      - dict  → .mappings().first() returns it
      - None  → .mappings().first() returns None
    """
    db = MagicMock()

    def side_effect(stmt, params=None):
        sql = str(stmt)
        m = MagicMock()
        for keyword, value in sql_results.items():
            if keyword in sql:
                if isinstance(value, list):
                    m.mappings.return_value.all.return_value = value
                    m.mappings.return_value.first.return_value = value[0] if value else None
                else:
                    m.mappings.return_value.first.return_value = value
                    m.mappings.return_value.all.return_value = [value] if value is not None else []
                return m
        m.mappings.return_value.first.return_value = None
        m.mappings.return_value.all.return_value = []
        return m

    db.execute.side_effect = side_effect
    return db


# ---------------------------------------------------------------------------
# Disposition Service
# ---------------------------------------------------------------------------

class TestDispositionService:
    def test_no_weight_data_returns_no_weight_data(self):
        from app.services.logistics_disposition_service import check_tour_disposition
        stop = {"id": "s1", "tour_id": "t1", "stop_order": 0, "delivery_note_ref": None, "planned_arrival": None}
        db = _mock_execute({"tour_stops": [stop]})
        result = check_tour_disposition(db, "t1", "tenant1")
        assert result["result"] == "NO_WEIGHT_DATA"
        assert result["total_weight_kg"] == 0.0

    def test_within_capacity_returns_ok(self):
        from app.services.logistics_disposition_service import check_tour_disposition
        stop = {"id": "s1", "tour_id": "t1", "stop_order": 0, "delivery_note_ref": "DN-001", "planned_arrival": None}
        dn_row = {"total_weight_kg": 5000.0}
        db = _mock_execute({"tour_stops": [stop], "delivery_notes": dn_row})
        result = check_tour_disposition(db, "t1", "tenant1", capacity_kg=20000.0)
        assert result["result"] == "OK"
        assert result["utilization_pct"] == pytest.approx(25.0)

    def test_overloaded_raises(self):
        from app.services.logistics_disposition_service import check_tour_disposition, DispositionError
        stop = {"id": "s1", "tour_id": "t1", "stop_order": 0, "delivery_note_ref": "DN-001", "planned_arrival": None}
        dn_row = {"total_weight_kg": 25000.0}
        db = _mock_execute({"tour_stops": [stop], "delivery_notes": dn_row})
        with pytest.raises(DispositionError, match="überbucht"):
            check_tour_disposition(db, "t1", "tenant1", capacity_kg=20000.0)

    def test_time_window_violation_raises(self):
        from app.services.logistics_disposition_service import check_tour_disposition, DispositionError
        from datetime import datetime
        stops = [
            {"id": "s1", "stop_order": 0, "delivery_note_ref": None, "planned_arrival": datetime(2026, 6, 23, 10, 0)},
            {"id": "s2", "stop_order": 1, "delivery_note_ref": None, "planned_arrival": datetime(2026, 6, 23, 9, 0)},
        ]
        db = _mock_execute({"tour_stops": stops})
        with pytest.raises(DispositionError, match="Zeitfenster"):
            check_tour_disposition(db, "t1", "tenant1")

    def test_empty_tour_returns_no_weight_data(self):
        from app.services.logistics_disposition_service import check_tour_disposition
        db = _mock_execute({"tour_stops": []})
        result = check_tour_disposition(db, "t1", "tenant1")
        assert result["stops_count"] == 0
        assert result["result"] == "NO_WEIGHT_DATA"


# ---------------------------------------------------------------------------
# ePOD Settlement Service
# ---------------------------------------------------------------------------

class TestEpodService:
    def test_settle_geliefert_stop_succeeds(self):
        from app.services.logistics_epod_service import settle_epod
        stop_data = {"id": "stop-1", "tour_id": "tour-1", "status": "GELIEFERT", "epod_status": None}
        db = _mock_execute({"tour_stops": stop_data, "epod_settlements": None})
        result = settle_epod(db, "tour-1", "stop-1", "tenant1", recipient_name="Test")
        assert result["epod_status"] == "SETTLED"
        db.commit.assert_called_once()

    def test_settle_wrong_status_raises(self):
        from app.services.logistics_epod_service import settle_epod, EpodError
        stop_data = {"id": "stop-1", "tour_id": "tour-1", "status": "GEPLANT", "epod_status": None}
        db = _mock_execute({"tour_stops": stop_data, "epod_settlements": None})
        with pytest.raises(EpodError, match="GELIEFERT"):
            settle_epod(db, "tour-1", "stop-1", "tenant1")

    def test_idempotent_returns_existing(self):
        from app.services.logistics_epod_service import settle_epod
        stop_data = {"id": "stop-1", "tour_id": "tour-1", "status": "SIGNED", "epod_status": "SIGNED"}
        existing = {"id": "settle-existing", "tour_id": "tour-1", "stop_id": "stop-1"}
        db = _mock_execute({"tour_stops": stop_data, "epod_settlements": existing})
        result = settle_epod(db, "tour-1", "stop-1", "tenant1")
        assert result["id"] == "settle-existing"
        db.commit.assert_not_called()

    def test_missing_stop_raises(self):
        from app.services.logistics_epod_service import settle_epod, EpodError
        db = _mock_execute({"tour_stops": None})
        with pytest.raises(EpodError, match="nicht gefunden"):
            settle_epod(db, "tour-1", "stop-missing", "tenant1")
