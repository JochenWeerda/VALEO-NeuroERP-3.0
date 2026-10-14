from copy import deepcopy
from uuid import uuid4
import pytest
from sqlalchemy.exc import OperationalError
from test_studio_token_identity import probe, create
from test_meridian_screen_studio_persistence import studio_db, _client, _HEADERS_A
from app.services import studio_draft_store as store
from app.services.studio_propose import propose_studio_draft


@pytest.mark.parametrize('mode', ['create', 'update'])
def test_http_save_replays_exact_result_without_extra_revision(probe, mode):
    client, _ = probe
    original = create(client)
    definition = deepcopy(original['definition']) if mode == 'update' else propose_studio_draft('Artikel')
    definition['title'] = 'Idempotenter Entwurf'
    payload = {'definition': definition, 'idempotency_key': str(uuid4())}
    path = '/studio/drafts'
    if mode == 'update':
        path += '/'+original['id']
        payload['expected_revision'] = original['revision']
    method = client.put if mode == 'update' else client.post
    first = method(path, json=payload)
    assert first.status_code == 200, first.text
    replay = method(path, json=payload)
    assert replay.status_code == 200, replay.text
    assert replay.json() == first.json()
    history = store.list_history(first.json()['tenant_id'], first.json()['id'])
    assert len(history) == (2 if mode == 'update' else 1)
    assert history[-1]['id'] == payload['idempotency_key']


def test_reused_save_key_rejects_changed_content_or_actor(probe):
    client, user = probe
    definition = propose_studio_draft('Kunden')
    payload = {'definition': definition, 'idempotency_key': str(uuid4())}
    original = client.post('/studio/drafts', json=payload).json()
    changed = {**definition, 'title': 'Anderer Inhalt'}
    assert client.post('/studio/drafts', json={**payload, 'definition': changed}).status_code == 409
    user['sub'] = 'other-person'
    assert client.post('/studio/drafts', json=payload).status_code == 409
    assert store.get_draft(original['tenant_id'], original['id'])['definition'] == definition


@pytest.mark.integration
@pytest.mark.parametrize('mode', ['create', 'update'])
def test_sql_save_unknown_ack_is_recoverable(studio_db, monkeypatch, mode):
    client = _client()
    prefix = '/api/v1/studio/drafts'
    definition = propose_studio_draft('Artikel')
    payload = {'definition': definition, 'idempotency_key': str(uuid4())}
    path = prefix
    if mode == 'update':
        created = client.post(prefix, headers=_HEADERS_A, json=payload).json()
        path += '/'+created['id']
        payload = {'definition': {**definition, 'title': 'Aktualisierung'},
                   'idempotency_key': str(uuid4()), 'expected_revision': created['revision']}
    original_save = store._sql_save
    calls = 0
    def lose_ack(*args, **kwargs):
        nonlocal calls
        result = original_save(*args, **kwargs)
        calls += 1
        if calls == 1:
            raise OperationalError('lost acknowledgement', {}, RuntimeError('transport failure'))
        return result
    monkeypatch.setattr(store, '_sql_save', lose_ack)
    method = client.put if mode == 'update' else client.post
    assert method(path, headers=_HEADERS_A, json=payload).status_code == 503
    retry = method(path, headers=_HEADERS_A, json=payload)
    assert retry.status_code == 200, retry.text
    history = store.list_history(retry.json()['tenant_id'], retry.json()['id'])
    assert len(history) == (2 if mode == 'update' else 1)
    assert history[-1]['id'] == payload['idempotency_key']


@pytest.mark.integration
def test_sql_key_lock_serializes_independent_connections(require_db):
    from sqlalchemy import text
    from app.core.database import engine
    assert engine.url.database == 'valeo_probe' or 'test' in engine.url.database.lower()
    key = str(uuid4())
    with engine.connect() as first, engine.connect() as second:
        first.execute(text('SELECT pg_advisory_xact_lock(hashtextextended(:key, 0))'), {'key': key})
        assert second.execute(text('SELECT pg_try_advisory_xact_lock(hashtextextended(:key, 0))'), {'key': key}).scalar() is False
        first.rollback()
        assert second.execute(text('SELECT pg_try_advisory_xact_lock(hashtextextended(:key, 0))'), {'key': key}).scalar() is True
        second.rollback()
