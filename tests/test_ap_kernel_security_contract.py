"""Actual kernel writes under signed HTTP identity, shared rollback probe."""
import pytest
from app.core.action_execution import ActionExecutionService, ActionExecutionRequest
from app.core.action_idempotency import get_action_idempotency_store
from app.services.command_handlers_finance import register_finance_command_mutations
from test_ap_workflow_security_contract import case, headers, request, count
from test_gdpr_subject_boundary import subject_data, keys, probe


@pytest.fixture
def kernel(case):
    get_action_idempotency_store().clear()
    register_finance_command_mutations()
    @case[0].app.post("/api/v1/ap-kernel-security-test")
    def execute(body: ActionExecutionRequest):
        from app.api.v1.endpoints.process_kernel_api import execute_action
        return execute_action(body, db=case[1])
    def run(ref, *, subject="human-b", role="FINANCE_ADMIN", command="ApproveAPInvoice", key="kernel-ap", **changes):
        body = dict(command_name=command, aggregate_type="ap_invoice", aggregate_id=case[5],
            payload={"status": "ZUR_FREIGABE", "approval_request_id": ref}, tenant_id=case[3],
            issuer_role="admin", issuer_type="human", human_confirmation=True, idempotency_key=key)
        body.update(changes)
        return case[0].post("/api/v1/ap-kernel-security-test", headers=headers(case, subject, role), json=body)
    yield run
    get_action_idempotency_store().clear()


def test_kernel_uses_verified_actor_same_review_and_bound_replay(case, kernel):
    ref = request(case)["approval_request_id"]
    response = kernel(ref)
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "accepted"
    assert kernel(ref).json()["status"] == "duplicate"
    assert count(case, "ap_approvals") == 1
    other = kernel(ref, subject="human-c")
    assert other.status_code == 409
    assert other.json()["detail"]["code"] == "IDEMPOTENCY_KEY_REUSED"
    assert kernel(ref, role="FINANCE_BEARBEITEN").status_code == 403


@pytest.mark.parametrize("change,expected", [
    ({"subject": "human-a"}, 403),
    ({"role": "manager"}, 403),
    ({"aggregate_id": "absent"}, 404),
    ({"payload": {"status": "ZUR_FREIGABE"}}, 422),
    ({"tenant_id": "00000000-0000-0000-0000-000000000099"}, 403)])
def test_kernel_rejects_forgery_missing_reference_and_foreign_context(case, kernel, change, expected):
    ref = request(case)["approval_request_id"]
    response = kernel(ref, **change)
    assert response.status_code == expected, response.text
    assert count(case, "ap_approvals") == 0


def test_kernel_reject_command_has_actual_same_transaction_effect(case, kernel):
    ref = request(case)["approval_request_id"]
    response = kernel(ref, command="RejectAPInvoice")
    assert response.status_code == 200 and response.json()["status"] == "accepted", response.text
    assert count(case, "ap_approvals") == 1
    from app.documents.repository import DocumentRepository
    assert DocumentRepository(case[1]).get_document("ap_invoice", case[5])["status"] == "ABGELEHNT"


def test_kernel_without_verified_context_never_reaches_sql():
    from fastapi import HTTPException
    class NoSql:
        def execute(self, *a, **k):
            pytest.fail("Unauthenticated command reached SQL")
    body = ActionExecutionRequest(command_name="ApproveAPInvoice", aggregate_type="ap_invoice",
        aggregate_id="a", tenant_id="t", issuer_type="human", issuer_role="admin", idempotency_key="x")
    with pytest.raises(HTTPException) as error:
        ActionExecutionService().execute(body, db=NoSql())
    assert error.value.status_code == 401


@pytest.mark.parametrize("outbox_failure", [False, True])
def test_actual_kernel_review_and_posting_are_atomic(case, kernel, monkeypatch, outbox_failure):
    from uuid import uuid4
    from sqlalchemy import text
    from app.finance.steuerschluessel import richte_skr03_ein
    from app.documents.repository import DocumentRepository
    from app.services.ap_invoice_approval_service import APApprovalWorkflowService
    richte_skr03_ein(case[1], case[3])
    number = "SYN-K-" + uuid4().hex[:8]
    created = case[0].post("/api/v1/finance/ap/invoices/", headers=headers(case), json={
        "number": number, "date": "2026-10-20", "dueDate": "2026-11-20", "customerId": "synthetic-kernel-supplier",
        "lines": [{"article": "Synthetic grain", "qty": 1, "price": 100, "taxCode": "9"}]})
    assert created.status_code == 201, created.text
    local_case = (*case[:5], number, case[6])
    ref = request(local_case)["approval_request_id"]
    reviewed = kernel(ref, aggregate_id=number)
    assert reviewed.status_code == 200 and reviewed.json()["status"] == "accepted", reviewed.text
    if outbox_failure:
        def fail(db, **kwargs):
            db.execute(text("SELECT * FROM synthetic_kernel_outbox_failure"))
        monkeypatch.setattr(APApprovalWorkflowService, "_post_event", staticmethod(fail))
    posted = kernel(ref, aggregate_id=number, subject="human-c", command="PostAPInvoice",
        payload={"status": "FREIGEGEBEN"}, key="kernel-post")
    assert posted.status_code == (503 if outbox_failure else 200), posted.text
    expected = 0 if outbox_failure else 1
    for table in ["domain_erp.journal_entries", "domain_erp.offene_posten", "outbox_events"]:
        assert case[1].execute(text(f"SELECT count(*) FROM {table} WHERE tenant_id=:t"),
            {"t":case[3]}).scalar_one() == expected
    doc = DocumentRepository(case[1]).get_document("ap_invoice", number)
    assert doc["status"] == ("FREIGEGEBEN" if outbox_failure else "VERBUCHT")
    if not outbox_failure:
        assert doc["postedBy"] == "human-c"
        journal = case[1].execute(text("SELECT total_debit,total_credit FROM domain_erp.journal_entries WHERE tenant_id=:t"),
            {"t":case[3]}).one()
        assert journal[0] == journal[1] == 119


def test_kernel_cached_decision_does_not_hide_changed_document(case, kernel):
    from sqlalchemy import text
    ref = request(case)["approval_request_id"]
    assert kernel(ref).status_code == 200
    case[1].execute(text("UPDATE documents SET data=jsonb_set(CAST(data AS jsonb),'{totalGross}','120') WHERE doc_number=:id"),
        {"id":case[5]})
    case[1].commit()
    assert kernel(ref).status_code == 409
    assert count(case, "ap_approvals") == 1
