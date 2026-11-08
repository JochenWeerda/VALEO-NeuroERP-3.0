"""Pure generation contracts; runnable without database/application lifespan fixtures."""
import json
from uuid import uuid4
import pytest
from pydantic import ValidationError
from app.services.studio_entity_contracts import EntitySpec, EntityCommand, normalized_command
from app.services.studio_entity_compiler import compile_entity


def spec():
    return EntitySpec(name='studio_contract_probe', domain='crm', label='Pruefvertrag', columns=[
        {'name':'description','label':'Bezeichnung','type':'text','nullable':False},
        {'name':'quantity','label':'Menge','type':'decimal','nullable':False}])


def test_deterministic_bundle_uses_central_renderer_and_explicit_disabled_writes():
    bundle=compile_entity(spec())
    assert bundle==compile_entity(spec())
    assert bundle['enabled'] is False
    definition=json.loads(bundle['files']['screen.json'])
    assert definition['tables'][0]['dataSourceKey']==spec().name
    assert definition['layout']['floorplan']=='worklist'
    assert definition['fields']==[]
    assert definition['actions'][0]['inputFields'][0]['label']=='Bezeichnung'
    assert definition['layout']['columnNavigation']=='single'
    assert all(action['disabled'] and action['forbiddenForAgents'] for action in definition['agentContract']['availableActions'])
    for name in ('migration.py','router.py'):compile(bundle['files'][name],name,'exec')
    assert 'FOREIGN KEY(tenant_id)' in bundle['files']['migration.py']
    assert 'immutable_history' in bundle['files']['migration.py']


@pytest.mark.parametrize('change',[{'name':'users'},{'domain':'finance'},{'tenant_id':'forged'},
    {'columns':[{'name':'tenant_id','type':'text'}]}, {'columns':[{'name':'data','type':'text'}]},
    {'columns':[{'name':'name','type':'text'},{'name':'name','type':'integer'}]}])
def test_protected_domain_and_identity_targets_are_rejected(change):
    with pytest.raises(ValidationError):EntitySpec.model_validate({**spec().model_dump(),**change})


def test_flat_human_fields_and_nested_machine_fields_have_same_canonical_command():
    controls={'_idempotencyKey':str(uuid4()),'_auditReason':'Pruefung','expected_version':3}
    data={'description':'Synthetic','quantity':'1.2345'}
    flat=spec().flat_command_model().model_validate_json(json.dumps({**controls,**data}))
    nested=EntityCommand.model_validate({**controls,'data':data})
    assert normalized_command(flat).model_dump()==nested.model_dump()


@pytest.mark.parametrize('quantity',['1.12345','NaN','Infinity','100000000000000.0000'])
def test_decimal_contract_forbids_rounding_and_nonfinite_values(quantity):
    with pytest.raises(ValidationError):
        spec().payload_model().model_validate_json(json.dumps({'description':'Synthetic','quantity':quantity}))


@pytest.mark.parametrize('description',['','   ',None])
def test_required_text_fields_cannot_be_empty(description):
    with pytest.raises(ValidationError):
        spec().payload_model().model_validate_json(json.dumps({'description':description,'quantity':'1.2345'}))


def test_generated_definition_obeys_existing_studio_catalog_validation(tmp_path,monkeypatch):
    from app.services import studio_validation
    source=tmp_path/'catalog.json'
    source.write_text(json.dumps({'version':1,'generated_entities':[{'spec':spec().model_dump()}]}),encoding='utf-8')
    monkeypatch.setattr(studio_validation,'_CONFIG_PATH',source)
    studio_validation.load_studio_catalog.cache_clear()
    try:
        definition=json.loads(compile_entity(spec())['files']['screen.json'])
        assert studio_validation.validate_studio_draft(definition,native_screen_ids=set())==[]
    finally:
        studio_validation.load_studio_catalog.cache_clear()


def test_generated_http_commands_are_disabled_before_any_database_access():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from app.auth.deps import get_current_user
    from app.core.tenant import get_tenant_id
    from app.core.database import get_db
    from app.services.studio_entity_router import build_router
    app=FastAPI();app.include_router(build_router(spec()),prefix='/api/v1/studio')
    app.dependency_overrides[get_current_user]=lambda:{'sub':'synthetic','roles':['CRM_BEARBEITEN']}
    app.dependency_overrides[get_tenant_id]=lambda:'synthetic-tenant'
    app.dependency_overrides[get_db]=lambda:None  # Any attempted SQL would fail the test.
    with TestClient(app) as client:
        response=client.post('/api/v1/studio/entities/studio_contract_probe/actions/create',json={
            '_idempotencyKey':str(uuid4()),'_auditReason':'Pruefung',
            'data':{'description':'Synthetic','quantity':'1.2345'}})
    assert response.status_code==403 and response.json()['detail']=='generated_capability_not_enabled'


def test_contract_fingerprint_is_stable_across_windows_and_linux_line_endings(monkeypatch):
    from pathlib import Path
    from app.services.studio_entity_contracts import contract_hash
    expected=contract_hash(spec());original=Path.read_bytes
    def windows_bytes(path):
        data=original(path)
        return data.replace(b'\r\n',b'\n').replace(b'\n',b'\r\n') if path.name.startswith('studio_entity_') else data
    monkeypatch.setattr(Path,'read_bytes',windows_bytes)
    assert contract_hash(spec())==expected


def test_registration_cannot_invent_agent_roles_or_duplicate_an_entity():
    from app.services.studio_entity_contracts import registrations
    entry={'spec':spec().model_dump(),'agent_roles':['FINANCE_ADMIN']}
    with pytest.raises(ValidationError):registrations({'generated_entities':[entry]})
    entry={'spec':spec().model_dump()}
    with pytest.raises(ValueError,match='duplicate'):registrations({'generated_entities':[entry,entry]})
    colliding={'spec':{**spec().model_dump(),'name':spec().name+'_events'}}
    with pytest.raises(ValueError,match='duplicate'):registrations({'generated_entities':[entry,colliding]})


@pytest.mark.parametrize('reason',['','   '])
def test_audit_reason_is_not_optional_or_whitespace(reason):
    with pytest.raises(ValidationError):
        EntityCommand.model_validate({'_idempotencyKey':str(uuid4()),'_auditReason':reason})


def test_existing_studio_router_installs_generated_paths_without_double_prefix(tmp_path,monkeypatch):
    from fastapi import APIRouter, FastAPI
    from app.services import studio_validation
    from app.services.studio_entity_router import install_registered_entities
    source=tmp_path/'catalog.json'
    source.write_text(json.dumps({'generated_entities':[{'spec':spec().model_dump()}]}),encoding='utf-8')
    monkeypatch.setattr(studio_validation,'_CONFIG_PATH',source)
    router=APIRouter(prefix='/studio');install_registered_entities(router)
    app=FastAPI();app.include_router(router,prefix='/api/v1')
    paths=app.openapi()['paths']
    assert '/api/v1/studio/entities/studio_contract_probe/actions/create' in paths
    assert not any('/studio/studio/' in path for path in paths)


def test_bundle_exports_same_typed_openapi_as_generated_command_router():
    from fastapi import FastAPI
    from app.services.studio_entity_router import build_router
    exported=json.loads(compile_entity(spec())['files']['openapi.json'])
    app=FastAPI();app.include_router(build_router(spec()),prefix='/api/v1/studio')
    runtime=app.openapi()
    assert exported['paths']==runtime['paths']
    assert exported['components']==runtime['components']
    row=exported['components']['schemas'][spec().name+'_record_v1']
    assert {'tenant_id','id','version','description','quantity'} <= set(row['required'])


@pytest.mark.parametrize('case',['unknown','stale','required','duplicate','reserved'])
def test_evolution_uses_trusted_registration_and_rejects_unsafe_changes(case, monkeypatch, tmp_path):
    import json
    from app.services.studio_entity_contracts import EntitySpec, EntityExtensionIn, contract_hash
    from app.services.studio_entity_evolution import compile_extension
    from app.services import studio_validation
    spec = EntitySpec(name='studio_evolution_probe',domain='crm',label='Synthetic',
        columns=[{'name':'name','type':'text','nullable':False}])
    config=tmp_path/'catalog.yaml';config.write_text(json.dumps({'generated_entities':[{'spec':spec.model_dump()}]}),encoding='utf-8')
    monkeypatch.setattr(studio_validation,'_CONFIG_PATH',config)
    body={'name':spec.name,'expected_contract_hash':contract_hash(spec),
          'columns':[{'name':'note','type':'text','nullable':True}]}
    if case=='unknown':body['name']='studio_unknown'
    if case=='stale':body['expected_contract_hash']='0'*64
    if case=='required':body['columns'][0]['nullable']=False
    if case=='duplicate':body['columns'][0]['name']='name'
    if case=='reserved':body['columns'][0]['name']='tenant_id'
    with pytest.raises(ValueError):compile_extension(EntityExtensionIn.model_validate(body))
