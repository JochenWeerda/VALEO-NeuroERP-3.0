from __future__ import annotations

import json
from datetime import date, datetime
from typing import Any

from fastapi.testclient import TestClient

from app.api.v1.endpoints.personal import _work_plan_findings_for_assignment, PlanningPreferenceOut, WorkPlanAssignmentOut
from app.core.database import get_db
from main import app


_HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "tenant-work-plan"}


class _Result:
    def __init__(self, rows: list[dict[str, Any]]):
        self._rows = rows

    def mappings(self) -> "_Result":
        return self

    def all(self) -> list[dict[str, Any]]:
        return self._rows


class _WorkPlanSession:
    def execute(self, statement: Any, params: dict[str, Any]) -> _Result:
        sql = str(statement)
        if "FROM domain_hr.employee_time_profiles" in sql:
            return _Result([
                {
                    "employee_ref": "driver-1",
                    "display_name": "Driver One",
                    "role_code": "lkw_fahrer",
                    "time_model": "driver",
                    "status": "active",
                    "qualifications": ["driver_time"],
                },
                {
                    "employee_ref": "office-1",
                    "display_name": "Office One",
                    "role_code": "office",
                    "time_model": "standard",
                    "status": "active",
                    "qualifications": [],
                },
            ])
        if "FROM domain_shared.users" in sql:
            return _Result([
                {
                    "id": "driver-1",
                    "preferences": json.dumps({
                        "planning": {
                            "avoidNightTours": True,
                            "childcareSensitive": True,
                            "schoolHolidayRegions": ["NI"],
                            "bridgeDayPolicy": "preload",
                        }
                    }),
                }
            ])
        if "FROM domain_hr.time_entries" in sql:
            return _Result([
                {
                    "id": "absence-1",
                    "employee_ref": "driver-1",
                    "entry_date": date(2026, 5, 15),
                    "entry_type": "Urlaub",
                    "status": "Approved",
                }
            ])
        if "FROM domain_hr.shifts" in sql:
            return _Result([
                {
                    "id": "shift-1",
                    "shift_date": date(2026, 5, 14),
                    "name": "Nachttour vor Feiertag",
                    "starts_at": "22:30",
                    "ends_at": "04:30",
                    "assigned_employee_refs": ["driver-1"],
                    "status": "planned",
                },
                {
                    "id": "shift-2",
                    "shift_date": date(2026, 5, 15),
                    "name": "Urlaubskollision",
                    "starts_at": "08:00",
                    "ends_at": "16:00",
                    "assigned_employee_refs": ["driver-1"],
                    "status": "planned",
                },
            ])
        if "FROM domain_hr.calendar_events" in sql:
            return _Result([])
        if "FROM domain_hr.field_service_plans" in sql:
            return _Result([])
        return _Result([])


def test_work_plan_findings_cover_night_school_holiday_and_pre_holiday_load():
    assignment = WorkPlanAssignmentOut(
        id="shift-1",
        datum="2026-05-14",
        employeeRef="driver-1",
        label="Nachttour",
        sourceType="shift",
        startTime="22:30",
        endTime="04:30",
        status="planned",
        printReady=True,
    )
    findings = _work_plan_findings_for_assignment(
        assignment,
        PlanningPreferenceOut(
            employeeRef="driver-1",
            avoidNightTours=True,
            childcareSensitive=True,
            bridgeDayPolicy="preload",
        ),
        absence_dates_by_employee={},
        school_holiday_dates={date(2026, 5, 14)},
        bridge_days=set(),
        holiday_dates={date(2026, 5, 15)},
    )

    assert {finding.code for finding in findings} == {
        "NIGHT_TOUR_AVOIDED",
        "SCHOOL_HOLIDAY_SENSITIVITY",
        "PRE_HOLIDAY_LOAD",
    }


def test_work_plan_endpoint_returns_assignments_preferences_and_blockers():
    session = _WorkPlanSession()

    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    try:
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get(
            "/api/v1/personal/work-plan",
            headers=_HEADERS,
            params={
                "period_from": "2026-05-14",
                "period_to": "2026-05-15",
                "holiday_dates": "2026-05-15",
                "school_holiday_dates": "2026-05-14",
            },
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    payload = response.json()
    assert payload["printTitle"] == "Arbeitsplan 2026-05-14 bis 2026-05-15"
    assert payload["preferences"][0]["avoidNightTours"] is True
    assert len(payload["assignments"]) == 3
    blocked = [item for item in payload["assignments"] if item["status"] == "blocked"]
    assert blocked[0]["id"] == "shift-2"
    assert blocked[0]["printReady"] is False
    assert "ABSENCE_COLLISION" in {finding["code"] for finding in payload["findings"]}
