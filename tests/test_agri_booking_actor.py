"""Actual JWT/JWKS and production middleware; only the final domain service is a spy."""
from functools import partial
from types import SimpleNamespace
import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from app.core.tenant import get_tenant_id
from app.core.tenant_binding import install_tenant_bindings
from app.api.v1.endpoints import agri_silo_material_flow as flow, agri_lot_link_booking as lot
from main import BearerAuthMiddleware
from test_system_tenant_binding import keys, probe  # noqa: F401

CASES = [
    ('transfer', {'warehouse_id': 'warehouse-a', 'from_cell_id': 'cell-a', 'to_cell_id': 'cell-b', 'quantity_kg': '12.5', 'article_id': 'article-a'}),
    ('flush-charge', {'warehouse_id': 'warehouse-a', 'from_cell_id': 'cell-a', 'to_cell_id': 'cell-b', 'flush_material_id': 'article-a', 'flush_quantity_kg': '12.5'}),
    ('lot-link', {'warehouse_id': 'warehouse-a', 'lot_id': 'lot-a', 'target_cell_id': 'cell-a', 'quantity_kg': '12.5'}),
    ('lot-link/auto-book', {'warehouse_id': 'warehouse-a', 'lot_id': 'lot-a'}),
]


@pytest.fixture
def booking(probe):
    app = FastAPI()
    app.add_middleware(BearerAuthMiddleware)
    prefix = '/api/v1/lager/wms/agri'
    app.include_router(flow.router, prefix=prefix)
    app.include_router(lot.router, prefix=prefix)
    calls = []

    def record(tenant, **body):
        calls.append((tenant, body))
        return {'actor': body['booked_by'], 'tenant_id': tenant}

    def service(tenant_id: str = Depends(get_tenant_id)):
        return SimpleNamespace(**{name: partial(record, tenant_id) for name in (
            'book_material_transfer', 'book_flush_charge', 'book_lot_to_cell', 'auto_book_lot_link_by_lot_id')})

    app.dependency_overrides[flow._svc] = service
    app.dependency_overrides[lot._svc] = service
    install_tenant_bindings(app, public_paths=BearerAuthMiddleware.PUBLIC_PATHS)
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client, probe, calls, prefix + '/material-flow/'


def headers(provider, *, roles=None, tenant='tenant-a', **options):
    return {'Authorization': 'Bearer ' + provider.token(tenant, changes={'roles': roles if roles is not None else ['LAGER_BEARBEITEN'], 'identity_type': 'human'}, **options)}


@pytest.mark.parametrize('path,body', CASES)
@pytest.mark.parametrize('legacy_actor', [None, 'forged-administrator'])
def test_actor_comes_from_verified_subject_not_body_or_header(booking, path, body, legacy_actor):
    client, provider, calls, prefix = booking
    payload = {**body, **({'booked_by': legacy_actor} if legacy_actor else {})}
    response = client.post(prefix + path, headers={**headers(provider), 'X-User-ID': 'forged-header'}, json=payload)
    assert response.status_code == 200, response.text
    assert response.json() == {'actor': 'human-a', 'tenant_id': 'tenant-a'}
    assert len(calls) == 1
    assert calls[0][0] == 'tenant-a'
    assert calls[0][1]['booked_by'] == 'human-a'


@pytest.mark.parametrize('path,body', CASES)
@pytest.mark.parametrize('roles', [[], ['manager'], ['LAGER_LESEN']])
def test_actor_binding_never_grants_missing_booking_right(booking, path, body, roles):
    client, provider, calls, prefix = booking
    response = client.post(prefix + path, headers=headers(provider, roles=roles), json=body)
    assert response.status_code == 403, response.text
    assert calls == []


@pytest.mark.parametrize('path,body', CASES)
def test_anonymous_forged_signature_and_foreign_tenant_cannot_reach_service(booking, path, body):
    client, provider, calls, prefix = booking
    assert client.post(prefix + path, json=body).status_code == 401
    assert client.post(prefix + path, headers=headers(provider, key=1), json=body).status_code == 401
    assert client.post(prefix + path, headers=headers(provider, omit=('sub',)), json=body).status_code == 401
    assert client.post(prefix + path, headers={**headers(provider), 'X-Tenant-ID': 'tenant-b'}, json=body).status_code == 403
    assert calls == []
