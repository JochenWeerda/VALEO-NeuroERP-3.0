"""Every executable endpoint surface is curated, including embedded views."""
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from app.core.studio_release import profile_errors
from app.services.studio_validation import validate_studio_draft


@pytest.fixture(autouse=True)
def _enable_dev_token():
    yield


@pytest.fixture(scope='session', autouse=True)
def _seed_contract_test_tenants():
    yield


def candidate():
    return {'schemaVersion': 1, 'id': 'tenant/transport-check', 'domain': 'agrar', 'mode': 'list',
            'title': 'Transport check', 'adapter': {'type': 'native', 'sourceId': 'tenant/transport-check', 'temporary': True},
            'dataSources': [{'key': 'items', 'endpoint': '/api/v1/articles'}]}


def check(definition):
    return validate_studio_draft(definition, native_screen_ids=set())


def test_registered_reads_keep_working():
    assert check(candidate()) == []


@pytest.mark.parametrize('surface', ['summary', 'twin', 'calendar', 'tile_count', 'lookup'])
def test_free_read_urls_cannot_hide_outside_the_main_source_list(surface):
    definition = candidate()
    endpoint = 'https://untrusted.test/collect'
    if surface == 'summary':
        definition['summaryEndpoint'] = endpoint
    elif surface in {'twin', 'calendar'}:
        definition[surface] = {'endpoint': endpoint}
    elif surface == 'tile_count':
        definition['tiles'] = [{'key': 'items', 'targetScreenId': 'x', 'countEndpoint': endpoint}]
    else:
        definition['fields'] = [{'key': 'choice', 'type': 'lookup', 'optionsSource': {'endpoint': endpoint}}]
    assert any('datenquelle_nicht_im_katalog' in item for item in check(definition))


@pytest.mark.parametrize('field', ['reprojectEndpoint', 'icsTokenEndpoint', 'submitEndpoint'])
def test_unregistered_embedded_writes_are_rejected(field):
    definition = candidate()
    definition['calendar'] = {field: 'https://untrusted.test/write'}
    assert 'schreibender_transport_nicht_im_katalog' in check(definition)


def test_creation_cannot_borrow_a_read_endpoint_as_a_write_command():
    definition = candidate()
    definition['creation'] = {'endpoint': '/api/v1/articles'}
    assert 'erstellung_nicht_im_studio_katalog' in check(definition)


@pytest.mark.parametrize('field', ['rowRouteTemplate', 'targetRoute', 'activateRouteTemplate'])
@pytest.mark.parametrize('route', ['https://untrusted.test/path', '//untrusted.test/path', '/\\untrusted.test', 'javascript:alert(1)', '/\n/untrusted.test'])
def test_navigation_does_not_accept_external_schemes_or_ambiguous_paths(field, route):
    definition = candidate()
    definition[field] = route
    assert 'navigation_muss_lokaler_maskenpfad_sein' in check(definition)


def test_registered_local_navigation_is_preserved():
    definition = candidate()
    definition['rowRouteTemplate'] = '/belege/sales_invoice/{id}'
    assert check(definition) == []


@pytest.mark.parametrize('surface', ['creation', 'twin', 'calendar', 'sourceProposals'])
def test_grain_proof_does_not_certify_unmodeled_embedded_effects(surface):
    definition = candidate()
    definition[surface] = {'endpoint': '/api/v1/articles'}
    assert 'embedded_transports_not_covered' in profile_errors(definition)


def test_untrusted_embedded_url_is_rejected_by_the_real_save_route_before_storage(monkeypatch):
    from app.api.v1.endpoints import studio_drafts as api
    from app.auth.deps import get_current_user
    from app.core.tenant import get_tenant_id
    calls = []
    def forbidden(*args, **kwargs):
        calls.append(True)
        raise AssertionError('Untrusted definition must not reach persistence')
    monkeypatch.setattr(api, 'save_draft', forbidden)
    app = FastAPI()
    app.include_router(api.router)
    app.dependency_overrides[get_tenant_id] = lambda: 'own'
    app.dependency_overrides[get_current_user] = lambda: {'sub': 'verified-designer', 'roles': ['EINKAUF_BEARBEITEN']}
    definition = candidate()
    definition['twin'] = {'endpoint': 'https://untrusted.test/collect'}
    with TestClient(app) as client:
        result = client.post('/studio/drafts', json={'definition': definition, 'idempotency_key': str(uuid4())})
    assert result.status_code == 400, result.text
    assert calls == []
