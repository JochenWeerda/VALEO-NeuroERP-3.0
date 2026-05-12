from __future__ import annotations

import json
from typing import Any

from fastapi.testclient import TestClient

from app.api.v1.endpoints.personal import _build_field_conflicts
from app.core.database import get_db
from main import app


_HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "tenant-field"}


class _Result:
    def __init__(self, rows: list[dict[str, Any]]):
        self._rows = rows

    def mappings(self) -> "_Result":
        return self

    def all(self) -> list[dict[str, Any]]:
        return self._rows

    def first(self) -> dict[str, Any] | None:
        return self._rows[0] if self._rows else None


class _FieldSession:
    def __init__(self):
        self.rows: list[dict[str, Any]] = []

    def execute(self, statement: Any, params: dict[str, Any]) -> _Result:
        sql = str(statement)
        if "FROM domain_hr.employee_time_profiles" in sql:
            return _Result([{"employee_ref": "berater-1", "status": "active", "time_model": "field_service"}])
        if "FROM domain_hr.time_entries" in sql:
            return _Result([])
        if "FROM domain_hr.calendar_events" in sql:
            return _Result([{"id": "busy-1"}])
        if "INSERT INTO domain_hr.field_service_plans" in sql:
            row = {
                "id": params["id"],
                "employee_ref": params["employee_ref"],
                "customer_ref": params["customer_ref"],
                "territory_code": params["territory_code"],
                "campaign_code": params["campaign_code"],
                "visit_type": params["visit_type"],
                "starts_at": params["starts_at"].isoformat(),
                "ends_at": params["ends_at"].isoformat(),
                "status": params["status"],
                "conflicts": json.loads(params["conflicts"]),
                "notes": params["notes"],
            }
            self.rows.append(row)
            return _Result([row])
        if "FROM domain_hr.field_service_plans" in sql:
            return _Result(self.rows)
        return _Result([])

    def commit(self) -> None:
        return None


def test_field_conflicts_detect_absence_and_calendar_collision():
    conflicts = _build_field_conflicts(
        [{"employee_ref": "berater-1", "status": "active", "time_model": "field_service"}],
        [{"employee_ref": "berater-1"}],
        [{"id": "busy-1"}],
    )

    assert {conflict.code for conflict in conflicts} == {"ABSENCE_COLLISION", "CALENDAR_COLLISION"}
    assert any(conflict.severity == "blocker" for conflict in conflicts)


def test_field_service_endpoint_creates_warning_plan_and_lists_it():
    session = _FieldSession()

    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    try:
        client = TestClient(app, raise_server_exceptions=False)
        create_response = client.post(
            "/api/v1/personal/field-service-plan",
            headers=_HEADERS,
            json={
                "employeeRef": "berater-1",
                "customerRef": "kunde-42",
                "territoryCode": "north",
                "campaignCode": "SAAT-2026",
                "visitType": "field_visit",
                "startsAt": "2026-03-20T09:00:00+01:00",
                "endsAt": "2026-03-20T11:00:00+01:00",
            },
        )
        list_response = client.get("/api/v1/personal/field-service-plan", headers=_HEADERS)
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert create_response.status_code == 201
    assert create_response.json()["status"] == "warning"
    assert create_response.json()["conflicts"][0]["code"] == "CALENDAR_COLLISION"
    assert list_response.status_code == 200
    assert list_response.json()[0]["customerRef"] == "kunde-42"
