"""Concrete choice routes are proven by GET path enums, never broad wildcards."""
import json

import pytest

from app.services import made_by_studio_gates as gates


@pytest.fixture
def route_keys(tmp_path, monkeypatch):
    path = tmp_path / "docs/schnittstellen/openapi.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"paths": {
        "/api/v1/choices/{kind}": {"get": {"parameters": [{"in": "path", "name": "kind", "schema": {"enum": ["customer", "article"]}}]}},
        "/api/v1/finance/{id}": {"get": {}},
        "/api/v1/write-only": {"post": {}},
        "/api/v1/items/{item_id}": {"get": {}},
        "/api/v1/shared/{kind}": {"parameters": [{"in": "path", "name": "kind", "schema": {"enum": ["allowed"]}}], "get": {}},
        "/api/v1/referenced/{kind}": {"get": {"parameters": [{"in": "path", "name": "kind", "schema": {"$ref": "#/components/schemas/Kind"}}]}},
    }, "components": {"schemas": {"Kind": {"type": "string", "enum": ["valid"]}}}}), encoding="utf-8")
    monkeypatch.setattr(gates, "ROOT", tmp_path)
    gates._openapi_route_keys.cache_clear()
    yield gates._openapi_route_keys()
    gates._openapi_route_keys.cache_clear()


@pytest.mark.parametrize("endpoint", [
    "/api/v1/choices/customer", "/api/v1/choices/article/?q=grain",
    "/api/v1/shared/allowed", "/api/v1/referenced/valid",
    "/api/v1/items/{entity_id}",
])
def test_existing_read_contract_matches(endpoint, route_keys):
    assert gates._endpoint_in_openapi(endpoint, route_keys)


@pytest.mark.parametrize("endpoint", [
    "/api/v1/choices/unknown", "/api/v1/choices/customer/extra",
    "/api/v2/choices/customer", "/api/v1/finance/datev-export",
    "/api/v1/write-only", "/api/v1/items", "/api/v1/items/constant",
])
def test_unproven_route_or_write_operation_is_rejected(endpoint, route_keys):
    assert not gates._endpoint_in_openapi(endpoint, route_keys)


def test_declared_post_calculation_does_not_become_a_get_contract(route_keys):
    assert "/api/v1/write-only" not in route_keys
    assert gates._endpoint_in_openapi("/api/v1/write-only", gates._openapi_route_keys("POST"))
    assert not gates._endpoint_in_openapi("/api/v1/choices/customer", gates._openapi_route_keys("POST"))


def test_gate_c_checks_the_declared_calculation_method(monkeypatch, route_keys):
    from app.api.v1.endpoints import mask_screen_definition
    monkeypatch.setattr(mask_screen_definition, "_check_readiness", lambda definition: {"generatorReady": True})
    definition = {"layout": {"floorplan": "worklist"}, "dataSources": [{"key": "preview", "endpoint": "/api/v1/write-only", "method": "POST"}]}
    assert gates.check_gate_c(definition, screen_id="synthetic/preview").passed
    definition["dataSources"][0].pop("method")
    assert not gates.check_gate_c(definition, screen_id="synthetic/preview").passed
