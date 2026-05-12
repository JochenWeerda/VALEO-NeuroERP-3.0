from __future__ import annotations

import json
from datetime import date
from typing import Any

from fastapi.testclient import TestClient

from app.api.v1.endpoints.personal import _build_shift_conflicts
from app.core.database import get_db
from main import app


_HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "tenant-shift"}


class _Result:
    def __init__(self, rows: list[dict[str, Any]]):
        self._rows = rows

    def mappings(self) -> "_Result":
        return self

    def all(self) -> list[dict[str, Any]]:
        return self._rows

    def first(self) -> dict[str, Any] | None:
        return self._rows[0] if self._rows else None


class _ShiftSession:
    def __init__(self):
        self.rows: list[dict[str, Any]] = []
        self.commits = 0

    def execute(self, statement: Any, params: dict[str, Any]) -> _Result:
        sql = str(statement)
        if "FROM domain_hr.employee_time_profiles" in sql:
            return _Result([
                {
                    "employee_ref": "driver-1",
                    "status": "active",
                    "qualifications": ["driver_time", "ce_license"],
                },
                {
                    "employee_ref": "warehouse-1",
                    "status": "active",
                    "qualifications": ["forklift"],
                },
            ])
        if "FROM domain_hr.time_entries" in sql:
            return _Result([
                {"employee_ref": "warehouse-1"},
            ])
        if "INSERT INTO domain_hr.shifts" in sql:
            row = {
                "id": params["id"],
                "shift_date": params["shift_date"],
                "name": params["name"],
                "location_code": params["location_code"],
                "required_role": params["required_role"],
                "required_qualifications": json.loads(params["required_qualifications"]),
                "required_headcount": params["required_headcount"],
                "starts_at": params["starts_at"],
                "ends_at": params["ends_at"],
                "assigned_employee_refs": json.loads(params["assigned_employee_refs"]),
                "status": params["status"],
                "conflicts": json.loads(params["conflicts"]),
                "notes": params["notes"],
            }
            self.rows.append(row)
            return _Result([row])
        if "FROM domain_hr.shifts" in sql:
            return _Result(self.rows)
        return _Result([])

    def commit(self) -> None:
        self.commits += 1


def test_build_shift_conflicts_flags_absence_and_missing_qualification():
    conflicts = _build_shift_conflicts(
        assigned_employee_refs=["driver-1", "warehouse-1"],
        required_headcount=2,
        required_qualifications=["forklift"],
        profile_rows=[
            {"employee_ref": "driver-1", "status": "active", "qualifications": ["driver_time"]},
            {"employee_ref": "warehouse-1", "status": "active", "qualifications": ["forklift"]},
        ],
        absence_rows=[{"employee_ref": "warehouse-1"}],
    )

    assert {conflict.code for conflict in conflicts} == {"QUALIFICATION_MISSING", "ABSENCE_COLLISION"}
    assert any(conflict.severity == "blocker" for conflict in conflicts)


def test_shift_endpoint_creates_blocked_shift_and_lists_it():
    session = _ShiftSession()

    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    try:
        client = TestClient(app, raise_server_exceptions=False)
        create_response = client.post(
            "/api/v1/personal/shifts",
            headers=_HEADERS,
            json={
                "name": "Ernteannahme Waage",
                "datum": "2026-07-20",
                "startTime": "06:00",
                "endTime": "14:00",
                "locationCode": "hof",
                "requiredRole": "waage",
                "requiredQualifications": ["forklift"],
                "requiredHeadcount": 2,
                "assignedEmployeeRefs": ["driver-1", "warehouse-1"],
            },
        )
        list_response = client.get(
            "/api/v1/personal/shifts",
            headers=_HEADERS,
            params={"datum_von": "2026-07-20", "datum_bis": "2026-07-20"},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert create_response.status_code == 201
    data = create_response.json()
    assert data["status"] == "blocked"
    assert {conflict["code"] for conflict in data["conflicts"]} == {"QUALIFICATION_MISSING", "ABSENCE_COLLISION"}
    assert list_response.status_code == 200
    assert list_response.json()[0]["name"] == "Ernteannahme Waage"


def test_shift_endpoint_flags_understaffing():
    session = _ShiftSession()

    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    try:
        client = TestClient(app, raise_server_exceptions=False)
        response = client.post(
            "/api/v1/personal/shifts",
            headers=_HEADERS,
            json={
                "name": "Silo Verladung",
                "datum": "2026-07-21",
                "startTime": "14:00",
                "endTime": "22:00",
                "requiredHeadcount": 2,
                "assignedEmployeeRefs": ["driver-1"],
            },
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 201
    assert response.json()["status"] == "blocked"
    assert response.json()["conflicts"][0]["code"] == "UNDERSTAFFED"
