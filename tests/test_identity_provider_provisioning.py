"""Provider configuration and additive role reconciliation without personal data."""
import copy
import json

import httpx
import pytest

from scripts.provision_identity_provider import ROOT, prepared_realm, reconcile_realm_roles


def test_preparation_is_idempotent_removes_examples_and_requires_pkce():
    source = {'realm': 'fixture', 'users': [{'username': 'sample-human'}],
              'clients': [{'clientId': 'sample-browser', 'publicClient': True,
                           'secret': 'sample-only-secret', 'directAccessGrantsEnabled': True}],
              'roles': {'realm': [{'name': 'custom_role', 'composite': True}]}}
    original = copy.deepcopy(source)
    result = prepared_realm(source)
    assert source == original
    assert prepared_realm(result) == result
    assert result['users'] == []
    client = result['clients'][0]
    assert 'secret' not in client
    assert client['directAccessGrantsEnabled'] is False
    assert client['implicitFlowEnabled'] is False
    assert client['attributes']['pkce.code.challenge.method'] == 'S256'
    assert result['revokeRefreshToken'] is True
    assert result['refreshTokenMaxReuse'] == 0
    catalog = json.loads((ROOT / 'config/keycloak/fachrollen.json').read_text())
    names = {role['name'] for role in result['roles']['realm']}
    assert {role['name'] for role in catalog['rollen']} <= names
    assert result['roles']['realm'][0] == original['roles']['realm'][0]


def test_existing_role_and_assignments_are_not_overwritten_missing_role_is_verified():
    calls = []
    existing = {'name': 'custom_role', 'composite': True}
    roles = [existing, {'name': 'required_role', 'description': 'fixture'}]

    def handler(request):
        calls.append((request.method, request.url.path))
        if request.method == 'POST':
            assert json.loads(request.content) == roles[1]
            return httpx.Response(201)
        if request.url.path.endswith('/custom_role'):
            return httpx.Response(200, json=existing)
        created = any(method == 'POST' for method, _ in calls)
        return httpx.Response(200, json=roles[1]) if created else httpx.Response(404)

    with httpx.Client(base_url='https://provider.invalid', transport=httpx.MockTransport(handler)) as client:
        reconcile_realm_roles(client, {}, 'fixture', roles)
        reconcile_realm_roles(client, {}, 'fixture', roles)
    assert [method for method, _ in calls].count('POST') == 1
    assert all(method in {'GET', 'POST'} for method, _ in calls)


@pytest.mark.parametrize('failure', ['inventory', 'create', 'persist'])
def test_role_reconciliation_fails_when_inventory_or_creation_is_not_confirmed(failure):
    reads = 0

    def handler(request):
        nonlocal reads
        if request.method == 'POST':
            return httpx.Response(403 if failure == 'create' else 201)
        reads += 1
        if reads == 1:
            return httpx.Response(503 if failure == 'inventory' else 404)
        return httpx.Response(200, json={'name': 'different_role'})

    with httpx.Client(base_url='https://provider.invalid', transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(RuntimeError):
            reconcile_realm_roles(client, {}, 'fixture', [{'name': 'required_role'}])
