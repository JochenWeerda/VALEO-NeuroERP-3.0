from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.workers.ration_lifecycle_worker import execute_due_ration_activations

client = TestClient(app, raise_server_exceptions=False)
BASE = "/api/v1/agrar/rations-optimization/lifecycle"
TENANT = "00000000-0000-0000-0000-000000000001"
HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-Id": TENANT}


def _group() -> dict:
    response = client.post(
        f"{BASE}/groups",
        headers=HEADERS,
        json={
            "external_ref": f"test-{uuid4()}",
            "name": f"Hochleistung {str(uuid4())[:8]}",
            "animal_count": 48,
            "body_mass_kg": 675,
            "days_in_milk": 92,
            "lactation_number": 2.4,
            "target_milk_kg": 38.5,
            "feeding_system": "TMR",
            "location": "Nordstall",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _ration(group_id: str, suffix: str) -> dict:
    response = client.post(
        f"{BASE}/rations",
        headers=HEADERS,
        json={
            "group_id": group_id,
            "name": f"Ration {suffix}",
            "description": "API-Lifecycle-Test",
            "source": "solver",
            "comment": "Erster Entwurf",
            "snapshot": {
                "profile": {"milk_kg": 38.5, "body_mass_kg": 675},
                "ration": [{"feed_id": "mais", "kg_dm": 8.2}],
                "result": {"cost_eur_cow_day": 4.72, "status": "optimal"},
            },
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _transition(version_id: str, current: str, target: str, **extra) -> dict:
    response = client.post(
        f"{BASE}/versions/{version_id}/transitions",
        headers=HEADERS,
        json={"expected_status": current, "target_status": target, **extra},
    )
    assert response.status_code == 200, response.text
    return response.json()


def _approve(version_id: str) -> None:
    _transition(version_id, "draft", "in_review")
    _transition(version_id, "in_review", "approved", reason="Fachlich geprueft")


def test_full_lifecycle_versions_single_active_and_tenant_isolation() -> None:
    group = _group()
    first = _ration(group["id"], "A")
    first_version = first["versions"][0]
    first_id = first_version["id"]
    assert first_version["version_no"] == 1
    assert first_version["status"] == "draft"

    _approve(first_id)
    future = (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
    scheduled = _transition(first_id, "approved", "scheduled", feeding_start=future)
    assert scheduled["feeding_start"] is not None

    too_early = client.post(
        f"{BASE}/versions/{first_id}/transitions",
        headers=HEADERS,
        json={"expected_status": "scheduled", "target_status": "active"},
    )
    assert too_early.status_code == 409
    _transition(first_id, "scheduled", "approved")
    _transition(first_id, "approved", "active")

    second = _ration(group["id"], "B")
    second_id = second["versions"][0]["id"]
    _approve(second_id)
    activation = _transition(second_id, "approved", "active")
    assert activation["superseded_version_ids"] == [first_id]

    active = client.get(f"{BASE}/active-rations", headers=HEADERS)
    assert active.status_code == 200
    active_for_group = [item for item in active.json() if item["group_id"] == group["id"]]
    assert len(active_for_group) == 1
    assert active_for_group[0]["version_id"] == second_id
    assert active_for_group[0]["snapshot"]["result"]["status"] == "optimal"

    refreshed_first = client.get(f"{BASE}/rations/{first['id']}", headers=HEADERS)
    assert refreshed_first.status_code == 200
    assert refreshed_first.json()["versions"][0]["status"] == "retired"
    assert any(event["event_type"] == "superseded" for event in refreshed_first.json()["audit"])

    second_v2 = client.post(
        f"{BASE}/rations/{second['id']}/versions",
        headers=HEADERS,
        json={
            "expected_latest_version_no": 1,
            "based_on_version_id": second_id,
            "source": "manual",
            "comment": "Maismenge angepasst",
            "snapshot": {
                "profile": {"milk_kg": 38.5, "body_mass_kg": 675},
                "ration": [{"feed_id": "mais", "kg_dm": 8.4}],
                "result": {"cost_eur_cow_day": 4.75, "status": "optimal"},
            },
        },
    )
    assert second_v2.status_code == 201, second_v2.text
    assert second_v2.json()["version_no"] == 2
    detail = client.get(f"{BASE}/rations/{second['id']}", headers=HEADERS).json()
    assert [version["version_no"] for version in detail["versions"]] == [2, 1]
    assert detail["versions"][1]["snapshot"]["ration"][0]["kg_dm"] == 8.2

    other_tenant = client.get(
        f"{BASE}/rations/{second['id']}",
        headers={"Authorization": "Bearer dev-token", "X-Tenant-Id": str(uuid4())},
    )
    assert other_tenant.status_code == 404


def test_optimistic_version_and_status_conflicts_are_explicit() -> None:
    group = _group()
    ration = _ration(group["id"], "Conflict")
    version = ration["versions"][0]

    stale = client.post(
        f"{BASE}/rations/{ration['id']}/versions",
        headers=HEADERS,
        json={
            "expected_latest_version_no": 2,
            "source": "manual",
            "snapshot": {"ration": [{"feed_id": "gras", "kg_dm": 9.1}]},
        },
    )
    assert stale.status_code == 409
    assert "aktuell v1" in stale.json()["detail"]

    wrong_status = client.post(
        f"{BASE}/versions/{version['id']}/transitions",
        headers=HEADERS,
        json={"expected_status": "approved", "target_status": "active"},
    )
    assert wrong_status.status_code == 409
    assert "Statuskonflikt" in wrong_status.json()["detail"]


def test_due_scheduled_ration_is_activated_by_worker() -> None:
    group = _group()
    ration = _ration(group["id"], "Scheduled")
    version_id = ration["versions"][0]["id"]
    _approve(version_id)
    feeding_start = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
    _transition(version_id, "approved", "scheduled", feeding_start=feeding_start)

    result = execute_due_ration_activations()

    assert result["activated"] >= 1
    detail = client.get(f"{BASE}/rations/{ration['id']}", headers=HEADERS)
    assert detail.status_code == 200
    assert detail.json()["latest_status"] == "active"


def test_readiness_blocker_requires_audited_override() -> None:
    group = _group()
    response = client.post(f"{BASE}/rations", headers=HEADERS, json={
        "group_id": group["id"], "name": "Blockierte Ration", "source": "solver",
        "snapshot": {"readiness": {"status": "blocked", "blocker_count": 1, "warning_count": 0, "materials": []}},
    })
    assert response.status_code == 201
    version_id = response.json()["latest_version_id"]
    _transition(version_id, "draft", "in_review")
    blocked = client.post(f"{BASE}/versions/{version_id}/transitions", headers=HEADERS,
        json={"expected_status": "in_review", "target_status": "approved", "reason": "Trotzdem"})
    assert blocked.status_code == 409
    approved = client.post(f"{BASE}/versions/{version_id}/transitions", headers=HEADERS,
        json={"expected_status": "in_review", "target_status": "approved", "reason": "OVERRIDE: Ersatzlieferung zugesagt"})
    assert approved.status_code == 200
