"""Uncovered definitions and cross-profile evidence cannot gain Studio release."""
import copy
import json
import pytest
from app.services import studio_validation
from app.services.studio_entity_contracts import EntitySpec, EntityRegistration
from app.services.studio_entity_compiler import registered_definition
from app.services.studio_entity_simulation import PROFILE, REQUIRED
from app.core import studio_release as release


@pytest.fixture
def registered(tmp_path,monkeypatch):
    spec=EntitySpec(name='studio_release_probe',domain='crm',label='Synthetic',
        columns=[{'name':'name','type':'text','nullable':False}])
    entry=EntityRegistration(spec=spec,writes_enabled=True)
    original=studio_validation._CONFIG_PATH.read_text(encoding='utf-8')
    import yaml
    data=yaml.safe_load(original);data['generated_entities']=[entry.model_dump()]
    path=tmp_path/'catalog.yaml';path.write_text(json.dumps(data),encoding='utf-8')
    monkeypatch.setattr(studio_validation,'_CONFIG_PATH',path)
    studio_validation.load_studio_catalog.cache_clear()
    try:yield registered_definition(entry),data,path
    finally:studio_validation.load_studio_catalog.cache_clear()


def test_exact_registered_definition_has_its_own_full_profile(registered):
    definition,_,_=registered
    assert release.profile_errors(definition)==[]
    assert release.simulation_requirements(definition)==(PROFILE,REQUIRED)
    assert studio_validation.validate_studio_draft(definition,native_screen_ids=set())==[]
    assert 'ledger' not in REQUIRED and 'outbox' in REQUIRED and 'rollback' in REQUIRED


@pytest.mark.parametrize('change',['url','disabled','agent','schema','field','domain','rule','title'])
def test_uncovered_definition_change_cannot_reuse_profile(registered,change):
    definition,_,_=registered;value=copy.deepcopy(definition)
    if change=='url':value['actions'][0]['commandEndpoint']='/api/v1/other'
    if change=='disabled':value['actions'][0]['disabled']=True
    if change=='agent':value['actions'][0]['forbiddenForAgents']=False
    if change=='schema':value['processSimulation']['contractHash']='0'*64
    if change=='field':value['actions'][0]['inputFields'][0]['required']=False
    if change=='domain':value['domain']='finance'
    if change=='rule':value['accountingRules']={'skip':True}
    if change=='title':value['title']='Changed without a matching registered definition'
    assert release.profile_errors(value)


def test_revoked_registration_disables_release_immediately(registered):
    definition,data,path=registered
    data['generated_entities'][0]['writes_enabled']=False
    path.write_text(json.dumps(data),encoding='utf-8')
    assert release.profile_errors(definition)==['entity_simulation_capability_not_enabled']


@pytest.mark.parametrize('broken',['profile','checks','hash'])
def test_entity_release_rejects_wrong_profile_or_incomplete_evidence(registered,monkeypatch,broken):
    from app.services.studio_process_simulation import simulation_artifact_hash
    definition,_,_=registered
    monkeypatch.setattr(release,'ensure_interface_sync',lambda:None)
    item={'id':'synthetic','tenant_id':'own','revision':'revision','definition':definition}
    proof={'tenant_id':'own','draft_id':'synthetic','candidate_revision':'revision',
        'definition_hash':release.definition_hash(definition),'artifact_hash':simulation_artifact_hash(),
        'passed':True,'profile':PROFILE,'checks':dict.fromkeys(REQUIRED,True)}
    if broken=='profile':proof['profile']='grain.v1'
    if broken=='checks':proof['checks'].pop('outbox')
    if broken=='hash':proof['artifact_hash']='stale'
    with pytest.raises(ValueError,match='simulation_unvollstaendig'):
        release.require_simulation(item,[{'action':'simulation','snapshot':{'simulation':proof}}])


def test_entity_fingerprint_includes_the_authorization_implementation(monkeypatch):
    from pathlib import Path
    from app.services.studio_entity_contracts import contract_hash
    spec=EntitySpec(name='studio_authorization_probe',domain='crm',label='Synthetic',
        columns=[{'name':'name','type':'text','nullable':False}])
    stamp=contract_hash(spec);original=Path.read_bytes
    def changed(path):
        raw=original(path)
        return raw+b'\n# synthetic policy change\n' if path.name=='bereich_roles.py' else raw
    monkeypatch.setattr(Path,'read_bytes',changed)
    assert contract_hash(spec)!=stamp


def test_old_loaded_router_cannot_adopt_a_changed_contract_without_restart(monkeypatch):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from app.auth.deps import get_current_user
    from app.core.tenant import get_tenant_id
    from app.core.database import get_db
    from app.services import studio_entity_contracts
    from app.services.studio_entity_router import build_router
    spec=EntitySpec(name='studio_loaded_probe',domain='crm',label='Synthetic',
        columns=[{'name':'name','type':'text','nullable':False}])
    app=FastAPI();app.include_router(build_router(spec,writes_enabled=True),prefix='/api/v1/studio')
    app.dependency_overrides[get_current_user]=lambda:{'sub':'synthetic','roles':['CRM_BEARBEITEN']}
    app.dependency_overrides[get_tenant_id]=lambda:'synthetic'
    app.dependency_overrides[get_db]=lambda:None
    monkeypatch.setattr(studio_entity_contracts,'contract_hash',lambda _: '0'*64)
    with TestClient(app) as client:
        response=client.get('/api/v1/studio/entities/'+spec.name)
    assert response.status_code==409
    assert response.json()['detail']=='generated_runtime_requires_restart'


def test_generated_registered_mask_passes_actual_readiness_without_exceptions(registered):
    from app.api.v1.endpoints.mask_screen_definition import _check_readiness
    definition,_,_=registered
    report=_check_readiness(definition)
    assert not [error for error in report['errors'] if 'non_temporary' not in error],report
    assert all(action['permission']=='studio.entity.crm.write' for action in definition['actions'])
