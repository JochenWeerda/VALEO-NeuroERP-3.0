"""Native baselines use Studio history without granting activation or commands."""
from copy import deepcopy
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from app.api.v1.endpoints.studio_native_import import router
from app.auth.deps import get_current_user
from app.core.tenant import get_tenant_id
from app.services import studio_draft_store as store
from app.services import studio_native_import as service


@pytest.fixture(autouse=True)
def _enable_dev_token():
    yield


@pytest.fixture(scope="session", autouse=True)
def _seed_contract_test_tenants():
    yield


@pytest.fixture
def boundary(monkeypatch):
    monkeypatch.setattr(store, "_prefer_memory", True)
    monkeypatch.setattr(store, "_DRAFTS", {})
    monkeypatch.setattr(store, "_HISTORY", [])
    app = FastAPI()
    app.include_router(router, prefix="/studio")
    app.dependency_overrides[get_tenant_id] = lambda: "own"
    app.dependency_overrides[get_current_user] = lambda: {"sub": "verified-designer", "roles": ["EINKAUF_BEARBEITEN"]}
    with TestClient(app) as client:
        yield app, client


def payload():
    source = service.source_definition("own", "agrar/duenger")
    return {"screen_id": "agrar/duenger", "expected_source_hash": service.definition_hash(source),
            "idempotency_key": str(uuid4())}


def test_import_is_versioned_idempotent_and_does_not_activate(boundary):
    _, client = boundary
    before = deepcopy(service.source_definition("own", "agrar/duenger"))
    body = payload()
    first = client.post('/studio/native-imports?tenant_id=foreign', json=body)
    assert first.status_code == 200, first.text
    record = first.json()
    repeated = client.post('/studio/native-imports', json=body)
    assert repeated.json() == record
    assert record['tenant_id'] == 'own' and record['created_by'] == 'verified-designer'
    assert record['status'] == 'draft' and len(record['revision']) == 64
    assert record['base_screen_id'] == 'agrar/duenger'
    assert record['readiness']['eligible_for_release'] is False
    assert service.definition_hash(record['readiness']['migration']['source_definition']) == body['expected_source_hash']
    assert len(store.list_history('own', record['id'])) == 1
    assert store.list_drafts('foreign') == []
    assert service.source_definition('own', 'agrar/duenger') == before
    assert store.get_published_definition('own', record['screen_id']) is None


def test_stale_source_hash_does_not_create_a_baseline(boundary):
    _, client = boundary
    body = payload(); body['expected_source_hash'] = '0' * 64
    assert client.post('/studio/native-imports', json=body).status_code == 409
    assert store.list_drafts('own') == []


def test_document_import_retains_exact_base_variant_and_materialization_in_history(boundary):
    from app.core.screen_definitions_beleg import NATIVE_BELEG_TENANTS, screen_id
    app, client = boundary
    tenant = next(iter(NATIVE_BELEG_TENANTS))
    app.dependency_overrides[get_tenant_id] = lambda: tenant
    key = screen_id('sales_invoice')
    source = service.source_definition(tenant, key)
    response = client.post('/studio/native-imports', json={
        'screen_id': key, 'expected_source_hash': service.definition_hash(source), 'idempotency_key': str(uuid4())})
    assert response.status_code == 200, response.text
    record = response.json()
    binding = source['documentVariant']
    assert record['definition']['documentVariant'] == binding
    assert record['readiness']['migration']['source_definition'] == source
    history = store.list_history(tenant, record['id'])
    assert history[0]['snapshot']['definition']['documentVariant'] == binding
    assert record['status'] == 'draft' and record['readiness']['eligible_for_release'] is False


@pytest.mark.parametrize('source', ['tenant/foreign-draft', 'beleg/sales-invoice', 'missing/source'])
def test_unregistered_or_foreign_source_is_not_importable(boundary, source):
    _, client = boundary
    body = payload(); body['screen_id'] = source
    assert client.post('/studio/native-imports', json=body).status_code == 404
    assert store.list_drafts('own') == []


def test_import_cannot_overwrite_existing_baseline_with_a_new_key(boundary):
    _, client = boundary
    first = client.post('/studio/native-imports', json=payload()).json()
    assert client.post('/studio/native-imports', json=payload()).status_code == 409
    assert store.get_draft('own', first['id'])['revision'] == first['revision']


@pytest.mark.parametrize('extra', ['tenant_id', 'actor', 'definition', 'readiness'])
def test_import_accepts_no_client_supplied_identity_definition_or_proof(boundary, extra):
    _, client = boundary
    body = payload(); body[extra] = 'forged'
    assert client.post('/studio/native-imports', json=body).status_code == 422
    assert store.list_drafts('own') == []


def test_existing_read_role_has_no_import_permission(boundary):
    app, client = boundary
    app.dependency_overrides[get_current_user] = lambda: {'sub': 'reader', 'roles': ['FINANCE_LESEN']}
    assert client.post('/studio/native-imports', json=payload()).status_code == 403
    assert store.list_drafts('own') == []


def test_source_catalog_is_bounded_and_tenant_scoped(boundary):
    _, client = boundary
    response = client.get('/studio/native-sources', params={'q': 'duenger', 'limit': 1})
    assert response.status_code == 200
    assert len(response.json()['items']) == 1
    assert len(response.json()['items'][0]['source_hash']) == 64
    assert client.get('/studio/native-sources?limit=101').status_code == 422


def test_baseline_cannot_bypass_existing_studio_release_gate(boundary):
    _, client = boundary
    first = client.post('/studio/native-imports', json=payload()).json()
    current = store.get_draft('own', first['id'])
    reviewed = store.set_status('own', first['id'], 'verified-designer', 'review', expected_snapshot=current)
    with pytest.raises(ValueError, match="studio_definition_nicht_freigabefaehig"):
        store.set_status('own', first['id'], 'another-reviewer', 'published_temp', expected_snapshot=reviewed)


def test_import_persists_one_exact_baseline_and_history_in_shared_probe(require_db, monkeypatch):
    from sqlalchemy import text
    from sqlalchemy.orm import Session
    from app.core.database import engine
    from testgrenze import pruefstand_erlaubt
    assert pruefstand_erlaubt(engine.url)
    tenant = str(uuid4())
    monkeypatch.setattr(store, '_prefer_memory', False)
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            connection.execute(text('INSERT INTO domain_shared.tenants (id,name,is_active) VALUES (:id,:id,true)'), {'id': tenant})
            monkeypatch.setattr(store, '_sql_session', lambda: Session(bind=connection, join_transaction_mode='create_savepoint'))
            source = service.source_definition(tenant, 'agrar/duenger')
            key = str(uuid4())
            first = service.import_source(tenant, 'synthetic-sql-designer', 'agrar/duenger', service.definition_hash(source), key)
            replay = service.import_source(tenant, 'synthetic-sql-designer', 'agrar/duenger', service.definition_hash(source), key)
            assert replay == first
            assert store.list_drafts(tenant)[0]['status'] == 'draft'
            entries = store.list_history(tenant, first['id'])
            assert len(entries) == 1
            assert entries[0]['snapshot']['readiness']['migration']['source_definition'] == source
        finally:
            transaction.rollback()
