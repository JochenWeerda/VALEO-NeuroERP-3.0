"""Three adapters, real signed HTTP/SQL effects; synthetic deployment, not Studio publication."""
import copy
import io
import json
from uuid import uuid4

import httpx
import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations

from app.core.tenant_binding import install_tenant_bindings
from app.core.screen_definitions import SCREEN_DEFINITION_BUILDERS
from app.services.studio_entity_compiler import compile_entity
from app.services.studio_entity_router import build_router
from app.services.studio_entity_commands import tables
from app.services import mcp_mask_actions
from app.api.v1.endpoints import mask_screen_definition, mcp_tool_registry
from app.infrastructure.eventbus.outbox import OutboxEvent
from main import BearerAuthMiddleware
from valeo_cli import cli
from test_studio_entity_generation import specification, command, values
from test_gdpr_subject_boundary import subject_data, keys, probe  # noqa: F401

pytestmark = [pytest.mark.integration, pytest.mark.needs_live_db]


def test_signed_http_cli_mcp_share_versioned_sql_command(subject_data, monkeypatch):
    client, db, provider, tenant, foreign, *_ = subject_data
    spec = specification()
    bundle = compile_entity(spec)
    namespace = {}
    exec(bundle['files']['migration.py'], namespace)
    with Operations.context(MigrationContext.configure(db.connection())):
        namespace['upgrade']()
    client.app.include_router(build_router(spec, writes_enabled=True, agent_roles=('CRM_BEARBEITEN',)), prefix='/api/v1/studio')
    client.app.include_router(mask_screen_definition.router, prefix='/api/v1')
    client.app.include_router(mcp_tool_registry.router, prefix='/api/v1')
    install_tenant_bindings(client.app, public_paths=BearerAuthMiddleware.PUBLIC_PATHS)
    definition = json.loads(bundle['files']['screen.json'])
    # Explicit synthetic deployment only. Never change the generated default-deny bundle.
    for action in mcp_mask_actions.iter_actions(definition):
        action['disabled'] = False
        action['forbiddenForAgents'] = False
    screen = definition['id']
    monkeypatch.setitem(SCREEN_DEFINITION_BUILDERS, screen, lambda: copy.deepcopy(definition))
    url = '/api/v1/studio/entities/' + spec.name
    def token(actor, kind='human', *, role=True, scope=True, tid=tenant):
        return provider.token(tid, changes={'sub':actor,'identity_type':kind,
            'roles':['CRM_BEARBEITEN'] if role else [],'scope':'masks:write' if scope else ''})
    human = token('synthetic-channel-editor')
    headers = {'Authorization':'Bearer '+human}
    body = command(values())
    flat = {k:v for k,v in body.items() if k != 'data'} | values()
    created = client.post(url+'/actions/create', headers=headers, json=flat)
    assert created.status_code == 200, created.text
    row = created.json()['result']
    assert row['tenant_id'] == tenant and row['version'] == 1
    monkeypatch.setenv('VALEO_ACCESS_TOKEN', human)
    lines = []
    args = ['ausfuehren',screen,spec.name+'_create','--daten','-','--grund',body['_auditReason'],
            '--idempotenz',body['_idempotencyKey'],'--ja','--json']
    assert cli.main(args,http=client,out=lines.append,stdin=io.StringIO(json.dumps(values()))) == 0, lines
    assert json.loads(lines[-1]) == created.json()

    # Transport only: loop the adapter back to the real signed HTTP route, not a fake business response.
    calls = []
    def forward(request):
        calls.append(request)
        response = client.request(request.method, request.url.path, content=request.content,
                                  headers=dict(request.headers))
        return httpx.Response(response.status_code, content=response.content,
                              headers={'content-type':'application/json'}, request=request)
    original = mcp_mask_actions.execute
    monkeypatch.setattr(mcp_mask_actions,'execute',lambda req,tid,authorization:
        original(req,tid,authorization,transport=httpx.MockTransport(forward)))
    update_key = str(uuid4())
    request = {'tool_name':'mask.action.execute','mode':'execute','idempotency_key':update_key,
        'parameters':{'screen_id':screen,'action':spec.name+'_update','entity_id':row['id'],
            'audit_reason':'Synthetische Kanalabnahme','input':{**values(),'quantity':'2.5000','expected_version':1}}}
    agent = token('synthetic-channel-agent','agent')
    def call(bearer, payload=request):
        return client.post('/api/v1/mcp/tools/call',headers={'Authorization':'Bearer '+bearer},json=payload)
    before = len(calls)
    assert call(token('synthetic-channel-agent','agent',scope=False)).status_code == 403
    assert len(calls) == before  # Scope denied by the real MCP engine before forwarding.
    assert call(token('synthetic-channel-agent','agent',role=False)).status_code == 403
    updated = call(agent)
    assert updated.status_code == 200, updated.text
    assert updated.json()['result']['result']['version'] == 2
    assert call(agent).json() == updated.json()
    assert call(token('synthetic-channel-agent','agent',tid=foreign)).status_code == 404
    stale = copy.deepcopy(request); stale['idempotency_key'] = str(uuid4())
    assert call(agent,stale).status_code == 409
    forged = copy.deepcopy(request); forged['parameters']['input']['tenant_id'] = foreign
    before_forgery = len(calls)
    assert call(agent,forged).status_code == 403
    assert len(calls) == before_forgery  # Central tenant boundary rejects before the adapter.
    # Same idempotency key belongs to its verified actor, never a cross-identity replay.
    assert call(token('synthetic-other-agent','agent')).status_code == 409
    rows, events = tables(spec)
    history = db.execute(sa.select(events).order_by(events.c.recorded_at)).mappings().all()
    assert len(history) == 2
    assert [e['actor'] for e in history] == ['synthetic-channel-editor','synthetic-channel-agent']
    assert [e['audit']['actor_kind'] for e in history] == ['human','agent']
    assert db.scalar(sa.select(sa.func.count()).select_from(rows)) == 1
    assert db.query(OutboxEvent).filter_by(tenant_id=tenant,event_type='StudioEntityChanged').count() == 2
    assert all('x-tenant-id' not in req.headers for req in calls)
    assert bundle['enabled'] is False  # No live registration/release implied by this contract test.


def test_registered_nullable_evolution_keeps_existing_rows_and_rejects_stale_deployment(subject_data, monkeypatch, tmp_path):
    from app.services.studio_entity_contracts import EntityExtensionIn, contract_hash
    from app.services.studio_entity_evolution import compile_extension
    from app.services import studio_validation
    from app.api.v1.endpoints import studio_drafts
    from sqlalchemy.exc import DBAPIError
    client, db, provider, tenant, _, *_ = subject_data
    spec = specification(); bundle = compile_entity(spec); namespace = {}
    exec(bundle['files']['migration.py'], namespace)
    with Operations.context(MigrationContext.configure(db.connection())):
        namespace['upgrade']()
    client.app.include_router(build_router(spec, writes_enabled=True), prefix='/api/v1/studio')
    client.app.include_router(studio_drafts.router, prefix='/api/v1')
    install_tenant_bindings(client.app, public_paths=BearerAuthMiddleware.PUBLIC_PATHS)
    token = provider.token(tenant,changes={'sub':'synthetic-evolution','roles':['CRM_BEARBEITEN','EINKAUF_BEARBEITEN'],'identity_type':'human'})
    headers = {'Authorization':'Bearer '+token}
    path = '/api/v1/studio/entities/'+spec.name
    original = client.post(path+'/actions/create',headers=headers,json=command(values()))
    assert original.status_code == 200, original.text
    row = original.json()['result']
    config = tmp_path/'catalog.yaml'
    config.write_text(json.dumps({'generated_entities':[{'spec':spec.model_dump(),'writes_enabled':True,'agent_roles':['CRM_BEARBEITEN']}]}),encoding='utf-8')
    monkeypatch.setattr(studio_validation,'_CONFIG_PATH',config)
    body = {'name':spec.name,'expected_contract_hash':contract_hash(spec),
            'columns':[{'name':'lieferhinweis','type':'text','nullable':True}]}
    response = client.post('/api/v1/studio/entity-extension-bundle',headers=headers,json=body)
    assert response.status_code == 200, response.text
    report = response.json(); assert report == compile_extension(EntityExtensionIn.model_validate(body))
    assert report['base_contract_hash'] == contract_hash(spec)
    assert report['bundle']['enabled'] is False
    registration = json.loads(report['bundle']['files']['registration.json'])['generated_entities'][0]
    assert registration['writes_enabled'] is False and registration['agent_roles'] == []
    # Authoring is read-only: existing row/schema remain exactly unchanged.
    assert client.get(path+'/'+row['id'],headers=headers).json() == row
    source = tmp_path/'extension.json';source.write_text(json.dumps(body),encoding='utf-8')
    monkeypatch.setenv('VALEO_ACCESS_TOKEN',token);lines=[]
    assert cli.main(['studio','entitaet-erweitern',str(source)],http=client,out=lines.append) == 0
    assert json.loads(lines[-1]) == report
    evolution = {}; exec(report['bundle']['files']['migration.py'],evolution)
    with Operations.context(MigrationContext.configure(db.connection())):
        evolution['upgrade']()
    from app.services.studio_entity_contracts import EntitySpec
    evolved = EntitySpec.model_validate(report['bundle']['spec'])
    newrows,_ = tables(evolved)
    existing = db.execute(sa.select(newrows)).mappings().one()
    assert existing['lieferhinweis'] is None and existing['version'] == 1
    assert str(existing['id']) == row['id']
    # Old runtime cannot operate against the changed schema marker.
    assert client.get(path+'/'+row['id'],headers=headers).status_code == 409
    client.app.include_router(build_router(evolved,writes_enabled=True),prefix='/api/v1/studio-next')
    install_tenant_bindings(client.app,public_paths=BearerAuthMiddleware.PUBLIC_PATHS)
    result = client.post('/api/v1/studio-next/entities/'+spec.name+'/'+row['id']+'/actions/update',
        headers=headers,json=command({**values(),'lieferhinweis':'Synthetischer Hinweis'},version=1))
    assert result.status_code == 200,result.text
    assert result.json()['result']['version'] == 2
    assert result.json()['result']['lieferhinweis'] == 'Synthetischer Hinweis'
    # The same migration cannot be accidentally applied twice or to a different basis.
    with pytest.raises(DBAPIError), db.begin_nested():
        with Operations.context(MigrationContext.configure(db.connection())):
            evolution['upgrade']()
    assert db.scalar(sa.select(sa.func.count()).select_from(newrows)) == 1
