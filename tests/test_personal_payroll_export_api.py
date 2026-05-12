from __future__ import annotations

import json
from datetime import date
from typing import Any

from fastapi.testclient import TestClient

from app.api.v1.endpoints.personal import _payroll_item_from_time_row
from app.core.database import get_db
from main import app


_HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "tenant-payroll"}


class _Result:
    def __init__(self, rows: list[dict[str, Any]]):
        self._rows = rows

    def mappings(self) -> "_Result":
        return self

    def all(self) -> list[dict[str, Any]]:
        return self._rows

    def first(self) -> dict[str, Any] | None:
        return self._rows[0] if self._rows else None


class _PayrollSession:
    def __init__(self):
        self.exports: list[dict[str, Any]] = []

    def execute(self, statement: Any, params: dict[str, Any]) -> _Result:
        sql = str(statement)
        if "FROM domain_hr.time_entries" in sql:
            return _Result([
                {
                    "id": "time-1",
                    "employee_ref": "driver-1",
                    "entry_date": date(2026, 5, 8),
                    "hours": 8.0,
                    "entry_type": "Arbeit",
                    "status": "Approved",
                    "cost_center": "LOG",
                },
                {
                    "id": "time-2",
                    "employee_ref": "driver-1",
                    "entry_date": date(2026, 5, 9),
                    "hours": 10.5,
                    "entry_type": "Arbeit",
                    "status": "Draft",
                    "cost_center": "LOG",
                },
            ])
        if "INSERT INTO domain_hr.payroll_exports" in sql:
            row = {
                "id": params["id"],
                "period_from": params["period_from"],
                "period_to": params["period_to"],
                "target_system": params["target_system"],
                "status": params["status"],
                "items": json.loads(params["items"]),
                "blockers": json.loads(params["blockers"]),
            }
            self.exports.append(row)
            return _Result([row])
        if "FROM domain_hr.payroll_exports" in sql:
            return _Result(self.exports)
        return _Result([])

    def commit(self) -> None:
        return None


def test_payroll_item_maps_regular_and_overtime_wage_types():
    regular = _payroll_item_from_time_row(
        {"id": "time-1", "employee_ref": "e-1", "entry_date": date(2026, 5, 8), "hours": 8, "entry_type": "Arbeit"}
    )
    overtime = _payroll_item_from_time_row(
        {"id": "time-2", "employee_ref": "e-1", "entry_date": date(2026, 5, 9), "hours": 10.5, "entry_type": "Arbeit"}
    )
    absence = _payroll_item_from_time_row(
        {"id": "time-3", "employee_ref": "e-1", "entry_date": date(2026, 5, 10), "hours": 0, "entry_type": "Urlaub"}
    )

    assert regular.wageType == "REGULAR"
    assert overtime.wageType == "OVERTIME"
    assert absence.wageType == "ABSENCE"


def test_payroll_export_blocks_unapproved_entries_and_lists_package():
    session = _PayrollSession()

    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    try:
        client = TestClient(app, raise_server_exceptions=False)
        create_response = client.post(
            "/api/v1/personal/payroll-exports",
            headers=_HEADERS,
            json={"periodFrom": "2026-05-01", "periodTo": "2026-05-31", "targetSystem": "datev"},
        )
        list_response = client.get("/api/v1/personal/payroll-exports", headers=_HEADERS)
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert create_response.status_code == 201
    data = create_response.json()
    assert data["status"] == "blocked"
    assert len(data["items"]) == 1
    assert data["items"][0]["wageType"] == "REGULAR"
    assert data["blockers"][0]["code"] == "TIME_ENTRY_NOT_APPROVED"
    assert list_response.status_code == 200
    assert list_response.json()[0]["targetSystem"] == "datev"
