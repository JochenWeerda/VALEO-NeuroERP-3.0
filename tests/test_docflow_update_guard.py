"""Real shared PostgreSQL update/replay/concurrency; only own committed rows cleaned."""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from types import SimpleNamespace
from uuid import uuid4
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.api.v1.endpoints import docflow
from app.auth.deps import get_current_user
from app.core.database import engine, get_db
from app.core.exceptions import ConflictError, EntityNotFoundError
from app.services.docflow_service import DocflowService
from testgrenze import pruefstand_erlaubt

pytestmark = [pytest.mark.integration, pytest.mark.needs_live_db]

@pytest.fixture(autouse=True)
def _enable_dev_token():
    yield

@pytest.fixture
def sql_doc(monkeypatch):
    assert pruefstand_erlaubt(engine.url), 'Only the declared shared probe is allowed'
    tenant = str(uuid4())
    # The mandatory command log is tested; optional cross-domain audit mirroring is outside this contract.
    monkeypatch.setattr(DocflowService, 'best_effort_audit', lambda *args, **kwargs: None)
    with Session(engine) as db:
        db.execute(text('INSERT INTO domain_shared.tenants (id,name,domain) VALUES (:t,:t,:domain)'),
                   {'t': tenant, 'domain': tenant + '.example.invalid'})
        doc_id = DocflowService(db, tenant, 'synthetic-editor').create_document(docflow.DocflowCreateRequest(
            doc_type='sales_offer', doc_number='TEST-' + uuid4().hex,
            items=[docflow.DocflowLineInput(article_number='SYNTHETIC', quantity=1, unit_price=10)]))
    context = SimpleNamespace(tenant=tenant, id=doc_id)
    try:
        yield context
    finally:
        with Session(engine) as db:
            db.execute(text("SELECT set_config('valeo.docflow_wartung', 'loeschen', true)"))
            for table in ['document_status_history', 'document_command_log', 'command_idempotency_keys',
                          'document_items', 'document_headers']:
                db.execute(text(f'DELETE FROM domain_docflow.{table} WHERE tenant_id=:t'), {'t': tenant})
            db.execute(text('DELETE FROM outbox_events WHERE tenant_id=:t'), {'t': tenant})
            db.execute(text('DELETE FROM domain_shared.tenants WHERE id=:t'), {'t': tenant})
            db.commit()
        with engine.connect() as connection:
            assert connection.execute(text('SELECT count(*) FROM domain_shared.tenants WHERE id=:t'), {'t': tenant}).scalar_one() == 0


def edit(context, key, version=1, **values):
    with Session(engine) as db:
        return DocflowService(db, context.tenant, 'synthetic-editor').update_document(context.id,
            docflow.DocflowUpdateRequest(expected_version=version, idempotency_key=key, **values))


def state(context):
    with Session(engine) as db:
        svc = DocflowService(db, context.tenant)
        return (svc.fetch_header(context.id), svc.fetch_items(context.id), len(svc.fetch_command_log(context.id)),
                db.execute(text("SELECT count(*) FROM outbox_events WHERE tenant_id=:t AND event_type='docflow.document.updated'"), {'t': context.tenant}).scalar_one())


def test_repeat_returns_original_snapshot_even_after_a_later_edit(sql_doc):
    first = edit(sql_doc, 'first-update-key', currency='USD')
    assert first['header']['version'] == 2
    edit(sql_doc, 'second-update-key', version=2, currency='EUR')
    assert edit(sql_doc, 'first-update-key', currency='USD') == first
    header, items, log_count, events = state(sql_doc)
    assert header['version'] == 3 and header['currency'] == 'EUR'
    assert log_count == 3 and events == 2  # create plus two updates, never a replay entry


def test_key_with_changed_content_is_conflict(sql_doc):
    edit(sql_doc, 'same-update-key', currency='USD')
    with pytest.raises(ConflictError):
        edit(sql_doc, 'same-update-key', currency='EUR')
    assert state(sql_doc)[0]['version'] == 2


def test_stale_version_does_not_overwrite(sql_doc):
    edit(sql_doc, 'first-update-key', currency='USD')
    with pytest.raises(ConflictError):
        edit(sql_doc, 'stale-update-key', currency='EUR')
    assert state(sql_doc)[0]['currency'] == 'USD'


@pytest.mark.parametrize('same_key', [True, False])
def test_real_parallel_updates_serialize_before_replay_or_version_check(sql_doc, same_key):
    barrier = Barrier(2)
    def worker(index):
        barrier.wait(timeout=10)
        try:
            return ('ok', edit(sql_doc, 'parallel-key' if same_key else f'parallel-key-{index}', currency='USD'))
        except ConflictError:
            return ('conflict', None)
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(worker, index) for index in range(2)]
        results = [future.result(timeout=20) for future in futures]
    assert [kind for kind, _ in results].count('ok') == (2 if same_key else 1)
    if same_key:
        assert results[0][1] == results[1][1]
    header, items, log_count, events = state(sql_doc)
    assert header['version'] == 2 and log_count == 2 and events == 1


@pytest.mark.parametrize('failure_site', ['upsert_outbox_event', 'store_idempotent_response'])
def test_failure_rolls_back_header_positions_log_outbox_and_replay(sql_doc, monkeypatch, failure_site):
    before = state(sql_doc)
    def fail(*args, **kwargs):
        raise RuntimeError('synthetic evidence failure')
    monkeypatch.setattr(DocflowService, failure_site, fail)
    with pytest.raises(RuntimeError, match='synthetic evidence failure'):
        edit(sql_doc, 'rollback-update-key', items=[docflow.DocflowLineInput(article_number='REPLACED', quantity=2, unit_price=20)])
    assert state(sql_doc) == before
    with Session(engine) as db:
        assert DocflowService(db, sql_doc.tenant).load_idempotent_response('update', sql_doc.id, 'rollback-update-key') is None


def test_foreign_tenant_cannot_update_or_replay(sql_doc):
    edit(sql_doc, 'same-update-key', currency='USD')
    with Session(engine) as db:
        with pytest.raises(EntityNotFoundError):
            DocflowService(db, str(uuid4()), 'synthetic-other').update_document(sql_doc.id,
                docflow.DocflowUpdateRequest(expected_version=1, idempotency_key='same-update-key', currency='USD'))
    assert state(sql_doc)[0]['version'] == 2


@pytest.fixture
def client(sql_doc):
    app = FastAPI()
    app.include_router(docflow.router, prefix='/docflow')
    app.dependency_overrides[docflow._docflow_tenant] = lambda: sql_doc.tenant
    app.dependency_overrides[get_current_user] = lambda: {'sub': 'synthetic-editor', 'roles': ['admin']}
    def database():
        with Session(engine) as db:
            yield db
    app.dependency_overrides[get_db] = database
    with TestClient(app, raise_server_exceptions=False) as http:
        yield http


@pytest.mark.parametrize('payload', [{}, {'expected_version': 1}, {'idempotency_key': 'missing-version'},
    {'expected_version': True, 'idempotency_key': 'bool-version'},
    {'expected_version': 0, 'idempotency_key': 'zero-version'}])
def test_http_requires_valid_version_and_key_before_business_write(sql_doc, client, payload):
    before = state(sql_doc)
    response = client.put('/docflow/' + sql_doc.id, json=payload)
    assert response.status_code == 422
    assert state(sql_doc) == before


def test_http_replay_returns_same_confirmed_header(sql_doc, client):
    payload = {'expected_version': 1, 'idempotency_key': 'http-update-key', 'currency': 'USD'}
    first = client.put('/docflow/' + sql_doc.id, json=payload)
    assert first.status_code == 200, first.text
    later = client.put('/docflow/' + sql_doc.id, json={**payload, 'expected_version': 2, 'idempotency_key': 'http-next-key', 'currency': 'EUR'})
    assert later.status_code == 200, later.text
    assert client.put('/docflow/' + sql_doc.id, json=payload).json() == first.json()


def test_request_actor_cannot_replace_missing_verified_actor(sql_doc):
    from app.core.exceptions import ValidationFailedError
    before = state(sql_doc)
    with Session(engine) as db:
        with pytest.raises(ValidationFailedError, match='Akteur'):
            DocflowService(db, sql_doc.tenant).update_document(sql_doc.id,
                docflow.DocflowUpdateRequest(expected_version=1, idempotency_key='actor-forgery-key', updated_by='forged'))
    assert state(sql_doc) == before


def test_another_actor_cannot_replay_the_same_key(sql_doc):
    edit(sql_doc, 'actor-bound-key', currency='USD')
    with Session(engine) as db:
        with pytest.raises(ConflictError):
            DocflowService(db, sql_doc.tenant, 'synthetic-other').update_document(sql_doc.id,
                docflow.DocflowUpdateRequest(expected_version=1, idempotency_key='actor-bound-key', currency='USD'))
    assert state(sql_doc)[0]['version'] == 2


def test_http_error_does_not_disclose_input_and_leaves_no_effect(sql_doc, client, monkeypatch):
    before = state(sql_doc)
    def fail(*args, **kwargs):
        raise RuntimeError('synthetic-private-customer-value')
    monkeypatch.setattr(DocflowService, 'upsert_outbox_event', fail)
    response = client.put('/docflow/' + sql_doc.id, json={
        'expected_version': 1, 'idempotency_key': 'http-error-key', 'currency': 'USD'})
    assert response.status_code == 500
    assert response.json()['detail'] == 'Document update failed'
    assert 'synthetic-private-customer-value' not in response.text
    assert state(sql_doc) == before


def test_http_permission_is_checked_before_replay(sql_doc, client):
    edit(sql_doc, 'permission-replay-key', currency='USD')
    before = state(sql_doc)
    client.app.dependency_overrides[get_current_user] = lambda: {'sub': 'synthetic-reader', 'roles': []}
    response = client.put('/docflow/' + sql_doc.id, json={
        'expected_version': 1, 'idempotency_key': 'permission-replay-key', 'currency': 'USD'})
    assert response.status_code == 403, response.text
    assert state(sql_doc) == before


@pytest.mark.parametrize('target', ['open', 'cancelled', 'released', 'unknown'])
def test_update_cannot_bypass_the_status_commands(sql_doc, target):
    from app.core.exceptions import ValidationFailedError
    before = state(sql_doc)
    with pytest.raises(ValidationFailedError, match='Fachkommandos'):
        edit(sql_doc, 'forbidden-status-key', status=target)
    assert state(sql_doc) == before


def test_issued_document_cannot_be_demoted_to_editable_draft(sql_doc):
    from app.core.exceptions import ValidationFailedError
    with Session(engine) as db:
        svc = DocflowService(db, sql_doc.tenant, 'synthetic-editor')
        svc.release(sql_doc.id, 'release-before-edit', 1, None)
    before = state(sql_doc)
    with pytest.raises(ValidationFailedError, match='Fachkommandos'):
        edit(sql_doc, 'forbidden-demotion-key', version=2, status='draft')
    assert state(sql_doc) == before
