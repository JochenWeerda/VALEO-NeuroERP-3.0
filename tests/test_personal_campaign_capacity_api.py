from __future__ import annotations

import json
from datetime import date
from typing import Any

from fastapi.testclient import TestClient

from app.api.v1.endpoints.personal import _build_campaign_findings
from app.core.database import get_db
from main import app


_HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "tenant-campaign"}


class _Result:
    def __init__(self, rows: list[dict[str, Any]]):
        self._rows = rows

    def mappings(self) -> "_Result":
        return self

    def all(self) -> list[dict[str, Any]]:
        return self._rows

    def first(self) -> dict[str, Any] | None:
        return self._rows[0] if self._rows else None


class _CampaignSession:
    def __init__(self):
        self.rows: list[dict[str, Any]] = []

    def execute(self, statement: Any, params: dict[str, Any]) -> _Result:
        sql = str(statement)
        if "FROM domain_hr.employee_time_profiles" in sql:
            return _Result([
                {"employee_ref": "driver-1", "role_code": "lkw_fahrer", "status": "active"},
                {"employee_ref": "driver-2", "role_code": "lkw_fahrer", "status": "active"},
                {"employee_ref": "waage-1", "role_code": "waage", "status": "active"},
            ])
        if "FROM domain_hr.time_entries" in sql:
            return _Result([{"employee_ref": "driver-2"}])
        if "FROM domain_hr.shifts" in sql:
            return _Result([{"assigned_employee_refs": ["driver-1"]}])
        if "INSERT INTO domain_hr.campaign_capacity_plans" in sql:
            row = {
                "id": params["id"],
                "campaign_code": params["campaign_code"],
                "name": params["name"],
                "period_from": params["period_from"],
                "period_to": params["period_to"],
                "location_code": params["location_code"],
                "role_demand": json.loads(params["role_demand"]),
                "expected_volume": params["expected_volume"],
                "status": params["status"],
                "findings": json.loads(params["findings"]),
            }
            self.rows.append(row)
            return _Result([row])
        if "FROM domain_hr.campaign_capacity_plans" in sql:
            return _Result(self.rows)
        return _Result([])

    def commit(self) -> None:
        return None


def test_campaign_findings_detect_capacity_shortage():
    findings = _build_campaign_findings(
        {"lkw_fahrer": 2},
        [
            {"employee_ref": "driver-1", "role_code": "lkw_fahrer", "status": "active"},
            {"employee_ref": "driver-2", "role_code": "lkw_fahrer", "status": "active"},
        ],
        [{"employee_ref": "driver-2"}],
        [{"assigned_employee_refs": ["driver-1"]}],
    )

    assert findings[0].code == "ROLE_CAPACITY_SHORTAGE"
    assert findings[0].severity == "blocker"


def test_campaign_capacity_endpoint_creates_blocked_plan_and_lists_it():
    session = _CampaignSession()

    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    try:
        client = TestClient(app, raise_server_exceptions=False)
        create_response = client.post(
            "/api/v1/personal/campaign-capacity",
            headers=_HEADERS,
            json={
                "campaignCode": "ERNTE-2026",
                "name": "Ernteannahme 2026",
                "periodFrom": "2026-07-20",
                "periodTo": "2026-08-15",
                "locationCode": "main",
                "roleDemand": {"lkw_fahrer": 2, "waage": 1},
                "expectedVolume": 12000,
            },
        )
        list_response = client.get("/api/v1/personal/campaign-capacity", headers=_HEADERS)
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert create_response.status_code == 201
    assert create_response.json()["status"] == "blocked"
    assert any(item["code"] == "ROLE_CAPACITY_SHORTAGE" for item in create_response.json()["findings"])
    assert list_response.status_code == 200
    assert list_response.json()[0]["campaignCode"] == "ERNTE-2026"
