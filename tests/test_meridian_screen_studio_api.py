"""Studio API: catalog, propose, validate, four-eyes publish."""

from __future__ import annotations
from uuid import uuid4
from studio_review_helper import publish_reviewed, simulation_ready_definition

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.auth.deps import get_current_user
from app.core.screen_definitions import get_screen_definition
from app.services.studio_draft_store import reset_studio_drafts, save_draft, set_status
from app.services.studio_propose import propose_studio_draft as original_proposal

def propose_studio_draft(intent):
    return simulation_ready_definition(original_proposal(intent))
from app.services.studio_validation import validate_studio_draft

pytestmark = pytest.mark.unit

_HEADERS = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-ID": "00000000-0000-0000-0000-000000000001",
}


_USER = {"sub": "anna", "roles": ["admin"], "raw": {"identity_type": "human"}}


@pytest.fixture(autouse=True)
def _reset_drafts():
    _USER.clear()
    _USER.update(sub="anna", roles=["admin"], raw={"identity_type": "human"})
    previous_user = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = lambda: _USER
    reset_studio_drafts()
    yield
    if previous_user is None:
        app.dependency_overrides.pop(get_current_user, None)
    else:
        app.dependency_overrides[get_current_user] = previous_user
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
    assert body["definitionReady"] is True
    assert body["canPublish"] is False
    assert body["requiresSimulation"] is True


def test_validate_rejects_foreign_endpoint() -> None:
    draft = propose_studio_draft("Lieferanten")
    draft["dataSources"][0]["endpoint"] = "https://evil.example/x"
    response = _client().post("/api/v1/studio/validate", headers=_HEADERS, json={"definition": draft, 'idempotency_key': str(uuid4())})
    assert response.status_code == 200
    assert any(item.startswith("datenquelle_nicht_im_katalog") for item in response.json()["violations"])


def test_save_and_same_actor_cannot_publish() -> None:
    client = _client()
    draft = propose_studio_draft("Lieferanten bewerten")
    created = client.post(
        "/api/v1/studio/drafts",
        headers={**_HEADERS, "X-Actor-ID": "anna"},
        json={"definition": draft, 'idempotency_key': str(uuid4())},
    )
    assert created.status_code == 200, created.text
    draft_id = created.json()["id"]
    forbidden = publish_reviewed(
        client, f"/api/v1/studio/drafts/{draft_id}/publish",
        headers={**_HEADERS, "X-Actor-ID": "anna"},
    )
    assert forbidden.status_code == 403
    _USER["sub"] = "berta"
    published = publish_reviewed(
        client, f"/api/v1/studio/drafts/{draft_id}/publish",
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
        json={"definition": draft, 'idempotency_key': str(uuid4())},
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


def _publish_sample(client: TestClient, intent: str = "Lieferanten bewerten") -> dict:
    draft = propose_studio_draft(intent)
    created = client.post(
        "/api/v1/studio/drafts",
        headers={**_HEADERS, "X-Actor-ID": "anna"},
        json={"definition": draft, 'idempotency_key': str(uuid4())},
    )
    assert created.status_code == 200, created.text
    _USER["sub"] = "berta"
    published = publish_reviewed(
        client, f"/api/v1/studio/drafts/{created.json()['id']}/publish",
        headers={**_HEADERS, "X-Actor-ID": "berta"},
    )
    assert published.status_code == 200, published.text
    return published.json()


def test_published_temp_is_in_runtime_catalog() -> None:
    record = _publish_sample(_client())
    screen_id = record["screen_id"]
    tenant_id = _HEADERS["X-Tenant-ID"]
    definition = get_screen_definition(screen_id, tenant_id=tenant_id)
    assert definition is not None
    assert definition["id"] == screen_id
    assert definition["adapter"]["temporary"] is True
    encoded = screen_id.replace("/", "__")
    response = _client().get(f"/api/v1/masks/{encoded}/screen-definition", headers=_HEADERS)
    assert response.status_code == 200, response.text
    assert response.json()["id"] == screen_id
    assert record["route"] == f"/studio/run/{encoded}"


def test_native_screen_is_never_shadowed_by_studio_draft() -> None:
    tenant_id = _HEADERS["X-Tenant-ID"]
    native = get_screen_definition("crm/customer-360", tenant_id=tenant_id)
    assert native is not None
    assert native["adapter"]["temporary"] is False
    poisoned = save_draft(
        tenant_id,
        "anna",
        {**propose_studio_draft("Kunden"), "id": "crm/customer-360"},
    )
    set_status(tenant_id, poisoned["id"], "anna", "review")
    with pytest.raises(ValueError, match="studio_definition_nicht_freigabefaehig"):
        set_status(tenant_id, poisoned["id"], "berta", "published_temp")
    still_native = get_screen_definition("crm/customer-360", tenant_id=tenant_id)
    assert still_native is not None
    assert still_native["adapter"]["temporary"] is False
    assert still_native["id"] == "crm/customer-360"


def test_omnibox_includes_published_studio_mask() -> None:
    record = _publish_sample(_client(), "Artikel für Aussendienst")
    response = _client().get("/api/v1/ui/mask-registry/omnibox-catalog", headers=_HEADERS)
    assert response.status_code == 200, response.text
    by_id = {item["screen_id"]: item for item in response.json()}
    entry = by_id[record["screen_id"]]
    assert entry["route"].startswith("/studio/run/")
    assert entry["title"]


def test_retire_removes_mask_from_runtime_catalog() -> None:
    client = _client()
    record = _publish_sample(client)
    retired = client.post(
        f"/api/v1/studio/drafts/{record['id']}/retire",
        json={"expected_revision": record["revision"], 'idempotency_key': str(uuid4())},
        headers={**_HEADERS, "X-Actor-ID": "clara"},
    )
    assert retired.status_code == 200, retired.text
    assert retired.json()["status"] == "retired"
    assert get_screen_definition(record["screen_id"], tenant_id=_HEADERS["X-Tenant-ID"]) is None
