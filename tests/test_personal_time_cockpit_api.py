from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

from fastapi.testclient import TestClient

from app.api.v1.endpoints.personal import (
    DriverTimeEventOut,
    _build_driver_time_summary,
    _build_time_cockpit,
)
from app.core.database import get_db
from main import app


_HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "tenant-time"}


class _Result:
    def __init__(self, rows: list[dict[str, Any]]):
        self._rows = rows

    def mappings(self) -> "_Result":
        return self

    def all(self) -> list[dict[str, Any]]:
        return self._rows


class _TimeCockpitSession:
    def execute(self, statement: Any, _params: dict[str, Any]) -> _Result:
        sql = str(statement)
        if "FROM domain_hr.driver_timesheets" in sql:
            return _Result([
                {
                    "id": "sheet-1",
                    "entry_date": date(2026, 5, 8),
                    "driver_name": "S. Weber",
                    "vehicle_plate": "",
                    "tours": [{"id": "TOUR-2411", "start": "06:20", "ende": "08:00", "pause": 0}],
                    "total_hours": 1.67,
                    "overtime_hours": 0,
                    "created_at": datetime(2026, 5, 8, 8, 5, tzinfo=timezone.utc),
                }
            ])
        if "FROM domain_hr.time_entries" in sql and "entry_type IN" in sql:
            return _Result([
                {"employee_ref": "S. Weber", "entry_date": date(2026, 5, 8), "entry_type": "Urlaub"}
            ])
        if "FROM domain_hr.time_entries" in sql:
            return _Result([
                {
                    "id": "time-1",
                    "employee_ref": "L. Meier",
                    "entry_date": date(2026, 5, 8),
                    "start_time": "07:00",
                    "end_time": "16:00",
                    "hours": 8.0,
                    "entry_type": "Arbeit",
                    "source": "terminal",
                    "status": "Approved",
                },
                {
                    "id": "time-2",
                    "employee_ref": "S. Weber",
                    "entry_date": date(2026, 5, 8),
                    "start_time": "06:20",
                    "end_time": "18:05",
                    "hours": 11.75,
                    "entry_type": "Arbeit",
                    "source": "driver-time",
                    "status": "Draft",
                },
            ])
        return _Result([])


def _override_db():
    yield _TimeCockpitSession()


def test_build_time_cockpit_flags_approval_compliance_and_payroll_blockers():
    driver_time = _build_driver_time_summary(
        "2026-05-08",
        [
            DriverTimeEventOut(
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
        ],
        absence_ranges=[("S. Weber", "2026-05-08", "2026-05-08")],
    )
    cockpit = _build_time_cockpit(
        "2026-05-08",
        [
            {
                "id": "time-1",
                "employee_ref": "S. Weber",
                "entry_date": "2026-05-08",
                "start_time": "06:20",
                "end_time": "18:05",
                "hours": 11.75,
                "entry_type": "Arbeit",
                "source": "driver-time",
                "status": "Draft",
            }
        ],
        driver_time,
        source="unit",
    )

    assert cockpit.kpis.pendingApprovals == 1
    assert cockpit.kpis.blockerCount == 2
    assert cockpit.kpis.warningCount == 1
    assert cockpit.payrollReadiness.status == "blocked"
    assert cockpit.approvalQueue[0].nextAction == "Freigeben oder korrigieren"


def test_time_cockpit_endpoint_returns_professional_contract():
    app.dependency_overrides[get_db] = _override_db
    try:
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/api/v1/personal/time-cockpit", params={"datum": "2026-05-08"}, headers=_HEADERS)
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    data = response.json()
    assert data["datum"] == "2026-05-08"
    assert data["source"] == "database"
    assert data["kpis"]["pendingApprovals"] == 1
    assert data["payrollReadiness"]["status"] == "blocked"
    assert data["driverTime"]["kpis"]["eventCount"] == 1
    assert any(item["code"] == "LONG_WORKDAY" for item in data["complianceIssues"])
    assert any(item["code"] == "ABSENCE_COLLISION" for item in data["complianceIssues"])
