"""Real rollback-only CRUD simulation for an exact registered Studio entity definition."""
import json
import os
from pathlib import Path
from uuid import uuid4
import sqlalchemy as sa
from sqlalchemy.orm import Session
from sqlalchemy.exc import DBAPIError
from fastapi import HTTPException
from app.services.studio_entity_contracts import registration_for, contract_hash, EntityCommand, POLICIES
from app.services.studio_entity_compiler import registered_definition
from app.services.studio_entity_commands import execute, read, tables, verify_deployment

PROFILE = 'studio.entity.v1'
REQUIRED = ('schema','create','read','update','deactivate','version','idempotency',
            'tenancy','permissions','audit','outbox','preview','rollback')


def registration(definition):
    requested = definition.get('processSimulation')
    if (not isinstance(requested,dict) or set(requested) != {'profile','entity','contractHash'}
            or requested.get('profile') != PROFILE):
        raise ValueError('entity_simulation_binding_required')
    entry = registration_for(requested.get('entity'))
    if entry is None or requested.get('contractHash') != contract_hash(entry.spec):
        raise ValueError('entity_simulation_contract_not_registered')
    if not entry.writes_enabled:
        raise ValueError('entity_simulation_capability_not_enabled')
    from app.core.studio_release import definition_hash
    if definition_hash(definition) != definition_hash(registered_definition(entry)):
        raise ValueError('entity_simulation_definition_not_covered')
    return entry


def profile_errors(definition):
    try:
        registration(definition)
    except (ValueError,TypeError,KeyError) as error:
        return [str(error)]
    return []


def _body(data=None, version=None, key=None, mode='execute'):
    return EntityCommand.model_validate({'_idempotencyKey':key or str(uuid4()),
        '_auditReason':'Synthetic Studio release simulation','_mode':mode,
        'expected_version':version,'data':data or {}})


def _values(spec):
    samples={'text':'Synthetic Studio value','integer':7,'boolean':True,'date':'2026-01-15',
             'datetime':'2026-01-15T12:00:00Z','decimal':'1.2345','uuid':str(uuid4())}
    return {column.name:samples[column.type] for column in spec.columns}


def _expect_status(status, call):
    try:
        call()
    except HTTPException as error:
        return error.status_code == status
    return False


def _chain(db, entry, seed, foreign, checks):
    from app.infrastructure.models import Tenant
    from app.infrastructure.eventbus.outbox import OutboxEvent
    from app.auth.deps import require_roles
    spec=entry.spec; rows, events=tables(spec); actor='synthetic-studio-entity'
    verify_deployment(db,spec); checks['schema']=True
    for tenant in (seed,foreign):
        db.add(Tenant(id=tenant,name='Synthetic Studio simulation',domain=tenant+'.simulation.invalid'))
    db.flush()
    values=_values(spec);body=_body(values)
    result=execute(db,spec,'create',seed,actor,body)
    identifier=result['id']
    checks['create']=result['version']==1 and result['tenant_id']==seed
    checks['read']=read(db,spec,seed,identifier)==result
    checks['idempotency']=(execute(db,spec,'create',seed,actor,body)==result
        and _expect_status(409,lambda:execute(db,spec,'create',seed,'other-actor',body)))
    checks['tenancy']=(_expect_status(404,lambda:read(db,spec,foreign,identifier))
        and read(db,spec,foreign)==[])
    writer=require_roles(*POLICIES[spec.domain][1])
    writer(user={'sub':actor,'roles':[POLICIES[spec.domain][1][0]]})
    checks['permissions']=_expect_status(403,lambda:writer(user={'sub':actor,'roles':[]}))
    preview=execute(db,spec,'update',seed,actor,_body(values,version=1,mode='dryRun'),identifier)
    checks['preview']=(preview.get('persisted') is False and read(db,spec,seed,identifier)==result
        and db.scalar(sa.select(sa.func.count()).select_from(events).where(events.c.tenant_id==seed))==1)
    update=_body(values,version=1)
    changed=execute(db,spec,'update',seed,actor,update,identifier)
    checks['update']=changed['version']==2
    checks['idempotency'] &= execute(db,spec,'update',seed,actor,update,identifier)==changed
    checks['version']=_expect_status(409,lambda:execute(db,spec,'update',seed,actor,_body(values,version=1),identifier))
    removed=execute(db,spec,'delete',seed,actor,_body(version=2),identifier)
    checks['deactivate']=(removed['version']==3 and removed['deleted'] is True
        and _expect_status(404,lambda:read(db,spec,seed,identifier))
        and db.scalar(sa.select(sa.func.count()).select_from(rows).where(rows.c.tenant_id==seed))==1)
    history=db.execute(sa.select(events).where(events.c.tenant_id==seed)).mappings().all()
    checks['audit']=(len(history)==3 and all(item['actor']==actor for item in history)
        and all(item['audit']['after']['tenant_id']==seed for item in history)
        and any(item['audit']['before'] and item['audit']['before']['version']==2 for item in history))
    try:
        with db.begin_nested():
            db.execute(events.update().where(events.c.tenant_id==seed).values(actor='forged'))
        checks['audit']=False
    except DBAPIError:
        pass
    outbox=db.query(OutboxEvent).filter_by(tenant_id=seed,event_type='StudioEntityChanged').all()
    checks['outbox']=len(outbox)==3 and all(json.loads(event.payload)['actor']==actor for event in outbox)


def simulate(definition, *, engine=None):
    from app.services import studio_process_simulation as common
    from app.core.studio_release import SimulationBusy
    stamp=common.simulation_artifact_hash();checks={name:False for name in REQUIRED}
    report={'profile':PROFILE,'artifact_hash':stamp,'checks':checks,'passed':False,
            'business_effect':'none','external_effect':'none'}
    if stamp != common._LOADED_ARTIFACT_HASH:
        return {**report,'error':'simulation_runtime_requires_restart','failed_checks':list(REQUIRED)}
    entry=registration(definition);seed,foreign=str(uuid4()),str(uuid4())
    try:
        engine=engine or common._configured_probe()
        if engine.url.database!='valeo_probe' and os.environ.get('CI','').lower()!='true':
            raise RuntimeError('simulation_database_not_authorized')
        with engine.connect() as connection:
            outer=connection.begin()
            if not connection.execute(sa.text("SELECT pg_try_advisory_xact_lock(hashtextextended('valeo.studio.simulation.entity.v1',0))")).scalar_one():
                outer.rollback();raise SimulationBusy('shared_simulation_busy')
            db=Session(bind=connection,join_transaction_mode='create_savepoint',expire_on_commit=False)
            try:
                _chain(db,entry,seed,foreign,checks)
                if not outer.is_active:raise RuntimeError('simulation_transaction_escaped')
            finally:
                db.close()
                if outer.is_active:outer.rollback()
        with engine.connect() as verify:
            checks['rollback']=verify.execute(sa.text('SELECT count(*) FROM domain_shared.tenants WHERE id IN (:own,:foreign)'),
                {'own':seed,'foreign':foreign}).scalar_one()==0
            from app.infrastructure.eventbus.outbox import OutboxEvent
            targets=(*tables(entry.spec),OutboxEvent.__table__)
            for table in targets:
                remaining=verify.scalar(sa.select(sa.func.count()).select_from(table).where(table.c.tenant_id.in_([seed,foreign])))
                checks['rollback'] &= remaining==0
    except SimulationBusy:
        raise
    except Exception as error:
        report['error']=type(error).__name__
        import traceback
        frame=traceback.extract_tb(error.__traceback__)[-1]
        report['error_location']=f'{Path(frame.filename).name}:{frame.lineno}:{frame.name}'
    report['passed']=all(checks.values()) and common.simulation_artifact_hash()==stamp
    report['failed_checks']=[name for name,passed in checks.items() if not passed]
    return report
