"""Typed histories and gifts remain real, unambiguous mask contracts."""
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from scripts.check_field_contracts import _zeilenform


def schema(properties):
    return {
        "components": {"schemas": {
            "Row": {"type": "object", "properties": {"id": {"type": "string"}}},
            "Envelope": {"type": "object", "properties": properties},
        }},
    }, {"responses": {"200": {"content": {"application/json": {
        "schema": {"$ref": "#/components/schemas/Envelope"},
    }}}}}


TYPED_LIST = {"type": "array", "items": {"$ref": "#/components/schemas/Row"}}


@pytest.mark.parametrize("properties,expected", [
    ({"vorgaenge": TYPED_LIST, "stand": {"type": "string"}}, {"id"}),
    ({"items": TYPED_LIST}, {"id"}),
    ({"a": TYPED_LIST, "b": TYPED_LIST}, None),
    ({"items": {"type": "array", "items": {}}, "vorgaenge": TYPED_LIST}, None),
    ({"vorgaenge": {"type": "array", "items": {}}}, None),
    ({"stand": {"type": "string"}}, None),
])
def test_named_history_requires_unambiguous_typed_rows(properties, expected):
    spec, operation = schema(properties)
    assert _zeilenform(spec, operation) == expected


def test_gifts_dispatch_before_generic_route_and_preserve_tenant(monkeypatch):
    from app.api.v1.endpoints import crm_360_tabs as endpoint
    from app.core.database import get_db
    from app.core.tenant import get_tenant_id

    db = MagicMock()
    lookup = MagicMock(return_value={"id": "canonical", "kunden_nr": "K-1"})
    read = MagicMock(return_value=("praesente", [{
        "id": "gift-1", "year": 2026, "gift_date": "2026-10-07",
        "occasion": "Besuch", "gift_name": "Kalender", "quantity": 2.0,
    }]))
    monkeypatch.setattr(endpoint, "_kunde_finden", lookup)
    monkeypatch.setattr(endpoint, "_fetch_customer_tab_items", read)
    app = FastAPI()
    app.include_router(endpoint.router)
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_tenant_id] = lambda: "own-tenant"
    client = TestClient(app)
    response = client.get("/customer/tabs/praesente")
    assert response.status_code == 200
    assert response.json()["items"][0]["gift_name"] == "Kalender"
    assert response.json()["total"] == 1
    lookup.assert_called_once_with(db, "customer", "own-tenant")
    assert read.call_args.kwargs["tenant_id"] == "own-tenant"
    assert read.call_args.kwargs["customer_id"] == "canonical"
    spec = app.openapi()
    model = spec["paths"]["/{customer_id}/tabs/praesente"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]
    assert model["$ref"].endswith("/CustomerGiftsTabOut")
    assert client.get("/customer/tabs/praesente", params={"filterPlan": "not-json"}).status_code == 422
    lookup.return_value = None
    read.reset_mock()
    assert client.get("/foreign/tabs/praesente").status_code == 404
    read.assert_not_called()
