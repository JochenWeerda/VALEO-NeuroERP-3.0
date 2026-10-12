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


def test_development_port_3001_has_exact_callback_and_no_wildcard():
    from scripts.provision_identity_provider import reconcile_callback_origins
    source=json.loads((ROOT/'config/keycloak/realm-export.json').read_text(encoding='utf-8'))
    desired=next(c for c in source['clients'] if c['clientId']=='valeo-neuro-erp-frontend')
    assert 'http://localhost:3001/auth/callback' in desired['redirectUris']
    assert 'http://localhost:3001/*' not in desired['redirectUris']
    assert 'http://localhost:3001' in desired['webOrigins']
    current={'redirectUris':['https://existing.invalid/auth/callback'],
             'webOrigins':['https://existing.invalid'],'secret':'synthetic-existing-secret'}
    reconcile_callback_origins(current,desired)
    assert 'http://localhost:3001/auth/callback' in current['redirectUris']
    assert 'https://existing.invalid/auth/callback' in current['redirectUris']
    assert current['secret']=='synthetic-existing-secret'
    expected=copy.deepcopy(current)
    reconcile_callback_origins(current,desired)
    assert current==expected


@pytest.mark.parametrize('realm_file',['realm-export.json','realm-staging.json'])
def test_every_declared_oidc_scope_exists_and_identity_kind_is_mapped(realm_file):
    realm=prepared_realm(json.loads((ROOT/'config/keycloak'/realm_file).read_text(encoding='utf-8')))
    known={scope['name'] for scope in realm['clientScopes']}|{'offline_access'}
    assert {'profile','email','roles','web-origins'}<=known
    for client in realm['clients']:
        assert set(client.get('defaultClientScopes',[])+client.get('optionalClientScopes',[]))<=known
        mapper=next(m for m in client['protocolMappers'] if m['name']=='erp-identity-type')
        assert mapper['config']['user.attribute']=='identity_type'
        assert mapper['config']['claim.name']=='identity_type'
        assert mapper['protocolMapper']=='oidc-usermodel-attribute-mapper'
        assert 'claim.value' not in mapper['config']  # No fabricated human/service claim.


def test_scope_creation_and_assignment_are_additive_verified_and_repeatable():
    from scripts.provision_identity_provider import reconcile_client_scopes, assign_declared_scopes, standard_login_scopes
    scopes={'roles':{'id':'roles-fixture','name':'roles','protocolMappers':[{'name':'preserved-custom'}]}}
    original=copy.deepcopy(scopes['roles'])
    assigned={'roles'}
    writes=[]
    def handler(request):
        path=request.url.path
        if path.endswith('/client-scopes'):
            if request.method=='POST':
                record=json.loads(request.content);scopes[record['name']]={**record,'id':record['name']+'-fixture'}
                writes.append(('create',record['name']))
                return httpx.Response(201)
            return httpx.Response(200,json=list(scopes.values()))
        if path.endswith('/default-client-scopes'):
            return httpx.Response(200,json=[scopes[name] for name in assigned])
        if request.method=='PUT':
            name=path.rsplit('/',1)[-1].removesuffix('-fixture');assigned.add(name);writes.append(('assign',name))
            return httpx.Response(204)
        raise AssertionError((request.method,path))
    with httpx.Client(base_url='https://provider.invalid',transport=httpx.MockTransport(handler)) as client:
        for _ in range(2):
            ids=reconcile_client_scopes(client,{},'fixture',standard_login_scopes())
            assign_declared_scopes(client,{},'fixture','browser',{'defaultClientScopes':['roles','profile','email']},ids)
    assert scopes['roles']==original
    assert assigned=={'roles','profile','email'}
    assert sorted(writes)==sorted([('create','profile'),('create','email'),('create','web-origins'),('assign','profile'),('assign','email')])
