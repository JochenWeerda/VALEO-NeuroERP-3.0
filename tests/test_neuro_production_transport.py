"""Default transport must select production and preserve its denial."""
import sys
from types import SimpleNamespace

import pytest
from fastapi import FastAPI, HTTPException
from app.core.mcp_tool_contracts import MCPToolContract, MCPToolKategorie
from app.services.neuro_tool_execution import NeuroToolExecutionService


@pytest.fixture(autouse=True)
def _enable_dev_token():
    # This transport contract does not use compatibility identity overrides.
    yield


def test_default_transport_preserves_production_denial(monkeypatch):
    production = FastAPI()
    legacy = FastAPI()

    @production.get("/protected")
    def denied():
        raise HTTPException(403, "required domain role")

    @legacy.get("/protected")
    def legacy_success():
        return {"unexpected": "compatibility success"}

    monkeypatch.setitem(sys.modules, "main", SimpleNamespace(app=production))
    monkeypatch.setitem(sys.modules, "app.main", SimpleNamespace(app=legacy))
    service = NeuroToolExecutionService()
    # Isolate app-selection and response propagation, not JWT verification.
    monkeypatch.setattr(service, "_execution_rejection", lambda *args: None)
    contract = MCPToolContract("valeo_process_probe", "process", "probe", "probe",
                              MCPToolKategorie.LESEN, api_endpoint="GET /protected")
    result = service.execute_contract(contract, parameters={}, tenant_id="probe",
                                      context={"auth_token": "synthetic-transport-only"})
    assert service._get_client().app is production
    assert result["http_status"] == 403
    assert result["mode"] == "fallback_contract"
    assert result["request"]["headers"]["Authorization"] == "[REDACTED]"
    assert "synthetic-transport-only" not in str(result)


def test_missing_production_app_does_not_fall_back(monkeypatch):
    monkeypatch.setitem(sys.modules, "main", None)
    monkeypatch.setitem(sys.modules, "app.main", SimpleNamespace(app=FastAPI()))
    with pytest.raises(ModuleNotFoundError):
        NeuroToolExecutionService()._get_client()
