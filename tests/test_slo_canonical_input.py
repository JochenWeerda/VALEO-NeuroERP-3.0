import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from pydantic import ValidationError
from app.api.v1.schemas.slo_input import SloCheckIn, reject_nonfinite_slo_json
from app.core.mcp_tool_contracts import get_process_kernel_mcp_tools
from app.core.mcp_rest_binding import check_request_binding
from app.services.neuro_tool_execution import NeuroToolExecutionService


@pytest.fixture(autouse=True)
def _enable_dev_token():
    yield


@pytest.mark.parametrize("value", [{}, {"slo_id": "probe"}, {"slo_id": "probe", "ist_wert": "0"},
    {"slo_id": "probe", "ist_wert": True}, {"slo_id": "probe", "ist_wert": float("nan")},
    {"slo_id": "probe", "ist_wert": float("inf")}, {"slo_id": "", "ist_wert": 0}])
def test_invalid_measurements(value):
    with pytest.raises(ValidationError): SloCheckIn.model_validate(value)


@pytest.mark.parametrize("name", ["valeo_finance_sla_check", "valeo_process_slo_check"])
def test_no_synthetic_id_or_zero_and_explicit_null_preserved(name, monkeypatch):
    class ForbiddenClient:
        def request(self, **kwargs): pytest.fail("Invalid measurement reached HTTP")
    service = NeuroToolExecutionService(ForbiddenClient())
    monkeypatch.setattr(service, "_execution_rejection", lambda *args: None)
    contract = get_process_kernel_mcp_tools().by_tool_name(name)
    assert contract.schema_version == 2
    assert contract.as_mcp_tool()["inputSchema"] == SloCheckIn.model_json_schema()
    for value in (None, 0, 5.5):
        body = service._build_body(contract, {}, {"slo_id": "probe", "ist_wert": value}, {}, "own")
        assert body["ist_wert"] == value
    result = service.execute_contract(contract, parameters={"amount": 0}, tenant_id="own",
                                     context={"auth_token": "synthetic-only"})
    assert result["http_status"] == 422
    assert result["rejection_reason"] == "invalid_contract_payload"


def client():
    from app.api.v1.endpoints.process_kernel_api import check_slo, router
    route = next(route for route in router.routes if route.path.endswith("/slo/check"))
    assert any(dep.dependency is reject_nonfinite_slo_json for dep in route.dependencies)
    app = FastAPI()
    app.post("/api/v1/process/slo/check", dependencies=[Depends(reject_nonfinite_slo_json)])(check_slo)
    return TestClient(app)


def test_unknown_and_zero_are_distinct_and_schemas_match():
    api = client()
    path = "/api/v1/process/slo/check"
    unknown = api.post(path, json={"slo_id": "SLO-API-VERF-01", "ist_wert": None})
    zero = api.post(path, json={"slo_id": "SLO-API-VERF-01", "ist_wert": 0})
    assert unknown.status_code == zero.status_code == 200
    assert unknown.json()["status"] == "UNBEKANNT"
    assert zero.json()["status"] == "VERLETZT"
    for name in ("valeo_finance_sla_check", "valeo_process_slo_check"):
        assert check_request_binding(api.app.openapi(), get_process_kernel_mcp_tools().by_tool_name(name)) == []


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-Infinity"])
def test_nonstandard_json_numbers_are_422_not_serialization_500(value):
    response = client().post("/api/v1/process/slo/check", content='{"slo_id":"probe","ist_wert":'+value+'}',
                             headers={"Content-Type": "application/json"})
    assert response.status_code == 422
