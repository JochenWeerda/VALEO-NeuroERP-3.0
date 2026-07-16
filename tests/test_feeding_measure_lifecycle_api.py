"""FEED-CONS-032 red API/DB contract for versioned measures."""

from datetime import date, timedelta
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api.v1.endpoints import feeding_measures
from app.auth.deps import get_current_user
from app.core.database import SessionLocal
from app.core.tenant import get_tenant_id
from app.main import app
from test_feeding_actual_api import BASE, HEADERS, TENANT, _plan


client = TestClient(app, raise_server_exceptions=False)


def _measure(*, due_date: date) -> dict:
    plan, feed_id = _plan()
    policy = client.post(
        f"{BASE}/feeding/actuals/deviation-policies",
        headers=HEADERS,
        json={
            "feed_class": "forage",
            "warning_pct": "5",
            "critical_pct": "10",
            "valid_from": "2026-01-01",
            "reason": "Grundfutterschwelle fuer Lifecycle-Test festlegen",
        },
    )
    assert policy.status_code == 201, policy.text
    actual = client.post(
        f"{BASE}/feeding/actuals",
        headers=HEADERS,
        json={
            "plan_version_id": plan["id"],
            "feeding_at": "2026-07-16T08:00:00Z",
            "source": "manual",
            "source_ref": f"lifecycle-{uuid4()}",
            "cause_class": "dosing_error",
            "comment": "Abweichung fuer Lifecycle-Abnahme",
            "idempotency_key": f"lifecycle-actual-{uuid4()}",
            "components": [{"feed_id": feed_id, "actual_kg": 115}],
        },
    )
    assert actual.status_code == 201, actual.text
    created = client.post(
        f"{BASE}/feeding/actuals/measures",
        headers=HEADERS,
        json={
            "actual_component_id": actual.json()["components"][0]["id"],
            "title": "Waage und Dosierung pruefen",
            "owner_subject": "dev",
            "due_date": due_date.isoformat(),
            "reason": "Kritische Abweichung bis zur Wirksamkeit verfolgen",
            "idempotency_key": f"lifecycle-measure-{uuid4()}",
        },
    )
    assert created.status_code == 201, created.text
    return created.json()


def test_measure_transition_is_optimistic_append_only_and_effectiveness_guarded() -> (
    None
):
    measure = _measure(due_date=date.today() + timedelta(days=2))
    direct = client.post(
        f"{BASE}/feeding/measures/{measure['id']}/transitions",
        headers=HEADERS,
        json={
            "expected_version": 1,
            "target_status": "completed",
            "reason": "Direkter Abschluss ohne Kontrolle ist verboten",
        },
    )
    assert direct.status_code == 409

    started = client.post(
        f"{BASE}/feeding/measures/{measure['id']}/transitions",
        headers=HEADERS,
        json={
            "expected_version": 1,
            "target_status": "in_progress",
            "reason": "Waagenkontrolle wurde dem Stallteam verbindlich zugewiesen",
        },
    )
    assert started.status_code == 200, started.text
    assert started.json()["version"] == 2
    assert started.json()["status"] == "in_progress"

    stale = client.post(
        f"{BASE}/feeding/measures/{measure['id']}/transitions",
        headers=HEADERS,
        json={
            "expected_version": 1,
            "target_status": "review_due",
            "reason": "Veraltete Revision darf nicht fortgeschrieben werden",
        },
    )
    assert stale.status_code == 409

    review = client.post(
        f"{BASE}/feeding/measures/{measure['id']}/transitions",
        headers=HEADERS,
        json={
            "expected_version": 2,
            "target_status": "review_due",
            "reason": "Umsetzung erfolgt Wirksamkeitskontrolle nach drei Tagen",
            "reminder_date": (date.today() + timedelta(days=3)).isoformat(),
        },
    )
    assert review.status_code == 200, review.text

    completed = client.post(
        f"{BASE}/feeding/measures/{measure['id']}/transitions",
        headers=HEADERS,
        json={
            "expected_version": 3,
            "target_status": "completed",
            "reason": "Wirksamkeitskontrolle wurde fachlich abgeschlossen",
            "effectiveness": "effective",
            "effectiveness_result": "Abweichung liegt an drei Folgetagen unter der Warnschwelle",
        },
    )
    assert completed.status_code == 200, completed.text
    assert completed.json()["version"] == 4
    history = client.get(
        f"{BASE}/feeding/measures/{measure['id']}/history", headers=HEADERS
    )
    assert [item["status"] for item in history.json()] == [
        "completed",
        "review_due",
        "in_progress",
        "open",
    ]
    worklist = client.get(f"{BASE}/feeding/actuals/measures", headers=HEADERS)
    projected = next(item for item in worklist.json() if item["id"] == measure["id"])
    assert projected["status"] == "completed"
    assert projected["version"] == 4
    assert projected["effectiveness"] == "effective"

    db = SessionLocal()
    try:
        count = db.execute(
            text(
                """SELECT count(*) FROM public.outbox_events
                WHERE tenant_id=:tenant_id AND event_type='feeding.measure.completed'
                  AND aggregate_id=:measure_id"""
            ),
            {"tenant_id": TENANT, "measure_id": measure["id"]},
        ).scalar_one()
        assert count == 1
    finally:
        db.close()


def test_overdue_run_is_idempotent_and_notification_is_recipient_scoped() -> None:
    measure = _measure(due_date=date.today())
    first = client.post(
        f"{BASE}/feeding/measures/process-overdue",
        headers=HEADERS,
        json={"as_of": (date.today() + timedelta(days=1)).isoformat()},
    )
    assert first.status_code == 200, first.text
    second = client.post(
        f"{BASE}/feeding/measures/process-overdue",
        headers=HEADERS,
        json={"as_of": (date.today() + timedelta(days=1)).isoformat()},
    )
    assert second.status_code == 200
    assert first.json()["created"] >= 1
    assert second.json()["created"] == 0

    notifications = client.get(f"{BASE}/feeding/notifications", headers=HEADERS)
    relevant = [
        item for item in notifications.json() if item["aggregate_id"] == measure["id"]
    ]
    assert len(relevant) == 1
    assert relevant[0]["deep_link"].endswith(measure["id"])
    db = SessionLocal()
    try:
        count = db.execute(
            text("""SELECT count(*) FROM public.outbox_events
              WHERE tenant_id=:tenant_id AND event_type='feeding.measure.overdue'
                AND aggregate_id=:measure_id"""),
            {"tenant_id": TENANT, "measure_id": measure["id"]},
        ).scalar_one()
        assert count == 1
    finally:
        db.close()


def test_measure_lifecycle_rejects_wrong_role_and_hides_ungranted_groups() -> None:
    measure = _measure(due_date=date.today() + timedelta(days=2))

    wrong_role_app = FastAPI()
    wrong_role_app.include_router(feeding_measures.router)
    wrong_role_app.dependency_overrides[get_current_user] = lambda: {
        "sub": "crm-reader",
        "roles": ["CRM_LESEN"],
    }
    wrong_role_app.dependency_overrides[get_tenant_id] = lambda: TENANT
    with TestClient(wrong_role_app, raise_server_exceptions=False) as wrong_role:
        assert (
            wrong_role.get(f"/feeding/measures/{measure['id']}/history").status_code
            == 403
        )
        assert wrong_role.get("/feeding/notifications").status_code == 403

    outsider_app = FastAPI()
    outsider_app.include_router(feeding_measures.router)
    outsider_app.dependency_overrides[get_current_user] = lambda: {
        "sub": f"external-reader-{uuid4()}",
        "roles": ["FUTTERMITTEL_LESEN"],
    }
    outsider_app.dependency_overrides[get_tenant_id] = lambda: TENANT
    with TestClient(outsider_app, raise_server_exceptions=False) as outsider:
        assert (
            outsider.get(f"/feeding/measures/{measure['id']}/history").status_code
            == 404
        )
        assert outsider.get("/feeding/notifications").json() == []
