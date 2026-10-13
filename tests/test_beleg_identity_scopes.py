"""Document token scopes are projections of existing domain roles, not new rights."""
import copy
import json

import httpx
import pytest
from test_system_tenant_binding import keys, probe

from app.auth.finance_roles import BELEG_READ_ROLES, BELEG_WRITE_ROLES
from scripts.keycloak_document_scopes import DOCUMENT_SCOPE_ROLES, ERP_CLIENT_IDS, reconcile_document_scope_roles
from scripts.provision_identity_provider import ROOT, prepared_realm


@pytest.mark.parametrize("file", ["realm-export.json", "realm-staging.json"])
def test_document_scopes_exist_and_are_default_only_on_erp_clients(file):
    realm = prepared_realm(json.loads((ROOT / "config/keycloak" / file).read_text(encoding="utf-8")))
    assert prepared_realm(realm) == realm
    scopes = {s["name"]:s for s in realm["clientScopes"]}
    for name in DOCUMENT_SCOPE_ROLES:
        assert scopes[name]["attributes"]["include.in.token.scope"] == "true"
    clients = [c for c in realm["clients"] if c["clientId"] in ERP_CLIENT_IDS]
    assert clients
    for client in clients:
        assert set(DOCUMENT_SCOPE_ROLES) <= set(client["defaultClientScopes"])
    # No second document-role system is introduced.
    assert not any(r["name"].startswith("BELEGE_") for r in realm["roles"]["realm"])


def test_scopes_use_the_existing_authorization_tuples():
    assert set(BELEG_READ_ROLES) <= set(DOCUMENT_SCOPE_ROLES["belege:read"])
    assert set(BELEG_WRITE_ROLES) <= set(DOCUMENT_SCOPE_ROLES["belege:write"])
    assert set(BELEG_WRITE_ROLES) <= set(BELEG_READ_ROLES)
    assert "CRM_LESEN" in BELEG_READ_ROLES
    assert "CRM_LESEN" not in BELEG_WRITE_ROLES
    assert not any(r.endswith("_LESEN") for r in BELEG_WRITE_ROLES)


@pytest.mark.parametrize("failure", [None, "unexpected", "missing_role", "mapping_failed", "not_persisted"])
def test_role_scope_mapping_is_verified_repeatable_and_fail_closed(failure):
    mapping = {name:set() for name in DOCUMENT_SCOPE_ROLES}
    if failure == "unexpected": mapping["belege:read"].add("user")
    writes=[]
    def handler(request):
        path = request.url.path
        if "/roles/" in path:
            name = path.rsplit("/",1)[-1]
            if failure == "missing_role": return httpx.Response(404)
            return httpx.Response(200,json={"id":"id-"+name,"name":name})
        scope = next(name for name in mapping if name in path)
        if path.endswith("/scope-mappings/realm"):
            if request.method == "GET":
                return httpx.Response(200,json=[{"id":"id-"+n,"name":n} for n in sorted(mapping[scope])])
            writes.append(scope)
            if failure == "mapping_failed": return httpx.Response(403)
            if failure != "not_persisted": mapping[scope].update(r["name"] for r in json.loads(request.content))
            return httpx.Response(204)
        return httpx.Response(200,json={"name":scope,"protocol":"openid-connect", "attributes":{"include.in.token.scope":"true"}})
    with httpx.Client(base_url="https://idp.invalid",transport=httpx.MockTransport(handler)) as client:
        if failure:
            with pytest.raises((RuntimeError,httpx.HTTPStatusError)):
                reconcile_document_scope_roles(client,{},"fixture",{s:s for s in mapping})
        else:
            reconcile_document_scope_roles(client,{},"fixture",{s:s for s in mapping})
            original=copy.deepcopy(mapping)
            reconcile_document_scope_roles(client,{},"fixture",{s:s for s in mapping})
            assert mapping == original
            assert writes == ["belege:read","belege:write"]
            assert mapping == {s:set(roles) for s,roles in DOCUMENT_SCOPE_ROLES.items()}


@pytest.mark.parametrize("scopes,expected", [("belege:read",200), ("belege:write",403), ("openid profile email",403)])
def test_signed_token_reaches_real_mcp_document_dispatch(probe,scopes,expected):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from app.api.v1.endpoints.mcp_tool_registry import router
    from app.core.database import get_db
    from main import BearerAuthMiddleware
    from unittest.mock import Mock
    app = FastAPI()
    app.add_middleware(BearerAuthMiddleware)
    app.include_router(router,prefix="/api/v1")
    database = Mock()
    app.dependency_overrides[get_db] = lambda: database
    response = TestClient(app).post("/api/v1/mcp/tools/call",
        headers={"Authorization":"Bearer "+probe.token(changes={"scope":scopes})},
        json={"tool_name":"beleg.arten","parameters":{},"mode":"dryRun"})
    assert response.status_code == expected,response.text
    if expected == 200:
        assert response.json()["success"] is True
        assert len(response.json()["belegarten"]) == 9
    database.execute.assert_not_called()



def test_scope_projection_matches_all_existing_document_rights():
    from app.auth.beleg_roles import rollen_fuer
    from app.core.belegvertrag import BELEGARTEN
    read = set().union(*(rollen_fuer("lesen", art) for art in BELEGARTEN))
    write = set().union(*(rollen_fuer(right, art) for art in BELEGARTEN
                         for right in ("bearbeiten","ausstellen","buchen","stornieren")))
    assert set(DOCUMENT_SCOPE_ROLES["belege:read"]) == read
    assert set(DOCUMENT_SCOPE_ROLES["belege:write"]) == write
    assert "LAGER_LESEN" in read and "LAGER_LESEN" not in write
    assert "LAGER_BEARBEITEN" in read & write
