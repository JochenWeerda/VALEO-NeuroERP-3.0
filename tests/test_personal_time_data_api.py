from __future__ import annotations

import json
from typing import Any

from fastapi.testclient import TestClient

from app.api.v1.endpoints.personal import (
    _profile_kpis,
    _time_profiles_from_rows,
    _time_profiles_from_user_rows,
)
from app.core.database import get_db
from main import app


_HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "tenant-hr-time"}


class _Result:
    def __init__(self, rows: list[dict[str, Any]]):
        self._rows = rows

    def mappings(self) -> "_Result":
        return self

    def all(self) -> list[dict[str, Any]]:
        return self._rows


class _ProfileSession:
    def execute(self, statement: Any, _params: dict[str, Any]) -> _Result:
        sql = str(statement)
        if "FROM domain_hr.employee_time_profiles" in sql:
            return _Result([
                {
                    "employee_ref": "driver-1",
                    "display_name": "M. Krueger",
                    "role_code": "lkw_fahrer",
                    "role_label": "LKW-Fahrer",
                    "location_code": "main",
                    "department": "Logistik",
                    "manager_ref": "disp-1",
                    "employment_type": "full_time",
                    "weekly_hours": 40,
                    "time_model": "driver",
                    "cost_center": "LOG",
                    "payroll_group": "stundenlohn",
                    "qualifications": ["ce_license", "tacho_card"],
                    "can_drive": True,
                    "driver_card_id": "D-1001",
                    "vehicle_refs": ["WL-VA 1840"],
                    "calendar_provider": "microsoft365",
                    "status": "active",
                }
            ])
        return _Result([])


class _UsersFallbackSession:
    def execute(self, statement: Any, _params: dict[str, Any]) -> _Result:
        sql = str(statement)
        if "FROM domain_hr.employee_time_profiles" in sql:
            return _Result([])
        if "FROM domain_shared.users" in sql:
            return _Result([
                {
                    "id": "user-1",
                    "username": "fahrer@example.test",
                    "email": "fahrer@example.test",
                    "first_name": "S.",
                    "last_name": "Weber",
                    "roles": ["lkw_fahrer"],
                    "is_active": True,
                    "preferences": json.dumps({
                        "abteilung": "Logistik",
                        "location_code": "hof",
                        "weekly_hours": 38.5,
                        "cost_center": "LOG",
                        "vehicle_refs": ["WL-VA 1217"],
                    }),
                }
            ])
        return _Result([])


def test_time_profiles_from_rows_normalizes_canonical_profile():
    profiles = _time_profiles_from_rows([
        {
            "employee_ref": "driver-1",
            "display_name": "M. Krueger",
            "role_code": "lkw_fahrer",
            "role_label": "LKW-Fahrer",
            "location_code": "main",
            "department": "Logistik",
            "employment_type": "full_time",
            "weekly_hours": 40,
            "time_model": "driver",
            "qualifications": '["ce_license","tacho_card"]',
            "can_drive": True,
            "vehicle_refs": '["WL-VA 1840"]',
            "calendar_provider": "microsoft365",
            "status": "active",
        }
    ])

    assert profiles[0].employeeRef == "driver-1"
    assert profiles[0].timeModel == "driver"
    assert profiles[0].qualifications == ["ce_license", "tacho_card"]
    assert profiles[0].vehicleRefs == ["WL-VA 1840"]
    assert _profile_kpis(profiles).driverCount == 1


def test_time_profiles_from_user_rows_derives_driver_profile_from_role():
    profiles = _time_profiles_from_user_rows([
        {
            "id": "user-1",
            "username": "fahrer@example.test",
            "email": "fahrer@example.test",
            "first_name": "S.",
            "last_name": "Weber",
            "roles": ["lkw_fahrer"],
            "is_active": True,
            "preferences": {"abteilung": "Logistik", "weekly_hours": 38.5},
        }
    ])

    assert profiles[0].employeeRef == "user-1"
    assert profiles[0].displayName == "S. Weber"
    assert profiles[0].canDrive is True
    assert profiles[0].timeModel == "driver"
    assert "driver_time" in profiles[0].qualifications


def test_time_profiles_endpoint_returns_database_contract():
    def override_db():
        yield _ProfileSession()

    app.dependency_overrides[get_db] = override_db
    try:
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/api/v1/personal/time-profiles", headers=_HEADERS)
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "database"
    assert data["kpis"]["employeeCount"] == 1
    assert data["kpis"]["driverCount"] == 1
    assert data["profiles"][0]["employeeRef"] == "driver-1"
    assert data["profiles"][0]["costCenter"] == "LOG"


def test_time_profiles_endpoint_falls_back_to_users_before_pilot():
    def override_db():
        yield _UsersFallbackSession()

    app.dependency_overrides[get_db] = override_db
    try:
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/api/v1/personal/time-profiles", headers=_HEADERS)
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "users-fallback"
    assert data["profiles"][0]["employeeRef"] == "user-1"
    assert data["profiles"][0]["timeModel"] == "driver"
