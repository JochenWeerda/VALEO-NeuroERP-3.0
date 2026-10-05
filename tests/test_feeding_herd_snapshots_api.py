"""FEED-HERD-043 (TDD-Red-Welle 1): AnimalGroupSnapshots aus Herd-Deltas,
Parameterhistorie und Veraltet-Warnung. Vor der Implementierung geschrieben.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.auth.deps import get_current_user
from app.core.database import SessionLocal, get_db
from app.core.tenant import get_tenant_id
from app.main import app as main_app

ROOT = "/api/v1/agrar/rations-optimization"
TENANT = "00000000-0000-0000-0000-000000000001"
HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-Id": TENANT}
client = TestClient(main_app, raise_server_exceptions=False)


@pytest.mark.parametrize(("method", "path"), [
    ("post", "/feeding/groups/g-1/snapshots/condense"),
    ("get", "/feeding/groups/g-1/parameter-history"),
    ("get", "/feeding/groups/g-1/parameter-staleness"),
    ("post", "/feeding/groups/g-1/confirm-parameters"),
])
def test_herd_history_endpoints_reject_user_without_role(method: str, path: str) -> None:
    from app.api.v1.endpoints import feeding_herd_history
    app = FastAPI()
    app.include_router(feeding_herd_history.router)
    app.dependency_overrides[get_current_user] = lambda: {"sub": "role-test", "roles": []}
    app.dependency_overrides[get_tenant_id] = lambda: "tenant-role-test"
    app.dependency_overrides[get_db] = lambda: object()
    with TestClient(app) as role_client:
        response = getattr(role_client, method)(path)
    assert response.status_code == 403, (method, path, response.text)


# ── Journey (Dev-DB) ────────────────────────────────────────────────────────

def _setup_group_with_observations(suffix: str) -> dict[str, Any]:
    herd_ref = f"herd-{suffix}"
    provider_group = f"ext-group-{suffix}"
    connection = client.post(f"{ROOT}/integrations/herd-data/connections", headers=HEADERS, json={
        "provider": "ddw", "herd_id": herd_ref,
        "base_url": "https://api.dairydatawarehouse.com",
        "endpoint_templates": {"group_kpi": "/kpi/{herd_id}",
                               "health_alert": "/alerts/{herd_id}",
                               "genetic_profile": "/genetics/{herd_id}"},
        "contract_ref": f"contract-{suffix}", "consent_ref": f"consent-{suffix}"})
    assert connection.status_code == 200, connection.text
    connection_id = connection.json()["id"]

    group = client.post(f"{ROOT}/lifecycle/groups", headers=HEADERS, json={
        "name": f"Herd {suffix}", "external_ref": provider_group,
        "animal_count": 50, "feeding_system": "TMR",
        "profile_code": "fresh_cow", "pregnancy_status": "unknown"})
    assert group.status_code == 201, group.text
    group_id = group.json()["id"]

    def ingest(day: str, cow_count: int, milk: float, sync: str) -> None:
        response = client.post(f"{ROOT}/integrations/herd-data/mock-import", headers=HEADERS, json={
            "connection_id": connection_id, "kind": "group_kpi", "persist": True,
            "payload": {"herd_id": herd_ref, "currency_date": day, "sync_timestamp": sync,
                        "group_metrics": [{"group_id": provider_group,
                                           "group_name": f"Herd {suffix}",
                                           "cow_count": cow_count,
                                           "kpis": {"milk_kg": milk}}]}})
        assert response.status_code == 200, response.text
        assert response.json()["imported_count"] == 1

    ingest("2026-07-14", 48, 31.2, "2026-07-14T06:00:00Z")
    ingest("2026-07-15", 49, 31.8, "2026-07-15T06:00:00Z")
    # Korrektur desselben Tages (juengerer Sync ersetzt den Datenstand)
    ingest("2026-07-15", 52, 32.4, "2026-07-15T18:00:00Z")
    return {"group_id": group_id, "connection_id": connection_id,
            "provider_group": provider_group}


def test_condense_builds_idempotent_daily_snapshots_with_history() -> None:
    setup = _setup_group_with_observations(uuid4().hex[:8])
    group_id = setup["group_id"]

    first = client.post(f"{ROOT}/feeding/groups/{group_id}/snapshots/condense",
                        headers=HEADERS)
    assert first.status_code == 200, first.text
    assert first.json()["snapshot_count"] == 2

    # idempotent: zweiter Lauf bei gleichem Datenstand aendert nichts
    second = client.post(f"{ROOT}/feeding/groups/{group_id}/snapshots/condense",
                         headers=HEADERS)
    assert second.status_code == 200
    assert second.json()["snapshot_count"] == 2

    history = client.get(f"{ROOT}/feeding/groups/{group_id}/parameter-history",
                         headers=HEADERS)
    assert history.status_code == 200, history.text
    days = history.json()
    assert [item["snapshot_date"] for item in days] == ["2026-07-15", "2026-07-14"]
    assert days[0]["cow_count"] == 52, "Tageskorrektur (juengster Sync) gewinnt"
    assert days[0]["kpis"]["milk_kg"] == 32.4
    assert days[1]["cow_count"] == 48

    # unbekannte Gruppe -> 404
    missing = client.post(f"{ROOT}/feeding/groups/{uuid4()}/snapshots/condense",
                          headers=HEADERS)
    assert missing.status_code == 404


def test_parameter_staleness_confirmation_and_editor_warning() -> None:
    setup = _setup_group_with_observations(uuid4().hex[:8])
    group_id = setup["group_id"]

    fresh = client.get(f"{ROOT}/feeding/groups/{group_id}/parameter-staleness",
                       headers=HEADERS)
    assert fresh.status_code == 200, fresh.text
    assert fresh.json()["stale"] is False
    assert fresh.json()["days_since_confirmation"] == 0

    # Bestaetigung kuenstlich altern lassen (60 Tage)
    db = SessionLocal()
    try:
        db.execute(text("""UPDATE domain_agrar.feeding_groups
          SET updated_at = now() - INTERVAL '60 days'
          WHERE tenant_id=:tenant_id AND id=:group_id"""),
                   {"tenant_id": TENANT, "group_id": group_id})
        db.commit()
    finally:
        db.close()

    stale = client.get(f"{ROOT}/feeding/groups/{group_id}/parameter-staleness",
                       headers=HEADERS)
    assert stale.status_code == 200
    assert stale.json()["stale"] is True
    assert stale.json()["days_since_confirmation"] >= 59

    # Editor-Bedarfswarnung: Draft-Bewertung nennt veraltete Gruppenparameter
    profile = client.post(f"{ROOT}/feeding/requirement-profiles", headers=HEADERS,
                          json={"group_id": group_id, "inputs": {"milk_kg_day": 30}})
    assert profile.status_code == 201, profile.text
    feed = client.post(f"{ROOT}/feed-catalog/feeds", headers=HEADERS, json={
        "artikel_nummer": f"HERD-{uuid4().hex[:8]}", "name": "Herdengras",
        "art": "Grundfutter", "feed_kind": "forage", "approval_status": "approved"})
    assert feed.status_code == 201, feed.text
    evaluated = client.post(f"{ROOT}/feeding/ration-drafts/evaluate", headers=HEADERS, json={
        "group_id": group_id,
        "components": [{"feed_id": feed.json()["id"], "kg_fm": 30.0}]})
    assert evaluated.status_code == 200, evaluated.text
    stale_findings = [item for item in evaluated.json()["findings"]
                      if item["code"] == "group_parameters_stale"]
    assert stale_findings, "Draft-Bewertung warnt vor veralteten Gruppenparametern"
    assert "Tag" in stale_findings[0]["message"], "Warnung nennt das Alter im Text"

    # Bestaetigung setzt die Warnung zurueck
    confirmed = client.post(f"{ROOT}/feeding/groups/{group_id}/confirm-parameters",
                            headers=HEADERS)
    assert confirmed.status_code == 200, confirmed.text
    assert confirmed.json()["days_since_confirmation"] == 0
    after = client.get(f"{ROOT}/feeding/groups/{group_id}/parameter-staleness",
                       headers=HEADERS)
    assert after.json()["stale"] is False
