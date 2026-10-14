"""DQ validates business data, never a JSON string/parameter envelope."""
from types import SimpleNamespace
from copy import deepcopy
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError
from app.api.v1.schemas.data_quality_input import DataQualityCheckIn
from app.core.mcp_tool_contracts import get_process_kernel_mcp_tools
from app.core.mcp_rest_binding import check_request_binding
from app.services.neuro_tool_execution import NeuroToolExecutionService
from app.services.neuro_tool_broker import NeuroToolBroker


@pytest.fixture(autouse=True)
def _enable_dev_token():
    # Pure contract tests, no compatibility identity or database required.
    yield


def payload():
    return {"entity_typ": "Artikel", "datensatz": {"artikel_nr": "  A-01  "}}


@pytest.mark.parametrize("value", [
    {"entity_typ": "Artikel"},
    {"entity_typ": "Artikel", "datensatz": "{}"},
    {"entity_typ": "Artikel", "datensatz_json": "{}"},
    {"entity_typ": " ", "datensatz": {}},
    {"entity_typ": "Artikel", "datensatz": {str(i): 1 for i in range(51)}},
    {"entity_typ": "Artikel", "datensatz": {"name": "x" * 1001}},
    {"entity_typ": "Artikel", "datensatz": {}, "kontext_datensaetze": [{}] * 101},
    {"entity_typ": "Artikel", "datensatz": {}, "kontext_datensaetze": ["not an object"]},
])
def test_invalid_envelopes_and_limits(value):
    with pytest.raises(ValidationError):
        DataQualityCheckIn.model_validate(value)


def test_transport_preserves_exact_business_object():
    contract = get_process_kernel_mcp_tools().by_tool_name("valeo_process_data_quality_validate")
    value = payload()
    result = NeuroToolExecutionService()._build_body(contract, {}, value, {}, "tenant")
    assert result["datensatz"] == value["datensatz"]
    assert result["entity_typ"] == "Artikel"
    assert "datensatz" not in result["datensatz"]
    assert contract.schema_version == 2
    assert contract.as_mcp_tool()["inputSchema"] == DataQualityCheckIn.model_json_schema()


def test_invalid_input_never_calls_http(monkeypatch):
    class ForbiddenClient:
        def request(self, **kwargs): pytest.fail("Invalid input reached transport")
    service = NeuroToolExecutionService(ForbiddenClient())
    monkeypatch.setattr(service, "_execution_rejection", lambda *args: None)
    contract = get_process_kernel_mcp_tools().by_tool_name("valeo_process_data_quality_validate")
    result = service.execute_contract(contract, parameters={"entity_typ": "Artikel", "datensatz_json": "private-payload"},
                                     tenant_id="tenant", context={"auth_token": "synthetic-only"})
    assert result["http_status"] == 422
    assert result["rejection_reason"] == "invalid_contract_payload"
    assert "private-payload" not in str(result)


def test_broker_wraps_flat_plan_and_preserves_canonical_request():
    step = SimpleNamespace(parameters={"artikel_nr": "A-01"}, entity_type="article")
    comparison = [{"artikel_nr": "A-02"}]
    result = NeuroToolBroker._dq_parameters(step, {"comparison_records": comparison})
    assert result == {"entity_typ": "Artikel", "datensatz": step.parameters, "kontext_datensaetze": comparison}
    assert result["datensatz"] is not step.parameters
    step.parameters = payload()
    assert NeuroToolBroker._dq_parameters(step, {}) == payload()


def test_rest_schema_and_actual_dataset_evaluation(monkeypatch):
    from app.api.v1.endpoints import process_kernel_api
    seen = []
    class Result:
        def as_dict(self): return {"valid": True}
    monkeypatch.setattr(process_kernel_api, "validate_datensatz",
                        lambda rules, data, context: (seen.append(data) or Result()))
    app = FastAPI()
    path = "/api/v1/process/data-quality/validate"
    app.post(path)(process_kernel_api.validate_dq)
    response = TestClient(app).post(path, json=payload())
    assert response.status_code == 200
    assert seen == [payload()["datensatz"]]
    contract = get_process_kernel_mcp_tools().by_tool_name("valeo_process_data_quality_validate")
    spec = app.openapi()
    assert check_request_binding(spec, contract) == []
    spec["components"]["schemas"]["DataQualityCheckIn"]["properties"]["datensatz"]["maxProperties"] = 500
    assert check_request_binding(spec, contract)


@pytest.mark.parametrize("source,target", [("supplier", "Lieferant"), ("invoice", "APRechnung"), ("article", "Artikel")])
def test_broker_uses_actual_ruleset_names(source, target):
    from app.core.data_quality_rules import get_default_dq_rulesets
    actual = NeuroToolBroker._dq_entity_type(source)
    assert actual == target
    assert actual in get_default_dq_rulesets()


def test_foreign_dataset_selector_is_rejected_before_http(monkeypatch):
    class ForbiddenClient:
        def request(self, **kwargs): pytest.fail("Foreign selector reached HTTP")
    service = NeuroToolExecutionService(ForbiddenClient())
    monkeypatch.setattr(service, "_execution_rejection", lambda *args: None)
    contract = get_process_kernel_mcp_tools().by_tool_name("valeo_process_data_quality_validate")
    value = payload()
    value["datensatz"]["tenant_id"] = "foreign"
    result = service.execute_contract(contract, parameters=value, tenant_id="own",
                                     context={"auth_token": "synthetic-only"})
    assert result["http_status"] == 403
    assert result["rejection_reason"] == "tenant_selector_rejected"
