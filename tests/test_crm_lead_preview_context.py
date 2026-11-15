"""HTTP router contract; provider verification and public source data are doubles.

Exercises the real tenant dependency, service constructor, preview and response
model. This is not a JWT, PostgreSQL/RLS or real GAP-data acceptance test.
"""
import pytest
from fastapi import FastAPI, HTTPException, Request
from fastapi.testclient import TestClient

from app.api.v1.endpoints import crm_lead_gen as endpoint
from app.core.database import get_db
from app.core.security import require_bearer_token
from app.services import crm_lead_gen_service as service

pytestmark = pytest.mark.unit
TENANT_A = "00000000-0000-0000-0000-000000000001"
TENANT_B = "00000000-0000-0000-0000-000000000002"
URL = "/api/v1/crm/lead-generierung/preview"
TOKEN = {"Authorization": "Bearer synthetic-boundary-token"}


@pytest.fixture(autouse=True)
def _enable_dev_token():
    """Use this isolated router app, never the compatibility-app dev identity."""
    yield


@pytest.fixture
def preview_client(monkeypatch):
    identity = {"tenant": TENANT_A, "verified": True}
    calls = []
    tenants = []
    db = object()  # Source doubles must prevent any database access.

    async def provider_boundary(request: Request):
        if request.headers.get("authorization") != TOKEN["Authorization"]:
            raise HTTPException(401, "Synthetic provider boundary: no identity")
        if identity["verified"]:
            request.state.tenant_id = identity["tenant"]
            request.state.tenant_verified = True
        return "synthetic-boundary-token"

    def source(kind):
        def candidates(session, plz_min, plz_max, top_pct, max_leads):
            assert session is db
            calls.append((kind, plz_min, plz_max, top_pct, max_leads))
            return [{"name": "Synthetic farm", "plz": "26500", "ort": "Synthetic",
                     "score": 100, "quelle": kind, "score_label": "Synthetic score"}]
        return candidates

    original_preview = service.CrmLeadGenService.preview

    def observed_preview(instance, **kwargs):
        tenants.append(instance.tenant_id)
        return original_preview(instance, **kwargs)

    monkeypatch.setattr(service, "gap_candidates", source("gap"))
    monkeypatch.setattr(service, "lkv_candidates", source("lkv"))
    monkeypatch.setattr(service.CrmLeadGenService, "preview", observed_preview)
    app = FastAPI()
    app.include_router(endpoint.router, prefix="/api/v1")
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[require_bearer_token] = provider_boundary
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client, identity, calls, tenants


@pytest.mark.parametrize("tenant,quelle", [(TENANT_A, "gap"), (TENANT_B, "lkv"), (TENANT_A, "beide")])
def test_preview_passes_verified_tenant_and_filters_to_real_service(preview_client, tenant, quelle):
    client, identity, calls, tenants = preview_client
    identity["tenant"] = tenant
    response = client.get(URL, headers=TOKEN, params={"quelle": quelle, "plz_min": "26000",
                          "plz_max": "26999", "top_pct": 0.25, "max_leads": 5,
                          "tenant_id": TENANT_B if tenant == TENANT_A else TENANT_A})
    assert response.status_code == 200
    assert tenants == [tenant]  # Query input must not select the security context.
    kinds = [quelle] if quelle != "beide" else ["gap", "lkv"]
    assert calls == [(kind, "26000", "26999", 0.25, 5) for kind in kinds]
    result = response.json()
    assert result["anzahl"] == len(kinds)
    assert result["top_pct"] == 0.25
    assert [item["quelle"] for item in result["kandidaten"]] == kinds
    assert all(item["name"] == "Synthetic farm" for item in result["kandidaten"])


@pytest.mark.parametrize("headers,verified,status", [
    ({}, True, 401),
    ({"X-Tenant-ID": TENANT_B}, True, 401),
    ({**TOKEN, "X-Tenant-ID": TENANT_B}, False, 403),
])
def test_preview_rejects_missing_identity_or_unverified_context_before_source_read(
    preview_client, headers, verified, status,
):
    client, identity, calls, tenants = preview_client
    identity["verified"] = verified
    response = client.get(URL, headers=headers)
    assert response.status_code == status
    assert calls == []
    assert tenants == []


@pytest.mark.parametrize("params", [{"top_pct": 0}, {"top_pct": 1.1}, {"max_leads": 0}, {"max_leads": 2001}])
def test_preview_preserves_filter_validation_without_source_reads(preview_client, params):
    client, _, calls, tenants = preview_client
    assert client.get(URL, headers=TOKEN, params=params).status_code == 422
    assert calls == []
    assert tenants == []
