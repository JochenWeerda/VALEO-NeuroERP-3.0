from __future__ import annotations

from datetime import date
from typing import Any

from fastapi.testclient import TestClient

from app.api.v1.endpoints.personal import DriverTimeEventOut, _build_driver_time_summary
from app.core.database import get_db
from main import app


_HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "tenant-absence"}


class _Result:
    def __init__(self, rows: list[dict[str, Any]]):
        self._rows = rows

    def mappings(self) -> "_Result":
        return self

    def all(self) -> list[dict[str, Any]]:
        return self._rows

    def first(self) -> dict[str, Any] | None:
        return self._rows[0] if self._rows else None


class _AbsenceSession:
    def __init__(self):
        self.rows: list[dict[str, Any]] = []
        self.commits = 0

    def execute(self, statement: Any, params: dict[str, Any]) -> _Result:
        sql = str(statement)
        if "INSERT INTO domain_hr.time_entries" in sql:
            row = {
                "id": params["id"],
                "employee_ref": params["employee_ref"],
                "entry_date": params["entry_date"],
                "entry_type": params["entry_type"],
                "source": "absence",
                "status": params["status"],
                "notes": params["notes"],
                "audit_ref": params["audit_ref"],
            }
            self.rows.append(row)
            return _Result([row])

        if "FROM domain_hr.time_entries" in sql:
            rows = self.rows
            if "datum_von" in params:
                rows = [row for row in rows if row["entry_date"] >= params["datum_von"]]
            if "datum_bis" in params:
                rows = [row for row in rows if row["entry_date"] <= params["datum_bis"]]
            if "status" in params:
                rows = [row for row in rows if row["status"] == params["status"]]
            return _Result(rows)

        return _Result([])

    def commit(self) -> None:
        self.commits += 1


def test_absence_import_creates_daily_planning_blockers_and_lists_them():
    session = _AbsenceSession()

    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    try:
        client = TestClient(app, raise_server_exceptions=False)
        import_response = client.post(
            "/api/v1/personal/absences/import",
            headers=_HEADERS,
            json={
                "employeeRef": "driver-1",
                "absenceType": "Urlaub",
                "fromDate": "2026-05-08",
                "toDate": "2026-05-09",
                "status": "Approved",
                "sourceSystem": "urlaubsverwaltung",
                "externalRef": "UV-42",
            },
        )
        list_response = client.get(
            "/api/v1/personal/absences",
            headers=_HEADERS,
            params={"datum_von": "2026-05-08", "datum_bis": "2026-05-09"},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert import_response.status_code == 201
    assert import_response.json()["imported"] == 2
    assert import_response.json()["absences"][0]["planningBlockers"] == ["tour", "shift", "calendar", "payroll"]
    assert list_response.status_code == 200
    assert len(list_response.json()) == 2
    assert list_response.json()[0]["externalRef"] == "UV-42"


def test_absence_collision_reuses_driver_time_blocker_logic():
    summary = _build_driver_time_summary(
        "2026-05-08",
        [
            DriverTimeEventOut(
                id="event-1",
                fahrer="M. Krueger",
                employeeRef="driver-1",
                datum="2026-05-08",
                tour="TOUR-1",
                fahrzeug="WL-VA 1840",
                start="07:00",
                ende="09:00",
                taetigkeit="Fahren",
                eventType="DRIVING",
                quelle="Tacho",
                dauer=2.0,
            )
        ],
        absence_ranges=[("driver-1", "2026-05-08", "2026-05-08")],
    )

    assert summary.kpis.blocker == 1
    assert summary.findings[0].code == "ABSENCE_COLLISION"
