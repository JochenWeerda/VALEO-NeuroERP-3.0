"""Direct domain authorization also rejects the retired generic role."""
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi import HTTPException
from starlette.requests import Request
from app.agrar.rations import authz
from app.core.akteur import verlange_rolle
from app.domains.inventory.api import inventory_auth
from app.services.recent_documents_service import RecentDocumentsService, RecentDocumentError
from app.api.v1.endpoints import kontrolle, billing_batch
from app.services import finance_freigabe
from importlib import import_module
policy_router = import_module("app.policy.router")


@pytest.mark.parametrize("allowed", [authz.READ_ROLES, authz.WRITE_ROLES, authz.APPROVE_ROLES, authz.CONNECTOR_ADMIN_ROLES])
def test_feed_manager_denied_and_explicit_domain_role_preserved(allowed):
    with pytest.raises(HTTPException) as error:
        authz.require_roles({"roles": ["manager"]}, allowed)
    assert error.value.status_code == 403
    authz.require_roles({"roles": ["manager", "FUTTERMITTEL_ADMIN"]}, allowed)


def test_action_guard_cannot_reintroduce_manager_from_legacy_allowed_list():
    with pytest.raises(HTTPException) as error:
        verlange_rolle({"roles": ["manager"]}, "manager", "FINANCE_BEARBEITEN")
    assert error.value.status_code == 403
    verlange_rolle({"roles": ["manager", "FINANCE_BEARBEITEN"]}, "FINANCE_BEARBEITEN")


@pytest.mark.parametrize("local", [None, SimpleNamespace(is_active=True, roles='["manager"]')])
def test_inventory_manager_denied_even_with_legacy_local_manager_profile(local):
    db = Mock()
    db.query.return_value.filter.return_value.first.return_value = local
    request = Request({"type": "http", "headers": []})
    request.state.token_claims = {"sub": "synthetic", "tenant_id": "synthetic-tenant", "roles": ["manager"]}
    with pytest.raises(HTTPException) as error:
        inventory_auth.require_inventory_access(request, token="verified", db=db)
    assert error.value.status_code == 403


def test_inventory_explicit_domain_role_still_works_without_local_fallback():
    db = Mock()
    request = Request({"type": "http", "headers": []})
    request.state.token_claims = {"sub": "synthetic", "roles": ["manager", "LAGER_LESEN"]}
    assert inventory_auth.require_inventory_access(request, token="verified", db=db) == "verified"
    db.query.assert_not_called()


def test_recent_document_manager_denied_before_database_access():
    db = Mock()
    service = RecentDocumentsService(db, "synthetic-tenant", "synthetic", ["manager"])
    with pytest.raises(RecentDocumentError):
        service.touch({"screen_id": "finance/journal"})
    db.execute.assert_not_called()
    RecentDocumentsService(db, "synthetic-tenant", "synthetic", ["manager", "FINANCE_LESEN"])._authorize("FINANCE_LESEN")


def test_control_reader_manager_denied_and_finance_reader_preserved():
    with pytest.raises(HTTPException) as error:
        kontrolle._nur_leser({"roles": ["manager"]})
    assert error.value.status_code == 403
    kontrolle._nur_leser({"roles": ["manager", "FINANCE_LESEN"]})


def test_batch_and_financial_approval_roles_have_no_generic_grant():
    for _, roles in billing_batch._BATCH_ACTIONS.values():
        with pytest.raises(HTTPException):
            verlange_rolle({"roles": ["manager"]}, *roles)
    engine = finance_freigabe.HauptbuchFreigabe(Mock(), "synthetic-tenant")
    assert "manager" not in engine.leserollen(None)
    assert "manager" not in engine.anfragerollen(None, "post")
    assert "FINANCE_BEARBEITEN" in engine.anfragerollen(None, "post")


@pytest.mark.parametrize("roles,allowed", [(["manager"], False), (["manager", "admin"], True)])
def test_policy_websocket_manager_denied_after_verified_identity(monkeypatch, roles, allowed):
    context = {"roles": roles, "subject": "synthetic", "tenant_id": "synthetic-tenant"}
    monkeypatch.setattr("app.core.security.verified_websocket_context", lambda *args: context)
    if allowed:
        assert policy_router._resolve_policy_ws_auth(Mock(), "verified") is context
    else:
        with pytest.raises(HTTPException) as error:
            policy_router._resolve_policy_ws_auth(Mock(), "verified")
        assert error.value.status_code == 403
