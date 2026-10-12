"""Prepare the existing Keycloak realm; never activate example users/passwords.

Admin credentials are read from named environment variables. This command does
not print credentials/tokens, reset realms or start containers. Personal user
provisioning only updates the explicitly selected account's owned attributes.
"""
from __future__ import annotations
import argparse
import copy
import json
import os
import secrets
from pathlib import Path
import httpx

ROOT = Path(__file__).resolve().parents[1]


def standard_login_scopes() -> list[dict]:
    """Explicit standard scopes: imported realms do not manufacture missing ones."""
    def property_mapper(name,attribute,claim,json_type='String'):
        return {'name':name,'protocol':'openid-connect','protocolMapper':'oidc-usermodel-property-mapper',
            'consentRequired':False,'config':{'user.attribute':attribute,'claim.name':claim,
            'jsonType.label':json_type,'id.token.claim':'true','access.token.claim':'true','userinfo.token.claim':'true'}}
    scopes=[]
    for name,mappers in [
        ('profile',[property_mapper('username','username','preferred_username'),
                    property_mapper('given name','firstName','given_name'),
                    property_mapper('family name','lastName','family_name')]),
        ('email',[property_mapper('email','email','email'),
                  property_mapper('email verified','emailVerified','email_verified','boolean')]),
        ('roles',[{'name':'realm roles','protocol':'openid-connect',
            'protocolMapper':'oidc-usermodel-realm-role-mapper','consentRequired':False,
            'config':{'claim.name':'roles','jsonType.label':'String','multivalued':'true',
                      'access.token.claim':'true','id.token.claim':'true'}},
            {'name':'tenant_id','protocol':'openid-connect','protocolMapper':'oidc-usermodel-attribute-mapper',
             'consentRequired':False,'config':{'claim.name':'tenant_id','user.attribute':'tenant_id',
             'jsonType.label':'String','access.token.claim':'true','id.token.claim':'true'}}]),
        ('web-origins',[{'name':'allowed web origins','protocol':'openid-connect',
            'protocolMapper':'oidc-allowed-origins-mapper','consentRequired':False,
            'config':{'access.token.claim':'true','id.token.claim':'false'}}])]:
        scopes.append({'name':name,'protocol':'openid-connect',
            'attributes':{'include.in.token.scope':'true','display.on.consent.screen':'true'},
            'protocolMappers':mappers})
    return scopes


def prepared_realm(source: dict) -> dict:
    realm = copy.deepcopy(source)
    realm['users'] = []
    scopes=realm.setdefault('clientScopes',[])
    existing_scopes={scope['name'] for scope in scopes}
    scopes.extend(scope for scope in standard_login_scopes() if scope['name'] not in existing_scopes)
    catalog = json.loads((ROOT / 'config/keycloak/fachrollen.json').read_text(encoding='utf-8'))
    roles = realm.setdefault('roles', {}).setdefault('realm', [])
    known = {role['name'] for role in roles}
    desired = [{'name': role['name'], 'description': role['beschreibung']}
               for role in catalog['rollen']]
    desired.append({'name': 'manager', 'description': 'Explicit management role; never assigned by default'})
    roles.extend(role for role in desired if role['name'] not in known)
    realm.update(accessTokenLifespan=300, ssoSessionIdleTimeout=900,
                 ssoSessionMaxLifespan=28800, revokeRefreshToken=True, refreshTokenMaxReuse=0)
    available_scopes={scope['name'] for scope in scopes}|{'offline_access'}
    for client in realm.get('clients', []):
        # Remove unused imported optional references that never had a scope.
        if 'optionalClientScopes' in client:
            client['optionalClientScopes']=[name for name in client['optionalClientScopes'] if name in available_scopes]
        client.pop('secret', None)
        client['directAccessGrantsEnabled'] = False
        client['implicitFlowEnabled'] = False
        if client.get('publicClient'):
            client.setdefault('attributes', {})['pkce.code.challenge.method'] = 'S256'
        mappers=client.setdefault('protocolMappers', [])
        mappers[:] = [m for m in mappers if m.get('name') != 'erp-api-audience']
        mappers.append({'name':'erp-api-audience','protocol':'openid-connect',
            'protocolMapper':'oidc-audience-mapper','consentRequired':False,
            'config':{'included.client.audience':'valeo-neuro-erp-backend',
                      'access.token.claim':'true','id.token.claim':'false'}})
        mappers[:] = [m for m in mappers if m.get('name') != 'erp-identity-type']
        mappers.append({'name':'erp-identity-type','protocol':'openid-connect',
            'protocolMapper':'oidc-usermodel-attribute-mapper','consentRequired':False,
            'config':{'user.attribute':'identity_type','claim.name':'identity_type','jsonType.label':'String',
                      'access.token.claim':'true','id.token.claim':'true'}})
        mappers[:] = [m for m in mappers if m.get('name') != 'erp-permissions']
        mappers.append({'name':'erp-permissions','protocol':'openid-connect',
            'protocolMapper':'oidc-usermodel-attribute-mapper','consentRequired':False,
            'config':{'user.attribute':'erp_scopes','claim.name':'erp_scopes','jsonType.label':'String',
                      'multivalued':'true','access.token.claim':'true','id.token.claim':'true'}})
    return realm


def reconcile_client_scopes(client: httpx.Client, headers: dict, realm: str, desired: list[dict]) -> dict[str,str]:
    route=f'/admin/realms/{realm}/client-scopes'
    inventory=client.get(route,headers=headers)
    inventory.raise_for_status()
    existing={scope['name']:scope for scope in inventory.json()}
    for scope in desired:
        if scope['name'] in existing:
            continue  # Preserve existing scope policy and unrelated mappers.
        response=client.post(route,headers=headers,json=scope)
        if response.status_code!=201: raise RuntimeError('Declared OIDC scope creation failed')
    verified=client.get(route,headers=headers);verified.raise_for_status()
    ids={scope['name']:scope['id'] for scope in verified.json()}
    if not {scope['name'] for scope in desired}<=ids.keys():
        raise RuntimeError('Declared OIDC scopes not persisted')
    return ids


def assign_declared_scopes(client: httpx.Client, headers: dict, realm: str, identifier: str,
                           desired: dict, scopes: dict[str,str]) -> None:
    for field,kind in [('defaultClientScopes','default-client-scopes'),('optionalClientScopes','optional-client-scopes')]:
        if not desired.get(field): continue
        route=f'/admin/realms/{realm}/clients/{identifier}/{kind}'
        assigned=client.get(route,headers=headers);assigned.raise_for_status()
        current={scope['name'] for scope in assigned.json()}
        for name in desired.get(field,[]):
            if name in current: continue
            if name not in scopes: raise RuntimeError('Client references a missing OIDC scope')
            response=client.put(route+'/'+scopes[name],headers=headers)
            if response.status_code!=204: raise RuntimeError('OIDC client scope assignment failed')
        verified=client.get(route,headers=headers);verified.raise_for_status()
        if not set(desired.get(field,[])) <= {scope['name'] for scope in verified.json()}:
            raise RuntimeError('OIDC client scope assignment not persisted')


def reconcile_callback_origins(current: dict, desired: dict) -> None:
    """Only declared callback origins, with existing deployment addresses retained."""
    for field in ('redirectUris','webOrigins'):
        current[field] = sorted(set(current.get(field,[])) | set(desired.get(field,[])))


def provision(client: httpx.Client, username: str, password: str, source: dict, profile: dict) -> dict:
    login=client.post('/realms/master/protocol/openid-connect/token',data={
        'grant_type':'password','client_id':'admin-cli','username':username,'password':password})
    if login.status_code != 200:
        raise RuntimeError(f'Provider administrator authentication failed ({login.status_code})')
    headers={'Authorization':'Bearer '+login.json()['access_token']}
    realm=prepared_realm(source); name=realm['realm']
    exists=client.get(f'/admin/realms/{name}',headers=headers)
    created=False
    if exists.status_code == 404:
        response=client.post('/admin/realms',headers=headers,json=realm)
        if response.status_code != 201:
            raise RuntimeError(f'Realm preparation failed ({response.status_code})')
        created=True
    elif exists.status_code != 200:
        raise RuntimeError(f'Realm inventory failed ({exists.status_code})')
    reconcile_realm_roles(client, headers, name, realm['roles']['realm'])
    scope_ids=reconcile_client_scopes(client,headers,name,realm['clientScopes'])
    for desired in realm.get('clients',[]):
        found=client.get(f'/admin/realms/{name}/clients',headers=headers,params={'clientId':desired['clientId']})
        found.raise_for_status()
        if len(found.json()) != 1:
            raise RuntimeError('Configured ERP client missing or ambiguous')
        client_id=found.json()[0]['id']
        current=client.get(f'/admin/realms/{name}/clients/{client_id}',headers=headers).json()
        current['directAccessGrantsEnabled'] = False
        current['implicitFlowEnabled'] = False
        if current.get('publicClient'):
            current.setdefault('attributes', {})['pkce.code.challenge.method'] = 'S256'
        reconcile_callback_origins(current,desired)
        owned_names={'erp-api-audience','erp-permissions','erp-identity-type'}
        mappers=[m for m in current.get('protocolMappers',[]) if m.get('name') not in owned_names]
        mappers.extend(m for m in desired.get('protocolMappers',[]) if m.get('name') in owned_names)
        current['protocolMappers']=mappers
        response=client.put(f'/admin/realms/{name}/clients/{client_id}',headers=headers,json=current)
        if response.status_code != 204:
            raise RuntimeError('ERP client mapper integration failed')
        assign_declared_scopes(client,headers,name,client_id,desired,scope_ids)
    representation=client.get(f'/admin/realms/{name}',headers=headers).json()
    for setting in ('accessTokenLifespan', 'ssoSessionIdleTimeout', 'ssoSessionMaxLifespan',
                    'revokeRefreshToken', 'refreshTokenMaxReuse'):
        representation[setting] = realm[setting]
    representation.setdefault('attributes',{})['userProfileEnabled']='true'
    response=client.put(f'/admin/realms/{name}',headers=headers,json=representation)
    if response.status_code != 204:
        raise RuntimeError(f'Managed user profile activation failed ({response.status_code})')
    # Preserve all existing managed profile fields while restricting sensitive attributes.
    existing=client.get(f'/admin/realms/{name}/users/profile',headers=headers)
    if existing.status_code != 200:
        raise RuntimeError(f'User profile API unavailable ({existing.status_code})')
    merged=existing.json()
    protected={'tenant_id','mandanten_id','identity_type','erp_scopes'}
    # Keycloak 22 exposes the earlier UPConfig schema; enable its managed profile.
    # Newer versions additionally support unmanagedAttributePolicy.
    if 'unmanagedAttributePolicy' in merged:
        merged['unmanagedAttributePolicy']='DISABLED'
    attrs=[a for a in merged.get('attributes',[]) if a.get('name') not in protected]
    attrs.extend(a for a in profile['attributes'] if a['name'] in protected)
    merged['attributes']=attrs
    response=client.put(f'/admin/realms/{name}/users/profile',headers=headers,json=merged)
    if response.status_code != 200:
        # This API contains profile validation diagnostics, never credentials.
        diagnostics=response.json().get('errors', response.json().get('errorMessage', 'profile_validation_failed'))
        raise RuntimeError(f'Administrative attribute protection failed ({response.status_code}): {diagnostics}')
    checked=client.get(f'/admin/realms/{name}/users/profile',headers=headers)
    checked.raise_for_status()
    tenants=[a for a in checked.json().get('attributes',[]) if a.get('name')=='tenant_id']
    if len(tenants)!=1 or tenants[0].get('permissions',{}).get('edit') != ['admin']:
        raise RuntimeError('Provider tenant attribute protection did not persist')
    return {'realm':name,'created':created,'tenant_edit':'admin_only','example_users_created':0}


def reconcile_realm_roles(client: httpx.Client, headers: dict, realm: str, roles: list[dict]) -> None:
    """Add missing declared roles; preserve assignments, composites and other roles."""
    for role in roles:
        response = client.get(f"/admin/realms/{realm}/roles/{role['name']}", headers=headers)
        if response.status_code == 200:
            continue
        if response.status_code != 404:
            raise RuntimeError(f'Realm role inventory failed ({response.status_code})')
        created = client.post(f'/admin/realms/{realm}/roles', headers=headers, json=role)
        if created.status_code != 201:
            raise RuntimeError(f'Realm role provisioning failed ({created.status_code})')
        checked = client.get(f"/admin/realms/{realm}/roles/{role['name']}", headers=headers)
        if checked.status_code != 200 or checked.json().get('name') != role['name']:
            raise RuntimeError('Realm role provisioning did not persist')


def enroll_person(client: httpx.Client, username: str, password: str, realm: str, private_file: Path) -> dict:
    """Explicit personal provisioning from a private file outside this checkout."""
    private_file=private_file.resolve()
    if private_file.is_relative_to(ROOT):
        raise ValueError('Personal provisioning input must be outside the repository')
    person=json.loads(private_file.read_text(encoding='utf-8'))
    login=client.post('/realms/master/protocol/openid-connect/token',data={
        'grant_type':'password','client_id':'admin-cli','username':username,'password':password})
    login.raise_for_status()
    headers={'Authorization':'Bearer '+login.json()['access_token']}
    existing=client.get(f'/admin/realms/{realm}/users',headers=headers,
                        params={'username':person['username'],'exact':'true'})
    existing.raise_for_status()
    if existing.json():
        record=existing.json()[0]
        if str(record.get('email','')).lower() != str(person['email']).lower():
            raise RuntimeError('Personal account definition conflicts with existing identity')
        # This operation only provisions the explicitly requested first administrator.
        attributes=dict(record.get('attributes',{}))
        attributes.update(tenant_id=[person['tenant_id']],identity_type=['human'],erp_scopes=['admin:all'])
        update=client.put(f"/admin/realms/{realm}/users/{record['id']}",headers=headers,json={'attributes':attributes})
        if update.status_code != 204:
            raise RuntimeError('Explicit administrator scope provisioning failed')
        return {'personal_user_created':False,'existing_account_preserved':True}
    profile=client.get(f'/admin/realms/{realm}/users/profile',headers=headers).json()
    tenant_fields=[a for a in profile.get('attributes',[]) if a.get('name')=='tenant_id']
    if len(tenant_fields)!=1 or tenant_fields[0].get('permissions',{}).get('edit') != ['admin']:
        raise RuntimeError('Refusing user activation before administrative tenant protection')
    temporary=secrets.token_urlsafe(32)
    payload={'username':person['username'],'email':person['email'],'enabled':True,
        'emailVerified':False,'attributes':{'tenant_id':[person['tenant_id']],'identity_type':['human'],'erp_scopes':['admin:all']},
        'requiredActions':['UPDATE_PASSWORD','CONFIGURE_TOTP'],
        'credentials':[{'type':'password','temporary':True,'value':temporary}]}
    response=client.post(f'/admin/realms/{realm}/users',headers=headers,json=payload)
    if response.status_code!=201:
        raise RuntimeError(f'Personal user preparation failed ({response.status_code})')
    user_id=response.headers['location'].rstrip('/').split('/')[-1]
    role=client.get(f'/admin/realms/{realm}/roles/admin',headers=headers)
    role.raise_for_status()
    response=client.post(f'/admin/realms/{realm}/users/{user_id}/role-mappings/realm',
                         headers=headers,json=[role.json()])
    if response.status_code!=204:
        # Fail closed if role assignment cannot complete.
        client.put(f'/admin/realms/{realm}/users/{user_id}',headers=headers,json={'enabled':False})
        raise RuntimeError('Personal administrator role assignment failed; account disabled')
    person['temporary_password']=temporary
    private_file.write_text(json.dumps(person,ensure_ascii=False,indent=2),encoding='utf-8')
    return {'personal_user_created':True,'first_login_password_change':True,'mfa_setup_required':True}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url',default='http://127.0.0.1:8080')
    parser.add_argument('--realm-file',default=str(ROOT/'config/keycloak/realm-export.json'))
    parser.add_argument('--personal-file', help='Private personal account definition outside the repository')
    args=parser.parse_args()
    username=os.environ.get('VALEO_IDP_ADMIN_USERNAME')
    password=os.environ.get('VALEO_IDP_ADMIN_PASSWORD')
    if not username or not password:
        raise SystemExit('Set VALEO_IDP_ADMIN_USERNAME and VALEO_IDP_ADMIN_PASSWORD; never pass passwords as CLI arguments')
    with httpx.Client(base_url=args.url,timeout=20) as client:
        result=provision(client,username,password,json.loads(Path(args.realm_file).read_text(encoding='utf-8')),
                         json.loads((ROOT/'config/keycloak/user-profile.json').read_text(encoding='utf-8')))
        if args.personal_file:
            result.update(enroll_person(client,username,password,result['realm'],Path(args.personal_file)))
    print(json.dumps(result))


if __name__=='__main__':
    main()
