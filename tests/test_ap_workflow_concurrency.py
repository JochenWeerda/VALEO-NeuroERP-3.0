"""Two real sessions contend on one synthetic document in the existing probe."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from threading import Barrier
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.v1.schemas.ap_approval_workflow_schemas import ApprovalAction, ApprovalRequest, ApprovalRuleResponse
from app.core.database import engine
from app.documents.repository import DocumentRepository
from app.services.ap_invoice_approval_service import APApprovalWorkflowService
from testgrenze import pruefstand_erlaubt


@pytest.mark.integration
@pytest.mark.parametrize("subjects,expected", [(("reviewer-b", "reviewer-c"), 2), (("reviewer-b", "reviewer-b"), 1)])
def test_parallel_reviewers_do_not_lose_votes_or_double_count_one_person(subjects, expected, require_db):
    assert pruefstand_erlaubt(engine.url), "Never run write contracts against the development database"
    tenant, invoice_id = "ap-race-" + uuid4().hex[:16], "ap-race-" + uuid4().hex
    now = datetime.now(timezone.utc)
    rule = ApprovalRuleResponse(id="synthetic-two", name="Two distinct reviewers", description=None,
        conditions=[{"field": "amount", "operator": "gt", "value": 0}], required_approvals=2,
        approval_roles=["FINANCE_ADMIN"], priority=1, active=True, created_at=now, updated_at=now)
    barrier = Barrier(2)
    try:
        with Session(engine) as db:
            db.execute(text("INSERT INTO domain_shared.tenants (id,name,is_active) VALUES (:id,'Synthetic concurrency contract',true)"), {"id": tenant})
            DocumentRepository(db).save_document("ap_invoice", invoice_id, {"number": invoice_id,
                "tenantId": tenant, "createdBy": "creator", "status": "ENTWURF", "totalGross": 1}, commit=False)
            pending = APApprovalWorkflowService(db, tenant).request(ApprovalRequest(invoice_id=invoice_id),
                {"sub": "requester", "roles": ["FINANCE_ADMIN"]}, [rule])
        def decide(subject):
            with Session(engine) as db:
                db.execute(text("SET LOCAL lock_timeout='5s'"))
                db.execute(text("SET LOCAL statement_timeout='15s'"))
                barrier.wait(timeout=5)
                return APApprovalWorkflowService(db, tenant).decide(ApprovalAction(invoice_id=invoice_id,
                    approval_request_id=pending.approval_request_id, action="approve"),
                    {"sub": subject, "roles": ["FINANCE_ADMIN"]})
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(decide, subject) for subject in subjects]
            results = [future.result(timeout=20) for future in futures]
        with Session(engine) as db:
            records = db.execute(text("SELECT approved_by FROM domain_erp.ap_approvals WHERE tenant_id=:t"), {"t": tenant}).scalars().all()
            assert len(records) == len(set(records)) == expected
            status = APApprovalWorkflowService(db, tenant).status(invoice_id)
            assert status.current_approvals == expected
            assert status.status == ("approved" if expected == 2 else "partially_approved")
            assert max(result.current_approvals for result in results) == expected
    finally:
        # Only this contract's committed synthetic business records are removed.
        # The few append-only audit entries intentionally remain in the probe.
        with engine.begin() as connection:
            for table in ("ap_approvals", "ap_approval_requests"):
                connection.execute(text(f"DELETE FROM domain_erp.{table} WHERE tenant_id=:t"), {"t": tenant})
            connection.execute(text("DELETE FROM documents WHERE doc_type='ap_invoice' AND doc_number=:id AND CAST(data AS jsonb)->>'tenantId'=:t"),
                {"id": invoice_id, "t": tenant})
            connection.execute(text("DELETE FROM domain_shared.tenants WHERE id=:t"), {"t": tenant})


@pytest.mark.integration
def test_concurrent_insert_only_documents_never_replace_another_tenant(require_db):
    from sqlalchemy.exc import IntegrityError
    from app.documents.repository import DocumentAlreadyExists
    assert pruefstand_erlaubt(engine.url)
    tenants = ['insert-' + uuid4().hex[:16] for _ in range(2)]
    number, barrier = 'insert-' + uuid4().hex, Barrier(2)
    try:
        with engine.begin() as connection:
            for tenant in tenants:
                connection.execute(text("INSERT INTO domain_shared.tenants (id,name,is_active) VALUES (:t,'Synthetic insert contract',true)"), {'t':tenant})
        def create(tenant):
            with Session(engine) as db:
                db.execute(text("SET LOCAL lock_timeout='5s'"))
                db.execute(text("SET LOCAL statement_timeout='15s'"))
                barrier.wait(timeout=5)
                try:
                    DocumentRepository(db).save_document('ap_invoice', number,
                        {'tenantId':tenant, 'status':'ENTWURF', 'notes':tenant}, create_only=True)
                    return tenant
                except (DocumentAlreadyExists, IntegrityError):
                    return None
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(create, tenant) for tenant in tenants]
            results = [future.result(timeout=20) for future in futures]
        winners = [result for result in results if result is not None]
        assert len(winners) == 1
        with Session(engine) as db:
            stored = DocumentRepository(db).get_document('ap_invoice', number)
            assert stored['tenantId'] == stored['notes'] == winners[0]
    finally:
        with engine.begin() as connection:
            connection.execute(text("DELETE FROM documents WHERE doc_type='ap_invoice' AND doc_number=:n AND CAST(data AS jsonb)->>'tenantId'=ANY(:tenants)"),
                {'n':number, 'tenants':tenants})
            connection.execute(text('DELETE FROM domain_shared.tenants WHERE id=ANY(:tenants)'), {'tenants':tenants})
