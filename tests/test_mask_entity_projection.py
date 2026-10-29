"""Entity projection uses the registered secured source for every mask channel."""
import asyncio
import json

import httpx
import pytest
from fastapi import FastAPI, HTTPException, Request
from fastapi.testclient import TestClient

from app.api.v1.schemas.mask_data_contracts import MaskDataReadIn
from app.services import mask_data_read


@pytest.fixture
def definition(monkeypatch):
    current = {
        "id": "fibu/anlage",
        "dataSources": [{"key": "entity", "endpoint": "/api/v1/finance/asset-accounting/assets/{entity_id}"}],
        "tabs": [{"key": "kopf", "fields": [{"key": key} for key in
                   ("id", "asset_number", "description", "acquisition_cost")]}],
        "entityProjection": {
            "id": "asset.id",
            "asset_number": "asset.asset_number",
            "description": "asset.description",
            "acquisition_cost": "asset.acquisition_cost",
        },
    }
    monkeypatch.setattr(mask_data_read, "get_screen_definition",
                        lambda screen, **kwargs: current if screen == current["id"] and kwargs.get("tenant_id") == "own" else None)
    return current


def _body(**updates):
    return MaskDataReadIn(screen_id="fibu/anlage", source_key="entity", entity_id="asset-42", **updates)


def _transport(payload=None, status=200, calls=None):
    value = payload if payload is not None else {
        "asset": {"id": "asset-42", "asset_number": "AN-42", "description": "Muehle",
                  "acquisition_cost": "1200.00", "tenant_id": "own", "private_note": "never project"},
        "depreciation_history": [{"private_note": "never project"}],
    }
    def respond(request):
        if calls is not None:
            calls.append(request)
        assert request.headers["authorization"] == "Bearer signed"
        assert request.url.path == "/api/v1/finance/asset-accounting/assets/asset-42"
        return httpx.Response(status, json=value)
    return httpx.MockTransport(respond)


def test_canonical_asset_definition_projects_its_real_domain_envelope():
    result = mask_data_read.read_sync(_body(), "own", "Bearer signed", transport=_transport())
    assert result.data == {"id": "asset-42", "asset_number": "AN-42", "description": "Muehle",
                           "acquisition_cost": "1200.00"}


def test_sync_async_projection_returns_only_declared_flat_fields(definition):
    calls = []
    transport = _transport(calls=calls)
    async def respond(request):
        calls.append(request)
        assert request.headers["authorization"] == "Bearer signed"
        return httpx.Response(200, json={
            "asset": {"id": "asset-42", "asset_number": "AN-42", "description": "Muehle",
                      "acquisition_cost": "1200.00", "private_note": "never project"},
            "depreciation_history": [{"private_note": "never project"}],
        })
    expected = {"id": "asset-42", "asset_number": "AN-42", "description": "Muehle",
                "acquisition_cost": "1200.00"}
    for result in (
        mask_data_read.read_sync(_body(), "own", "Bearer signed", transport=transport),
        asyncio.run(mask_data_read.read_async(_body(), "own", "Bearer signed", transport=httpx.MockTransport(respond))),
    ):
        assert result.data == expected
        assert result.screen_id == "fibu/anlage" and result.source_key == "entity"
    assert len(calls) == 2


@pytest.mark.parametrize("projection", [
    {"id": "asset.__proto__"}, {"id": "asset..id"}, {"id": "asset[0].id"},
    {"id": "asset.id", "constructor": "asset.private_note"},
    {"id": "asset.id", "bad": "asset.__class__"},
    {"asset_number": "asset.asset_number"},
])
def test_invalid_registered_projection_fails_before_domain_request(definition, projection):
    definition["entityProjection"] = projection
    calls = []
    with pytest.raises(HTTPException) as error:
        mask_data_read.read_sync(_body(), "own", "Bearer signed", transport=_transport(calls=calls))
    assert error.value.status_code == 409 and not calls


@pytest.mark.parametrize("payload", [
    {"asset": {"id": "asset-42"}},
    {"asset": {"id": "other", "asset_number": "AN-42", "description": "Muehle", "acquisition_cost": 1200}},
    {"asset": {"id": "asset-42", "asset_number": "AN-42", "description": {}, "acquisition_cost": 1200}},
])
def test_missing_path_wrong_identity_and_nonscalar_are_rejected(definition, payload):
    with pytest.raises(HTTPException) as error:
        mask_data_read.read_sync(_body(), "own", "Bearer signed", transport=_transport(payload))
    assert error.value.status_code == 502


def test_published_tenant_projection_is_not_a_trusted_field_selector(definition, monkeypatch):
    definition["id"] = "tenant/custom-asset"
    monkeypatch.setattr(mask_data_read, "get_screen_definition", lambda *_args, **_kwargs: definition)
    calls = []
    body = MaskDataReadIn(screen_id=definition["id"], source_key="entity", entity_id="asset-42")
    with pytest.raises(HTTPException) as error:
        mask_data_read.read_sync(body, "own", "Bearer signed", transport=_transport(calls=calls))
    assert error.value.status_code == 409 and not calls


def test_projection_cannot_select_a_field_absent_from_the_screen(definition):
    definition["entityProjection"]["private_note"] = "asset.private_note"
    calls = []
    with pytest.raises(HTTPException) as error:
        mask_data_read.read_sync(_body(), "own", "Bearer signed", transport=_transport(calls=calls))
    assert error.value.status_code == 409 and not calls


def test_boolean_identity_never_matches_entity_id(definition):
    payload = {"asset": {"id": True, "asset_number": "AN-42", "description": "Muehle",
                         "acquisition_cost": 1200}}
    body = MaskDataReadIn(screen_id="fibu/anlage", source_key="entity", entity_id="True")
    with pytest.raises(HTTPException) as error:
        mask_data_read.read_sync(body, "own", "Bearer signed",
                                 transport=httpx.MockTransport(lambda _request: httpx.Response(200, json=payload)))
    assert error.value.status_code == 502


def test_tenant_missing_definition_and_secured_domain_denial_fail_closed(definition):
    with pytest.raises(HTTPException) as error:
        mask_data_read.read_sync(_body(), "foreign", "Bearer signed", transport=_transport())
    assert error.value.status_code == 404
    for status in (403, 404):
        with pytest.raises(HTTPException) as error:
            mask_data_read.read_sync(_body(), "own", "Bearer signed", transport=_transport(status=status))
        assert error.value.status_code == status


def test_unprojected_source_preserves_domain_envelope(definition):
    definition.pop("entityProjection")
    result = mask_data_read.read_sync(_body(), "own", "Bearer signed", transport=_transport())
    assert "asset" in result.data and "depreciation_history" in result.data


def test_human_mcp_and_cli_share_projected_fields_without_a_database(definition, monkeypatch):
    from app.api.v1.endpoints import mask_screen_definition
    from app.services.mcp_mask_actions import read_source
    from valeo_cli import cli

    app = FastAPI()
    app.include_router(mask_screen_definition.router, prefix="/api/v1")
    app.dependency_overrides[mask_screen_definition.get_current_user] = lambda: {"sub": "signed"}
    def verified_tenant(request: Request) -> str:
        return "own" if request.headers.get("Authorization") == "Bearer signed" else "foreign"
    app.dependency_overrides[mask_screen_definition.get_tenant_id] = verified_tenant
    domain_calls = []
    transport = _transport(calls=domain_calls)
    original_async, original_sync = mask_data_read.read_async, mask_data_read.read_sync

    async def inprocess_async(body, tenant, authorization):
        return await original_async(body, tenant, authorization, transport=transport)

    def inprocess_sync(body, tenant, authorization):
        return original_sync(body, tenant, authorization, transport=transport)

    monkeypatch.setattr(mask_data_read, "read_async", inprocess_async)
    monkeypatch.setattr(mask_data_read, "read_sync", inprocess_sync)
    monkeypatch.setenv("VALEO_ACCESS_TOKEN", "signed")
    monkeypatch.setenv("VALEO_API_URL", "http://testserver")
    expected = {"id": "asset-42", "asset_number": "AN-42", "description": "Muehle",
                "acquisition_cost": "1200.00"}
    with TestClient(app) as client:
        human = client.get("/api/v1/masks/fibu%2Fanlage/data/entity?entity_id=asset-42",
                           headers={"Authorization": "Bearer signed"})
        assert human.status_code == 200, human.text
        mcp = read_source(_body().model_dump(exclude_none=True), "own", "Bearer signed")
        lines = []
        code = cli.main(["daten", "fibu/anlage", "entity", "--id", "asset-42"], http=client, out=lines.append)
        assert code == 0
        assert human.json()["data"] == mcp["data"] == json.loads(lines[0])["data"] == expected
        assert len(domain_calls) == 3
        denied = client.get("/api/v1/masks/fibu%2Fanlage/data/entity?entity_id=asset-42",
                            headers={"Authorization": "Bearer foreign"})
        assert denied.status_code == 404 and len(domain_calls) == 3
        with pytest.raises(HTTPException) as error:
            read_source(_body().model_dump(exclude_none=True), "foreign", "Bearer signed")
        assert error.value.status_code == 404 and len(domain_calls) == 3
