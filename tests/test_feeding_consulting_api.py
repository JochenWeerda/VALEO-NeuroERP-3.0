"""FEED-CONS-031: Beratungsfall und Beobachtungen (TDD-Red-Welle 1).

Vor der Implementierung geschrieben; scheiterte zunaechst mit ImportError auf
app.api.v1.endpoints.feeding_consulting.
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
    from app.api.v1.endpoints import feeding_consulting
    app = FastAPI()
    app.include_router(feeding_consulting.router)
    app.dependency_overrides[get_current_user] = lambda: {"sub": "role-test", "roles": _CONTEXT["roles"]}
    app.dependency_overrides[get_tenant_id] = lambda: "tenant-role-test"
    app.dependency_overrides[get_db] = lambda: object()
    return app


REQUESTS = [
    ("post", "/feeding/consulting-cases", {"title": "Besuch", "case_type": "visit"}),
    ("get", "/feeding/consulting-cases", None),
    ("get", "/feeding/consulting-cases/c-1", None),
    ("post", "/feeding/consulting-cases/c-1/observations", {
        "category": "fuetterung", "text": "Beobachtung", "client_ref": "m-1"}),
    ("post", "/feeding/consulting-cases/c-1/close", {"summary": "Fazit"}),
]


@pytest.mark.parametrize(("method", "path", "body"), REQUESTS)
def test_consulting_endpoints_reject_user_without_domain_role(method: str, path: str, body: dict | None) -> None:
    _CONTEXT["roles"] = []
    with TestClient(_build_role_app()) as client:
        response = getattr(client, method)(path, **({"json": body} if body is not None else {}))
    assert response.status_code == 403, (method, path, response.text)


# ── Journey (Dev-DB) ────────────────────────────────────────────────────────

from app.main import app as main_app  # noqa: E402

client = TestClient(main_app, raise_server_exceptions=False)
ROOT = "/api/v1/agrar/rations-optimization/feeding"
LIFECYCLE = "/api/v1/agrar/rations-optimization/lifecycle"
TENANT = "00000000-0000-0000-0000-000000000001"
HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-Id": TENANT}


def test_consulting_case_journey_with_idempotent_mobile_observation() -> None:
    suffix = uuid4().hex[:8]

    group = client.post(f"{LIFECYCLE}/groups", headers=HEADERS, json={
        "name": f"Beratung {suffix}", "animal_count": 20, "feeding_system": "TMR",
        "profile_code": "fresh_cow", "pregnancy_status": "unknown"})
    assert group.status_code == 201, group.text
    group_id = group.json()["id"]

    created = client.post(f"{ROOT}/consulting-cases", headers=HEADERS, json={
        "title": f"Stallbesuch {suffix}", "case_type": "visit",
        "group_id": group_id,
        "initial_situation": "Futteraufnahme schwankt seit zwei Wochen."})
    assert created.status_code == 201, created.text
    case = created.json()
    assert case["status"] == "open"
    case_id = case["id"]

    # Mobiler Pfad: dieselbe client_ref zweimal -> exakt eine Beobachtung
    body = {"category": "fuetterung", "text": "Restfutter selektiert, Silage warm.",
            "client_ref": f"mobil-{suffix}",
            "photo_document_refs": ["dms://beleg/123"]}
    first = client.post(f"{ROOT}/consulting-cases/{case_id}/observations", headers=HEADERS, json=body)
    assert first.status_code == 201, first.text
    second = client.post(f"{ROOT}/consulting-cases/{case_id}/observations", headers=HEADERS, json=body)
    assert second.status_code == 201, second.text
    assert second.json()["id"] == first.json()["id"], "client_ref muss idempotent sein"
    assert second.json()["duplicate"] is True

    detail = client.get(f"{ROOT}/consulting-cases/{case_id}", headers=HEADERS)
    assert detail.status_code == 200, detail.text
    payload = detail.json()
    assert len(payload["observations"]) == 1
    assert payload["observations"][0]["photo_document_refs"] == ["dms://beleg/123"]

    listed = client.get(f"{ROOT}/consulting-cases?status=open", headers=HEADERS)
    assert listed.status_code == 200
    assert any(item["id"] == case_id for item in listed.json())

    closed = client.post(f"{ROOT}/consulting-cases/{case_id}/close", headers=HEADERS,
                         json={"summary": "Silomanagement angepasst; Nachkontrolle in 14 Tagen."})
    assert closed.status_code == 200, closed.text
    assert closed.json()["status"] == "closed"
    assert closed.json()["closing_summary"].startswith("Silomanagement")

    # Geschlossener Fall nimmt keine neuen Beobachtungen an -> 409
    late = client.post(f"{ROOT}/consulting-cases/{case_id}/observations", headers=HEADERS,
                       json={"category": "sonstiges", "text": "zu spaet", "client_ref": f"x-{suffix}"})
    assert late.status_code == 409

    # Tenant-Isolation
    foreign = client.get(f"{ROOT}/consulting-cases/{case_id}",
                         headers={**HEADERS, "X-Tenant-Id": str(uuid4())})
    assert foreign.status_code == 404

    # Unbekannte Gruppe -> 404 statt Waisen-Fall
    orphan = client.post(f"{ROOT}/consulting-cases", headers=HEADERS, json={
        "title": "Waise", "case_type": "remote", "group_id": str(uuid4())})
    assert orphan.status_code == 404
