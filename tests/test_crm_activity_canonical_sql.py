"""Real signed HTTP commands, shared PostgreSQL and rollback-only additive DDL."""
import importlib.util
import os
from pathlib import Path
from uuid import uuid4
import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import inspect, text
from sqlalchemy.engine import make_url

from app.core.database import engine
from app.core.tenant_binding import install_tenant_bindings
from app.api.v1.endpoints import activities
from main import BearerAuthMiddleware
from test_gdpr_subject_boundary import subject_data,keys,probe

pytestmark=[pytest.mark.integration,pytest.mark.needs_live_db]


@pytest.fixture
def require_db():
    ci=os.environ.get("CI","").casefold()=="true"
    raw=os.environ.get("TEST_DATABASE_URL") or (os.environ.get("DATABASE_URL") if ci else None)
    assert raw and make_url(raw)==engine.url and (ci or engine.url.database not in {"valeo_neuro_erp","postgres"}), "Explicit shared test database required"


@pytest.fixture
def canonical(require_db,subject_data):
    client,db,provider,tenant,foreign,*_=subject_data
    path=Path(__file__).resolve().parents[1]/"alembic/versions/crm_activity_canonical_20261029.py"
    spec=importlib.util.spec_from_file_location("crm_activity_migration",path)
    migration=importlib.util.module_from_spec(spec);spec.loader.exec_module(migration)
    context=MigrationContext.configure(db.connection())
    if "origin" not in {column["name"] for column in inspect(db.connection()).get_columns("activities",schema="domain_crm")}:
        with Operations.context(context):migration.upgrade()
    db.commit()  # Release fixture savepoint only; outer shared-probe transaction still rolls back.
    client.app.include_router(activities.router,prefix="/api/v1/crm/activities")
    from app.api.v1.endpoints import mcp_tool_registry,mask_screen_definition,mask_actions,opportunities
    client.app.include_router(mcp_tool_registry.router,prefix="/api/v1")
    client.app.include_router(opportunities.router,prefix="/api/v1/crm/opportunities")
    client.app.include_router(mask_actions.router,prefix="/api/v1")
    client.app.include_router(mask_screen_definition.router,prefix="/api/v1")
    install_tenant_bindings(client.app,public_paths=BearerAuthMiddleware.PUBLIC_PATHS)
    yield client,db,provider,tenant,foreign


def headers(data,role="CRM_BEARBEITEN",tenant=None,subject="human-a"):
    return {"Authorization":"Bearer "+data[2].token(tenant or data[3],changes={"sub":subject,"roles":[role] if role else [],"scope":"crm:write masks:read","identity_type":"human"})}


def create(data,**changes):
    payload={"type":"call","title":"SYNTH canonical callback","idempotency_key":str(uuid4()),
             "main_topics":["Synthetic topic"],"orders_placed":[],"follow_up_actions":["Synthetic follow-up"],**changes}
    return data[0].post("/api/v1/crm/activities",json=payload,headers=headers(data)),payload


def test_real_creation_replay_and_changed_repeat_are_atomic(canonical):
    client,db,_,tenant,_=canonical
    response,payload=create(canonical)
    assert response.status_code==201,response.text
    row=response.json();assert row["version"]==1 and row["created_by"]=="human-a"
    assert row["date"] is None and not row["overdue"]
    again=client.post("/api/v1/crm/activities",json=payload,headers=headers(canonical))
    assert again.status_code==201 and again.json()["id"]==row["id"]
    conflict=client.post("/api/v1/crm/activities",json={**payload,"title":"Changed intent"},headers=headers(canonical))
    assert conflict.status_code==409
    assert db.execute(text("SELECT count(*) FROM domain_crm.activities WHERE tenant_id=:t"),{"t":tenant}).scalar()==1
    assert db.execute(text("SELECT count(*) FROM public.outbox_events WHERE tenant_id=:t AND aggregate_id=:id"),{"t":tenant,"id":row["id"]}).scalar()==1
    assert db.execute(text("SELECT performed_by FROM domain_crm.crm_action_audit_log WHERE tenant_id=:t AND entity_id=:id"),{"t":tenant,"id":row["id"]}).scalar()=="human-a"


def test_all_three_collections_roundtrip_in_one_versioned_update(canonical):
    client,db,_,_,_=canonical
    response,_=create(canonical);assert response.status_code==201,response.text
    row=response.json();path="/api/v1/crm/activities/"+row["id"]
    update={"expected_version":1,"idempotency_key":str(uuid4()),"main_topics":["Revised"],"orders_placed":["Synthetic order"],"follow_up_actions":[],"date":None}
    changed=client.put(path,json=update,headers=headers(canonical));assert changed.status_code==200,changed.text
    assert changed.json()["version"]==2 and changed.json()["orders_placed"]==["Synthetic order"]
    assert client.put(path,json=update,headers=headers(canonical)).json()==changed.json()
    stale=client.put(path,json={**update,"idempotency_key":str(uuid4())},headers=headers(canonical))
    assert stale.status_code==409
    current=client.get(path,headers=headers(canonical)).json()
    assert current["main_topics"]==["Revised"] and current["follow_up_actions"]==[]
    assert client.get(path+"/orders-placed",headers=headers(canonical)).json()==["Synthetic order"]


def test_foreign_records_and_insufficient_roles_cannot_write(canonical):
    client,db,_,tenant,foreign=canonical
    response,_=create(canonical);assert response.status_code==201,response.text
    path="/api/v1/crm/activities/"+response.json()["id"]
    command={"expected_version":1,"idempotency_key":str(uuid4()),"title":"Forged"}
    assert client.get(path,headers=headers(canonical,tenant=foreign)).status_code==404
    assert client.put(path,json=command,headers=headers(canonical,tenant=foreign)).status_code==404
    assert client.put(path,json=command,headers=headers(canonical,role="CRM_LESEN")).status_code==403
    assert client.get(path).status_code==401
    assert client.put(path,json={**command,"tenant_id":foreign},headers=headers(canonical)).status_code==403
    assert client.put(path,json={**command,"created_by":"forged"},headers=headers(canonical)).status_code==422
    assert client.get(path,headers=headers(canonical)).json()["title"]=="SYNTH canonical callback"


def test_delete_checks_version_and_replays_without_duplicate_effect(canonical):
    client,*_=canonical
    response,_=create(canonical);assert response.status_code==201,response.text
    path="/api/v1/crm/activities/"+response.json()["id"]
    payload={"expected_version":2,"idempotency_key":str(uuid4())}
    assert client.delete(path,headers={**headers(canonical),"If-Match":'"2"',"Idempotency-Key":payload["idempotency_key"]}).status_code==412
    payload={"expected_version":1,"idempotency_key":str(uuid4())}
    assert client.delete(path,headers={**headers(canonical),"If-Match":'"1"',"Idempotency-Key":payload["idempotency_key"]}).status_code==204
    assert client.delete(path,headers={**headers(canonical),"If-Match":'"1"',"Idempotency-Key":payload["idempotency_key"]}).status_code==204
    assert client.get(path,headers=headers(canonical)).status_code==404


def test_audit_failure_rolls_back_activity_receipt_and_outbox(canonical,monkeypatch):
    from app.services import crm_activity_service
    client,db,_,tenant,_=canonical
    def fail(*a,**k):raise RuntimeError("Synthetic audit failure")
    monkeypatch.setattr(crm_activity_service,"_write_audit",fail)
    response,payload=create(canonical)
    assert response.status_code==503,response.text
    assert "Synthetic audit failure" not in response.text
    for statement in ("SELECT count(*) FROM domain_crm.activities WHERE tenant_id=:t",
                      "SELECT count(*) FROM public.mcp_tool_executions WHERE tenant_id=:t",
                      "SELECT count(*) FROM public.outbox_events WHERE tenant_id=:t"):
        assert db.execute(text(statement),{"t":tenant}).scalar()==0


def test_list_and_detail_are_the_same_dto_and_pagination_contract(canonical):
    client,*_=canonical
    first,_=create(canonical,title="SYNTH first");second,_=create(canonical,title="SYNTH last")
    assert first.status_code==second.status_code==201
    listing=client.get("/api/v1/crm/activities?limit=1",headers=headers(canonical))
    assert listing.status_code==200,listing.text
    body=listing.json();assert body["total"]==2 and body["has_next"]
    row=body["items"][0]
    assert client.get("/api/v1/crm/activities/"+row["id"],headers=headers(canonical)).json()==row
    assert client.get("/api/v1/crm/activities/",headers=headers(canonical)).json()["total"]==2


def test_rest_mcp_and_cli_share_command_replay_and_version(canonical,monkeypatch):
    from valeo_cli import cli
    client,db,_,tenant,_=canonical
    first,payload=create(canonical)
    assert first.status_code==201,first.text
    row=first.json()
    mcp=client.post("/api/v1/mcp/tools/call",headers=headers(canonical),json={"tool_name":"crm.activity.create","mode":"execute",
        "idempotency_key":payload["idempotency_key"],"parameters":{key:value for key,value in payload.items() if key!="idempotency_key"}})
    assert mcp.status_code==200,mcp.text
    assert mcp.json()["activity_id"]==row["id"] and mcp.json()["replayed"] is True
    key=str(uuid4())
    updated=client.put("/api/v1/crm/activities/"+row["id"],headers=headers(canonical),json={"title":"SYNTH cross-channel","type":"call","expected_version":1,"idempotency_key":key})
    assert updated.status_code==200,updated.text
    monkeypatch.setenv("VALEO_ACCESS_TOKEN",headers(canonical)["Authorization"][7:])
    lines=[]
    code=cli.main(["ausfuehren","crm/aktivitaet","update","--id",row["id"],"--feld","title=SYNTH cross-channel","--feld","type=call",
                   "--version","1","--idempotenz",key,"--json"],http=client,out=lines.append)
    assert code==0,lines
    import json
    result=json.loads(lines[-1])
    assert result["activity"]["id"]==row["id"] and result["replayed"] is True
    assert db.execute(text("SELECT count(*) FROM domain_crm.activities WHERE tenant_id=:t"),{"t":tenant}).scalar()==1
    assert db.execute(text("SELECT count(*) FROM public.outbox_events WHERE tenant_id=:t AND aggregate_id=:id"),{"t":tenant,"id":row["id"]}).scalar()==2


def test_preview_has_no_business_audit_receipt_or_outbox_effect(canonical):
    client,db,_,tenant,_=canonical
    response,_=create(canonical);assert response.status_code==201,response.text
    row=response.json();path="/api/v1/crm/activities/"+row["id"]+"/actions/delete"
    key=str(uuid4())
    preview=client.post(path,headers=headers(canonical),json={"_mode":"dryRun","expected_version":1,"_idempotencyKey":key})
    assert preview.status_code==200,preview.text
    assert preview.json()["success"] and preview.json()["mode"]=="dryRun"
    assert db.execute(text("SELECT count(*) FROM public.mcp_tool_executions WHERE tenant_id=:t"),{"t":tenant}).scalar()==1
    current=client.get("/api/v1/crm/activities/"+row["id"],headers=headers(canonical))
    assert current.status_code==200 and current.json()["version"]==1
    executed=client.post(path,headers=headers(canonical),json={"expected_version":1,"_idempotencyKey":key})
    assert executed.status_code==200,executed.text
    assert client.get("/api/v1/crm/activities/"+row["id"],headers=headers(canonical)).status_code==404


def test_nonhuman_write_stays_disabled_despite_crm_role(canonical):
    client,db,provider,tenant,_=canonical
    token=provider.token(tenant,changes={"identity_type":"service","roles":["CRM_BEARBEITEN"],"scope":"crm:write"})
    denied=client.post("/api/v1/crm/activities",headers={"Authorization":"Bearer "+token},
        json={"type":"call","title":"SYNTH agent write","idempotency_key":str(uuid4())})
    assert denied.status_code==403
    assert db.execute(text("SELECT count(*) FROM domain_crm.activities WHERE tenant_id=:t"),{"t":tenant}).scalar()==0


def test_calendar_and_repository_read_the_same_tenant_bound_activity(canonical):
    from datetime import datetime,timezone
    from app.infrastructure.models import Activity
    from app.infrastructure.repositories.implementations import ActivityRepositoryImpl
    from app.services.calendar_projection_service import CrmWiedervorlagenProjector
    client,db,_,tenant,foreign=canonical
    first,_=create(canonical,date="2026-10-15T10:00:00Z");assert first.status_code==201,first.text
    create(canonical,title="Cancelled",date="2026-10-15T10:00:00Z",status="cancelled")
    db.add(Activity(id=str(uuid4()),tenant_id=foreign,type="call",title="Foreign synthetic",customer="",contact_person="",date=None,status="planned",assigned_to="",version=1))
    db.flush()
    records=CrmWiedervorlagenProjector().project(db,tenant,horizon_days=30,now=datetime(2026,10,1,tzinfo=timezone.utc))
    assert len(records)==1 and records[0].object_id==first.json()["id"]
    assert records[0].object_screen_id=="crm/aktivitaet" and records[0].object_route=="/crm/aktivitaet/"+first.json()["id"]
    repository=ActivityRepositoryImpl(db)
    def complete(coroutine):
        try:coroutine.send(None)
        except StopIteration as result:return result.value
        finally:coroutine.close()
        raise AssertionError("Unexpected async suspension")
    assert complete(repository.count(tenant))==2
    assert all(row.tenant_id==tenant for row in complete(repository.get_all(tenant)))
    with pytest.raises(ValueError):complete(repository.count(""))


def test_foreign_customer_is_blocked_by_command_and_database_fk(canonical):
    from app.infrastructure.models import Customer
    from sqlalchemy.exc import IntegrityError
    client,db,_,tenant,foreign=canonical
    customer=str(uuid4())
    db.add(Customer(id=customer,tenant_id=foreign,customer_number="SYNTH-"+uuid4().hex[:12],company_name="Synthetic foreign customer",is_active=True))
    db.flush()
    db.commit()  # Keep the foreign parent in the outer fixture transaction when the rejected command rolls back.
    response,_=create(canonical,customer_id=customer)
    assert response.status_code==404,response.text
    # FK checks bypass RLS: the composite key, not a SELECT filter, must block this write.
    with pytest.raises(IntegrityError) as error:
        with db.begin_nested():
            # Fresh CI does not provision application logins. A missing standard role
            # is created NOLOGIN inside this rolled-back savepoint, never persisted.
            if not db.execute(text("SELECT 1 FROM pg_roles WHERE rolname='valeo_app'")).scalar():
                db.execute(text("CREATE ROLE valeo_app NOLOGIN NOSUPERUSER NOBYPASSRLS"))
            db.execute(text("GRANT USAGE ON SCHEMA domain_crm TO valeo_app"))
            db.execute(text("GRANT INSERT ON domain_crm.activities TO valeo_app"))
            db.execute(text("SET LOCAL ROLE valeo_app"))
            db.execute(text("INSERT INTO domain_crm.activities(id,tenant_id,customer_id,type,title,customer,contact_person,status,assigned_to) VALUES (:id,:tenant,:customer,'call','Synthetic cross reference','','','planned','')"),
                {"id":str(uuid4()),"tenant":tenant,"customer":customer})
    assert getattr(error.value.orig,"pgcode",None)=="23503"


def test_opportunity_rest_mask_and_mcp_replay_one_canonical_command(canonical,monkeypatch):
    from app.services import crm_opportunity_reference
    client,db,_,tenant,foreign=canonical
    own_opportunity=str(uuid4());foreign_opportunity=str(uuid4());calls=[]
    async def source(oid):
        calls.append(oid)
        return {"id":oid,"tenant_id":foreign if oid==foreign_opportunity else tenant,"customer_name":"Synthetic linked customer"}
    monkeypatch.setattr(crm_opportunity_reference,"get_opportunity",source)
    key=str(uuid4())
    first=client.post("/api/v1/crm/opportunities/"+own_opportunity+"/activities",headers={**headers(canonical),"Idempotency-Key":key},
        params={"subject":"SYNTH opportunity note","activity_type":"CALL"})
    assert first.status_code==201,first.text
    assert first.json()["activity_type"]=="call" and calls==[own_opportunity]
    replay=client.post("/api/v1/crm/opportunities/"+own_opportunity+"/actions/create_activity",headers=headers(canonical),
        json={"subject":"SYNTH opportunity note","activity_type":"call","_idempotencyKey":key})
    assert replay.status_code==200,replay.text
    assert replay.json()["success"] is True
    mcp=client.post("/api/v1/mcp/tools/call",headers=headers(canonical),json={"tool_name":"crm.activity.create","mode":"execute","idempotency_key":key,
        "parameters":{"title":"SYNTH opportunity note","type":"call","opportunity_id":own_opportunity}})
    assert mcp.status_code==200,mcp.text
    assert mcp.json()["replayed"] is True and mcp.json()["activity_id"]==first.json()["id"]
    assert calls==[own_opportunity]
    assert db.execute(text("SELECT count(*) FROM domain_crm.activities WHERE tenant_id=:t"),{"t":tenant}).scalar()==1
    assert db.execute(text("SELECT count(*) FROM domain_crm.crm_action_audit_log WHERE tenant_id=:t"),{"t":tenant}).scalar()==1
    assert db.execute(text("SELECT count(*) FROM public.outbox_events WHERE tenant_id=:t"),{"t":tenant}).scalar()==1
    denied=client.post("/api/v1/crm/opportunities/"+foreign_opportunity+"/activities",headers={**headers(canonical),"Idempotency-Key":str(uuid4())},params={"subject":"Foreign"})
    assert denied.status_code==404,denied.text


@pytest.mark.parametrize("ci,database,declared,allowed", [
    (False, "valeo_neuro_erp", "valeo_neuro_erp", False),
    (True, "valeo_neuro_erp", None, True),
    (True, "valeo_test", "another_database", False),
    (False, "valeo_probe", "valeo_probe", True),
])
def test_database_policy_accepts_only_declared_ci_or_explicit_local_probe(monkeypatch,ci,database,declared,allowed):
    from types import SimpleNamespace
    import sys
    url=make_url("postgresql://synthetic@localhost/"+database)
    monkeypatch.setattr(sys.modules[__name__],"engine",SimpleNamespace(url=url))
    monkeypatch.setenv("CI","true" if ci else "false")
    monkeypatch.setenv("DATABASE_URL",str(url))
    monkeypatch.delenv("TEST_DATABASE_URL",raising=False)
    if declared:monkeypatch.setenv("TEST_DATABASE_URL","postgresql://synthetic@localhost/"+declared)
    if allowed:require_db.__wrapped__()
    else:
        with pytest.raises(AssertionError,match="Explicit shared test database"):
            require_db.__wrapped__()
