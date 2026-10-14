from uuid import uuid4
import pytest
from sqlalchemy.exc import OperationalError
from test_studio_token_identity import probe, create
from test_meridian_screen_studio_persistence import studio_db, _client, _HEADERS_A, _USER
from app.services import studio_draft_store as store
from app.services.studio_propose import propose_studio_draft


def body(revision):
    return {'expected_revision': revision, 'idempotency_key': str(uuid4())}


def test_each_status_repeats_without_duplicate_history(probe):
    client, user = probe
    record = create(client)
    path = '/studio/drafts/'+record['id']
    for index, action in enumerate(('submit-review', 'publish', 'retire')):
        user['sub'] = 'reviewer'
        request = body(record['revision'])
        first = client.post(path+'/'+action, json=request)
        assert first.status_code == 200, first.text
        second = client.post(path+'/'+action, json=request)
        assert second.status_code == 200, second.text
        assert second.json() == first.json()
        assert len(store.list_history(record['tenant_id'], record['id'])) == index + 2
        record = first.json()


def test_key_cannot_change_actor_action_or_revision(probe):
    client, user = probe
    record = create(client)
    path = '/studio/drafts/'+record['id']
    request = body(record['revision'])
    assert client.post(path+'/submit-review', json=request).status_code == 200
    user['sub'] = 'other-actor'
    assert client.post(path+'/submit-review', json=request).status_code == 409
    assert client.post(path+'/publish', json=request).status_code == 409
    user['sub'] = 'editor'
    assert client.post(path+'/submit-review', json={**request, 'expected_revision': '0' * 64}).status_code == 409
    assert len(store.list_history(record['tenant_id'], record['id'])) == 2


def test_revoked_publisher_cannot_replay(probe):
    client, user = probe
    record = create(client)
    path = '/studio/drafts/'+record['id']
    reviewed = client.post(path+'/submit-review', json=body(record['revision'])).json()
    user['sub'] = 'reviewer'
    request = body(reviewed['revision'])
    assert client.post(path+'/publish', json=request).status_code == 200
    user['roles'] = []
    assert client.post(path+'/publish', json=request).status_code == 403


@pytest.mark.integration
def test_sql_unknown_ack_replays_committed_history_once(studio_db, monkeypatch):
    client = _client()
    prefix = '/api/v1/studio/drafts'
    created = client.post(prefix, headers=_HEADERS_A, json={'definition': propose_studio_draft('Kunden'), 'idempotency_key': str(uuid4())}).json()
    path = prefix+'/'+created['id']
    reviewed = client.post(path+'/submit-review', headers=_HEADERS_A, json=body(created['revision'])).json()
    _USER['sub'] = 'berta'
    request = body(reviewed['revision'])
    original = store._sql_set_status
    def lose_ack(*args, **kwargs):
        original(*args, **kwargs)
        raise OperationalError('lost acknowledgement', {}, RuntimeError('transport failure'))
    monkeypatch.setattr(store, '_sql_set_status', lose_ack)
    lost = client.post(path+'/publish', headers=_HEADERS_A, json=request)
    assert lost.status_code == 503, lost.text
    retry = client.post(path+'/publish', headers=_HEADERS_A, json=request)
    assert retry.status_code == 200, retry.text
    assert retry.json()['status'] == 'published_temp'
    history = store.list_history(created['tenant_id'], created['id'])
    assert [entry['action'] for entry in history] == ['create', 'review', 'published_temp']
    assert history[-1]['id'] == request['idempotency_key']


@pytest.mark.integration
def test_sql_key_collision_rolls_back_status(studio_db, monkeypatch):
    from test_meridian_screen_studio_persistence import _TENANT_A
    original = store.save_draft(_TENANT_A, 'editor', propose_studio_draft('Kunden'))
    reviewed = store.set_status(_TENANT_A, original['id'], 'editor', 'review', expected_snapshot=original)
    other = store.save_draft(_TENANT_A, 'editor', propose_studio_draft('Artikel'))
    key = store.list_history(_TENANT_A, other['id'])[0]['id']
    # Force the cache miss that two different aggregate writers can observe.
    monkeypatch.setattr(store, '_sql_replay', lambda *args: None)
    with pytest.raises(ValueError, match='idempotenzschluessel_anderer_auftrag'):
        store.set_status(_TENANT_A, original['id'], 'reviewer', 'published_temp',
                         expected_snapshot=reviewed, idempotency_key=key, request_revision=reviewed['revision'])
    assert store.get_draft(_TENANT_A, original['id']) == reviewed
    assert len(store.list_history(_TENANT_A, original['id'])) == 2
