"""Shared source resolution, safe adapters and real signed three-channel AP reads."""
import asyncio
import json

import httpx
import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.api.v1.schemas.mask_data_contracts import MaskDataReadIn
from app.services import mask_data_read as service
from test_ap_workflow_security_contract import case, subject_data, keys, probe  # noqa: F401


@pytest.fixture
def source(monkeypatch):
    definition = {"id": "tenant/example", "dataSources": [{"key": "rows", "endpoint": "/api/v1/example?state=open&state=review"}]}
    monkeypatch.setattr(service, "get_screen_definition", lambda screen, **kwargs: definition if screen == definition["id"] else None)
    return definition["dataSources"][0]


def body(**updates):
    return MaskDataReadIn(screen_id="tenant/example", source_key="rows", **updates)


def test_source_preserves_fixed_filters_and_uses_bounded_runtime_paging(source):
    path = service.resolve_source(body(page=2, limit=10, q="A & B"), "own")
    url = httpx.URL(path)
    assert url.params.get_list("state") == ["open", "review"]
    assert url.params["page"] == "2" and url.params["limit"] == "10" and url.params["q"] == "A & B"


@pytest.mark.parametrize("endpoint", ["https://outside.invalid/data", "//outside.invalid/data", "/api/v1/../admin", "/api/v1/%2e%2e/admin", "/api/v1/x#fragment", "/api/v1/x?tenant_id=foreign", "/api/v1/x?actor=forged", "/api/v1/x\\y", "/api/v1/x\n"])
def test_unsafe_registered_source_fails_before_network(source, endpoint):
    source["endpoint"] = endpoint
    calls = []
    with pytest.raises(HTTPException):
        service.read_sync(body(), "own", "Bearer signed", transport=httpx.MockTransport(lambda request: calls.append(request)))
    assert not calls


@pytest.mark.parametrize("updates", [{"limit": 101}, {"page": 0}, {"tenant_id": "foreign"}, {"entity_id": ".."}, {"entity_id": "x/y"}, {"q": "x"*201}])
def test_input_cannot_override_identity_escape_paths_or_overrun_limits(updates):
    with pytest.raises(ValidationError):body(**updates)


def test_context_comes_from_verified_tenant_and_explicit_record(source):
    source["endpoint"] = "/api/v1/example/{entity_id}?tenant_id={tenant_id}"
    with pytest.raises(HTTPException) as err:service.resolve_source(body(), "own")
    assert err.value.status_code == 422
    path = service.resolve_source(body(entity_id="safe-record"), "own")
    assert "/safe-record?" in path and httpx.URL(path).params["tenant_id"] == "own"


def test_non_get_sources_missing_bearer_and_unknown_mask_are_denied(source):
    source["method"] = "POST"
    with pytest.raises(HTTPException) as err:service.resolve_source(body(), "own")
    assert err.value.status_code == 409
    with pytest.raises(HTTPException) as err:service.read_sync(body(), "own", None)
    assert err.value.status_code == 401
    with pytest.raises(HTTPException) as err:
        service.resolve_source(MaskDataReadIn(screen_id="tenant/unknown", source_key="rows"), "own")
    assert err.value.status_code == 404


@pytest.mark.parametrize("status,payload,expected", [(302, {}, 502), (403, {"detail": "sensitive input"}, 403),
                                                    (200, {"_stub": True, "items": []}, 503), (200, 123, 502)])
def test_sync_and_async_transport_share_safe_failure_contract(source, status, payload, expected):
    calls=[]
    def endpoint(request):
        calls.append(request)
        assert request.method == "GET" and request.headers["authorization"] == "Bearer signed"
        assert "x-tenant-id" not in request.headers
        return httpx.Response(status, json=payload, headers={"location": "https://outside.invalid"})
    transport=httpx.MockTransport(endpoint)
    for execute in (lambda: service.read_sync(body(), "own", "Bearer signed", transport=transport),
                    lambda: asyncio.run(service.read_async(body(), "own", "Bearer signed", transport=transport))):
        with pytest.raises(HTTPException) as err:execute()
        assert err.value.status_code == expected and "sensitive" not in str(err.value.detail)
    assert len(calls)==2


def test_oversized_and_non_json_responses_are_rejected(source):
    for payload in (b"x"*(service._MAX_BYTES+1), b"<html>not JSON</html>", b'{"x": NaN}', b'{"x": 1, "x": 2}'):
        with pytest.raises(HTTPException) as err:
            service.read_sync(body(), "own", "Bearer signed", transport=httpx.MockTransport(lambda _: httpx.Response(200,content=payload)))
        assert err.value.status_code == 502


@pytest.fixture
def channels(case, monkeypatch):
    from app.api.v1.endpoints import mask_screen_definition, mcp_tool_registry
    from app.core.tenant_binding import install_tenant_bindings
    from main import BearerAuthMiddleware
    client = case[0]; app = client.app
    app.include_router(mask_screen_definition.router, prefix="/api/v1")
    app.include_router(mcp_tool_registry.router, prefix="/api/v1")
    install_tenant_bindings(app, public_paths=BearerAuthMiddleware.PUBLIC_PATHS)
    original_async, original_sync = service.read_async, service.read_sync
    async def inprocess_async(body, tenant, authorization):
        return await original_async(body, tenant, authorization, transport=httpx.ASGITransport(app=app))
    def target(request):
        result = client.request(request.method, str(request.url), headers={"Authorization":request.headers["authorization"]})
        return httpx.Response(result.status_code, content=result.content)
    def inprocess_sync(body, tenant, authorization):
        return original_sync(body, tenant, authorization, transport=httpx.MockTransport(target))
    monkeypatch.setattr(service, "read_async", inprocess_async)
    monkeypatch.setattr(service, "read_sync", inprocess_sync)
    monkeypatch.setenv("VALEO_API_URL", "http://testserver")
    return case


def _headers(case, role="FINANCE_LESEN", scope="masks:read", tenant=None):
    token = case[2].token(tenant or case[3], changes={"roles": [role] if role else [], "scope": scope})
    return {"Authorization": "Bearer " + token}


def _mcp(case, headers, entity):
    return case[0].post("/api/v1/mcp/tools/call", headers=headers, json={
        "tool_name":"mask.data.read", "mode":"dryRun", "parameters":{
            "screen_id":"finance/ap-invoice", "source_key":"entity", "entity_id":entity}})


def _cli(case, monkeypatch, headers, entity):
    from valeo_cli import cli
    monkeypatch.setenv("VALEO_ACCESS_TOKEN", headers["Authorization"].removeprefix("Bearer "))
    lines=[]
    code=cli.main(["daten","finance/ap-invoice","entity","--id",entity],http=case[0],out=lines.append)
    return code, lines


def test_signed_human_cli_and_mcp_read_same_real_domain_document(channels, monkeypatch):
    case=channels;headers=_headers(case);entity=case[5]
    human=case[0].get(f"/api/v1/finance/ap/invoices/{entity}",headers=headers)
    assert human.status_code==200,human.text
    common=case[0].get(f"/api/v1/masks/finance/ap-invoice/data/entity?entity_id={entity}",headers=headers)
    assert common.status_code==200,common.text
    assert common.json()["data"]==human.json()
    mcp=_mcp(case,headers,entity)
    assert mcp.status_code==200,mcp.text
    assert mcp.json()["data"]==human.json()
    code,lines=_cli(case,monkeypatch,headers,entity)
    assert code==0 and json.loads(lines[0])["data"]==human.json()
    # Repeated reads must neither mutate the invoice nor manufacture an approval.
    assert case[0].get(f"/api/v1/finance/ap/invoices/{entity}",headers=headers).json()==human.json()


@pytest.mark.parametrize("kind",["foreign_record","no_business_role","other_tenant","no_mcp_scope"])
def test_three_channel_permissions_and_tenant_boundaries(channels, monkeypatch, kind):
    case=channels;entity=case[6] if kind=="foreign_record" else case[5]
    headers=_headers(case,role=None if kind=="no_business_role" else "FINANCE_LESEN",
                     tenant=case[4] if kind=="other_tenant" else None,
                     scope="" if kind=="no_mcp_scope" else "masks:read")
    expected=403 if kind=="no_business_role" else 404 if kind in {"foreign_record","other_tenant"} else 200
    assert case[0].get(f"/api/v1/finance/ap/invoices/{entity}",headers=headers).status_code==expected
    assert case[0].get(f"/api/v1/masks/finance/ap-invoice/data/entity?entity_id={entity}",headers=headers).status_code==expected
    assert _mcp(case,headers,entity).status_code==(403 if kind=="no_mcp_scope" else expected)
    code,_=_cli(case,monkeypatch,headers,entity)
    assert code==(0 if expected==200 else 3 if expected==403 else 2)


def test_forged_selectors_and_invalid_token_never_read_data(channels):
    case=channels;headers=_headers(case)
    base=f"/api/v1/masks/finance/ap-invoice/data/entity?entity_id={case[5]}"
    assert case[0].get(base+"&tenant_id="+case[4],headers=headers).status_code==403
    assert case[0].get(base,headers={**headers,"X-Tenant-ID":case[4]}).status_code==403
    assert case[0].get(base,headers={"Authorization":"Bearer invalid"}).status_code==401
    assert case[0].get(base).status_code==401
