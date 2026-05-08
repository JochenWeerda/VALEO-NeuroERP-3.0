from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

from fastapi.testclient import TestClient

from app.core.database import get_db
from main import app


_HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "tenant-booking"}


class _Result:
    def __init__(self, rows: list[dict[str, Any]]):
        self._rows = rows

    def mappings(self) -> "_Result":
        return self

    def first(self) -> dict[str, Any] | None:
        return self._rows[0] if self._rows else None


class _BookingSession:
    def __init__(self, initial_status: str | None = None):
        self.rows: dict[str, dict[str, Any]] = {}
        if initial_status:
            self.rows["entry-1"] = self._row("entry-1", initial_status)
        self.commits = 0

    def _row(self, entry_id: str, status: str) -> dict[str, Any]:
        return {
            "id": entry_id,
            "employee_ref": "driver-1",
            "entry_date": date(2026, 5, 8),
            "start_time": "07:00",
            "end_time": "16:00",
            "hours": 8.0,
            "entry_type": "Arbeit",
            "source": "manual",
            "status": status,
            "cost_center": "LOG",
            "work_area": "Tour",
            "correction_reason": None,
            "approved_by": None,
            "approved_at": None,
            "audit_ref": None,
        }

    def execute(self, statement: Any, params: dict[str, Any]) -> _Result:
        sql = str(statement)
        if "INSERT INTO domain_hr.time_entries" in sql:
            row = self._row(str(params["id"]), "Draft")
            row.update(
                employee_ref=params["employee_ref"],
                entry_date=params["entry_date"],
                start_time=params["start_time"],
                end_time=params["end_time"],
                hours=params["hours"],
                entry_type=params["entry_type"],
                source=params["source"],
                cost_center=params["cost_center"],
                work_area=params["work_area"],
            )
            self.rows[row["id"]] = row
            return _Result([row])

        if "SET status = 'Submitted'" in sql:
            row = self.rows.get(str(params["entry_id"]))
            if not row or row["status"] not in {"Draft", "Rejected", "Corrected"}:
                return _Result([])
            row["status"] = "Submitted"
            return _Result([row])

        if "SET status = 'Approved'" in sql:
            row = self.rows.get(str(params["entry_id"]))
            if not row or row["status"] != "Submitted":
                return _Result([])
            row["status"] = "Approved"
            row["approved_by"] = params["approved_by"]
            row["approved_at"] = datetime(2026, 5, 8, 16, 5, tzinfo=timezone.utc)
            return _Result([row])

        if "SELECT status" in sql:
            row = self.rows.get(str(params["entry_id"]))
            return _Result([{"status": row["status"]}]) if row else _Result([])

        if "status = 'Corrected'" in sql:
            row = self.rows.get(str(params["entry_id"]))
            if not row:
                return _Result([])
            row.update(
                start_time=params["start_time"],
                end_time=params["end_time"],
                hours=params["hours"],
                entry_type=params["entry_type"],
                status="Corrected",
                cost_center=params["cost_center"],
                work_area=params["work_area"],
                correction_reason=params["correction_reason"],
            )
            return _Result([row])

        return _Result([])

    def commit(self) -> None:
        self.commits += 1


def test_time_entry_booking_create_submit_and_approve_flow():
    session = _BookingSession()

    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    try:
        client = TestClient(app, raise_server_exceptions=False)
        create_response = client.post(
            "/api/v1/personal/time-entries",
            headers=_HEADERS,
            json={
                "employeeRef": "driver-1",
                "datum": "2026-05-08",
                "startTime": "07:00",
                "endTime": "16:00",
                "hours": 8,
                "entryType": "Arbeit",
                "source": "mobile",
                "costCenter": "LOG",
                "workArea": "Tour",
            },
        )
        entry_id = create_response.json()["id"]
        submit_response = client.post(f"/api/v1/personal/time-entries/{entry_id}/submit", headers=_HEADERS)
        approve_response = client.post(
            f"/api/v1/personal/time-entries/{entry_id}/approve",
            headers=_HEADERS,
            json={"approvedBy": "manager-1"},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert create_response.status_code == 201
    assert create_response.json()["status"] == "Draft"
    assert submit_response.status_code == 200
    assert submit_response.json()["entry"]["status"] == "Submitted"
    assert approve_response.status_code == 200
    assert approve_response.json()["entry"]["status"] == "Approved"
    assert approve_response.json()["entry"]["approvedBy"] == "manager-1"


def test_time_entry_approve_requires_submitted_status():
    session = _BookingSession(initial_status="Draft")

    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    try:
        client = TestClient(app, raise_server_exceptions=False)
        response = client.post(
            "/api/v1/personal/time-entries/entry-1/approve",
            headers=_HEADERS,
            json={"approvedBy": "manager-1"},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 409
    assert "eingereicht" in response.json()["detail"]


def test_time_entry_correction_requires_reason_and_blocks_exported_entries():
    session = _BookingSession(initial_status="Exported")

    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    try:
        client = TestClient(app, raise_server_exceptions=False)
        missing_reason = client.post(
            "/api/v1/personal/time-entries/entry-1/correct",
            headers=_HEADERS,
            json={"hours": 7.5},
        )
        exported = client.post(
            "/api/v1/personal/time-entries/entry-1/correct",
            headers=_HEADERS,
            json={"hours": 7.5, "correctionReason": "Tacho-Import korrigiert"},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert missing_reason.status_code == 422
    assert exported.status_code == 409
    assert "Exportierte" in exported.json()["detail"]
