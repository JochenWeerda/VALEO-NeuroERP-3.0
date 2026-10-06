"""Public portal documentation and route matching follow the active shop contract."""
import pytest
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute
from starlette.routing import Match

from app.api.v1.endpoints import portal_shop
from app.core.config import settings
from main import app


@pytest.fixture(scope="module")
def portal_spec():
    paths = {settings.API_V1_STR + "/portal/" + suffix for suffix in (
        "products", "orders", "orders/{order_id}", "contracts", "pre-purchases")}
    return get_openapi(title="Portal contract", version="3.0.0", routes=[
        route for route in app.routes if isinstance(route, APIRoute) and route.path in paths])


@pytest.mark.parametrize("suffix,method,model", [
    ("products", "get", "PortalProductList"),
    ("orders", "get", "OrderList"),
    ("orders/{order_id}", "get", "OrderResponse"),
    ("orders", "post", "OrderResponse"),
])
def test_portal_documents_actual_response_and_required_tenant(portal_spec, suffix, method, model):
    operation = portal_spec["paths"][settings.API_V1_STR + "/portal/" + suffix][method]
    tenant = next(p for p in operation["parameters"] if p["name"] == "tenant_id")
    assert tenant["required"] is True
    assert tenant["in"] == "query"
    success = "201" if method == "post" else "200"
    assert operation["responses"][success]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/" + model}
    if method == "post":
        assert operation["requestBody"]["content"]["application/json"]["schema"] == {
            "$ref": "#/components/schemas/OrderCreate"}


@pytest.mark.parametrize("suffix", ["contracts", "pre-purchases"])
def test_portal_entitlements_have_the_actual_list_contract(portal_spec, suffix):
    operation = portal_spec["paths"][settings.API_V1_STR + "/portal/" + suffix]["get"]
    response = operation["responses"]["200"]["content"]["application/json"]["schema"]
    assert response["type"] == "array"
    assert response["items"] == {"$ref": "#/components/schemas/PortalShopOut"}
    assert next(p for p in operation["parameters"] if p["name"] == "tenant_id")["required"]


@pytest.mark.parametrize("suffix,endpoint", [
    ("reconciliation", portal_shop.reconcile_orders),
    ("observability", portal_shop.get_orders_observability),
    ("real-order-id", portal_shop.get_order),
])
def test_first_full_match_dispatches_to_the_intended_handler(suffix, endpoint):
    scope = {"type": "http", "method": "GET",
             "path": settings.API_V1_STR + "/portal/orders/" + suffix,
             "root_path": ""}
    first = next(route for route in app.routes if route.matches(scope)[0] == Match.FULL)
    assert first.endpoint is endpoint
