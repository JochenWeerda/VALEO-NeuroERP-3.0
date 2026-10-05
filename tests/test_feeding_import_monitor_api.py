"""FEED-INT-034: Integrationsmonitor (TDD-Red-Welle 1).

Vor der Implementierung geschrieben; scheiterte zunaechst mit ImportError auf
app.api.v1.endpoints.feeding_import_monitor.
"""
from __future__ import annotations

from typing import Any
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.auth.deps import get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id

_CONTEXT: dict[str, Any] = {"roles": []}


def _build_role_app() -> FastAPI:
    from app.api.v1.endpoints import feeding_import_monitor
    app = FastAPI()
    app.include_router(feeding_import_monitor.router)
    app.dependency_overrides[get_current_user] = lambda: {"sub": "role-test", "roles": _CONTEXT["roles"]}
    app.dependency_overrides[get_tenant_id] = lambda: "tenant-role-test"
    app.dependency_overrides[get_db] = lambda: object()
    return app


REQUESTS = [
    ("post", "/feeding/imports/preview", {"adapter": "laboratory", "payload": {}}),
    ("post", "/feeding/imports", {"adapter": "laboratory", "payload": {}}),
    ("get", "/feeding/imports", None),
    ("post", "/feeding/imports/j-1/accept", {}),
    ("post", "/feeding/imports/j-1/reject", {"reason": "unplausibel"}),
]


@pytest.mark.parametrize(("method", "path", "body"), REQUESTS)
def test_import_monitor_rejects_user_without_domain_role(method: str, path: str, body: dict | None) -> None:
    _CONTEXT["roles"] = []
    with TestClient(_build_role_app()) as client:
        response = getattr(client, method)(path, **({"json": body} if body is not None else {}))
    assert response.status_code == 403, (method, path, response.text)


# ── Journey (Dev-DB) ────────────────────────────────────────────────────────

from app.main import app as main_app  # noqa: E402

client = TestClient(main_app, raise_server_exceptions=False)
ROOT = "/api/v1/agrar/rations-optimization/feeding"
TENANT = "00000000-0000-0000-0000-000000000001"
HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-Id": TENANT}


def _lab_payload(suffix: str) -> dict[str, Any]:
    # Vertrag von laboratory_to_feed_ingredient (Validierungs-SSOT im Adapter)
    return {
        "sample_id": f"probe-{suffix}",
        "material": "Grassilage 1. Schnitt",
        "dry_matter_pct": 34.5,
        "me_mj_kgdm": 10.4,
        "sidp_g_kgdm": 68.0,
        "laboratory": "LUFA Nord-West",
    }


def test_preview_validates_without_persisting() -> None:
    suffix = uuid4().hex[:8]
    preview = client.post(f"{ROOT}/imports/preview", headers=HEADERS,
                          json={"adapter": "laboratory", "payload": _lab_payload(suffix)})
    assert preview.status_code == 200, preview.text
    payload = preview.json()
    assert payload["valid"] is True
    assert payload["adapter"] == "laboratory"
    assert payload["mapped"]["external_id"], "Vorschau zeigt die Zuordnung"

    # Kaputte Payload -> valid=false mit verstaendlichem Befund, KEIN Job
    broken = client.post(f"{ROOT}/imports/preview", headers=HEADERS,
                         json={"adapter": "laboratory", "payload": {"foo": "bar"}})
    assert broken.status_code == 200, broken.text
    assert broken.json()["valid"] is False
    assert broken.json()["findings"], "Validierungsbericht benennt den Fehler"

    jobs = client.get(f"{ROOT}/imports", headers=HEADERS)
    assert jobs.status_code == 200
    assert not any(j.get("adapter") == "laboratory" and suffix in str(j.get("payload_excerpt", ""))
                   for j in jobs.json()), "Preview darf nichts persistieren"


def test_import_job_quarantine_and_controlled_acceptance() -> None:
    suffix = uuid4().hex[:8]

    # Gueltige Payload -> Job validated
    created = client.post(f"{ROOT}/imports", headers=HEADERS,
                          json={"adapter": "laboratory", "payload": _lab_payload(suffix)})
    assert created.status_code == 201, created.text
    job = created.json()
    assert job["status"] == "validated"
    job_id = job["id"]

    # Accept uebernimmt kontrolliert ueber den bestehenden idempotenten Importpfad
    accepted = client.post(f"{ROOT}/imports/{job_id}/accept", headers=HEADERS, json={})
    assert accepted.status_code == 200, accepted.text
    assert accepted.json()["status"] == "accepted"
    assert accepted.json()["result_ref"], "Uebernahme referenziert das Importergebnis"

    # Zweites Accept ist idempotent-freundlich verboten -> 409
    again = client.post(f"{ROOT}/imports/{job_id}/accept", headers=HEADERS, json={})
    assert again.status_code == 409

    # Kaputte Payload -> Quarantaene mit Befunden (kein Wegwerfen)
    quarantined = client.post(f"{ROOT}/imports", headers=HEADERS,
                              json={"adapter": "laboratory", "payload": {"foo": "bar"}})
    assert quarantined.status_code == 201, quarantined.text
    qjob = quarantined.json()
    assert qjob["status"] == "quarantined"
    assert qjob["findings"], "Quarantaene traegt den Validierungsbefund"

    # Quarantaene kann nicht uebernommen werden -> 409; Reject verlangt Begruendung
    blocked = client.post(f"{ROOT}/imports/{qjob['id']}/accept", headers=HEADERS, json={})
    assert blocked.status_code == 409
    no_reason = client.post(f"{ROOT}/imports/{qjob['id']}/reject", headers=HEADERS, json={"reason": ""})
    assert no_reason.status_code == 422
    rejected = client.post(f"{ROOT}/imports/{qjob['id']}/reject", headers=HEADERS,
                           json={"reason": "Analysewerte unplausibel, Labor kontaktiert."})
    assert rejected.status_code == 200, rejected.text
    assert rejected.json()["status"] == "rejected"
    assert rejected.json()["decision_reason"].startswith("Analysewerte")

    # Monitor-Worklist zeigt beide Jobs mit Status
    jobs = client.get(f"{ROOT}/imports?status=rejected", headers=HEADERS)
    assert jobs.status_code == 200
    assert any(item["id"] == qjob["id"] for item in jobs.json())

    # Tenant-Isolation + unbekannter Job
    foreign = client.post(f"{ROOT}/imports/{job_id}/accept",
                          headers={**HEADERS, "X-Tenant-Id": str(uuid4())}, json={})
    assert foreign.status_code == 404
    missing = client.post(f"{ROOT}/imports/{uuid4()}/accept", headers=HEADERS, json={})
    assert missing.status_code == 404
