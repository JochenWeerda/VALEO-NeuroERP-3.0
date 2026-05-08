from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

from fastapi.testclient import TestClient

from app.api.v1.endpoints.personal import (
    DriverTimeEventOut,
    _build_driver_time_summary,
)
from app.core.database import get_db
from main import app


_HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "tenant-driver"}


class _Result:
    def __init__(self, rows: list[dict[str, Any]]):
        self._rows = rows

    def mappings(self) -> "_Result":
        return self

    def all(self) -> list[dict[str, Any]]:
        return self._rows


class _DriverTimeSession:
    def execute(self, statement: Any, _params: dict[str, Any]) -> _Result:
        sql = str(statement)
        if "FROM domain_hr.driver_timesheets" in sql:
            return _Result([
                {
                    "id": "sheet-1",
                    "entry_date": date(2026, 5, 8),
                    "driver_name": "M. Krueger",
                    "vehicle_plate": "WL-VA 1840",
                    "tours": [
                        {"id": "TOUR-2407", "start": "05:45", "ende": "07:55", "pause": 30},
                    ],
                    "total_hours": 2.17,
                    "overtime_hours": 0,
                    "created_at": datetime(2026, 5, 8, 8, 0, tzinfo=timezone.utc),
                },
                {
                    "id": "sheet-2",
                    "entry_date": date(2026, 5, 8),
                    "driver_name": "S. Weber",
                    "vehicle_plate": "",
                    "tours": [
                        {"id": "TOUR-2411", "start": "06:20", "ende": "08:00", "pause": 0},
                    ],
                    "total_hours": 1.67,
                    "overtime_hours": 0,
                    "created_at": datetime(2026, 5, 8, 8, 5, tzinfo=timezone.utc),
                },
            ])
        if "FROM domain_hr.time_entries" in sql:
            return _Result([
                {
                    "employee_ref": "S. Weber",
                    "entry_date": date(2026, 5, 8),
                    "entry_type": "Urlaub",
                }
            ])
        return _Result([])


def _override_db():
    yield _DriverTimeSession()


def test_build_driver_time_summary_reports_missing_vehicle_and_absence_collision():
    event = DriverTimeEventOut(
        id="event-1",
        fahrer="S. Weber",
        employeeRef="S. Weber",
        datum="2026-05-08",
        tour="TOUR-2411",
        fahrzeug=None,
        start="06:20",
        ende="08:00",
        taetigkeit="Fahren",
        eventType="DRIVING",
        quelle="Manuell",
        dauer=1.67,
    )

    summary = _build_driver_time_summary(
        "2026-05-08",
        [event],
        absence_ranges=[("S. Weber", "2026-05-08", "2026-05-08")],
    )

    assert summary.kpis.blocker == 2
    assert {finding.code for finding in summary.findings} == {"MISSING_VEHICLE", "ABSENCE_COLLISION"}
    assert summary.events[0].findings[0].severity == "blocker"


def test_driver_time_summary_endpoint_returns_api_contract():
    app.dependency_overrides[get_db] = _override_db
    try:
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get(
            "/api/v1/personal/driver-time/summary",
            params={"datum": "2026-05-08"},
            headers=_HEADERS,
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    data = response.json()
    assert data["datum"] == "2026-05-08"
    assert data["source"] == "database"
    assert data["kpis"]["eventCount"] == 3
    assert data["kpis"]["fahrerCount"] == 2
    assert data["kpis"]["blocker"] >= 2
    assert any(finding["code"] == "MISSING_VEHICLE" for finding in data["findings"])
    assert any(finding["code"] == "ABSENCE_COLLISION" for finding in data["findings"])


def test_driver_time_summary_endpoint_falls_back_to_pilot_contract_on_db_error():
    def broken_db():
        class _BrokenSession:
            def execute(self, *_args: Any, **_kwargs: Any) -> Any:
                raise RuntimeError("db unavailable")

        yield _BrokenSession()

    app.dependency_overrides[get_db] = broken_db
    try:
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get(
            "/api/v1/personal/driver-time/summary",
            params={"datum": "2026-05-08"},
            headers=_HEADERS,
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "pilot-fallback"
    assert data["kpis"]["eventCount"] == 4
    assert any(event["fahrzeug"] is None for event in data["events"])
