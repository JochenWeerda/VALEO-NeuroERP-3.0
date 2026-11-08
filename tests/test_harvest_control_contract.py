"""Mandatory CI parity: domain DTOs, native masks, UI adapter and actual REST."""
import json
from pathlib import Path
import pytest
from fastapi import FastAPI
from app.api.v1.endpoints.harvest_acceptance import router
from app.core.screen_definitions_harvest_controls import build_harvest_controls
from scripts.generate_harvest_control_contract import INPUTS, OUTPUT, render


@pytest.fixture(autouse=True)
def _enable_dev_token():
    yield


def test_generated_transport_contract_matches_domain_models_and_native_actions():
    assert OUTPUT.read_text(encoding="utf-8") == render(), "Regenerate harvest.control.v1 projection"
    contract = json.loads(render())
    actions = {a["key"]: a for a in build_harvest_controls()["actions"]}
    for command, path in contract["paths"].items():
        assert actions[command]["commandEndpoint"] == path
        assert actions[command]["commandBinding"] == {"adapter": "harvest.control.v1", "command": command, "preview": False}
        assert actions[command]["forbiddenForAgents"] is True


def test_every_registered_write_has_the_exact_typed_rest_input():
    app = FastAPI(); app.include_router(router, prefix="/api/v1/agrar/harvest-acceptance")
    spec = app.openapi(); contract = json.loads(render())
    for command, path in contract["paths"].items():
        operation = spec["paths"][path.split("?")[0]]["post"]
        schema = operation["requestBody"]["content"]["application/json"]["schema"]
        expected = "#/components/schemas/" + INPUTS[command].__name__
        assert expected in json.dumps(schema)
        if command != "release": assert operation["requestBody"]["required"] is True
        assert contract["request_schemas"][command]["additionalProperties"] is False
