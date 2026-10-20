"""Signed identities and real shared-probe transactions, never a new database."""
from uuid import uuid4
import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api.v1.endpoints import ap_approval_workflow, ap_invoices
from app.core.database import get_db
from app.core.tenant_binding import install_tenant_bindings
from app.documents.repository import DocumentRepository
from main import BearerAuthMiddleware
from test_gdpr_subject_boundary import subject_data, keys, probe  # noqa: F401


PREFIX = "/api/v1/finance/ap/approval-workflow"


@pytest.fixture
def case(subject_data, monkeypatch):
    monkeypatch.setattr("app.core.endpoint_gateways._approval_workflow_gateway", None)
    _, db, provider, tenant, foreign, *_ = subject_data
    own, other = "ap-review-" + uuid4().hex, "ap-review-" + uuid4().hex
    for number, tid in [(own, tenant), (other, foreign)]:
        DocumentRepository(db).save_document("ap_invoice", number,
            {"number": number, "tenantId": tid, "status": "ENTWURF", "totalGross": 119.0,
             "customerId": "synthetic-supplier", "createdBy": "creator", "items": []}, commit=False)
    db.commit()  # Release fixture savepoint; the outer transaction always rolls back.
    app = FastAPI()
    app.add_middleware(BearerAuthMiddleware)
    app.include_router(ap_approval_workflow.router, prefix="/api/v1/finance")
    app.include_router(ap_invoices.router, prefix="/api/v1/finance")
    app.dependency_overrides[get_db] = lambda: db
    install_tenant_bindings(app, public_paths=BearerAuthMiddleware.PUBLIC_PATHS)
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client, db, provider, tenant, foreign, own, other


def headers(case, subject="human-a", role="FINANCE_ADMIN", tenant=None, **claims):
    return {"Authorization": "Bearer " + case[2].token(tenant or case[3],
        changes={"sub": subject, "roles": [role] if role else [], **claims})}


def request(case, **body):
    response = case[0].post(PREFIX + "/request", headers=headers(case),
        json={"invoice_id": case[5], "requested_by": "forged-requester", **body})
    assert response.status_code == 200, response.text
    return response.json()


def decide(case, request_id, subject="human-b", action="approve", **body):
    return case[0].post(PREFIX + "/approve", headers=headers(case, subject), json={
        "invoice_id": case[5], "approval_request_id": request_id, "approved_by": "forged-reviewer",
        "action": action, **body})


def count(case, table):
    assert table in {"ap_approval_requests", "ap_approvals"}
    return case[1].execute(text(f"SELECT count(*) FROM domain_erp.{table} WHERE tenant_id=:t"),
        {"t": case[3]}).scalar_one()


def test_verified_requester_replay_independent_decision_and_raw_audit_subject(case):
    first = request(case)
    assert first["status"] == "pending" and not first["can_post"]
    assert request(case)["approval_request_id"] == first["approval_request_id"]
    assert count(case, "ap_approval_requests") == 1
    stored = case[1].execute(text("SELECT requested_by FROM domain_erp.ap_approval_requests WHERE id=:id"),
        {"id": first["approval_request_id"]}).scalar_one()
    assert stored == "human-a"
    result = decide(case, first["approval_request_id"], subject="human-b")
    assert result.status_code == 200, result.text
    assert result.json()["status"] == "approved" and result.json()["current_approvals"] == 1
    assert result.json()["approvals"][0]["approved_by"] == "human-b"
    assert decide(case, first["approval_request_id"]).status_code == 200
    assert count(case, "ap_approvals") == 1
    assert decide(case, first["approval_request_id"], action="reject").status_code == 409
    audit = case[1].execute(text("""SELECT user_id, changes FROM domain_shared.audit_logs
        WHERE tenant_id=:t AND entity_id=:id AND action='ap_approval_approve'"""),
        {"t": case[3], "id": case[5]}).one()
    assert audit[0] == "human-b" and audit[1]["approval_request_id"] == first["approval_request_id"]


@pytest.mark.parametrize("subject", ["human-a", "creator"])
def test_requester_and_document_creator_cannot_decide_even_as_admin(case, subject):
    pending = request(case)
    result = decide(case, pending["approval_request_id"], subject=subject)
    assert result.status_code == 403, result.text
    assert count(case, "ap_approvals") == 0


@pytest.mark.parametrize("role", [None, "manager", "FINANCE_LESEN", "EINKAUF_ADMIN"])
def test_invalid_decision_roles_never_reach_database(case, monkeypatch, role):
    monkeypatch.setattr(case[1], "execute", lambda *a, **k: pytest.fail("Denied role reached SQL"))
    response = case[0].post(PREFIX + "/approve", headers=headers(case, role=role),
        json={"invoice_id": case[5], "approval_request_id": "x", "action": "approve"})
    assert response.status_code == 403, response.text


def test_foreign_objects_request_ids_and_tenant_header_are_rejected(case):
    pending = request(case)
    foreign = case[0].post(PREFIX + "/request", headers=headers(case, tenant=case[4]), json={"invoice_id": case[6]})
    assert foreign.status_code == 200, foreign.text
    assert decide(case, foreign.json()["approval_request_id"]).status_code == 409
    assert case[0].get(PREFIX + "/status/" + case[5], headers=headers(case, tenant=case[4])).status_code == 404
    assert case[0].post(PREFIX + "/request", headers=headers(case), json={"invoice_id": case[6]}).status_code == 404
    assert case[0].post(PREFIX + "/approve", headers={**headers(case), "X-Tenant-ID": case[4]},
        json={"invoice_id": case[5], "approval_request_id": pending["approval_request_id"], "action": "approve"}).status_code == 403
    assert count(case, "ap_approvals") == 0


@pytest.mark.parametrize("status", ["ENTWURF", "FREIGEGEBEN", "unrecognized"])
def test_invoice_status_without_persisted_review_never_grants_approval(case, status):
    case[1].execute(text("UPDATE documents SET data=jsonb_set(CAST(data AS jsonb),'{status}',CAST(:s AS jsonb)) WHERE doc_number=:id"),
        {"s": json.dumps(status), "id": case[5]})
    result = case[0].get(PREFIX + "/status/" + case[5], headers=headers(case))
    assert result.status_code == 200, result.text
    assert result.json()["status"] == "not_requested"
    assert not result.json()["can_post"] and not result.json()["can_pay"]


@pytest.mark.parametrize("change", ["amount", "expiry"])
def test_content_change_or_expiry_invalidates_the_exact_request(case, change):
    pending = request(case)
    if change == "amount":
        case[1].execute(text("UPDATE documents SET data=jsonb_set(CAST(data AS jsonb),'{totalGross}','238') WHERE doc_number=:id"), {"id": case[5]})
    else:
        case[1].execute(text("""UPDATE domain_erp.ap_approval_requests SET applicable_rule=
            jsonb_set(CAST(applicable_rule AS jsonb),'{expires_at}','"2000-01-01T00:00:00+00:00"') WHERE id=:id"""),
            {"id": pending["approval_request_id"]})
    case[1].commit()
    assert decide(case, pending["approval_request_id"]).status_code == 409
    status = case[0].get(PREFIX + "/status/" + case[5], headers=headers(case)).json()
    assert status["status"] == "not_requested" and not status["can_post"]
    assert request(case)["approval_request_id"] != pending["approval_request_id"]


@pytest.mark.parametrize("phase", ["decision", "document", "commit"])
def test_real_sql_failure_rolls_back_entire_decision_without_private_error_text(case, monkeypatch, caplog, phase):
    pending = request(case)
    execute, commit = case[1].execute, case[1].commit
    def fail(statement, *args, **kwargs):
        sql = str(statement)
        if (phase == "decision" and "INSERT INTO domain_erp.ap_approvals" in sql) or (
            phase == "document" and "UPDATE documents" in sql):
            return execute(text("SELECT * FROM synthetic_private_ap_failure"))
        return execute(statement, *args, **kwargs)
    def failed_commit():
        execute(text("SELECT * FROM synthetic_private_ap_failure"))
        commit()
    monkeypatch.setattr(case[1], "execute", fail)
    if phase == "commit":
        monkeypatch.setattr(case[1], "commit", failed_commit)
    result = decide(case, pending["approval_request_id"])
    assert result.status_code == 503, result.text
    assert "synthetic_private_ap_failure" not in result.text + caplog.text
    monkeypatch.setattr(case[1], "execute", execute)
    monkeypatch.setattr(case[1], "commit", commit)
    assert count(case, "ap_approvals") == 0
    invoice = DocumentRepository(case[1]).get_document("ap_invoice", case[5])
    assert invoice["status"] == "ZUR_FREIGABE"
    assert decide(case, pending["approval_request_id"]).status_code == 200


@pytest.mark.parametrize("payload", [
    {"approval_roles": ["manager"]}, {"approval_roles": ["FINANCE_BEARBEITEN"]},
    {"conditions": [{"field": "unknown", "operator": "eq", "value": 1}]},
    {"conditions": [{"field": "amount", "operator": "always", "value": 1}]},
    {"conditions": [{"field": "amount", "operator": "gt", "value": "NaN"}]},
])
def test_invalid_policy_never_reaches_sql(case, monkeypatch, payload):
    monkeypatch.setattr(case[1], "execute", lambda *a, **k: pytest.fail("Invalid policy reached SQL"))
    result = case[0].post(PREFIX + "/rules", headers=headers(case), json={"name": "Synthetic",
        "conditions": [{"field": "amount", "operator": "gt", "value": 0}],
        "required_approvals": 1, "approval_roles": ["FINANCE_ADMIN"], **payload})
    assert result.status_code == 422, result.text


def test_multiple_distinct_humans_rule_role_and_both_direct_adapters(case):
    rule = case[0].post(PREFIX + "/rules", headers=headers(case), json={"name": "Synthetic two reviewers",
        "conditions": [{"field": "amount", "operator": "gt", "value": 0}],
        "required_approvals": 2, "approval_roles": ["FINANCE_ADMIN"]})
    assert rule.status_code == 201, rule.text
    pending = request(case)
    # Technical admin alone is not the role named by this concrete rule.
    denied = case[0].post(PREFIX + "/approve", headers=headers(case, "human-b", role="admin"),
        json={"invoice_id": case[5], "approval_request_id": pending["approval_request_id"], "action": "approve"})
    assert denied.status_code == 403, denied.text
    first = decide(case, pending["approval_request_id"])
    assert first.status_code == 200 and first.json()["status"] == "partially_approved", first.text
    second = case[0].post("/api/v1/finance/ap/invoices/" + case[5] + "/approve",
        headers=headers(case, "human-c"), json={"approval_request_id": pending["approval_request_id"]})
    assert second.status_code == 200, second.text
    assert second.json()["data"]["status"] == "approved"
    assert count(case, "ap_approvals") == 2


@pytest.mark.parametrize("changes", [{"preferred_username": "service-account-synthetic"}, {"agent_id": "synthetic-agent"},
                                    {"act":{"sub":"synthetic-delegate"}}, {"actor_type":"ai_agent"}])
def test_technical_or_agent_identity_cannot_act_as_second_human(case, changes):
    pending = request(case)
    result = case[0].post(PREFIX + "/approve", headers=headers(case, "human-b", **changes),
        json={"invoice_id": case[5], "approval_request_id": pending["approval_request_id"], "action": "approve"})
    assert result.status_code == 403, result.text
    assert count(case, "ap_approvals") == 0


def test_missing_request_and_unknown_action_are_rejected_before_sql(case, monkeypatch):
    monkeypatch.setattr(case[1], "execute", lambda *a, **k: pytest.fail("Invalid action reached SQL"))
    for payload in [{"invoice_id": case[5], "action": "approve"},
                    {"invoice_id": case[5], "approval_request_id": "x", "action": "anything"}]:
        assert case[0].post(PREFIX + "/approve", headers=headers(case), json=payload).status_code == 422


@pytest.mark.parametrize("mode", ["validate", "dryRun", "propose", "execute"])
def test_mask_modes_apply_the_same_maker_checker_and_request_policy(case, mode):
    pending = request(case)
    path = "/api/v1/finance/ap/invoices/" + case[5] + "/actions/freigeben"
    body = {"_mode": mode, "_idempotencyKey": "synthetic-key", "approval_request_id": pending["approval_request_id"]}
    denied = case[0].post(path, headers=headers(case), json=body)
    assert denied.status_code == 200 and not denied.json()["success"], denied.text
    assert count(case, "ap_approvals") == 0
    allowed = case[0].post(path, headers=headers(case, "human-b"), json=body)
    assert allowed.status_code == 200 and allowed.json()["success"], allowed.text
    assert count(case, "ap_approvals") == (1 if mode == "execute" else 0)
    if mode == "execute":
        assert case[0].post(path, headers=headers(case, "human-b"), json=body).json()["success"]
        # Knowledge of a reviewer's key is not permission to replay their approval.
        assert not case[0].post(path, headers=headers(case), json=body).json()["success"]
        assert not case[0].post(path, headers=headers(case, "human-b", preferred_username="service-account-synthetic"), json=body).json()["success"]
        assert count(case, "ap_approvals") == 1


def test_rule_lookup_database_failure_is_not_fabricated_default_policy(case, monkeypatch, caplog):
    execute = case[1].execute
    def broken(statement, *args, **kwargs):
        if "FROM domain_erp.ap_approval_rules" in str(statement):
            return execute(text("SELECT * FROM synthetic_private_ap_failure"))
        return execute(statement, *args, **kwargs)
    monkeypatch.setattr(case[1], "execute", broken)
    result = case[0].post(PREFIX + "/request", headers=headers(case), json={"invoice_id": case[5]})
    assert result.status_code == 503, result.text
    assert "synthetic_private_ap_failure" not in result.text + caplog.text
    monkeypatch.setattr(case[1], "execute", execute)
    assert count(case, "ap_approval_requests") == 0


def test_old_unbound_review_is_not_approval_and_must_be_requested_again(case):
    pending = request(case)
    case[1].execute(text("UPDATE domain_erp.ap_approval_requests SET applicable_rule=NULL, status='approved' WHERE id=:id"),
        {"id": pending["approval_request_id"]})
    case[1].commit()
    result = case[0].get(PREFIX + "/status/" + case[5], headers=headers(case))
    assert result.status_code == 200 and not result.json()["can_post"]
    assert decide(case, pending["approval_request_id"]).status_code == 409
    assert request(case)["approval_request_id"] != pending["approval_request_id"]


def test_internal_adapter_cannot_supply_a_different_verified_tenant(case):
    from app.api.v1.schemas.ap_approval_workflow_schemas import ApprovalRequest
    from app.services.ap_invoice_approval_service import APApprovalWorkflowService
    from fastapi import HTTPException
    import jwt
    from test_system_tenant_binding import AUDIENCE
    claims = jwt.decode(case[2].token(case[3], changes={"roles":["FINANCE_ADMIN"]}), case[2].keys[0].public_key(), algorithms=["RS256"], audience=AUDIENCE)
    with pytest.raises(HTTPException) as error:
        APApprovalWorkflowService(case[1], case[4]).request(ApprovalRequest(invoice_id=case[6]),
            {"sub": "human-a", "roles": ["FINANCE_ADMIN"], "raw": claims}, [])
    assert error.value.status_code == 403


@pytest.mark.parametrize("subject,role,expected", [
    ("human-a", "FINANCE_ADMIN", False), ("creator", "FINANCE_ADMIN", False),
    ("human-b", "FINANCE_ADMIN", True), ("human-b", "FINANCE_LESEN", False),
])
def test_status_and_native_entity_publish_the_same_server_decision_right(case, subject, role, expected):
    pending = request(case)
    response = case[0].get(PREFIX + "/status/" + case[5], headers=headers(case, subject, role))
    assert response.status_code == 200, response.text
    assert response.json()["can_decide"] is expected
    entity = case[0].get("/api/v1/finance/ap/invoices/" + case[5], headers=headers(case, subject, role))
    assert entity.status_code == 200, entity.text
    assert entity.json()["approval_can_decide"] is expected
    assert entity.json()["approval_request_id"] == pending["approval_request_id"]


def valid_update(case):
    return {"number": case[5], "date": "2026-10-20", "dueDate": "2026-11-20",
        "customerId": "synthetic-supplier", "totalGross": 119, "status": "FREIGEGEBEN", "lines": []}


def test_edit_preserves_creator_tracks_verified_editor_and_invalidates_review(case, monkeypatch):
    pending = request(case)
    monkeypatch.setattr(ap_invoices, "calculate_invoice_totals", lambda doc, *a: doc)  # Amount calculation has separate SQL contracts.
    result = case[0].put("/api/v1/finance/ap/invoices/" + case[5], headers=headers(case, "human-b"), json=valid_update(case))
    assert result.status_code == 200, result.text
    stored = DocumentRepository(case[1]).get_document("ap_invoice", case[5])
    assert stored["createdBy"] == "creator" and stored["updatedBy"] == "human-b"
    assert stored["status"] == "ENTWURF"
    assert decide(case, pending["approval_request_id"], subject="human-c").status_code == 409
    renewed = request(case)
    assert decide(case, renewed["approval_request_id"], subject="human-b").status_code == 403
    assert decide(case, renewed["approval_request_id"], subject="human-c").status_code == 200


@pytest.mark.parametrize("status", ["VERBUCHT", "BEZAHLT", "STORNIERT", "unrecognized"])
def test_closed_or_unknown_document_cannot_be_edited_deleted_or_re_requested(case, monkeypatch, status):
    case[1].execute(text("UPDATE documents SET data=jsonb_set(CAST(data AS jsonb),'{status}',CAST(:s AS jsonb)) WHERE doc_number=:id"),
        {"s": json.dumps(status), "id": case[5]})
    case[1].commit()
    monkeypatch.setattr(ap_invoices, "calculate_invoice_totals", lambda *a: pytest.fail("Immutable document reached amount calculation"))
    path = "/api/v1/finance/ap/invoices/" + case[5]
    assert case[0].put(path, headers=headers(case), json=valid_update(case)).status_code == 409
    assert case[0].delete(path, headers=headers(case)).status_code == 409
    assert case[0].post(PREFIX + "/request", headers=headers(case), json={"invoice_id": case[5]}).status_code == 409
    assert DocumentRepository(case[1]).get_document("ap_invoice", case[5])["status"] == status
    assert count(case, "ap_approval_requests") == 0


@pytest.mark.parametrize("status", ["VERBUCHT", "BEZAHLT", "STORNIERT", "ENTWURF"])
def test_old_approval_does_not_enable_reposting_after_lifecycle_change(case, status):
    pending = request(case)
    assert decide(case, pending["approval_request_id"]).status_code == 200
    case[1].execute(text("UPDATE documents SET data=jsonb_set(CAST(data AS jsonb),'{status}',CAST(:s AS jsonb)) WHERE doc_number=:id"),
        {"s": json.dumps(status), "id": case[5]})
    case[1].commit()
    result = case[0].get(PREFIX + "/status/" + case[5], headers=headers(case))
    assert result.status_code == 200 and not result.json()["can_post"], result.text
    if status in {"BEZAHLT", "STORNIERT", "ENTWURF"}:
        assert not result.json()["can_pay"]


def test_native_action_uses_server_permission_and_is_human_only():
    from app.core.screen_definitions import build_finance_ap_invoice_screen_definition
    action = next(a for a in build_finance_ap_invoice_screen_definition()["actions"] if a["key"] == "freigeben")
    assert action["enabledWhen"] == "approval_can_decide"
    assert action["humanApprovalRequired"] and action["forbiddenForAgents"] and action["requiresConfirmation"]


def test_missing_workflow_is_an_outage_not_a_status_based_posting_fallback(case, monkeypatch):
    from app.services.ap_invoice_approval_service import APApprovalWorkflowService
    from fastapi import HTTPException
    pending = request(case)
    assert decide(case, pending["approval_request_id"]).status_code == 200
    def unavailable(*args, **kwargs):
        raise HTTPException(503, "Freigabepruefung derzeit nicht verfuegbar")
    monkeypatch.setattr(APApprovalWorkflowService, "status", unavailable)
    from app.services.ap_invoice_approval_service import finance_periods
    monkeypatch.setattr(finance_periods, "gesperrter_zustand",
        lambda *a: pytest.fail("Unavailable review reached accounting checks"))
    result = case[0].post("/api/v1/finance/ap/invoices/" + case[5] + "/post", headers=headers(case, "human-c"))
    assert result.status_code == 503, result.text
    assert "synthetic private" not in result.text
    assert DocumentRepository(case[1]).get_document("ap_invoice", case[5])["status"] == "FREIGEGEBEN"


def test_repository_cannot_move_a_document_to_another_tenant_or_upsert_an_insert_only_call(case):
    from app.documents.repository import DocumentOwnershipError, DocumentAlreadyExists
    repo = DocumentRepository(case[1])
    before = repo.get_document('ap_invoice', case[5])
    with pytest.raises(DocumentOwnershipError):
        repo.save_document('ap_invoice', case[5], {**before, 'tenantId': case[4]}, commit=False)
    with pytest.raises(DocumentAlreadyExists):
        repo.save('ap_invoice', case[5], {**before, 'notes': 'private override'}, commit=False, create_only=True)
    assert repo.get_document('ap_invoice', case[5]) == before


def test_local_posting_profile_lookup_is_tenant_bound(case):
    from app.services.finance_transaction_service import FinanceTransactionService
    own = case[1].execute(text('SELECT id FROM domain_shared.users WHERE tenant_id=:t LIMIT 1'), {'t':case[3]}).scalar_one()
    foreign = case[1].execute(text('SELECT id FROM domain_shared.users WHERE tenant_id=:t LIMIT 1'), {'t':case[4]}).scalar_one()
    service = FinanceTransactionService(case[1], case[3], commit_on_success=False)
    assert service._resolve_user_id(own) == own
    assert service._resolve_user_id(foreign) is None


@pytest.mark.parametrize('outbox_failure', [False, True])
def test_complete_review_posting_chain_and_atomic_outbox(case, monkeypatch, outbox_failure):
    from app.finance.steuerschluessel import richte_skr03_ein
    richte_skr03_ein(case[1], case[3])
    number = 'SYN-' + uuid4().hex[:10]
    result = case[0].post('/api/v1/finance/ap/invoices/', headers=headers(case), json={
        'number': number, 'date': '2026-10-20', 'dueDate': '2026-11-20', 'customerId': 'synthetic-post-supplier',
        'lines': [{'article': 'Synthetic grain', 'qty': 1, 'price': 100, 'taxCode': '9'}]})
    assert result.status_code == 201, result.text
    posted_case = (*case[:5], number, case[6])
    pending = request(posted_case)
    assert decide(posted_case, pending['approval_request_id']).status_code == 200
    if outbox_failure:
        def fail(db, **kwargs):
            db.execute(text('SELECT * FROM synthetic_private_ap_outbox_failure'))
        from app.services.ap_invoice_approval_service import APApprovalWorkflowService
        monkeypatch.setattr(APApprovalWorkflowService, '_post_event', staticmethod(fail))
    response = case[0].post('/api/v1/finance/ap/invoices/'+number+'/post', headers=headers(case))
    assert response.status_code == (503 if outbox_failure else 200), response.text
    invoice = DocumentRepository(case[1]).get_document('ap_invoice', number)
    expected = 0 if outbox_failure else 1
    assert invoice['status'] == ('FREIGEGEBEN' if outbox_failure else 'VERBUCHT')
    assert case[1].execute(text('SELECT count(*) FROM domain_erp.journal_entries WHERE tenant_id=:t'), {'t':case[3]}).scalar_one() == expected
    assert case[1].execute(text('SELECT count(*) FROM domain_erp.offene_posten WHERE tenant_id=:t'), {'t':case[3]}).scalar_one() == expected
    assert case[1].execute(text('SELECT count(*) FROM outbox_events WHERE tenant_id=:t AND aggregate_id=:n'),
        {'t':case[3], 'n':number}).scalar_one() == expected
    if not outbox_failure:
        balances = case[1].execute(text('SELECT total_debit,total_credit FROM domain_erp.journal_entries WHERE tenant_id=:t'), {'t':case[3]}).one()
        assert balances[0] == balances[1] == 119
        actor = case[1].execute(text("SELECT user_id FROM domain_shared.audit_logs WHERE tenant_id=:t AND entity_id=:j AND action='create'"),
            {'t':case[3], 'j':invoice['journalEntryId']}).scalar_one()
        assert actor == 'human-a'
        # Posting metadata and the original review's expiration cannot invalidate an executed invoice.
        case[1].execute(text("""UPDATE domain_erp.ap_approval_requests SET applicable_rule=
            jsonb_set(CAST(applicable_rule AS jsonb),'{expires_at}','"2000-01-01T00:00:00+00:00"') WHERE id=:id"""),
            {'id':pending['approval_request_id']})
        case[1].commit()
        status = case[0].get(PREFIX+'/status/'+number, headers=headers(case)).json()
        assert status['status'] == 'approved' and status['can_pay'] and not status['can_post'], status


def test_changed_tax_basis_cannot_post_different_amount_under_old_review(case):
    from app.finance.steuerschluessel import richte_skr03_ein
    richte_skr03_ein(case[1], case[3])
    number = "SYN-T-" + uuid4().hex[:8]
    created = case[0].post("/api/v1/finance/ap/invoices/", headers=headers(case), json={
        "number": number, "date": "2026-10-20", "dueDate": "2026-11-20", "customerId": "synthetic-tax-supplier",
        "lines": [{"article": "Synthetic grain", "qty": 1, "price": 100, "taxCode": "9"}]})
    assert created.status_code == 201, created.text
    local_case = (*case[:5], number, case[6])
    pending = request(local_case)
    assert decide(local_case, pending["approval_request_id"]).status_code == 200
    case[1].execute(text("UPDATE domain_erp.tax_keys SET steuersatz=7 WHERE tenant_id=:t AND code='9'"), {"t":case[3]})
    case[1].commit()
    posted = case[0].post("/api/v1/finance/ap/invoices/"+number+"/post", headers=headers(case))
    assert posted.status_code == 409, posted.text
    for table in ["domain_erp.journal_entries", "domain_erp.offene_posten", "outbox_events"]:
        assert case[1].execute(text(f"SELECT count(*) FROM {table} WHERE tenant_id=:t"),
            {"t":case[3]}).scalar_one() == 0
    doc = DocumentRepository(case[1]).get_document("ap_invoice", number)
    assert doc["status"] == "FREIGEGEBEN" and doc["totalGross"] == 119
