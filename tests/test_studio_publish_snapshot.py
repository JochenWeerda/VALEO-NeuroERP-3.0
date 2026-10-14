from uuid import uuid4
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
            store.save_draft(record['tenant_id'], 'editor', definition, draft_id=record['id'])
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
    current = store.set_status(_TENANT_A, record['id'], 'new-editor', 'review', expected_snapshot=current)
    published = store.set_status(_TENANT_A, record['id'], 'reviewer', 'published_temp', expected_snapshot=current)
    assert published['definition'] == changed


@pytest.mark.parametrize('body', [None, {}, {'expected_revision': '0' * 64, 'idempotency_key': str(uuid4())}])
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
    updated = client.put('/studio/drafts/'+record['id'], json={'definition': changed, 'expected_revision': record['revision'], 'idempotency_key': str(uuid4())}).json()
    assert updated['revision'] != record['revision']
    user['sub'] = 'reviewer'
    rejected = client.post('/studio/drafts/'+record['id']+'/publish', json={'expected_revision': record['revision'], 'idempotency_key': str(uuid4())})
    assert rejected.status_code == 409
    fetched = client.post('/studio/drafts/'+record['id']+'/submit-review', json={'expected_revision': updated['revision'], 'idempotency_key': str(uuid4())}).json()
    assert fetched['definition'] == changed
    assert client.post('/studio/drafts/'+record['id']+'/publish', json={'expected_revision': fetched['revision'], 'idempotency_key': str(uuid4())}).status_code == 200


def test_review_is_required_and_edit_invalidates_it(probe):
    client, user = probe
    record = create(client)
    user['sub'] = 'reviewer'
    path = '/studio/drafts/'+record['id']
    assert client.post(path+'/publish', json={'expected_revision': record['revision'], 'idempotency_key': str(uuid4())}).status_code == 409
    reviewed = client.post(path+'/submit-review', json={'expected_revision': record['revision'], 'idempotency_key': str(uuid4())})
    assert reviewed.status_code == 200
    changed = deepcopy(record['definition'])
    changed['title'] = 'Nach Einreichung geaendert'
    edited = client.put(path, json={'definition': changed, 'expected_revision': reviewed.json()['revision'], 'idempotency_key': str(uuid4())}).json()
    assert edited['status'] == 'draft'
    assert client.post(path+'/publish', json={'expected_revision': edited['revision'], 'idempotency_key': str(uuid4())}).status_code == 409
    assert client.post(path+'/submit-review', json={'expected_revision': reviewed.json()['revision'], 'idempotency_key': str(uuid4())}).status_code == 409
    latest = client.post(path+'/submit-review', json={'expected_revision': edited['revision'], 'idempotency_key': str(uuid4())}).json()
    user['sub'] = 'third-person'
    published = client.post(path+'/publish', json={'expected_revision': latest['revision'], 'idempotency_key': str(uuid4())}).json()
    assert published['status'] == 'published_temp'
    assert client.post(path+'/submit-review', json={'expected_revision': published['revision'], 'idempotency_key': str(uuid4())}).status_code == 409
    assert client.put(path, json={'definition': changed, 'expected_revision': published['revision'], 'idempotency_key': str(uuid4())}).status_code == 409
    assert client.post(path+'/retire', json={'expected_revision': latest['revision'], 'idempotency_key': str(uuid4())}).status_code == 409
    retired = client.post(path+'/retire', json={'expected_revision': published['revision'], 'idempotency_key': str(uuid4())})
    assert retired.status_code == 200
    assert client.post(path+'/submit-review', json={'expected_revision': retired.json()['revision'], 'idempotency_key': str(uuid4())}).status_code == 409
    reopened = client.put(path, json={'definition': changed, 'expected_revision': retired.json()['revision'], 'idempotency_key': str(uuid4())})
    assert reopened.status_code == 200
    assert reopened.json()['status'] == 'draft'


@pytest.mark.integration
def test_sql_edit_invalidates_review(studio_db):
    from test_meridian_screen_studio_persistence import _TENANT_A
    from app.services.studio_propose import propose_studio_draft
    record = store.save_draft(_TENANT_A, 'editor', propose_studio_draft('Kunden'))
    reviewed = store.set_status(_TENANT_A, record['id'], 'editor', 'review', expected_snapshot=record)
    changed = deepcopy(reviewed['definition'])
    changed['title'] = 'Review entwertet'
    edited = store.save_draft(_TENANT_A, 'editor', changed, draft_id=record['id'])
    assert edited['status'] == 'draft'
    with pytest.raises(ValueError):
        store.set_status(_TENANT_A, record['id'], 'reviewer', 'published_temp', expected_snapshot=reviewed)
    with pytest.raises(ValueError, match='statuswechsel'):
        store.set_status(_TENANT_A, record['id'], 'reviewer', 'published_temp', expected_snapshot=edited)


def test_http_update_requires_current_display_revision(probe):
    client, _ = probe
    record = create(client)
    path = '/studio/drafts/'+record['id']
    changed = deepcopy(record['definition'])
    changed['title'] = 'Erster Bearbeiter'
    assert client.put(path, json={'definition': changed, 'idempotency_key': str(uuid4())}).status_code == 422
    first = client.put(path, json={'definition': changed, 'expected_revision': record['revision'], 'idempotency_key': str(uuid4())})
    assert first.status_code == 200
    second = deepcopy(changed)
    second['title'] = 'Veralteter zweiter Bearbeiter'
    assert client.put(path, json={'definition': second, 'expected_revision': record['revision'], 'idempotency_key': str(uuid4())}).status_code == 409
    assert client.get(path).json()['definition'] == changed


def test_create_does_not_overwrite_existing_screen(probe):
    client, _ = probe
    record = create(client)
    duplicate = deepcopy(record['definition'])
    duplicate['title'] = 'Unbeabsichtigte Ueberschreibung'
    assert client.post('/studio/drafts', json={'definition': duplicate, 'idempotency_key': str(uuid4())}).status_code == 409
    assert client.get('/studio/drafts/'+record['id']).json()['definition'] == record['definition']


@pytest.mark.integration
def test_sql_revision_conflict_preserves_first_writer(studio_db):
    from test_meridian_screen_studio_persistence import _TENANT_A
    from app.services.studio_propose import propose_studio_draft
    record = store.save_draft(_TENANT_A, 'editor', propose_studio_draft('Artikel'))
    changed = deepcopy(record['definition'])
    changed['title'] = 'Erster Stand'
    first = store.save_draft(_TENANT_A, 'first-editor', changed, draft_id=record['id'], expected_revision=record['revision'])
    with pytest.raises(ValueError, match='entwurf_seit_anzeige_geaendert'):
        store.save_draft(_TENANT_A, 'second-editor', record['definition'], draft_id=record['id'], expected_revision=record['revision'])
    with pytest.raises(ValueError, match='screen_id_bereits_vorhanden'):
        store.save_draft(_TENANT_A, 'second-editor', record['definition'])
    assert store.get_draft(_TENANT_A, record['id']) == first


def test_foreign_update_is_hidden_before_revision_comparison(probe):
    client, _ = probe
    from app.services.studio_propose import propose_studio_draft
    foreign = store.save_draft('foreign-tenant', 'foreign-editor', propose_studio_draft('Artikel'))
    response = client.put('/studio/drafts/'+foreign['id'], json={
        'definition': foreign['definition'], 'expected_revision': '0' * 64, 'idempotency_key': str(uuid4())})
    assert response.status_code == 404
    assert store.get_draft('foreign-tenant', foreign['id']) == foreign
