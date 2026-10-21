"""Mandatory plan gate and actual signed REST/CLI/MCP authoring parity."""
from uuid import uuid4
from copy import deepcopy
import json
import pytest
import httpx
from app.services import studio_draft_store as store, studio_migration_store as plans
from app.api.v1.schemas.studio_migration import StudioSavedMigrationIn
from app.core import studio_release as release
from test_studio_release_gate import candidate, proof
from test_studio_saved_migration import signed, subject_data, keys, probe, headers  # noqa: F401

@pytest.fixture
def memory():
    store.reset_studio_drafts()
    item=candidate()
    yield item
    store.use_sql_studio_drafts()

def prepare(item,changes=None):
    return plans.save_migration_plan(item['tenant_id'],item['id'],'editor',StudioSavedMigrationIn(
        expected_revision=item['revision'],idempotency_key=uuid4(),schema_changes=changes or []))

def simulate(item,monkeypatch):
    monkeypatch.setattr(release,'simulate_candidate',proof)
    store.simulate_draft(item['tenant_id'],item['id'],'editor',item['revision'],str(uuid4()))

def publish(item):
    return store.set_status(item['tenant_id'],item['id'],'reviewer','published_temp',expected_snapshot=item)

def test_valid_simulation_cannot_replace_missing_plan(memory,monkeypatch):
    simulate(memory,monkeypatch)
    with pytest.raises(ValueError,match='migrationsplan_fuer_diese_revision_fehlt'): publish(memory)
    assert store.get_draft('own',memory['id'])['status']=='review'

@pytest.mark.parametrize('broken',['binding_hash','candidate_definition_hash','event_id'])
def test_manipulated_plan_never_publishes(memory,monkeypatch,broken):
    prepare(memory);simulate(memory,monkeypatch)
    entry=next(e for e in store._HISTORY if e['action']=='migration_plan')
    entry['snapshot']['saved_migration'][broken]='0'*64
    with pytest.raises(ValueError,match='migrationsplan_'): publish(memory)

def test_compiler_or_catalog_drift_invalidates_plan(memory,monkeypatch):
    prepare(memory);simulate(memory,monkeypatch)
    original=plans.plan_migration
    monkeypatch.setattr(plans,'plan_migration',lambda *a:original(*a).model_copy(update={'plan_hash':'0'*64}))
    with pytest.raises(ValueError,match='migrationsplan_nachweis_veraltet'): publish(memory)

def test_schema_proposal_needs_separate_deployment_evidence(memory,monkeypatch):
    prepare(memory,[{'operation':'create_table','schema_name':'domain_crm','table':'integration_probe',
                     'columns':[{'name':'note','type':'text'}]}])
    simulate(memory,monkeypatch)
    with pytest.raises(ValueError,match='schema_deployment_nachweis_fehlt'): publish(memory)

def test_runtime_rechecks_attached_plan(memory,monkeypatch):
    prepare(memory);simulate(memory,monkeypatch);publish(memory)
    assert store.get_published_definition('own',memory['screen_id']) is not None
    store._DRAFTS[memory['id']]['readiness']['release_evidence'].pop('migration_plan')
    assert store.get_published_definition('own',memory['screen_id']) is None

@pytest.fixture
def channels(signed,monkeypatch):
    from app.api.v1.endpoints import mcp_tool_registry
    from app.core.tenant_binding import install_tenant_bindings
    from main import BearerAuthMiddleware
    from app.services import mcp_studio_plans
    client=signed[0]
    client.app.include_router(mcp_tool_registry.router,prefix='/api/v1')
    install_tenant_bindings(client.app,public_paths=BearerAuthMiddleware.PUBLIC_PATHS)
    original=mcp_studio_plans.execute
    def target(request):
        assert 'x-tenant-id' not in request.headers
        result=client.request(request.method,str(request.url),headers={'Authorization':request.headers['authorization'],'Content-Type':'application/json'},content=request.content)
        return httpx.Response(result.status_code,content=result.content)
    monkeypatch.setattr(mcp_studio_plans,'execute',lambda request,auth:original(request,auth,transport=httpx.MockTransport(target)))
    return signed

def mcp(data,body,*,role='FINANCE_ADMIN',scope='belege:write',tenant=None,mode='execute'):
    client,provider,own,_,item=data
    token=provider.token(tenant or own,changes={'sub':'planner','roles':[role] if role else [],'scope':scope,'identity_type':'agent'})
    return client.post('/api/v1/mcp/tools/call',headers={'Authorization':'Bearer '+token},json={
        'tool_name':'studio.migration.plan','mode':mode,'idempotency_key':body['idempotency_key'],
        'parameters':{'draft_id':item['id'],'expected_revision':body['expected_revision']}})

def test_three_transports_return_one_durable_plan(channels,monkeypatch):
    from valeo_cli import cli
    client,provider,tenant,_,item=channels
    body={'expected_revision':item['revision'],'idempotency_key':str(uuid4()),'schema_changes':[]}
    auth=headers(channels)
    rest=client.post('/api/v1/studio/drafts/'+item['id']+'/migration-plan',headers=auth,json=body)
    assert rest.status_code==200,rest.text
    monkeypatch.setenv('VALEO_ACCESS_TOKEN',auth['Authorization'][7:])
    lines=[]
    assert cli.main(['studio','plan-speichern',item['id'],'--revision',item['revision'],'--idempotenz',body['idempotency_key']],http=client,out=lines.append)==0
    agent=mcp(channels,body)
    assert agent.status_code==200,agent.text
    assert agent.json()==json.loads(lines[0])==rest.json()
    assert len(store.list_history(tenant,item['id']))==2
    assert store.get_draft(tenant,item['id'])==item

@pytest.mark.parametrize('kind,expected',[('scope',403),('role',403),('tenant',404)])
def test_mcp_never_adds_scope_role_or_tenant_access(channels,kind,expected):
    item=channels[4];body={'expected_revision':item['revision'],'idempotency_key':str(uuid4())}
    kwargs={'scope':''} if kind=='scope' else {'role':None} if kind=='role' else {'tenant':channels[3]}
    response=mcp(channels,body,**kwargs)
    assert response.status_code==expected,response.text
    assert len(store.list_history(channels[2],item['id']))==1

@pytest.mark.parametrize('mode',['dryRun','validate','propose'])
def test_nonexecuting_modes_never_persist(channels,mode):
    body={'expected_revision':channels[4]['revision'],'idempotency_key':str(uuid4())}
    result=mcp(channels,body,mode=mode)
    assert result.status_code==200 and result.json()['persisted'] is False
    assert result.json()['validation_only'] is True
    assert len(store.list_history(channels[2],channels[4]['id']))==1

def test_catalog_entry_without_explicit_capability_enablement_cannot_write(channels,monkeypatch):
    from app.services.mcp_tool_registry_service import mcp_tool_registry_service as registry
    original=registry.get_tool
    monkeypatch.setattr(registry,'get_tool',lambda tool:{**original(tool),'agent_write_enabled':False})
    body={'expected_revision':channels[4]['revision'],'idempotency_key':str(uuid4())}
    assert mcp(channels,body).status_code==403
    assert len(store.list_history(channels[2],channels[4]['id']))==1


def test_sql_publication_requires_current_plan_and_serves_attached_evidence(signed, monkeypatch):
    """Real transaction/history; simulation proof is an explicit lifecycle double."""
    from app.services.studio_propose import propose_studio_draft
    tenant = signed[2]
    definition = propose_studio_draft('Artikel')
    screen_id = 'tenant/sql-plan-' + uuid4().hex
    definition.update(id=screen_id, domain='agrar',
                      adapter={'type':'native','sourceId':screen_id,'temporary':True}, actions=[])
    definition['agentContract']['availableActions'] = []
    definition['agentContract']['editableFields'] = []
    draft = store.save_draft(tenant, 'planner', definition)
    item = store.set_status(tenant, draft['id'], 'planner', 'review', expected_snapshot=draft)
    simulate(item, monkeypatch)
    with pytest.raises(ValueError, match='migrationsplan_fuer_diese_revision_fehlt'):
        publish(item)
    prepare(item)
    assert publish(item)['status'] == 'published_temp'
    assert store.get_published_definition(tenant, screen_id) is not None
    assert [entry['action'] for entry in store.list_history(tenant, item['id'])] == [
        'create', 'review', 'simulation', 'migration_plan', 'published_temp']
