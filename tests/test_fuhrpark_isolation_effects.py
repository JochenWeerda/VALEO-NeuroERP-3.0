"""Real shared-probe effects: no new database, own rows rolled back."""
from datetime import datetime, timezone
import os
from uuid import uuid4
from unittest.mock import Mock

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.api.v1.endpoints import fuhrpark
from app.auth.deps_oidc import get_current_user
from app.core.database import get_db
from app.domains.operations import models, repository
from app.services import mcp_execution_service as mcp
from app.services.mcp_tool_registry_service import mcp_tool_registry_service as registry

CASES = [
    ("fahrzeuge", models.Fahrzeug, repository.FahrzeugRepository, {"kennzeichen":"TEST-01", "typ":"LKW"}, "logistik.fahrzeug.speichern"),
    ("terminarten", models.FuhrparkTerminart, repository.FuhrparkTerminartRepository, {"terminart":"TEST-TUEV"}, "logistik.terminart.speichern"),
    ("rechnungen", models.FuhrparkRechnung, repository.FuhrparkRechnungRepository, {"rechnungs_nr":"TEST-R01", "datum":datetime(2026,10,9,tzinfo=timezone.utc), "betrag_eur":10}, "logistik.rechnung.speichern"),
    ("ausgehende-dokumente", models.FuhrparkAusgehendesDokument, repository.FuhrparkAusgehendesDokumentRepository, {"beleg_typ":"TEST-PDF"}, "logistik.ausgehendes_dokument.speichern"),
]

@pytest.fixture
def db():
    from sqlalchemy.engine import make_url
    is_github_job = os.environ.get("GITHUB_ACTIONS") == "true"
    raw = os.environ.get("TEST_DATABASE_URL") or (
        os.environ.get("DATABASE_URL") if is_github_job else None
    )
    if not raw:
        pytest.fail("Set TEST_DATABASE_URL to the existing shared probe; no local development fallback")
    url = make_url(raw)
    assert url.database and (
        any(k in url.database for k in ("test", "probe", "pruefstand"))
        or (is_github_job and url.database == "valeo_neuro_erp")
    ), "Use only the shared probe or the database already provided by the GitHub job"
    engine=create_engine(url, connect_args={"connect_timeout":5})
    with engine.connect() as connection:
        transaction=connection.begin()
        with Session(bind=connection, join_transaction_mode="create_savepoint") as session:
            yield session
        transaction.rollback()
    engine.dispose()

@pytest.fixture
def seeded(db):
    tenant="iso-"+uuid4().hex
    foreign=tenant+"-foreign"
    ids={}
    for name, model, repo, data, tool in CASES:
        row=repo(db).create(foreign, data, commit=False)
        ids[name]=row.id
    db.commit()
    return tenant, foreign, ids

def client(db, tenant):
    app=FastAPI();app.include_router(fuhrpark.router,prefix="/api/v1")
    app.dependency_overrides[get_db]=lambda:db
    app.dependency_overrides[get_current_user]=lambda:{"sub":"isolation-test", "scopes":["logistics:read","logistics:write"], "raw":{"tenant_id":tenant}}
    return TestClient(app)

def body(data):
    return {k:v.isoformat() if isinstance(v,datetime) else v for k,v in data.items()}

@pytest.mark.needs_live_db
@pytest.mark.parametrize("case", CASES, ids=lambda c:c[0])
def test_repository_crud_foreign_rows_are_invisible(db, seeded, case):
    tenant,foreign,ids=seeded
    name,model,repo,data,_=case
    service=repo(db)
    assert service.get_by_id(tenant,ids[name]) is None
    assert service.get_all(tenant)==[]
    assert service.update(tenant,ids[name],data,commit=False) is None
    assert service.delete(tenant,ids[name],commit=False) is False
    row=service.get_by_id(foreign,ids[name]);assert row and row.tenant_id==foreign
    own=service.create(tenant,data,commit=False)
    assert own.tenant_id==tenant

@pytest.mark.needs_live_db
@pytest.mark.parametrize("case", CASES, ids=lambda c:c[0])
@pytest.mark.parametrize("mode", ["validate","dryRun","propose","execute"])
def test_http_command_rejects_foreign_entity_in_all_modes(db, seeded, case, mode):
    tenant,foreign,ids=seeded
    name,model,repo,data,_=case
    response=client(db,tenant).post(f"/api/v1/fuhrpark/{name}/actions/speichern",headers={"X-Tenant-ID":tenant},json={**body(data),"id":ids[name],"_mode":mode})
    assert response.status_code==200
    assert response.json()["success"] is False
    assert repo(db).get_by_id(foreign,ids[name]) is not None
    assert repo(db).get_all(tenant)==[]

@pytest.mark.needs_live_db
@pytest.mark.parametrize("case", CASES, ids=lambda c:c[0])
@pytest.mark.parametrize("mode", ["validate","dryRun","propose","execute"])
def test_mcp_command_rejects_foreign_entity_in_all_modes(db, seeded, case, mode):
    tenant,foreign,ids=seeded
    name,model,repo,data,tool=case
    user={"sub":"isolation-test", "scopes":["logistics:write"],"raw":{"tenant_id":tenant}}
    request=mcp.ToolExecutionRequest(tool_name=tool,parameters={**body(data),"id":ids[name],"reason":"isolation test"},mode=mode,idempotency_key=uuid4().hex)
    with pytest.raises(HTTPException) as error:mcp.execute_mcp_tool(db,request,user,tenant)
    assert error.value.status_code==404
    assert repo(db).get_by_id(foreign,ids[name]) is not None

@pytest.mark.needs_live_db
@pytest.mark.parametrize("case", CASES, ids=lambda c:c[0])
def test_http_header_cannot_choose_foreign_tenant(db,seeded,case):
    tenant,foreign,ids=seeded
    response=client(db,tenant).get(f"/api/v1/fuhrpark/{case[0]}",headers={"X-Tenant-ID":foreign})
    assert response.status_code==403

@pytest.mark.needs_live_db
@pytest.mark.parametrize("mode", ["validate","dryRun","propose","execute"])
def test_invoice_cannot_reference_foreign_vehicle(db,seeded,mode):
    tenant,foreign,ids=seeded
    response=client(db,tenant).post("/api/v1/fuhrpark/rechnungen/actions/speichern",headers={"X-Tenant-ID":tenant},json={"rechnungs_nr":"OWN-INV", "datum":"2026-10-09", "betrag_eur":10,"fahrzeug_id":ids["fahrzeuge"],"_mode":mode})
    assert response.json()["success"] is False
    assert repository.FuhrparkRechnungRepository(db).get_all(tenant)==[]

@pytest.mark.parametrize("tool", registry.list_tools(), ids=lambda t:t["tool_id"])
@pytest.mark.parametrize("poison", ["tenant_id","mandanten_id"])
def test_every_registered_tool_rejects_tenant_override_before_sql(tool,poison):
    db=Mock()
    user={"sub":"isolation-test", "scopes":[tool["scope"]],"raw":{"tenant_id":"tenant-a"}}
    with pytest.raises(HTTPException) as error:
        mcp.execute_mcp_tool(db,mcp.ToolExecutionRequest(tool_name=tool["tool_id"],parameters={poison:"tenant-b"}),user,"tenant-a")
    assert error.value.status_code==422
    db.execute.assert_not_called();db.commit.assert_not_called()

def test_conflicting_token_tenant_aliases_are_rejected():
    db=Mock();user={"sub":"test", "raw":{"tenant_id":"tenant-a","mandanten_id":"tenant-b"},"scopes":["crm:read"]}
    with pytest.raises(HTTPException) as error:
        mcp.execute_mcp_tool(db,mcp.ToolExecutionRequest(tool_name="crm.customer.search",parameters={"query":"test"}),user,None)
    assert error.value.status_code==403
    db.execute.assert_not_called()


@pytest.mark.needs_live_db
@pytest.mark.parametrize("case", CASES, ids=lambda c:c[0])
@pytest.mark.parametrize("failure", [None,"audit"])
@pytest.mark.parametrize("transport", ["http","mcp"])
def test_real_writes_and_audit_are_atomic(db,seeded,case,failure,transport):
    from unittest.mock import patch
    from app.services import mask_action_runtime_service as runtime
    tenant,foreign,ids=seeded
    name,model,repo,data,tool=case
    module=runtime if transport=="http" else mcp
    actual=module._write_audit
    def audit(*args,**kwargs):
        result=actual(*args,**kwargs)
        if failure:raise RuntimeError("synthetic audit failure")
        return result
    with patch.object(module,"_write_audit",side_effect=audit):
        if transport=="http":
            result=client(db,tenant).post(f"/api/v1/fuhrpark/{name}/actions/speichern",headers={"X-Tenant-ID":tenant},json={**body(data),"_mode":"execute"}).json()
            assert result["success"] is (failure is None)
        else:
            user={"sub":"test", "scopes":["logistics:write"], "raw":{"tenant_id":tenant}}
            request=mcp.ToolExecutionRequest(tool_name=tool,parameters={**body(data),"reason":"atomic effects"},mode="execute",idempotency_key="same-key")
            if failure:
                with pytest.raises(HTTPException) as error:mcp.execute_mcp_tool(db,request,user,None)
                assert error.value.status_code==503
            else:
                result=mcp.execute_mcp_tool(db,request,user,None)
                assert result["success"] is True
                replay=mcp.execute_mcp_tool(db,request,user,None)
                assert replay["replayed"] is True
    assert len(repo(db).get_all(tenant))==(0 if failure else 1)
    audits=db.execute(text("SELECT COUNT(*) FROM domain_crm.crm_action_audit_log WHERE tenant_id=:tenant"),{"tenant":tenant}).scalar_one()
    assert audits==(0 if failure else 1)
    assert repo(db).get_by_id(foreign,ids[name]) is not None

@pytest.mark.needs_live_db
@pytest.mark.parametrize("case", CASES, ids=lambda c:c[0])
def test_repository_cannot_change_primary_key_or_tenant(db,seeded,case):
    tenant,foreign,ids=seeded
    name,model,repo,data,tool=case
    service=repo(db)
    row=service.update(foreign,ids[name],{"id":"injected-id","tenant_id":tenant,"mandanten_id":tenant},commit=False)
    assert row.id==ids[name] and row.tenant_id==foreign

@pytest.mark.needs_live_db
@pytest.mark.parametrize("mode", ["validate","dryRun","propose","execute"])
def test_mcp_delete_rejects_actual_foreign_vehicle(db,seeded,mode):
    tenant,foreign,ids=seeded
    user={"sub":"test", "scopes":["logistics:write"],"raw":{"tenant_id":tenant}}
    with pytest.raises(HTTPException) as error:
        mcp.execute_mcp_tool(db,mcp.ToolExecutionRequest(tool_name="logistik.fahrzeug.loeschen",parameters={"fahrzeug_id":ids["fahrzeuge"],"reason":"isolation"},mode=mode,idempotency_key="delete-test"),user,None)
    assert error.value.status_code==404
    assert repository.FahrzeugRepository(db).get_by_id(foreign,ids["fahrzeuge"]) is not None

@pytest.mark.parametrize("tool", registry.list_tools(), ids=lambda t:t["tool_id"])
def test_all_registered_tools_reject_foreign_header_without_sql(tool):
    db=Mock();user={"sub":"test", "scopes":[tool["scope"]],"raw":{"tenant_id":"tenant-a"}}
    with pytest.raises(HTTPException) as error:
        mcp.execute_mcp_tool(db,mcp.ToolExecutionRequest(tool_name=tool["tool_id"],parameters={}),user,"tenant-b")
    assert error.value.status_code==403
    db.execute.assert_not_called();db.commit.assert_not_called()
