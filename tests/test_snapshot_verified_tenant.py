"""Snapshot reads and writes cannot select another tenant through query input."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import read_model_snapshots as endpoint
from app.auth.deps import get_current_user
from app.core.read_model_persistence import ReadModelSnapshot, ReadModelSnapshotStore
from app.core.tenant import get_tenant_id


@pytest.fixture
def boundary():
    app = FastAPI()
    app.include_router(endpoint.router)
    store = ReadModelSnapshotStore()
    for tenant in ("own", "foreign"):
        store.save(ReadModelSnapshot.build("orders", tenant, {"owner": tenant}))
    app.dependency_overrides[get_tenant_id] = lambda: "own"
    app.dependency_overrides[get_current_user] = lambda: {"sub": "synthetic", "roles": ["admin"]}
    app.dependency_overrides[endpoint._get_store] = lambda: store
    with TestClient(app) as client:
        yield app, client, store


def test_query_cannot_read_another_tenants_latest_snapshot(boundary):
    _, client, _ = boundary
    result = client.get('/read-models/snapshots/latest', params={'model_name': 'orders', 'tenant_id': 'foreign'})
    assert result.status_code == 200
    assert result.json()['tenant_id'] == 'own'


def test_query_cannot_read_another_tenants_page(boundary):
    _, client, _ = boundary
    result = client.get('/read-models/snapshots/page', params={'model_name': 'orders', 'tenant_id': 'foreign'})
    assert result.status_code == 200
    assert [row['tenant_id'] for row in result.json()['items']] == ['own']


def test_query_cannot_write_into_another_tenant(boundary):
    _, client, store = boundary
    result = client.post('/read-models/snapshots', params={'model_name': 'orders', 'tenant_id': 'foreign'}, json={'value': 1})
    assert result.status_code == 201
    assert result.json()['tenant_id'] == 'own'
    assert len([item for item in store.snapshots.values() if item.tenant_id == 'foreign']) == 1


def test_read_role_cannot_create_projection_snapshots(boundary):
    app, client, store = boundary
    app.dependency_overrides[get_current_user] = lambda: {'sub': 'synthetic', 'roles': ['FINANCE_LESEN']}
    result = client.post('/read-models/snapshots', params={'model_name': 'orders'}, json={})
    assert result.status_code == 403
    assert len(store.snapshots) == 2


def test_snapshot_route_requires_authenticated_tenant():
    app = FastAPI()
    app.include_router(endpoint.router)
    app.dependency_overrides[endpoint._get_store] = lambda: ReadModelSnapshotStore()
    with TestClient(app) as client:
        result = client.get('/read-models/snapshots/latest', params={'model_name': 'orders', 'tenant_id': 'foreign'})
    assert result.status_code == 401


@pytest.mark.parametrize('path', ['latest', 'page'])
def test_domain_read_role_cannot_read_arbitrary_technical_projection(boundary, path):
    app, client, _ = boundary
    app.dependency_overrides[get_current_user] = lambda: {'sub': 'reader', 'roles': ['FINANCE_LESEN']}
    result = client.get('/read-models/snapshots/' + path, params={'model_name': 'orders'})
    assert result.status_code == 403
