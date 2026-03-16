from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints.ki_usability import router as ki_usability_router
from app.core.ki_action_registry import resolve_actions_for_context


def _build_client() -> TestClient:
    app = FastAPI()
    app.include_router(ki_usability_router, prefix="/api/v1")
    return TestClient(app)


def test_resolve_actions_prefers_mask_specific_entries() -> None:
    actions = resolve_actions_for_context(domain="sales", mask="order-editor")

    assert actions[0].id == "save-document"
    assert actions[0].context_scope == "mask"
    assert any(action.id == "action-new-order" and action.context_scope == "domain" for action in actions)
    assert any(action.id == "nav-dashboard" and action.context_scope == "global" for action in actions)


def test_actions_endpoint_returns_contextual_metadata_and_sorted_relevance() -> None:
    client = _build_client()

    response = client.get("/api/v1/actions", params={"domain": "finance", "mask": "invoice"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] >= 4
    assert payload["actions"][0]["id"] == "save-document"
    assert payload["actions"][0]["context_scope"] == "mask"
    assert "toolbar-primary" in payload["actions"][0]["surfaces"]
    assert payload["actions"][0]["relevance_score"] > payload["actions"][-1]["relevance_score"]


def test_get_action_returns_definition_even_without_context_match() -> None:
    client = _build_client()

    response = client.get("/api/v1/actions/nav-dashboard", params={"domain": "crm", "mask": "customer"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == "nav-dashboard"
    assert payload["context_scope"] == "global"


def test_voice_resolve_uses_registry_intent_phrases() -> None:
    client = _build_client()

    response = client.post("/api/v1/voice/resolve", json={"text": "Bitte neuen Auftrag anlegen"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["action_id"] == "action-new-order"
