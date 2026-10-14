from uuid import uuid4
"""Durable studio operations never fall back to per-process drafts."""
import pytest
from sqlalchemy.exc import OperationalError, ProgrammingError
from test_studio_token_identity import probe
from app.services import studio_draft_store as store
from app.services.studio_propose import propose_studio_draft


@pytest.mark.parametrize('error_type', [OperationalError, ProgrammingError])
@pytest.mark.parametrize('operation', ['list', 'get', 'save', 'status', 'runtime', 'runtime_list'])
def test_unavailable_sql_never_uses_existing_process_drafts(monkeypatch, error_type, operation):
    store.reset_studio_drafts()
    record = store.save_draft('tenant', 'editor', propose_studio_draft('Kunden'))
    store.set_status('tenant', record['id'], 'editor', 'review')
    store.set_status('tenant', record['id'], 'reviewer', 'published_temp')
    monkeypatch.setattr(store, '_prefer_memory', False)
    def unavailable():
        raise error_type('private-connection-detail', {}, RuntimeError('private-password'))
    monkeypatch.setattr(store, '_sql_session', unavailable)
    calls = {
        'list': lambda: store.list_drafts('tenant'),
        'get': lambda: store.get_draft('tenant', record['id']),
        'save': lambda: store.save_draft('tenant', 'editor', record['definition']),
        'status': lambda: store.set_status('tenant', record['id'], 'reviewer', 'retired'),
        'runtime': lambda: store.get_published_definition('tenant', record['screen_id']),
        'runtime_list': lambda: store.list_published_definitions('tenant'),
    }
    try:
        with pytest.raises(store.StudioStorageUnavailable, match='studio_persistenz_nicht_verfuegbar'):
            calls[operation]()
        assert len(store._DRAFTS) == 1
        assert store._DRAFTS[record['id']]['status'] == 'published_temp'
    finally:
        store.reset_studio_drafts()


@pytest.mark.parametrize('method,path,body', [
    ('get', '/studio/drafts', None),
    ('get', '/studio/drafts/missing', None),
    ('post', '/studio/drafts', 'definition'),
    ('put', '/studio/drafts/missing', 'definition'),
    ('post', '/studio/drafts/missing/submit-review', 'revision'),
    ('post', '/studio/drafts/missing/publish', 'revision'),
    ('post', '/studio/drafts/missing/retire', 'revision'),
])
def test_studio_http_storage_failure_is_sanitized_503(probe, monkeypatch, method, path, body):
    client, _ = probe
    store.use_sql_studio_drafts()
    def unavailable():
        raise OperationalError('private-connection-detail', {}, RuntimeError('private-password'))
    monkeypatch.setattr(store, '_sql_session', unavailable)
    payload = {'definition': propose_studio_draft('Kunden'), 'expected_revision': '0' * 64, 'idempotency_key': str(uuid4())} if body == 'definition' else {'expected_revision': '0' * 64, 'idempotency_key': str(uuid4())}
    response = getattr(client, method)(path, **({'json': payload} if method != 'get' else {}))
    assert response.status_code == 503, response.text
    assert 'private-' not in response.text
    assert not store._DRAFTS
