from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import terminology
from app.core.terminology_registry import build_landhandel_terminology_registry


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(terminology.router)
    return TestClient(app)


def test_terminology_registry_contains_canonical_landhandel_terms():
    registry = build_landhandel_terminology_registry()

    assert registry.manifest_kind == "LANDHANDEL_TERMINOLOGY_REGISTRY"
    assert registry.term_count >= 10
    assert registry.by_term_key("reklamation") is not None
    assert registry.by_term_key("settlement") is not None
    assert "crm" in registry.domains
    assert "dms" in registry.domains


def test_terminology_registry_search_filters_by_domain_and_query():
    registry = build_landhandel_terminology_registry()

    hits = registry.search(query="claim", domain="crm")
    assert hits
    assert all(entry.domain.value == "crm" for entry, _, _ in hits)
    assert any(entry.term_key == "reklamation" for entry, _, _ in hits)


def test_terminology_api_registry_and_single_entry():
    client = _client()

    response = client.get("/terminology/registry", params={"domain": "finance"})
    assert response.status_code == 200
    body = response.json()
    assert body["manifest_kind"] == "LANDHANDEL_TERMINOLOGY_REGISTRY"
    assert body["term_count"] >= 3
    assert "finance" in body["domains"]
    assert all(term["domain"] == "finance" for term in body["terms"])

    single = client.get("/terminology/terms/reklamation")
    assert single.status_code == 200
    term = single.json()
    assert term["term_key"] == "reklamation"
    assert term["canonical_de"] == "Reklamation"
    assert term["canonical_en"] == "Claim"


def test_terminology_api_unknown_entry_returns_404():
    client = _client()

    response = client.get("/terminology/terms/does-not-exist")

    assert response.status_code == 404
