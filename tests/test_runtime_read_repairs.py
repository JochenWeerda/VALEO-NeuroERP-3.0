"""Real signed identities and SQL reads for failures exposed by runtime sweep."""
from uuid import uuid4
import json
from unittest.mock import AsyncMock
import pytest
from fastapi import FastAPI, APIRouter
from fastapi.testclient import TestClient
from sqlalchemy import text
from app.core.database import get_db
from app.core.tenant_binding import install_tenant_bindings
from app.api.v1.endpoints import users, compat
from app.routers.numbering_router import router as numbering_router
from app.services.numbering_service_pg import NumberingServicePG
from app.documents.repository import DocumentRepository
from app.infrastructure.models import User
from main import BearerAuthMiddleware
from test_gdpr_subject_boundary import keys, probe, subject_data  # noqa: F401


@pytest.fixture
def read_client(subject_data, monkeypatch):
    _, db, provider, tenant, foreign_tenant, own, other, foreign = subject_data
    for uid in (own, other, foreign):
        db.get(User, uid).email = uid + '@example.org'
    db.flush()
    app = FastAPI()
    app.add_middleware(BearerAuthMiddleware)
    app.include_router(users.router, prefix='/api/v1/users')
    app.include_router(numbering_router)
    reports = APIRouter()
    reports.routes.extend(route for route in compat.router.routes if route.path in ('/einkauf/reports', '/einkauf/reports/standard'))
    app.include_router(reports, prefix='/api/v1')
    app.dependency_overrides[get_db] = lambda: db
    install_tenant_bindings(app, public_paths=BearerAuthMiddleware.PUBLIC_PATHS)
    monkeypatch.setattr(compat, 'cache_get_json', lambda *a: None)
    monkeypatch.setattr(compat, 'cache_set_json', lambda *a, **k: None)
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client, db, provider, tenant, foreign_tenant, own, other, foreign


def auth(data, admin=False, **changes):
    return {'Authorization': 'Bearer ' + data[2].token(data[3], changes={'roles': ['admin'] if admin else ['user'], 'scope': 'admin:all' if admin else '', **changes})}


def test_current_profile_uses_verified_provider_mapping(read_client):
    client, db, _, _, _, own, other, _ = read_client
    response = client.get('/api/v1/users/me', headers={**auth(read_client), 'X-User-ID': other})
    assert response.status_code == 200, response.text
    assert response.json()['id'] == own
    assert json.loads(response.json()['roles']) == ['user']
    assert client.get('/api/v1/users/me', headers=auth(read_client, sub='missing-profile')).status_code == 404
    assert client.get('/api/v1/users/me').status_code == 401
    db.get(User, own).is_active = False
    db.flush()
    assert client.get('/api/v1/users/me', headers=auth(read_client)).status_code == 404


def test_user_directory_is_admin_only_and_tenant_bound(read_client):
    client, _, _, tenant, foreign_tenant, own, other, foreign = read_client
    assert client.get('/api/v1/users/', headers=auth(read_client)).status_code == 403
    result = client.get('/api/v1/users/', headers=auth(read_client, True))
    assert result.status_code == 200, result.text
    assert {row['id'] for row in result.json()['items']} == {own, other}
    assert result.json()['total'] == 2
    assert client.get('/api/v1/users/', params={'tenant_id': foreign_tenant}, headers=auth(read_client, True)).status_code == 403
    page = client.get('/api/v1/users/', params={'skip': 1, 'limit': 1}, headers=auth(read_client, True))
    assert page.status_code == 200 and len(page.json()['items']) == 1 and page.json()['total'] == 2
    assert client.get(f'/api/v1/users/{own}', headers=auth(read_client)).status_code == 200
    assert client.get(f'/api/v1/users/{other}', headers=auth(read_client)).status_code == 403
    assert client.get(f'/api/v1/users/{other}', headers=auth(read_client, True)).status_code == 200
    assert client.get(f'/api/v1/users/{foreign}', headers=auth(read_client, True)).status_code == 404


def test_purchase_reports_use_tenant_document_store_without_poisoning_transaction(read_client):
    client, db, _, tenant, foreign_tenant, *_ = read_client
    repository = DocumentRepository(db)
    for tid, value in [(tenant, '0.10'), (tenant, '0.20'), (foreign_tenant, '700')]:
        repository.save_document('purchase_order', 'SYNTH-' + uuid4().hex, {'tenantId': tid, 'subtotal': value, 'category': 'Synthetic category'}, commit=False)
    result = client.get('/api/v1/einkauf/reports', headers=auth(read_client, True))
    assert result.status_code == 200, result.text
    assert result.json()['spend'] == [{'kategorie': 'Synthetic category', 'anteil': 100.0, 'betrag': 0.3}]
    standard = client.get('/api/v1/einkauf/reports/standard', headers=auth(read_client, True))
    assert standard.status_code == 200, standard.text
    assert len(standard.json()['openOrders']) == 2
    assert db.execute(text('SELECT 1')).scalar_one() == 1


def test_number_series_uses_actual_sync_session_and_tenant_filter(read_client):
    client, db, _, tenant, foreign_tenant, *_ = read_client
    domain = 'synthetic_' + uuid4().hex
    for tid in (tenant, foreign_tenant):
        db.execute(text('INSERT INTO number_series (id,domain,tenant_id,year,prefix,width,counter) VALUES (:id,:d,:t,2026,:p,4,7)'), {'id': str(uuid4()), 'd': domain, 't': tid, 'p': 'SYNTH-'})
    result = client.get('/api/numbering/series', params={'tenant_id': tenant}, headers=auth(read_client, True))
    assert result.status_code == 200, result.text
    rows = [row for row in result.json() if row['domain'] == domain]
    assert len(rows) == 1 and rows[0]['next_number'] == 'SYNTH-0008' and rows[0]['tenant_id'] == tenant
    assert client.get('/api/numbering/series', params={'tenant_id': foreign_tenant}, headers=auth(read_client, True)).status_code == 403


@pytest.mark.asyncio
async def test_numbering_keeps_async_session_support():
    db = AsyncMock()
    service = NumberingServicePG(db)
    assert await service.execute('synthetic statement') is db.execute.return_value
    await service.commit()
    db.execute.assert_awaited_once_with('synthetic statement')
    db.commit.assert_awaited_once_with()
