"""The public memo contract must describe the handlers that actually run."""
import pytest
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute

from app.core.config import settings
from main import app


@pytest.fixture(scope="module")
def memo_spec():
    paths = {settings.API_V1_STR + "/einkauf/" + kind + suffix
             for kind in ("credit-memos", "debit-memos")
             for suffix in ("", "/{memo_id}/settle")}
    routes = [route for route in app.routes
              if isinstance(route, APIRoute) and route.path in paths]
    return get_openapi(title="Memo contract", version="3.0.0", routes=routes)


@pytest.mark.parametrize("kind,model", [("credit-memos", "CreditMemo"),
                                       ("debit-memos", "DebitMemo")])
def test_creation_documents_validated_input_and_actual_success_status(memo_spec, kind, model):
    operation = memo_spec["paths"][settings.API_V1_STR + "/einkauf/" + kind]["post"]
    body = operation["requestBody"]["content"]["application/json"]["schema"]
    assert body == {"$ref": f"#/components/schemas/{model}Create"}
    definition = memo_spec["components"]["schemas"][model + "Create"]
    assert {"supplierId", "memoDate", "reason", "items"} <= set(definition["required"])
    assert definition["properties"]["items"]["minItems"] == 1
    assert "201" not in operation["responses"]
    assert operation["responses"]["200"]["content"]["application/json"]["schema"] == {
        "$ref": f"#/components/schemas/{model}Response"}


@pytest.mark.parametrize("kind,model", [("credit-memos", "CreditMemo"),
                                       ("debit-memos", "DebitMemo")])
def test_list_documents_filters_and_typed_response(memo_spec, kind, model):
    operation = memo_spec["paths"][settings.API_V1_STR + "/einkauf/" + kind]["get"]
    assert {"skip", "limit", "supplier_id", "settled"} <= {
        parameter["name"] for parameter in operation["parameters"]}
    response = operation["responses"]["200"]["content"]["application/json"]["schema"]
    assert response["type"] == "array"
    assert response["items"] == {"$ref": f"#/components/schemas/{model}Response"}


@pytest.mark.parametrize("kind", ["credit-memos", "debit-memos"])
def test_settlement_requires_invoice_references(memo_spec, kind):
    operation = memo_spec["paths"][
        settings.API_V1_STR + "/einkauf/" + kind + "/{memo_id}/settle"]["post"]
    assert operation["requestBody"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/SettlementRequest"}
    definition = memo_spec["components"]["schemas"]["SettlementRequest"]
    assert "invoiceIds" in definition["required"]
    assert definition["properties"]["invoiceIds"]["minItems"] == 1
