from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from fastapi.testclient import TestClient

from app.api.v1.endpoints.personal import _calendar_event_from_row
from app.core.database import get_db
from main import app


_HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "tenant-calendar"}


class _Result:
    def __init__(self, rows: list[dict[str, Any]]):
        self._rows = rows

    def mappings(self) -> "_Result":
        return self

    def all(self) -> list[dict[str, Any]]:
        return self._rows

    def first(self) -> dict[str, Any] | None:
        return self._rows[0] if self._rows else None


class _CalendarSession:
    def __init__(self):
        self.rows: list[dict[str, Any]] = []
        self.commits = 0

    def execute(self, statement: Any, params: dict[str, Any]) -> _Result:
        sql = str(statement)
        if "INSERT INTO domain_hr.calendar_events" in sql:
            row = {
                "id": params["id"],
                "source_system": params["source_system"],
                "provider": params["provider"],
                "external_event_ref": params["external_event_ref"],
                "event_type": params["event_type"],
                "title": params["title"],
                "employee_ref": params["employee_ref"],
                "resource_ref": params["resource_ref"],
                "starts_at": params["starts_at"].isoformat(),
                "ends_at": params["ends_at"].isoformat(),
                "timezone": params["timezone"],
                "visibility": params["visibility"],
                "status": params["status"],
                "sync_state": params["sync_state"],
                "conflict_level": params["conflict_level"],
                "source_ref": params["source_ref"],
                "metadata": json.loads(params["metadata"]),
            }
            self.rows.append(row)
            return _Result([row])
        if "FROM domain_hr.calendar_events" in sql:
            return _Result(self.rows)
        return _Result([])

    def commit(self) -> None:
        self.commits += 1


def test_calendar_event_masks_private_details():
    event = _calendar_event_from_row(
        {
            "id": "event-1",
            "source_system": "google",
            "provider": "google",
            "external_event_ref": "g-1",
            "event_type": "external_busy",
            "title": "Privater Arzttermin",
            "employee_ref": "employee-1",
            "starts_at": datetime(2026, 5, 12, 8, tzinfo=timezone.utc).isoformat(),
            "ends_at": datetime(2026, 5, 12, 9, tzinfo=timezone.utc).isoformat(),
            "timezone": "Europe/Berlin",
            "visibility": "private",
            "status": "confirmed",
            "sync_state": "synced",
            "conflict_level": "warning",
            "source_ref": "external",
            "metadata": {"busy": True, "private_note": "hidden"},
        }
    )

    assert event.title == "Besetzt"
    assert event.metadata == {"busy": True}


def test_calendar_event_endpoint_creates_and_lists_contract():
    session = _CalendarSession()

    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    try:
        client = TestClient(app, raise_server_exceptions=False)
        create_response = client.post(
            "/api/v1/personal/calendar-events",
            headers=_HEADERS,
            json={
                "sourceSystem": "valeo",
                "provider": "internal",
                "eventType": "shift",
                "title": "Ernteannahme Waage",
                "employeeRef": "warehouse-1",
                "startsAt": "2026-07-20T06:00:00+02:00",
                "endsAt": "2026-07-20T14:00:00+02:00",
                "visibility": "team",
                "syncState": "pending",
                "conflictLevel": "none",
                "sourceRef": "shift-1",
                "metadata": {"location": "hof"},
            },
        )
        list_response = client.get(
            "/api/v1/personal/calendar-events",
            headers=_HEADERS,
            params={"start": "2026-07-20T00:00:00+02:00", "end": "2026-07-21T00:00:00+02:00"},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert create_response.status_code == 201
    assert create_response.json()["syncState"] == "pending"
    assert create_response.json()["sourceRef"] == "shift-1"
    assert list_response.status_code == 200
    assert list_response.json()[0]["eventType"] == "shift"


def test_calendar_event_rejects_invalid_range():
    session = _CalendarSession()

    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    try:
        client = TestClient(app, raise_server_exceptions=False)
        response = client.post(
            "/api/v1/personal/calendar-events",
            headers=_HEADERS,
            json={
                "eventType": "shift",
                "title": "Invalid",
                "startsAt": "2026-07-20T14:00:00+02:00",
                "endsAt": "2026-07-20T06:00:00+02:00",
            },
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 400
    assert "after" in response.json()["detail"]
