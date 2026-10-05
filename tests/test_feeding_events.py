"""FEED-INT-036: Schemafeste Feeding-Events (TDD-Red-Welle 1).

Vor der Implementierung geschrieben; scheiterte zunaechst mit ImportError auf
app.agrar.rations.events.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.database import SessionLocal
from app.main import app as main_app

client = TestClient(main_app, raise_server_exceptions=False)
ROOT = "/api/v1/agrar/rations-optimization"
TENANT = "00000000-0000-0000-0000-000000000001"
HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-Id": TENANT}


# ── Contract (ohne DB) ──────────────────────────────────────────────────────


def test_event_builder_produces_stable_schema_and_rejects_unknown_types() -> None:
    from app.agrar.rations.events import FEEDING_EVENT_TYPES, build_feeding_event

    assert FEEDING_EVENT_TYPES == {
        "feeding.analysis.released",
        "feeding.ration.version.activated",
        "feeding.plan.published",
        "feeding.actual.recorded",
        "feeding.deviation.exceeded",
        "feeding.measure.created",
        "feeding.measure.completed",
        "feeding.measure.overdue",
        "feeding.import.quarantined",
        "feeding.supply.procurement_handoff.created",
    }

    event = build_feeding_event(
        "feeding.import.quarantined",
        aggregate_id="job-1",
        payload={"adapter": "laboratory"},
    )
    assert event["schema_version"] == "1.0"
    assert event["event_type"] == "feeding.import.quarantined"
    assert event["aggregate_id"] == "job-1"
    assert UUID(event["event_id"])
    assert "T" in event["timestamp"], "ISO-Zeitstempel"
    assert event["payload"] == {"adapter": "laboratory"}

    with pytest.raises(ValueError):
        build_feeding_event("feeding.unknown.event", aggregate_id="x", payload={})


def test_event_insert_participates_in_callers_transaction() -> None:
    from app.agrar.rations.events import emit_feeding_event

    aggregate_id = f"rollback-{uuid4()}"
    db = SessionLocal()
    try:
        emit_feeding_event(
            db,
            tenant_id=TENANT,
            event_type="feeding.import.quarantined",
            aggregate_id=aggregate_id,
            payload={"reason": "rollback-contract"},
        )
        db.rollback()
    finally:
        db.close()
    assert _outbox_events("feeding.import.quarantined", aggregate_id) == []


# ── Emissions-Journeys (Dev-DB) ─────────────────────────────────────────────


def _outbox_events(event_type: str, aggregate_id: str) -> list[dict[str, Any]]:
    db = SessionLocal()
    try:
        rows = (
            db.execute(
                text("""
          SELECT id, payload FROM public.outbox_events
          WHERE tenant_id=:tenant_id AND event_type=:event_type AND aggregate_id=:aggregate_id
        """),
                {
                    "tenant_id": TENANT,
                    "event_type": event_type,
                    "aggregate_id": aggregate_id,
                },
            )
            .mappings()
            .all()
        )
        return [dict(row) for row in rows]
    finally:
        db.close()


def test_ration_activation_emits_exactly_one_event_in_same_transaction() -> None:
    suffix = uuid4().hex[:8]
    group = client.post(
        f"{ROOT}/lifecycle/groups",
        headers=HEADERS,
        json={
            "name": f"Events {suffix}",
            "animal_count": 10,
            "feeding_system": "TMR",
            "profile_code": "fresh_cow",
            "pregnancy_status": "unknown",
        },
    )
    assert group.status_code == 201, group.text
    ration = client.post(
        f"{ROOT}/lifecycle/rations",
        headers=HEADERS,
        json={
            "group_id": group.json()["id"],
            "name": f"EventRation {suffix}",
            "snapshot": {"components": [{"feed_id": f"f-{suffix}", "kg_fm": 10.0}]},
        },
    )
    assert ration.status_code == 201, ration.text
    version_id = ration.json()["latest_version_id"]

    for target, expected in (
        ("in_review", "draft"),
        ("approved", "in_review"),
        ("active", "approved"),
    ):
        transition = client.post(
            f"{ROOT}/lifecycle/versions/{version_id}/transitions",
            headers=HEADERS,
            json={"target_status": target, "expected_status": expected},
        )
        assert transition.status_code == 200, transition.text

    events = _outbox_events("feeding.ration.version.activated", version_id)
    assert len(events) == 1, "genau ein Aktivierungsereignis je Aktivierung"
    payload = events[0]["payload"]
    if isinstance(payload, str):
        import json as _json

        payload = _json.loads(payload)
    assert payload["schema_version"] == "1.0"
    assert payload["payload"]["group_id"] == group.json()["id"]
    assert payload["payload"]["version_no"] == 1


def test_quarantined_import_emits_event() -> None:
    quarantined = client.post(
        f"{ROOT}/feeding/imports",
        headers=HEADERS,
        json={"adapter": "laboratory", "payload": {"foo": "bar"}},
    )
    assert quarantined.status_code == 201, quarantined.text
    job = quarantined.json()
    assert job["status"] == "quarantined"

    events = _outbox_events("feeding.import.quarantined", job["id"])
    assert len(events) == 1
