from copy import deepcopy
import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from test_meridian_screen_studio_persistence import studio_db, _TENANT_A
from test_studio_token_identity import probe, create
from studio_review_helper import publish_reviewed
from app.services import studio_draft_store as store
from app.services.studio_propose import propose_studio_draft


def test_http_history_preserves_reviewed_content_and_identity(probe):
    client, user = probe
    record = create(client)
    user['sub'] = 'reviewer'
    published = publish_reviewed(client, '/studio/drafts/'+record['id']+'/publish')
    assert published.status_code == 200
    history = client.get('/studio/drafts/'+record['id']+'/history').json()['history']
    assert [e['action'] for e in history] == ['create', 'review', 'migration_plan', 'simulation', 'published_temp']
    assert history[0]['actor'] == 'editor'
    assert history[-1]['actor'] == 'reviewer'
    assert history[-1]['snapshot']['definition'] == record['definition']
    assert history[1]['previous_revision'] == history[0]['revision']
    assert history[2]['previous_revision'] == history[1]['revision']
    assert store.list_history('other-tenant', record['id']) == []
    page = client.get('/studio/drafts/'+record['id']+'/history?limit=1').json()
    assert page['history'][0]['id'] == history[0]['id']
    assert page['has_more'] and page['next_skip'] == 1
    assert client.get('/studio/drafts/'+record['id']+'/history?skip=-1').status_code == 422


@pytest.mark.integration
def test_sql_history_cannot_be_updated_or_deleted(studio_db):
    record = store.save_draft(_TENANT_A, 'editor', propose_studio_draft('Kunden'))
    entry = store.list_history(_TENANT_A, record['id'])[0]
    for sql in ("UPDATE domain_shared.screen_definition_history SET actor='forged' WHERE id=:id",
                'DELETE FROM domain_shared.screen_definition_history WHERE id=:id',
                'TRUNCATE domain_shared.screen_definition_history'):
        session = store._sql_session()
        try:
            with pytest.raises(DBAPIError, match='append-only'):
                session.execute(text(sql), {'id': entry['id']})
            session.rollback()
        finally:
            session.close()
    assert store.list_history(_TENANT_A, record['id'])[0] == entry
    assert store.list_history('foreign', record['id']) == []


@pytest.mark.integration
def test_sql_history_failure_rolls_back_status(studio_db, monkeypatch):
    record = store.save_draft(_TENANT_A, 'editor', propose_studio_draft('Artikel'))
    def fail(*args, **kwargs):
        raise RuntimeError('audit insertion failed')
    monkeypatch.setattr(store, '_append_sql_history', fail)
    with pytest.raises(RuntimeError, match='audit insertion failed'):
        store.set_status(_TENANT_A, record['id'], 'editor', 'review', expected_snapshot=record)
    assert store.get_draft(_TENANT_A, record['id']) == record
    assert len(store.list_history(_TENANT_A, record['id'])) == 1


@pytest.mark.integration
def test_sql_history_preserves_previous_definition(studio_db):
    record = store.save_draft(_TENANT_A, 'editor', propose_studio_draft('Kunden'))
    changed = deepcopy(record['definition'])
    changed['title'] = 'Neue Fassung'
    store.save_draft(_TENANT_A, 'next-editor', changed, draft_id=record['id'], expected_revision=record['revision'])
    history = store.list_history(_TENANT_A, record['id'])
    assert history[0]['snapshot']['definition'] == record['definition']
    assert history[1]['snapshot']['definition'] == changed
    assert history[1]['previous_revision'] == record['revision']
