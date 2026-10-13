from studio_review_helper import publish_reviewed
"""Explicit HTTP identity doubles; no production authentication override."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.api.v1.endpoints import studio_drafts
from app.auth.deps import get_current_user
from app.services import studio_draft_store as store
from app.services.studio_propose import propose_studio_draft
from testgrenze import ersetze_mandant


@pytest.fixture
def probe():
    app = FastAPI()
    app.include_router(studio_drafts.router)
    ersetze_mandant(app, 'studio-test-tenant')
    user = {'sub': 'editor', 'roles': ['admin'], 'raw': {'identity_type': 'human'}}
    app.dependency_overrides[get_current_user] = lambda: user
    store.reset_studio_drafts()
    with TestClient(app) as client:
        yield client, user
    store.reset_studio_drafts()


def create(client):
    response = client.post('/studio/drafts', headers={'X-Actor-ID': 'forged-actor'},
                           json={'definition': propose_studio_draft('Kunden')})
    assert response.status_code == 200, response.text
    return response.json()


def test_creator_and_editor_ignore_caller_identity_headers(probe):
    client, user = probe
    record = create(client)
    assert record['created_by'] == record['updated_by'] == 'editor'
    user['sub'] = 'second-editor'
    updated = client.put('/studio/drafts/'+record['id'], headers={'X-Actor-ID': 'forged-editor'},
                         json={'definition': record['definition']})
    assert updated.status_code == 200, updated.text
    assert updated.json()['updated_by'] == 'second-editor'


def test_header_change_cannot_impersonate_an_independent_publisher(probe):
    client, _ = probe
    record = create(client)
    response = publish_reviewed(client, '/studio/drafts/'+record['id']+'/publish', headers={'X-Actor-ID': 'another-person'})
    assert response.status_code == 403
    assert store.get_draft('studio-test-tenant', record['id'])['status'] == 'draft'


@pytest.mark.parametrize('identity_type,roles', [('service', ['admin']), (None, ['admin']), ('human', []), ('human', ['FINANCE_ADMIN'])])
def test_publishing_requires_verified_human_and_existing_admin_role(probe, identity_type, roles):
    client, user = probe
    record = create(client)
    user.update(sub='reviewer', roles=roles, raw={'identity_type': identity_type})
    for operation in ('publish', 'retire'):
        response = client.post('/studio/drafts/'+record['id']+'/'+operation, headers={'X-Actor-ID': 'fake-admin', 'X-VALEO-Roles': 'admin', 'X-Identity-Type': 'human'})
        assert response.status_code == 403, response.text
    assert store.get_draft('studio-test-tenant', record['id'])['status'] == 'draft'


def test_review_submission_cannot_relabel_the_content_editor(probe):
    client, user = probe
    record = create(client)
    user['sub'] = 'other-submitter'
    review = client.post('/studio/drafts/'+record['id']+'/submit-review')
    assert review.status_code == 200
    assert review.json()['updated_by'] == 'editor'
    user['sub'] = 'editor'
    assert publish_reviewed(client, '/studio/drafts/'+record['id']+'/publish').status_code == 403
    user['sub'] = 'independent-reviewer'
    assert publish_reviewed(client, '/studio/drafts/'+record['id']+'/publish').status_code == 200


def test_missing_verified_subject_cannot_create_a_draft(probe):
    client, user = probe
    user['sub'] = ''
    response = client.post('/studio/drafts', json={'definition': propose_studio_draft('Kunden')})
    assert response.status_code == 403
    assert store.list_drafts('studio-test-tenant') == []


@pytest.mark.parametrize('path', ['/studio/catalog', '/studio/drafts'])
def test_no_unauthenticated_studio_reads(path):
    app = FastAPI()
    app.include_router(studio_drafts.router)
    with TestClient(app) as client:
        assert client.get(path).status_code in (401, 403)
