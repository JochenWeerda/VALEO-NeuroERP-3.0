"""Canonical roles and verified audit authors guard harvest commands before storage."""
from types import SimpleNamespace
from unittest.mock import MagicMock
import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from app.auth.deps import get_current_user
from app.core.tenant import get_tenant_id
from app.core.database import get_db
from app.core.exceptions import EntityNotFoundError, ValidationFailedError
from app.api.v1.endpoints import harvest_acceptance as api
from app.services.harvest_acceptance_service import HarvestAcceptanceService

@pytest.fixture(autouse=True)
def _enable_dev_token():
    yield

@pytest.mark.parametrize("roles",[["PORTAL_INHABER"],["EINKAUF_LESEN"],[]])
def test_read_only_principal_cannot_release_stock_or_self_billing(monkeypatch,roles):
    app=FastAPI();app.include_router(api.router,prefix="/harvest")
    app.dependency_overrides[get_current_user]=lambda:{"sub":"reader","roles":roles}
    app.dependency_overrides[get_tenant_id]=lambda:"own"
    app.dependency_overrides[get_db]=lambda:MagicMock()
    def unexpected(*args):
        pytest.fail("Unauthorized harvest command reached storage")
    monkeypatch.setattr(api,"_svc",unexpected)
    response=TestClient(app).post("/harvest/owned/release?release_status=final")
    assert response.status_code==403


def test_release_author_is_verified_subject_not_header(monkeypatch):
    app=FastAPI();app.include_router(api.router,prefix="/harvest")
    app.dependency_overrides[get_current_user]=lambda:{"sub":"verified-actor","roles":["EINKAUF_BEARBEITEN"]}
    def tenant(request:Request):
        request.state.tenant_verified=True;request.state.token_claims={"sub":"verified-actor"}
        return "own"
    app.dependency_overrides[get_tenant_id]=tenant
    app.dependency_overrides[get_db]=lambda:MagicMock()
    captured=[]
    class Probe:
        def release_acceptance(self,*args):
            captured.append(args);raise EntityNotFoundError("HarvestAcceptance","owned")
    monkeypatch.setattr(api,"_svc",lambda *args:Probe())
    response=TestClient(app).post("/harvest/owned/release?release_status=final",headers={"X-User-ID":"spoofed"})
    assert response.status_code==404
    assert captured[0][-1]=="verified-actor"

@pytest.mark.parametrize("status",["final","credit_note_created","paid"])
def test_settlement_cannot_recalculate_frozen_acceptance(status):
    db=MagicMock();svc=HarvestAcceptanceService(db,"own")
    svc._get_or_raise=lambda _,**kwargs:SimpleNamespace(release_status=status,invoice_id="issued")
    with pytest.raises(ValidationFailedError):
        svc.calculate_settlement("owned")
    db.commit.assert_not_called()

@pytest.mark.parametrize("field",["tenant_id","id","invoice_id","release_status"])
def test_service_update_rejects_identity_and_command_field_overrides(field):
    db=MagicMock();svc=HarvestAcceptanceService(db,"own")
    obj=SimpleNamespace(release_status="draft",invoice_id=None)
    svc._get_or_raise=lambda _,**kwargs:obj
    with pytest.raises(ValidationFailedError):
        svc.update_acceptance("owned",{field:"foreign"},"actor")
    db.commit.assert_not_called()

@pytest.mark.parametrize("field",["article_id","warehouse_id","weighing_ticket_id","contract_id"])
def test_foreign_reference_blocks_before_mutation(field):
    db=MagicMock();db.query.return_value.filter.return_value.first.return_value=None
    svc=HarvestAcceptanceService(db,"own")
    with pytest.raises(ValidationFailedError):
        svc._validate_references({field:"foreign-id"})
    db.commit.assert_not_called()
