from studio_review_helper import publish_reviewed
"""Publication rejects changes made after the server validates a snapshot."""
from copy import deepcopy
import pytest
from test_studio_token_identity import probe, create
from test_meridian_screen_studio_persistence import studio_db
from app.api.v1.endpoints import studio_drafts
from app.services import studio_draft_store as store


@pytest.mark.parametrize('change', ['content', 'editor', 'status'])
def test_publish_rejects_intervening_changes(probe, monkeypatch, change):
    client, user = probe
    record = create(client)
    user['sub'] = 'reviewer'
    original_report = studio_drafts._report

    def report_then_change(definition):
        result = original_report(definition)
        if change == 'status':
            store.set_status(record['tenant_id'], record['id'], 'editor', 'review')
        else:
            edited = deepcopy(definition)
            if change == 'content':
                edited['title'] = 'Ungepruefter Inhalt'
            store.save_draft(record['tenant_id'], 'new-editor', edited, draft_id=record['id'])
        return result

    monkeypatch.setattr(studio_drafts, '_report', report_then_change)
    response = publish_reviewed(client, '/studio/drafts/'+record['id']+'/publish')
    assert response.status_code == 409, response.text
    assert store.get_draft(record['tenant_id'], record['id'])['status'] != 'published_temp'
    assert store.get_published_definition(record['tenant_id'], record['screen_id']) is None


def test_unchanged_snapshot_publishes(probe):
    client, user = probe
    record = create(client)
    user['sub'] = 'reviewer'
    response = publish_reviewed(client, '/studio/drafts/'+record['id']+'/publish')
    assert response.status_code == 200, response.text
    assert response.json()['definition'] == record['definition']


@pytest.mark.integration
def test_sql_rejects_stale_snapshot(studio_db):
    from test_meridian_screen_studio_persistence import _TENANT_A
    from app.services.studio_propose import propose_studio_draft
    record = store.save_draft(_TENANT_A, 'editor', propose_studio_draft('Artikel'))
    changed = deepcopy(record['definition'])
    changed['title'] = 'Neu bearbeitet'
    store.save_draft(_TENANT_A, 'new-editor', changed, draft_id=record['id'])
    with pytest.raises(ValueError, match='entwurf_seit_pruefung_geaendert'):
        store.set_status(_TENANT_A, record['id'], 'reviewer', 'published_temp', expected_snapshot=record)
    current = store.get_draft(_TENANT_A, record['id'])
    assert current['definition'] == changed
    assert current['status'] == 'draft'
    published = store.set_status(_TENANT_A, record['id'], 'reviewer', 'published_temp', expected_snapshot=current)
    assert published['definition'] == changed


@pytest.mark.parametrize('body', [None, {}, {'expected_revision': '0' * 64}])
def test_missing_or_wrong_display_revision_cannot_publish(probe, body):
    client, user = probe
    record = create(client)
    user['sub'] = 'reviewer'
    response = client.post('/studio/drafts/'+record['id']+'/publish', json=body)
    assert response.status_code == (409 if body and 'expected_revision' in body else 422)
    assert store.get_draft(record['tenant_id'], record['id'])['status'] == 'draft'


def test_display_revision_expires_after_edit(probe):
    client, user = probe
    record = create(client)
    changed = deepcopy(record['definition'])
    changed['title'] = 'Geaendert'
    updated = client.put('/studio/drafts/'+record['id'], json={'definition': changed}).json()
    assert updated['revision'] != record['revision']
    user['sub'] = 'reviewer'
    rejected = client.post('/studio/drafts/'+record['id']+'/publish', json={'expected_revision': record['revision']})
    assert rejected.status_code == 409
    fetched = client.get('/studio/drafts/'+record['id']).json()
    assert fetched['definition'] == changed
    assert client.post('/studio/drafts/'+record['id']+'/publish', json={'expected_revision': fetched['revision']}).status_code == 200
