"""Bound migration plans: immutable existing history, retries, SQL and signed HTTP."""
from copy import deepcopy
from uuid import uuid4
import json

import pytest
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, DBAPIError

from app.api.v1.schemas.studio_migration import StudioSavedMigrationIn
from app.core.studio_release import definition_hash
from app.services import studio_draft_store as store, studio_migration_store as plans
from app.services.studio_propose import propose_studio_draft
from test_gdpr_subject_boundary import subject_data, keys, probe  # noqa: F401


def definition():
    item = propose_studio_draft("Kunden")
    item["id"] = "tenant/plan-" + uuid4().hex[:12]
    item["adapter"]["sourceId"] = item["id"]
    return item


def request(item, **kwargs):
    return StudioSavedMigrationIn(expected_revision=item["revision"], idempotency_key=uuid4(), **kwargs)


@pytest.fixture
def memory():
    store.reset_studio_drafts()
    yield store.save_draft("own", "editor", definition())
    store.reset_studio_drafts()


def test_revision_bound_plan_does_not_change_candidate_or_publish(memory):
    body = request(memory)
    result = plans.save_migration_plan("own", memory["id"], "planner", body)
    assert result["candidate_revision"] == memory["revision"]
    assert result["candidate_definition_hash"] == definition_hash(memory["definition"])
    assert result["plan"]["actor"] == "planner" and result["plan"]["tenant_id"] == "own"
    assert result["plan"]["can_activate"] is False
    assert all(value == "not_verified" for value in result["plan"]["channel_status"].values())
    assert store.get_draft("own", memory["id"]) == memory
    history = store.list_history("own", memory["id"])
    assert len(history) == 2 and history[-1]["action"] == "migration_plan"
    assert history[-1]["snapshot"]["saved_migration"] == result
    result["plan"]["definition"]["title"] = "mutated response"
    assert store.list_history("own", memory["id"])[-1] == history[-1]


def test_retry_returns_original_without_recompiling(memory, monkeypatch):
    body = request(memory)
    result = plans.save_migration_plan("own", memory["id"], "editor", body)
    monkeypatch.setattr(plans, "plan_migration", lambda *a: pytest.fail("Retry must not recompile"))
    assert plans.save_migration_plan("own", memory["id"], "editor", body) == result
    assert len(store.list_history("own", memory["id"])) == 2


@pytest.mark.parametrize("change", ["tenant", "actor", "revision", "schema", "draft"])
def test_idempotency_cannot_change_context_or_request(memory, change):
    body = request(memory)
    plans.save_migration_plan("own", memory["id"], "editor", body)
    tenant, draft, actor = "own", memory["id"], "editor"
    if change == "tenant": tenant = "foreign"
    if change == "actor": actor = "forged"
    if change == "revision": body = body.model_copy(update={"expected_revision":"0"*64})
    if change == "draft": draft = str(uuid4())
    if change == "schema":
        body = StudioSavedMigrationIn(expected_revision=body.expected_revision,idempotency_key=body.idempotency_key,
            schema_changes=[{"operation":"create_table","schema_name":"domain_crm","table":"plan_test","columns":[{"name":"note","type":"text"}]}])
    with pytest.raises(ValueError): plans.save_migration_plan(tenant, draft, actor, body)
    assert len(store.list_history("own", memory["id"])) == 2


def test_foreign_or_stale_candidate_never_creates_plan(memory):
    with pytest.raises(KeyError): plans.save_migration_plan("foreign", memory["id"], "editor", request(memory))
    with pytest.raises(ValueError): plans.save_migration_plan("own", memory["id"], "editor", request(memory).model_copy(update={"expected_revision":"0"*64}))
    assert len(store.list_history("own", memory["id"])) == 1


def test_failed_compilation_leaves_no_event(memory, monkeypatch):
    def fail(*args): raise ValueError("compiler unavailable")
    monkeypatch.setattr(plans, "plan_migration", fail)
    with pytest.raises(ValueError): plans.save_migration_plan("own", memory["id"], "editor", request(memory))
    assert len(store.list_history("own", memory["id"])) == 1


@pytest.fixture
def signed(subject_data, require_db, monkeypatch):
    from app.api.v1.endpoints import studio_drafts
    from app.core.tenant_binding import install_tenant_bindings
    from main import BearerAuthMiddleware
    client, db, provider, own, foreign, *_ = subject_data
    db.commit()  # Release fixture savepoint; the outer test transaction remains.
    monkeypatch.setattr(store, "_prefer_memory", False)
    monkeypatch.setattr(store, "_sql_session", lambda: Session(bind=db.get_bind(), join_transaction_mode="create_savepoint"))
    client.app.include_router(studio_drafts.router, prefix="/api/v1")
    install_tenant_bindings(client.app, public_paths=BearerAuthMiddleware.PUBLIC_PATHS)
    item = store.save_draft(own, "editor", definition())
    return client, provider, own, foreign, item


def headers(data, role="FINANCE_ADMIN", tenant=None):
    return {"Authorization":"Bearer "+data[1].token(tenant or data[2], changes={"sub":"planner", "roles":[role] if role else []})}


def test_signed_http_cli_and_sql_share_immutable_plan(signed, monkeypatch):
    from valeo_cli import cli
    client, _, tenant, _, item = signed
    body = request(item).model_dump(mode="json")
    path = "/api/v1/studio/drafts/"+item["id"]+"/migration-plan"
    auth = headers(signed)
    response = client.post(path, headers={**auth,"X-Actor-ID":"forged"}, json=body)
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["plan"]["actor"] == "planner" and result["plan"]["tenant_id"] == tenant
    assert store.history_event(tenant,item["id"],event_id=body["idempotency_key"])["snapshot"]["saved_migration"] == result
    monkeypatch.setenv("VALEO_ACCESS_TOKEN",auth["Authorization"][7:])
    lines=[]
    assert cli.main(["studio","plan-speichern",item["id"],"--revision",item["revision"],"--idempotenz",body["idempotency_key"]],http=client,out=lines.append) == 0
    assert json.loads(lines[0]) == result
    assert len(store.list_history(tenant,item["id"])) == 2
    assert store.get_draft(tenant,item["id"]) == item
    with store._sql_session() as db:
        with pytest.raises(DBAPIError):
            db.execute(text("UPDATE domain_shared.screen_definition_history SET actor='forged' WHERE id=:id"),{"id":body["idempotency_key"]})
        db.rollback()
    assert store.history_event(tenant,item["id"],event_id=body["idempotency_key"])["actor"] == "planner"


@pytest.mark.parametrize("kind,expected",[("foreign",404),("no_role",403),("forged_tenant",403),("forged_actor",422),("invalid_token",401),("missing_token",401)])
def test_signed_permissions_and_tenant_binding(signed, kind, expected):
    client, _, tenant, foreign, item = signed
    body = request(item).model_dump(mode="json")
    auth = headers(signed,role=None if kind=="no_role" else "FINANCE_ADMIN", tenant=foreign if kind=="foreign" else None)
    if kind == "forged_tenant": auth["X-Tenant-ID"] = foreign
    if kind == "forged_actor": body["actor"] = "forged"
    if kind == "invalid_token": auth={"Authorization":"Bearer invalid"}
    if kind == "missing_token": auth={}
    response=client.post("/api/v1/studio/drafts/"+item["id"]+"/migration-plan",headers=auth,json=body)
    assert response.status_code == expected,response.text
    assert len(store.list_history(tenant,item["id"])) == 1


def test_sql_history_failure_rolls_back_plan(signed, monkeypatch):
    item=signed[4]
    def fail(*args): raise OperationalError("INSERT history",{},Exception("synthetic database failure"))
    monkeypatch.setattr(store,"_append_sql_history",fail)
    with pytest.raises(store.StudioStorageUnavailable): plans.save_migration_plan(signed[2],item["id"],"planner",request(item))
    assert len(store.list_history(signed[2],item["id"])) == 1
    assert store.get_draft(signed[2],item["id"]) == item


def test_draft_edit_requires_new_plan_and_old_retry_stays_historical(memory):
    body = request(memory)
    old = plans.save_migration_plan("own",memory["id"],"editor",body)
    changed = deepcopy(memory["definition"])
    changed["title"] = "New candidate"
    current = store.save_draft("own","editor",changed,draft_id=memory["id"],expected_revision=memory["revision"])
    with pytest.raises(ValueError,match="entwurf_seit_anzeige_geaendert"):
        plans.save_migration_plan("own",memory["id"],"editor",body.model_copy(update={"idempotency_key":uuid4()}))
    assert plans.save_migration_plan("own",memory["id"],"editor",body) == old
    new = plans.save_migration_plan("own",memory["id"],"editor",request(current))
    assert new["binding_hash"] != old["binding_hash"]
    assert new["candidate_revision"] == current["revision"]


def test_wiring_suggestions_are_not_saved_silently(memory):
    initial = plans.save_migration_plan("own",memory["id"],"editor",request(memory))
    assert initial["requires_definition_update"] == (initial["candidate_definition_hash"] != initial["plan"]["definition_hash"])
    saved = store.save_draft("own","editor",initial["plan"]["definition"],draft_id=memory["id"],expected_revision=memory["revision"])
    bound = plans.save_migration_plan("own",memory["id"],"editor",request(saved))
    assert bound["requires_definition_update"] is False


@pytest.mark.parametrize("status",["retired","published_temp"])
def test_new_plan_rejects_closed_or_published_candidate(memory,status):
    store._DRAFTS[memory["id"]]["status"] = status  # Unit setup only, no production status bypass.
    current = store.get_draft("own",memory["id"])
    with pytest.raises(ValueError,match="migrationsplan_erfordert_entwurf_oder_review"):
        plans.save_migration_plan("own",memory["id"],"editor",request(current))
    assert len(store.list_history("own",memory["id"])) == 1


def test_sql_retry_cannot_replace_schema_or_actor(signed):
    client,provider,tenant,_,item=signed
    body=request(item).model_dump(mode="json")
    path="/api/v1/studio/drafts/"+item["id"]+"/migration-plan"
    auth=headers(signed)
    assert client.post(path,headers=auth,json=body).status_code == 200
    changed={**body,"schema_changes":[{"operation":"create_table","schema_name":"domain_crm","table":"plan_changed","columns":[{"name":"note","type":"text"}]}]}
    response=client.post(path,headers=auth,json=changed)
    assert response.status_code == 409 and response.json()["detail"] == "idempotenzschluessel_anderer_inhalt"
    other={"Authorization":"Bearer "+provider.token(tenant,changes={"sub":"different-planner","roles":["FINANCE_ADMIN"]})}
    assert client.post(path,headers=other,json=body).status_code == 409
    assert len(store.list_history(tenant,item["id"])) == 2
