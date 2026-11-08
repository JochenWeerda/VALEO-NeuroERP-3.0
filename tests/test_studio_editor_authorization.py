"""Studio edits use existing domain roles; read-only customers cannot mutate metadata."""
from uuid import uuid4
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.api.v1.endpoints import studio_drafts
from app.auth.deps import get_current_user
from app.core.tenant import get_tenant_id
from app.services import studio_draft_store as store
from app.services.studio_propose import propose_studio_draft

@pytest.fixture(autouse=True)
def _enable_dev_token():
    yield

@pytest.mark.parametrize("roles", [["EINKAUF_LESEN"],["PORTAL_INHABER"],[]])
def test_read_only_identity_cannot_create_update_review_or_simulate(roles):
    store.reset_studio_drafts()
    app=FastAPI();app.include_router(studio_drafts.router)
    app.dependency_overrides[get_current_user]=lambda:{"sub":"synthetic-reader","roles":roles,"raw":{"identity_type":"human"}}
    app.dependency_overrides[get_tenant_id]=lambda:"own"
    client=TestClient(app)
    before=store.save_draft("own","editor",propose_studio_draft("Artikel"))
    key=str(uuid4());path="/studio/drafts/"+before["id"]
    assert client.post("/studio/drafts",json={"definition":before["definition"],"idempotency_key":key}).status_code==403
    assert client.put(path,json={"definition":before["definition"],"expected_revision":before["revision"],"idempotency_key":key}).status_code==403
    for action in ("submit-review","simulate"):
        assert client.post(path+"/"+action,json={"expected_revision":before["revision"],"idempotency_key":key}).status_code==403
    assert store.get_draft("own",before["id"])==before
    assert store.count_history("own",before["id"])==1
    assert client.get("/studio/catalog").json()["permissions"]=={"canDesign":False,"canPublish":False}
    store.use_sql_studio_drafts()
