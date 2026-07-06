"""UIX-060: Omnibox-Katalog — Matching-Basis fuer den Intent-Compiler.

Der Katalog projiziert die ScreenDefinition-Registry (Titel, Synonyme,
examplePrompts, filterbare Spalten) fuer das Frontend. Read-only, typisiert.
"""
from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)
HEADERS = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-Id": "00000000-0000-0000-0000-000000000001",
}
BASE = "/api/v1/ui/mask-registry/omnibox-catalog"


def test_catalog_returns_all_registry_screens():
    from app.core.screen_definitions import _SCREEN_DEFINITIONS

    resp = client.get(BASE, headers=HEADERS)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert len(body) == len(_SCREEN_DEFINITIONS)
    ids = {e["screen_id"] for e in body}
    assert "crm/customer-360" in ids
    assert "finance/payment-run" in ids


def test_catalog_entry_shape_and_synonyms():
    resp = client.get(BASE, headers=HEADERS)
    body = resp.json()
    by_id = {e["screen_id"]: e for e in body}

    op = by_id["finance/ar-open-item"]
    assert op["title"]
    assert op["domain"] == "finance"
    assert op["floorplan"]  # Meridian-Dekoration greift auch im Katalog
    assert "offene posten" in op["synonyms"]
    assert isinstance(op["example_prompts"], list)

    for field in op["filterable_fields"]:
        assert set(field.keys()) == {"key", "label", "type"}
        assert field["type"] in {"enum", "date", "number", "text"}


def test_catalog_synonyms_curated_for_all_native_screens():
    """Jede Registry-Maske hat kuratierte Synonyme (Wartungsstelle _AGENT_SYNONYMS)."""
    resp = client.get(BASE, headers=HEADERS)
    missing = [e["screen_id"] for e in resp.json() if not e["synonyms"]]
    assert missing == [], f"Ohne Synonyme: {missing}"


def test_catalog_filterable_fields_present_for_table_masks():
    resp = client.get(BASE, headers=HEADERS)
    by_id = {e["screen_id"]: e for e in resp.json()}
    # Bestandsmaske hat filterbare Spalten (inventory-Profil verlangt Filter)
    stock = by_id["lager/article-stock"]
    assert len(stock["filterable_fields"]) > 0


def test_catalog_is_read_only_contract():
    """Der Katalog akzeptiert nur GET — keine Mutations-Methoden."""
    assert client.post(BASE, headers=HEADERS).status_code == 405
    assert client.delete(BASE, headers=HEADERS).status_code == 405
