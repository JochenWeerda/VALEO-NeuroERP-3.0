"""DOM-LOG-004 Unit Tests — Disposition-Service (.2) + ePOD-Service (.3)."""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Disposition Service
# ---------------------------------------------------------------------------

class TestDispositionService:
    def _make_db(self, stops=None, weight=None):
        db = MagicMock()
        stop_rows = stops or []

        def execute_side_effect(stmt, params=None):
            sql = str(stmt)
            m = MagicMock()
            if "tour_stops" in sql and "SELECT" in sql:
                m.mappings.return_value.all.return_value = stop_rows
            elif "delivery_notes" in sql:
                row = MagicMock()
                row.get = lambda k, d=None: weight if k == "total_weight_kg" else d
                m.mappings.return_value.first.return_value = row if weight is not None else None
            else:
                # INSERT into tour_disposition_checks — no return needed
                m.mappings.return_value.all.return_value = []
                m.mappings.return_value.first.return_value = None
            return m

        db.execute.side_effect = execute_side_effect
        return db

    def test_no_weight_data_returns_ok(self):
        from app.services.logistics_disposition_service import check_tour_disposition
        stop = {"id": "s1", "tour_id": "t1", "stop_order": 0, "delivery_note_ref": None, "planned_arrival": None}
        db = self._make_db(stops=[stop])
        result = check_tour_disposition(db, "t1", "tenant1")
        assert result["result"] == "NO_WEIGHT_DATA"
        assert result["total_weight_kg"] == 0.0

    def test_within_capacity_returns_ok(self):
        from app.services.logistics_disposition_service import check_tour_disposition
        stop = {"id": "s1", "tour_id": "t1", "stop_order": 0, "delivery_note_ref": "DN-001", "planned_arrival": None}
        db = self._make_db(stops=[stop], weight=5000.0)
        result = check_tour_disposition(db, "t1", "tenant1", capacity_kg=20000.0)
        assert result["result"] == "OK"
        assert result["utilization_pct"] == pytest.approx(25.0)

    def test_overloaded_raises(self):
        from app.services.logistics_disposition_service import check_tour_disposition, DispositionError
        stop = {"id": "s1", "tour_id": "t1", "stop_order": 0, "delivery_note_ref": "DN-001", "planned_arrival": None}
        db = self._make_db(stops=[stop], weight=25000.0)
        with pytest.raises(DispositionError, match="überbucht"):
            check_tour_disposition(db, "t1", "tenant1", capacity_kg=20000.0)

    def test_time_window_violation_raises(self):
        from app.services.logistics_disposition_service import check_tour_disposition, DispositionError
        from datetime import datetime
        stops = [
            {"id": "s1", "stop_order": 0, "delivery_note_ref": None,
             "planned_arrival": datetime(2026, 6, 23, 10, 0)},
            {"id": "s2", "stop_order": 1, "delivery_note_ref": None,
             "planned_arrival": datetime(2026, 6, 23, 9, 0)},  # earlier than s1 — violation
        ]
        db = self._make_db(stops=stops)
        with pytest.raises(DispositionError, match="Zeitfenster"):
            check_tour_disposition(db, "t1", "tenant1")

    def test_empty_tour_returns_no_weight_data(self):
        from app.services.logistics_disposition_service import check_tour_disposition
        db = self._make_db(stops=[])
        result = check_tour_disposition(db, "t1", "tenant1")
        assert result["stops_count"] == 0
        assert result["result"] == "NO_WEIGHT_DATA"


# ---------------------------------------------------------------------------
# ePOD Settlement Service
# ---------------------------------------------------------------------------

class TestEpodService:
    def _make_db(self, stop_status="GELIEFERT", existing_settlement=None):
        db = MagicMock()

        def execute_side_effect(stmt, params=None):
            sql = str(stmt)
            m = MagicMock()
            if "tour_stops" in sql and "SELECT" in sql:
                row = MagicMock()
                row.get = lambda k, d=None: {
                    "id": "stop-1", "tour_id": "tour-1",
                    "status": stop_status, "epod_status": None,
                }.get(k, d)
                m.mappings.return_value.first.return_value = row
            elif "epod_settlements" in sql and "SELECT" in sql:
                m.mappings.return_value.first.return_value = existing_settlement
            else:
                m.mappings.return_value.first.return_value = None
            return m

        db.execute.side_effect = execute_side_effect
        return db

    def test_settle_geliefert_stop_succeeds(self):
        from app.services.logistics_epod_service import settle_epod
        db = self._make_db(stop_status="GELIEFERT")
        result = settle_epod(db, "tour-1", "stop-1", "tenant1", recipient_name="Test")
        assert result["epod_status"] == "SETTLED"
        db.commit.assert_called_once()

    def test_settle_wrong_status_raises(self):
        from app.services.logistics_epod_service import settle_epod, EpodError
        db = self._make_db(stop_status="GEPLANT")
        with pytest.raises(EpodError, match="GELIEFERT"):
            settle_epod(db, "tour-1", "stop-1", "tenant1")

    def test_idempotent_returns_existing(self):
        from app.services.logistics_epod_service import settle_epod
        existing = {"id": "settle-existing", "tour_id": "tour-1", "stop_id": "stop-1"}
        db = self._make_db(stop_status="SIGNED", existing_settlement=existing)
        result = settle_epod(db, "tour-1", "stop-1", "tenant1")
        assert result["id"] == "settle-existing"
        db.commit.assert_not_called()

    def test_missing_stop_raises(self):
        from app.services.logistics_epod_service import settle_epod, EpodError
        db = MagicMock()
        m = MagicMock()
        m.mappings.return_value.first.return_value = None
        db.execute.return_value = m
        with pytest.raises(EpodError, match="nicht gefunden"):
            settle_epod(db, "tour-1", "stop-missing", "tenant1")
