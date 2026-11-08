"""Real deployed entity profile, shared database only; own DDL and rollback-only data."""
import copy
import json
from uuid import uuid4
import pytest
import sqlalchemy as sa
from sqlalchemy.orm import Session
from alembic.migration import MigrationContext
from alembic.operations import Operations
from app.core.database import engine
from app.core import studio_release as release
from app.services import studio_draft_store as store, studio_validation
from app.services import studio_process_simulation as common
from app.services.studio_entity_contracts import EntitySpec, EntityRegistration
from app.services.studio_entity_compiler import compile_entity, registered_definition
from app.services.studio_entity_commands import tables
from app.services.studio_entity_simulation import simulate, REQUIRED
from test_gdpr_subject_boundary import subject_data, keys, probe  # noqa: F401

pytestmark=[pytest.mark.integration,pytest.mark.needs_live_db]


@pytest.fixture
def deployment(monkeypatch,tmp_path):
    from testgrenze import pruefstand_erlaubt
    assert pruefstand_erlaubt(engine.url)
    spec=EntitySpec(name='studio_release_'+uuid4().hex[:12],domain='crm',label='Synthetic release',
        columns=[{'name':kind+'_value','type':kind,'nullable':False}
                 for kind in ('text','integer','boolean','date','datetime','decimal','uuid')])
    # Only this fixture owns these exact random table names. No database/container creation.
    bundle=compile_entity(spec);namespace={};exec(bundle['files']['migration.py'],namespace)
    with engine.begin() as connection:
        with Operations.context(MigrationContext.configure(connection)):
            namespace['upgrade']()
    rows,events=tables(spec)
    assert rows.name.startswith('studio_release_') and events.name==rows.name+'_events'
    try:
        import yaml
        data=yaml.safe_load(studio_validation._CONFIG_PATH.read_text(encoding='utf-8'))
        entry=EntityRegistration(spec=spec,writes_enabled=True)
        data['generated_entities']=[entry.model_dump()]
        path=tmp_path/'catalog.yaml';path.write_text(json.dumps(data),encoding='utf-8')
        monkeypatch.setattr(studio_validation,'_CONFIG_PATH',path)
        monkeypatch.setattr(common,'_configured_probe',lambda:engine)
        studio_validation.load_studio_catalog.cache_clear()
        yield registered_definition(entry),entry,path,data
    finally:
        studio_validation.load_studio_catalog.cache_clear()
        # Exact own tables/function only. Live business data and shared schema are preserved.
        with engine.begin() as connection:
            events.drop(connection);rows.drop(connection)
            connection.execute(sa.text(f'DROP FUNCTION "{rows.schema}"."{spec.name}_immutable"()'))


def test_actual_entity_chain_rolls_back_all_business_effects(deployment):
    definition,entry,_,_=deployment
    before={}
    with engine.connect() as connection:
        for table in tables(entry.spec):
            before[table.name]=connection.scalar(sa.select(sa.func.count()).select_from(table))
    report=simulate(definition,engine=engine)
    assert report['passed'] is True,report
    assert set(report['checks'])==set(REQUIRED) and all(report['checks'].values())
    assert report['business_effect']=='none' and report['external_effect']=='none'
    with engine.connect() as connection:
        for table in tables(entry.spec):
            assert connection.scalar(sa.select(sa.func.count()).select_from(table))==before[table.name]


def test_actual_entity_simulation_busy_has_no_false_evidence(deployment):
    definition,*_=deployment
    with engine.connect() as held:
        transaction=held.begin()
        held.execute(sa.text("SELECT pg_advisory_xact_lock(hashtextextended('valeo.studio.simulation.entity.v1',0))"))
        try:
            with pytest.raises(release.SimulationBusy):simulate(definition,engine=engine)
        finally:transaction.rollback()


def test_durable_entity_evidence_allows_independent_publish_and_revocation(deployment,monkeypatch):
    definition,entry,path,data=deployment
    from app.infrastructure.models import Tenant
    from app.api.v1.schemas.studio_migration import StudioSavedMigrationIn
    from app.services.studio_migration_store import save_migration_plan
    connection=engine.connect();outer=connection.begin();own=str(uuid4())
    db=Session(bind=connection,join_transaction_mode='create_savepoint',expire_on_commit=False)
    try:
        db.add(Tenant(id=own,name='Synthetic Studio release',domain=own+'.example.invalid'));db.commit()
        monkeypatch.setattr(store,'_prefer_memory',False)
        monkeypatch.setattr(store,'_use_sql',lambda:True)
        monkeypatch.setattr(store,'_sql_session',lambda:Session(bind=connection,join_transaction_mode='create_savepoint',expire_on_commit=False))
        draft=store.save_draft(own,'editor',definition)
        item=store.set_status(own,draft['id'],'editor','review',expected_snapshot=draft)
        with pytest.raises(ValueError,match='simulation_fuer_diese_revision_fehlt'):
            store.set_status(own,item['id'],'reviewer','published_temp',expected_snapshot=item)
        saved=save_migration_plan(own,item['id'],'editor',StudioSavedMigrationIn(expected_revision=item['revision'],idempotency_key=uuid4()))
        assert saved['requires_definition_update'] is False
        key=str(uuid4());result=store.simulate_draft(own,item['id'],'editor',item['revision'],key)
        assert result['simulation']['passed'] is True,result['simulation']
        assert result['simulation']['profile']=='studio.entity.v1'
        with monkeypatch.context() as phase:
            phase.setattr(release,'simulate_candidate',lambda _:pytest.fail('Replay must not simulate again'))
            assert store.simulate_draft(own,item['id'],'editor',item['revision'],key)==result
        with pytest.raises(PermissionError,match='vier_augen'):
            store.set_status(own,item['id'],'editor','published_temp',expected_snapshot=item)
        published=store.set_status(own,item['id'],'reviewer','published_temp',expected_snapshot=item)
        assert published['status']=='published_temp'
        active=store.get_published_definition(own,definition['id'])
        assert active['studioRelease']['candidateRevision']==item['revision']
        assert active['actions'][0]['disabled'] is False
        assert store.get_published_definition('foreign',definition['id']) is None
        broken=copy.deepcopy(published);broken['readiness']['release_evidence']['profile']='grain.v1'
        assert release.published_definition(broken) is None
        data['generated_entities'][0]['writes_enabled']=False
        path.write_text(json.dumps(data),encoding='utf-8')
        assert store.get_published_definition(own,definition['id']) is None
    finally:
        db.close();assert outer.is_active;outer.rollback();connection.close()


def test_signed_cli_import_review_plan_simulate_publish_and_retire(deployment,subject_data,monkeypatch,tmp_path):
    from app.api.v1.endpoints import studio_drafts,mask_screen_definition
    from app.core.tenant_binding import install_tenant_bindings
    from main import BearerAuthMiddleware
    from valeo_cli import cli
    definition,entry,_,_=deployment
    client,db,provider,tenant,foreign,*_=subject_data
    monkeypatch.setattr(store,'_prefer_memory',False)
    monkeypatch.setattr(store,'_use_sql',lambda:True)
    monkeypatch.setattr(store,'_sql_session',lambda:Session(bind=db.get_bind(),join_transaction_mode='create_savepoint',expire_on_commit=False))
    client.app.include_router(studio_drafts.router,prefix='/api/v1')
    client.app.include_router(mask_screen_definition.router,prefix='/api/v1')
    install_tenant_bindings(client.app,public_paths=BearerAuthMiddleware.PUBLIC_PATHS)
    def token(actor,roles,tid=tenant):
        return provider.token(tid,changes={'sub':actor,'roles':roles,'identity_type':'human'})
    editor=token('synthetic-cli-editor',['CRM_BEARBEITEN','EINKAUF_BEARBEITEN'])
    reviewer=token('synthetic-cli-reviewer',['admin'])
    monkeypatch.setenv('VALEO_ACCESS_TOKEN',editor)
    def run(*args):
        lines=[];status=cli.main(['studio',*args],http=client,out=lines.append)
        return status,lines
    endpoint='/api/v1/studio/entity-definitions/'+entry.spec.name
    assert client.get(endpoint).status_code==401
    assert client.get(endpoint,headers={'Authorization':'Bearer '+token('reader',[])}).status_code==403
    assert client.get(endpoint,headers={'Authorization':'Bearer '+editor}).json()['definition']==definition
    output=tmp_path/'draft.json';key=str(uuid4())
    args=('entitaet-uebernehmen',entry.spec.name,'--idempotenz',key,'--ausgabe',str(output))
    status,lines=run(*args);assert status==0,lines
    created=json.loads(output.read_text(encoding='utf-8'))
    assert created['definitionReady'] is True,created
    status,lines=run(*args);assert status==0,lines
    assert json.loads(output.read_text(encoding='utf-8'))==created
    draft_id=created['id']
    status,lines=run('pruefung',draft_id,'--revision',created['revision']);assert status==0,lines
    headers={'Authorization':'Bearer '+editor}
    review=client.get('/api/v1/studio/drafts/'+draft_id,headers=headers).json()
    assert review['status']=='review'
    status,lines=run('plan-speichern',draft_id,'--revision',review['revision'],'--ausgabe',str(tmp_path/'plan.json'));assert status==0,lines
    status,lines=run('simulieren',draft_id,'--revision',review['revision']);assert status==0,lines
    event=store.list_history(tenant,draft_id)[-1]
    assert event['snapshot']['simulation']['passed'] is True
    assert event['snapshot']['simulation']['profile']=='studio.entity.v1'
    monkeypatch.setenv('VALEO_ACCESS_TOKEN',token('synthetic-cli-editor',['admin']))
    status,lines=run('freigeben',draft_id,'--revision',review['revision'])
    assert status==3 and any('vier_augen' in line for line in lines),lines
    monkeypatch.setenv('VALEO_ACCESS_TOKEN',reviewer)
    status,lines=run('freigeben',draft_id,'--revision',review['revision']);assert status==0,lines
    route='/api/v1/masks/'+definition['id']+'/screen-definition'
    active=client.get(route,headers=headers)
    assert active.status_code==200,active.text
    assert active.json()['studioRelease']['candidateRevision']==review['revision']
    assert active.json()['actions'][0]['disabled'] is False
    assert client.get(route,headers={'Authorization':'Bearer '+token('foreign-reader',['CRM_BEARBEITEN'],foreign)}).status_code==404
    published=client.get('/api/v1/studio/drafts/'+draft_id,headers=headers).json()
    status,lines=run('zurueckziehen',draft_id,'--revision',published['revision']);assert status==0,lines
    assert client.get(route,headers=headers).status_code==404
    for table in tables(entry.spec):
        assert db.scalar(sa.select(sa.func.count()).select_from(table))==0
