"""Studio API: catalog, propose, validate, four-eyes publish."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.studio_draft_store import reset_studio_drafts
from app.services.studio_propose import propose_studio_draft
from app.services.studio_validation import validate_studio_draft

pytestmark = pytest.mark.unit

_HEADERS = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-ID": "00000000-0000-0000-0000-000000000001",
}


@pytest.fixture(autouse=True)
def _reset_drafts():
    reset_studio_drafts()
    yield
    reset_studio_drafts()


def _client() -> TestClient:
    return TestClient(app, raise_server_exceptions=False)


def test_catalog_exposes_floorplans_and_sources() -> None:
    response = _client().get("/api/v1/studio/catalog", headers=_HEADERS)
    assert response.status_code == 200
    body = response.json()
    assert "worklist" in body["floorplans"]
    assert body["dataSources"]
    assert body["actions"]


def test_propose_builds_tenant_worklist() -> None:
    response = _client().post("/api/v1/studio/propose", headers=_HEADERS, json={"intent": "Kundenliste für Aussendienst"})
    assert response.status_code == 200
    body = response.json()
    assert body["definition"]["id"].startswith("tenant/")
    assert body["definition"]["layout"]["columnNavigation"] == "listDetail"
    assert body["violations"] == []
    assert body["canPublish"] is True


def test_validate_rejects_foreign_endpoint() -> None:
    draft = propose_studio_draft("Lieferanten")
    draft["dataSources"][0]["endpoint"] = "https://evil.example/x"
    response = _client().post("/api/v1/studio/validate", headers=_HEADERS, json={"definition": draft})
    assert response.status_code == 200
    assert any(item.startswith("datenquelle_nicht_im_katalog") for item in response.json()["violations"])


def test_save_and_same_actor_cannot_publish() -> None:
    client = _client()
    draft = propose_studio_draft("Lieferanten bewerten")
    created = client.post(
        "/api/v1/studio/drafts",
        headers={**_HEADERS, "X-Actor-ID": "anna"},
        json={"definition": draft},
    )
    assert created.status_code == 200, created.text
    draft_id = created.json()["id"]
    forbidden = client.post(
        f"/api/v1/studio/drafts/{draft_id}/publish",
        headers={**_HEADERS, "X-Actor-ID": "anna"},
    )
    assert forbidden.status_code == 403
    published = client.post(
        f"/api/v1/studio/drafts/{draft_id}/publish",
        headers={**_HEADERS, "X-Actor-ID": "berta"},
    )
    assert published.status_code == 200, published.text
    assert published.json()["status"] == "published_temp"


def test_tenant_isolation() -> None:
    client = _client()
    draft = propose_studio_draft("Artikel")
    created = client.post(
        "/api/v1/studio/drafts",
        headers={**_HEADERS, "X-Actor-ID": "anna"},
        json={"definition": draft},
    )
    draft_id = created.json()["id"]
    other = client.get(
        "/api/v1/studio/drafts",
        headers={"Authorization": "Bearer dev-token", "X-Tenant-ID": "tenant-b"},
    )
    assert other.json()["drafts"] == []
    missing = client.get(
        f"/api/v1/studio/drafts",
        headers=_HEADERS,
    )
    assert any(item["id"] == draft_id for item in missing.json()["drafts"])


def test_validation_kernel_flags_unknown_data_source() -> None:
    draft = propose_studio_draft("Lieferanten")
    draft["dataSources"][0]["endpoint"] = "/api/v1/not-in-catalog"
    assert any("datenquelle_nicht_im_katalog" in item for item in validate_studio_draft(
        draft, native_screen_ids=set(),
    ))
