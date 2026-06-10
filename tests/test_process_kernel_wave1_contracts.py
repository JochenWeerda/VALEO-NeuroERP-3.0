from __future__ import annotations

import asyncio
import importlib.util
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from app.core import endpoint_gateways
from app.core.ap_approval_status import build_approval_status_response
from app.api.v1.endpoints import (
    ap_approval_workflow,
    ap_invoices,
    closing_checklists,
    compat,
    finance_actions,
    finance_read_models,
    payment_runs,
    vat_return_export,
)
from app.core.policy_decisions import PolicyOverrideResolution
from app.core.process_references import build_process_reference_context
from app.core.workflow_definitions import WorkflowDefinition
from app.documents import router_helpers
from app.services.policy_service import Decision


REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_module(module_name: str, relative_path: str):
    module_path = REPO_ROOT / relative_path
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


policies = _load_module("wave1_test_policies", "app/api/v1/endpoints/policies.py")
admin_core = _load_module("wave1_test_admin_core", "app/api/v1/endpoints/admin_core.py")
admin_core.WorkflowSandboxPreviewIn.model_rebuild(_types_namespace={"date": date})
admin_core.WorkflowSandboxPreviewOut.model_rebuild(
    _types_namespace={
        "Any": Any,
        "WorkflowSandboxCampaignMatchOut": admin_core.WorkflowSandboxCampaignMatchOut,
    }
)
def test_policy_test_returns_structured_explainability_without_effective_override(monkeypatch):
    monkeypatch.setattr(policies.policy_store, "list", lambda: [])
    monkeypatch.setattr(
        policies.PolicyEngine,
        "decide",
        lambda roles, alert, rules: Decision(
            type="allow",
            execute=False,
            needsApproval=True,
            approverRoles=["manager"],
            ruleId="rule.margin",
            resolvedParams={"threshold": 5},
        ),
    )
    monkeypatch.setattr(
        policies,
        "resolve_tenant_policy_override",
        lambda db, tenant_id, rule_id, base_params=None: PolicyOverrideResolution(
            rule_id=rule_id,
            effective_scope="global",
            effective_scope_key="policy-engine",
            effective_enabled=True,
            effective_params=dict(base_params or {}),
            applied_reason="policy default",
            applied_source="policy-engine",
        ),
    )

    payload = policies.TestRequest.model_validate(
        {
            "alert": {
                "id": "sim-1",
                "kpiId": "margin",
                "title": "Margin below target",
                "message": "Margin 14.2%",
                "severity": "warn",
                "delta": -3,
            },
            "roles": ["manager"],
        }
    )

    response = asyncio.run(policies.test_policy(payload, tenant_id="tenant-wave1", db=None))

    assert response.override_resolution.rule_id == "rule.margin"
    assert response.override_resolution.effective_params == {"threshold": 5}
    assert response.explainability.status == "approval-required"
    assert response.explainability.source_scope == "global"


def test_policy_test_turns_disabled_override_into_blocked_explainability(monkeypatch):
    monkeypatch.setattr(policies.policy_store, "list", lambda: [])
    monkeypatch.setattr(
        policies.PolicyEngine,
        "decide",
        lambda roles, alert, rules: Decision(
            type="allow",
            execute=True,
            needsApproval=False,
            ruleId="rule.credit",
            resolvedParams={"limit": 1000},
        ),
    )
    monkeypatch.setattr(
        policies,
        "resolve_tenant_policy_override",
        lambda db, tenant_id, rule_id, base_params=None: PolicyOverrideResolution(
            rule_id=rule_id,
            effective_scope="tenant",
            effective_scope_key=tenant_id,
            effective_enabled=False,
            effective_params={"limit": 750},
            applied_reason="credit limit disabled for tenant",
            applied_source="tenant-settings",
        ),
    )

    payload = policies.TestRequest.model_validate(
        {
            "alert": {
                "id": "sim-2",
                "kpiId": "credit",
                "title": "Credit check",
                "message": "Limit reached",
                "severity": "warn",
            },
            "roles": ["operator"],
        }
    )

    response = asyncio.run(policies.test_policy(payload, tenant_id="tenant-wave1", db=None))

    assert response.decision.type == "deny"
    assert response.decision.resolvedParams == {"limit": 750}
    assert response.override_resolution.effective_enabled is False
    assert response.explainability.status == "blocked"
    assert any(detail.value == "credit limit disabled for tenant" for detail in response.explainability.details)


def test_workflow_sandbox_preview_returns_versioned_metadata(monkeypatch):
    monkeypatch.setattr(admin_core, "_load_tenant_settings", lambda db, tenant_id: {})
    monkeypatch.setattr(
        admin_core,
        "merge_workflow_variants",
        lambda defaults, custom, tenant_id=None: {
            "annahme": WorkflowDefinition(
                process_key="annahme",
                version=3,
                origin="tenant-override",
                tenant_id=tenant_id,
                status="active",
                steps=["wiegen", "qualitaet", "freigabe"],
                required_roles={"freigabe": ["manager"]},
                description="Annahmeprozess",
            )
        },
    )

    payload = admin_core.WorkflowSandboxPreviewIn.model_validate(
        {
            "process_key": "annahme",
            "simulation_date": "2026-03-11",
        }
    )

    response = asyncio.run(admin_core.preview_workflow_sandbox(payload, tenant_id="tenant-wave1", db=None))

    assert response.definition_version == 3
    assert response.definition_origin == "tenant-override"
    assert response.definition_status == "active"
    assert response.steps == ["wiegen", "qualitaet", "freigabe"]


def test_harvest_acceptance_reference_context_uses_process_kernel_shape():
    context = build_process_reference_context(
        process_key="harvest_acceptance",
        anchor_entity="harvest_acceptance",
        anchor_id="ha-1",
        contract_id="contract-1",
        harvest_acceptance_id="ha-1",
        weighing_ticket_id="wt-1",
        quality_protocol_id="qp-1",
        supplier_id="supplier-1",
        article_id="article-1",
    ).model_dump(exclude_none=True)

    assert context["process_key"] == "harvest_acceptance"
    assert context["anchor_entity"] == "harvest_acceptance"
    assert context["anchor_id"] == "ha-1"
    assert context["chain"]["contract_id"] == "contract-1"
    assert context["chain"]["harvest_acceptance_id"] == "ha-1"
    assert context["chain"]["weighing_ticket_id"] == "wt-1"
    assert context["chain"]["supplier_id"] == "supplier-1"
    assert context["chain"]["article_id"] == "article-1"


def test_quality_protocol_mapping_returns_reference_context_for_acceptance_chain():
    context = build_process_reference_context(
        process_key="quality_protocol",
        anchor_entity="quality_protocol",
        anchor_id="qp-2",
        contract_id="contract-2",
        harvest_acceptance_id="ha-2",
        weighing_ticket_id="wt-2",
        quality_protocol_id="qp-2",
        supplier_id="supplier-2",
        article_id="article-2",
    ).model_dump(exclude_none=True)

    assert context["process_key"] == "quality_protocol"
    assert context["anchor_entity"] == "quality_protocol"
    assert context["anchor_id"] == "qp-2"
    assert context["chain"]["contract_id"] == "contract-2"
    assert context["chain"]["harvest_acceptance_id"] == "ha-2"
    assert context["chain"]["supplier_id"] == "supplier-2"


def test_ap_approval_status_response_uses_structured_explainability_and_resolution():
    response = build_approval_status_response(
        invoice_id="inv-1",
        tenant_id="tenant-wave1",
        status="partially_approved",
        required_approvals=3,
        approvals=[{"approved_by": "lead"}],
        rejections=[],
        applicable_rule={
            "id": "rule.ap.high-value",
            "name": "High Value",
            "required_approvals": 3,
            "approval_roles": ["manager", "finance", "controller"],
        },
    )

    assert response.override_resolution.rule_id == "rule.ap.high-value"
    assert response.override_resolution.effective_scope == "tenant"
    assert response.override_resolution.effective_params["required_approvals"] == 3
    assert response.explainability.status == "approval-required"
    assert any(detail.value == "1/3" for detail in response.explainability.details)


def test_ap_approval_audit_payload_reuses_same_kernel_models():
    response = build_approval_status_response(
        invoice_id="inv-2",
        tenant_id="tenant-wave1",
        status="rejected",
        required_approvals=2,
        approvals=[],
        rejections=[{"approved_by": "finance"}],
        applicable_rule=None,
    )

    captured: list[object] = []

    class DummyDb:
        def add(self, entry):
            captured.append(entry)

    ap_approval_workflow._write_approval_audit_log(
        DummyDb(),
        tenant_id="tenant-wave1",
        user_id="finance",
        user_email="finance@example.com",
        action="approval_reject",
        invoice_id="inv-2",
        response=response,
        comment="threshold exceeded",
    )

    assert len(captured) == 1
    entry = captured[0]
    assert entry.entity_type == "ap_invoice_approval"
    assert entry.changes["override_resolution"]["rule_id"] == "ap.approval.default"
    assert entry.changes["explainability"]["status"] == "blocked"
    assert entry.changes["comment"] == "threshold exceeded"
    # Package A: WorkflowInstanceReference muss im Audit-Payload liegen
    wir = entry.changes["workflow_instance_ref"]
    assert wir["process_key"] == "ap_approval"
    assert wir["workflow_instance_id"] == "wf-ap-inv-2"
    assert wir["status"] == "failed"
    assert wir["current_step"] == "approval_reject"
    assert wir["business_reference"]["reference_type"] == "ap_invoice"
    assert wir["business_reference"]["reference_id"] == "inv-2"


def test_ap_approval_audit_workflow_instance_ref_maps_status_to_instance_status():
    """WorkflowInstanceReference.status folgt dem Mapping approval_status → instance_status."""
    for approval_status, expected_instance_status in [
        ("not_requested", "running"),
        ("pending", "waiting"),
        ("partially_approved", "waiting"),
        ("approved", "completed"),
        ("rejected", "failed"),
    ]:
        ref = ap_approval_workflow._build_workflow_instance_reference(
            invoice_id="inv-x",
            tenant_id="t1",
            approval_status=approval_status,
            action="test_action",
            applicable_rule=None,
        )
        assert ref.status == expected_instance_status, f"{approval_status} → {expected_instance_status}"
        assert ref.definition_origin == "default"
        assert ref.process_key == "ap_approval"


def test_ap_approval_audit_workflow_instance_ref_uses_tenant_override_when_rule_applies():
    """Wenn eine Freigaberegel aktiv ist, setzt definition_origin auf 'tenant-override'."""
    ref = ap_approval_workflow._build_workflow_instance_reference(
        invoice_id="inv-y",
        tenant_id="t2",
        approval_status="approved",
        action="approval_approve",
        applicable_rule={"id": "rule.ap.high-value", "name": "High Value", "required_approvals": 3, "approval_roles": ["manager"]},
    )
    assert ref.definition_origin == "tenant-override"
    assert ref.status == "completed"


def test_ap_invoice_legacy_approve_facade_delegates_to_workflow(monkeypatch):
    monkeypatch.setattr(ap_invoices, "get_repository", lambda db: object())
    monkeypatch.setattr(
        ap_invoices,
        "get_from_store",
        lambda doc_type, invoice_id, repo: {"number": invoice_id, "tenantId": "tenant-wave1", "status": "ENTWURF"},
    )

    async def fake_get_approval_status(invoice_id, tenant_id, db):
        return build_approval_status_response(
            invoice_id=invoice_id,
            tenant_id=tenant_id,
            status="not_requested",
            required_approvals=0,
            approvals=[],
            rejections=[],
            applicable_rule=None,
        )

    async def fake_request_approval(request, tenant_id, db):
        return build_approval_status_response(
            invoice_id=request.invoice_id,
            tenant_id=tenant_id,
            status="pending",
            required_approvals=1,
            approvals=[],
            rejections=[],
            applicable_rule=None,
        )

    async def fake_approve_invoice(action, tenant_id, db):
        return build_approval_status_response(
            invoice_id=action.invoice_id,
            tenant_id=tenant_id,
            status="approved",
            required_approvals=1,
            approvals=[{"approved_by": action.approved_by}],
            rejections=[],
            applicable_rule=None,
        )

    endpoint_gateways.register_approval_workflow_gateway(
        endpoint_gateways.ApprovalWorkflowGateway(
            get_status=fake_get_approval_status,
            request_approval=lambda invoice_id, tenant_id, requested_by, comment, db: fake_request_approval(
                ap_approval_workflow.ApprovalRequest(
                    invoice_id=invoice_id,
                    requested_by=requested_by,
                    comment=comment,
                ),
                tenant_id,
                db,
            ),
            approve_invoice=lambda invoice_id, tenant_id, approved_by, action, comment, db: fake_approve_invoice(
                ap_approval_workflow.ApprovalAction(
                    invoice_id=invoice_id,
                    approved_by=approved_by,
                    action=action,
                    comment=comment,
                ),
                tenant_id,
                db,
            ),
        )
    )

    response = asyncio.run(ap_invoices.approve_ap_invoice("inv-legacy", approved_by="lead", db=None))

    assert response["status"] == "ok"
    assert response["data"]["status"] == "approved"
    assert response["data"]["override_resolution"]["rule_id"] == "ap.approval.default"
    assert response["data"]["explainability"]["status"] == "allowed"


def test_ap_approval_request_syncs_invoice_to_zur_freigabe(monkeypatch):
    stored_invoice = {
        "number": "inv-request",
        "tenantId": "tenant-wave1",
        "status": "ENTWURF",
    }

    async def fake_list_approval_rules(active_only, tenant_id, db):
        return []

    class DummyResult:
        def fetchone(self):
            return ("req-1", "inv-request", "pending", 1, None, datetime(2026, 3, 11, 9, 0, 0), datetime(2026, 3, 11, 9, 0, 0))

    class DummyDb:
        def execute(self, _query, _params):
            return DummyResult()

        def add(self, _entry):
            return None

        def commit(self):
            return None

        def rollback(self):
            raise AssertionError("rollback should not be called")

    monkeypatch.setattr(ap_approval_workflow, "list_approval_rules", fake_list_approval_rules)
    monkeypatch.setattr(ap_approval_workflow, "uuid7", lambda: "req-1")
    monkeypatch.setattr(router_helpers, "get_repository", lambda db: object())
    monkeypatch.setattr(router_helpers, "get_from_store", lambda doc_type, invoice_id, repo: stored_invoice)
    monkeypatch.setattr(
        router_helpers,
        "save_to_store",
        lambda doc_type, invoice_id, invoice, repo: stored_invoice.update(invoice) or stored_invoice,
    )

    response = asyncio.run(
        ap_approval_workflow.request_approval(
            ap_approval_workflow.ApprovalRequest(invoice_id="inv-request", requested_by="lead"),
            tenant_id="tenant-wave1",
            db=DummyDb(),
        )
    )

    assert response.status == "pending"
    assert stored_invoice["status"] == "ZUR_FREIGABE"
    assert stored_invoice["approvalRequestId"] == "req-1"


def test_ap_approval_reject_syncs_invoice_to_abgelehnt(monkeypatch):
    stored_invoice = {
        "number": "inv-reject",
        "tenantId": "tenant-wave1",
        "status": "ZUR_FREIGABE",
    }
    approvals_rows: list[tuple[str, datetime, str | None]] = []
    rejections_rows: list[tuple[str, datetime, str | None]] = []

    class DummyDb:
        def execute(self, query, params):
            query_str = str(query)
            if "FROM domain_erp.ap_approval_requests" in query_str:
                return type("Result", (), {"fetchone": lambda self: ("req-1", "inv-reject", 2, None, "pending")})()
            if "SELECT approved_by, approved_at, comment" in query_str and "action = 'approve'" in query_str:
                return type("Result", (), {"fetchall": lambda self: approvals_rows})()
            if "SELECT approved_by, approved_at, comment" in query_str and "action = 'reject'" in query_str:
                return type("Result", (), {"fetchall": lambda self: rejections_rows})()
            if "SELECT id FROM domain_erp.ap_approvals" in query_str:
                return type("Result", (), {"fetchone": lambda self: None})()
            if "INSERT INTO domain_erp.ap_approvals" in query_str:
                rejections_rows.append((params["approved_by"], datetime(2026, 3, 11, 9, 30, 0), params.get("comment")))
                return type("Result", (), {})()
            if "UPDATE domain_erp.ap_approval_requests" in query_str:
                return type("Result", (), {})()
            raise AssertionError(query_str)

        def add(self, _entry):
            return None

        def commit(self):
            return None

        def rollback(self):
            raise AssertionError("rollback should not be called")

    monkeypatch.setattr(router_helpers, "get_repository", lambda db: object())
    monkeypatch.setattr(router_helpers, "get_from_store", lambda doc_type, invoice_id, repo: stored_invoice)
    monkeypatch.setattr(
        router_helpers,
        "save_to_store",
        lambda doc_type, invoice_id, invoice, repo: stored_invoice.update(invoice) or stored_invoice,
    )

    response = asyncio.run(
        ap_approval_workflow.approve_invoice(
            ap_approval_workflow.ApprovalAction(invoice_id="inv-reject", approved_by="finance", action="reject", comment="threshold"),
            tenant_id="tenant-wave1",
            db=DummyDb(),
        )
    )

    assert response.status == "rejected"
    assert stored_invoice["status"] == "ABGELEHNT"


def test_ap_invoice_detail_returns_workflow_snapshot(monkeypatch):
    monkeypatch.setattr(ap_invoices, "get_repository", lambda db: object())
    monkeypatch.setattr(
        ap_invoices,
        "get_from_store",
        lambda doc_type, invoice_id, repo: {
            "number": invoice_id,
            "tenantId": "tenant-wave1",
            "status": "ZUR_FREIGABE",
        },
    )

    async def fake_get_approval_status(invoice_id, tenant_id, db):
        return build_approval_status_response(
            invoice_id=invoice_id,
            tenant_id=tenant_id,
            status="partially_approved",
            required_approvals=2,
            approvals=[{"approved_by": "lead"}],
            rejections=[],
            applicable_rule={"id": "rule.ap", "name": "AP Rule", "required_approvals": 2, "approval_roles": ["manager"]},
        )

    endpoint_gateways.register_approval_workflow_gateway(
        endpoint_gateways.ApprovalWorkflowGateway(
            get_status=fake_get_approval_status,
            request_approval=lambda invoice_id, tenant_id, requested_by, comment, db: ap_approval_workflow.request_approval(
                ap_approval_workflow.ApprovalRequest(
                    invoice_id=invoice_id,
                    requested_by=requested_by,
                    comment=comment,
                ),
                tenant_id=tenant_id,
                db=db,
            ),
            approve_invoice=lambda invoice_id, tenant_id, approved_by, action, comment, db: ap_approval_workflow.approve_invoice(
                ap_approval_workflow.ApprovalAction(
                    invoice_id=invoice_id,
                    approved_by=approved_by,
                    action=action,
                    comment=comment,
                ),
                tenant_id=tenant_id,
                db=db,
            ),
        )
    )

    response = asyncio.run(ap_invoices.get_ap_invoice("inv-snapshot", db=None))

    assert response["approval_status"] == "partially_approved"
    assert response["approval_required_approvals"] == 2
    assert response["approval_current_approvals"] == 1
    assert response["approval_explainability"]["status"] == "approval-required"


def test_ap_invoice_list_filters_zur_freigabe_via_workflow_status(monkeypatch):
    monkeypatch.setattr(ap_invoices, "get_repository", lambda db: object())
    monkeypatch.setattr(
        ap_invoices,
        "list_from_store",
        lambda doc_type, skip, limit, tenant_id, repo: {
            "data": [
                {"number": "inv-pending", "tenantId": "tenant-wave1", "status": "ZUR_FREIGABE", "customerId": "s1"},
                {"number": "inv-approved", "tenantId": "tenant-wave1", "status": "FREIGEGEBEN", "customerId": "s2"},
            ]
        },
    )

    async def fake_get_approval_status(invoice_id, tenant_id, db):
        if invoice_id == "inv-pending":
            return build_approval_status_response(
                invoice_id=invoice_id,
                tenant_id=tenant_id,
                status="pending",
                required_approvals=2,
                approvals=[],
                rejections=[],
                applicable_rule=None,
            )
        return build_approval_status_response(
            invoice_id=invoice_id,
            tenant_id=tenant_id,
            status="approved",
            required_approvals=1,
            approvals=[{"approved_by": "lead"}],
            rejections=[],
            applicable_rule=None,
        )

    endpoint_gateways.register_approval_workflow_gateway(
        endpoint_gateways.ApprovalWorkflowGateway(
            get_status=fake_get_approval_status,
            request_approval=lambda invoice_id, tenant_id, requested_by, comment, db: ap_approval_workflow.request_approval(
                ap_approval_workflow.ApprovalRequest(
                    invoice_id=invoice_id,
                    requested_by=requested_by,
                    comment=comment,
                ),
                tenant_id=tenant_id,
                db=db,
            ),
            approve_invoice=lambda invoice_id, tenant_id, approved_by, action, comment, db: ap_approval_workflow.approve_invoice(
                ap_approval_workflow.ApprovalAction(
                    invoice_id=invoice_id,
                    approved_by=approved_by,
                    action=action,
                    comment=comment,
                ),
                tenant_id=tenant_id,
                db=db,
            ),
        )
    )

    response = asyncio.run(ap_invoices.list_ap_invoices(status="ZUR_FREIGABE", db=None))

    assert len(response) == 1
    assert response[0]["number"] == "inv-pending"
    assert response[0]["approval_status"] == "pending"


def test_payment_run_response_returns_structured_approval_snapshot():
    row = (
        "run-1",
        "ZR-2026-001",
        date(2026, 3, 11),
        "Valero GmbH",
        "DE02120300000000202051",
        "BYLADEM1001",
        1250.50,
        2,
        "approved",
        None,
        "finance@example.com",
        None,
        None,
        "Wave 1",
        datetime(2026, 3, 11, 9, 0, 0),
        datetime(2026, 3, 11, 9, 0, 0),
    )
    response = payment_runs._build_payment_run_response(row, payments=[])

    assert response.status == "approved"
    assert response.approval_status == "approved"
    assert response.approval_can_execute is True
    assert response.approval_override_resolution.rule_id == "finance.payment_run.execution"
    assert response.approval_explainability.status == "allowed"


def test_store_payment_run_event_in_outbox_uses_real_event_type(monkeypatch):
    captured: dict[str, Any] = {}

    class FakeOutbox:
        async def store_event(self, event, tenant_id=None):
            captured["event_type"] = event.event_type
            captured["aggregate_id"] = event.aggregate_id
            captured["tenant_id"] = tenant_id
            captured["payload"] = event.payload

    monkeypatch.setattr(payment_runs, "OutboxPublisher", lambda db, publisher: FakeOutbox())
    monkeypatch.setattr(payment_runs, "get_event_publisher", lambda: object())

    asyncio.run(
        payment_runs._store_payment_run_event_in_outbox(
            db=object(),
            tenant_id="tenant-wave1",
            event_type="payment_run.executed",
            run_id="run-1",
            payload={"status": "executed"},
        )
    )

    assert captured["event_type"] == "payment_run.executed"
    assert captured["aggregate_id"] == "run-1"
    assert captured["tenant_id"] == "tenant-wave1"
    assert captured["payload"]["status"] == "executed"


def test_store_ap_invoice_posted_event_in_outbox_uses_process_event(monkeypatch):
    captured: dict[str, Any] = {}

    class FakeOutbox:
        async def store_event(self, event, tenant_id=None):
            captured["event_type"] = event.__class__.__name__
            captured["aggregate_id"] = event.aggregate_id
            captured["tenant_id"] = tenant_id
            captured["journal_entry_id"] = event.journal_entry_id

    monkeypatch.setattr(ap_invoices, "OutboxPublisher", lambda db, publisher: FakeOutbox())
    monkeypatch.setattr(ap_invoices, "get_event_publisher", lambda: object())

    asyncio.run(
        ap_invoices._store_ap_invoice_posted_event_in_outbox(
            db=object(),
            tenant_id="tenant-wave1",
            invoice_id="inv-1",
            posted_by="finance@example.com",
            journal_entry_id="je-1",
        )
    )

    assert captured["event_type"] == "APInvoicePosted"
    assert captured["aggregate_id"] == "inv-1"
    assert captured["tenant_id"] == "tenant-wave1"
    assert captured["journal_entry_id"] == "je-1"


def test_payment_run_approve_request_accepts_legacy_empty_body_and_uses_default_actor(monkeypatch):
    captured: dict[str, object] = {}

    class DummyResult:
        def fetchone(self):
            return ("run-1",)

    class DummyDb:
        def execute(self, _query, params):
            captured.update(params)
            return DummyResult()

        def commit(self):
            captured["committed"] = True

        def rollback(self):
            raise AssertionError("rollback should not be called")

    async def fake_get_payment_run(run_id, tenant_id, db):
        return payment_runs.PaymentRunResponse(
            id=run_id,
            run_number="ZR-2026-001",
            execution_date=date(2026, 3, 11),
            initiator_name="Valero GmbH",
            initiator_iban="DE02120300000000202051",
            initiator_bic="BYLADEM1001",
            total_amount=1,
            payment_count=1,
            status="approved",
            approved_at=None,
            approved_by="api",
            executed_at=None,
            sepa_file_id=None,
            notes=None,
            payments=[],
            approval_status="approved",
            approval_can_execute=True,
            approval_override_resolution=payment_runs.PolicyOverrideResolution(rule_id="finance.payment_run.execution"),
            approval_explainability=payment_runs.ExplainabilityView(status="allowed", summary="ok"),
            created_at=datetime(2026, 3, 11, 9, 0, 0),
            updated_at=datetime(2026, 3, 11, 9, 0, 0),
        )

    monkeypatch.setattr(payment_runs, "get_payment_run", fake_get_payment_run)

    request = payment_runs.ApprovePaymentRunRequest.model_validate({})
    response = asyncio.run(payment_runs.approve_payment_run("run-1", request, tenant_id="tenant-wave1", db=DummyDb()))

    assert captured["approved_by"] == "api"
    assert captured["committed"] is True
    assert response.approved_by == "api"


def test_return_payment_persists_outbox_event(monkeypatch):
    captured: dict[str, Any] = {}

    class DummyResult:
        def __init__(self, row=None):
            self._row = row

        def fetchone(self):
            return self._row

    class DummyDb:
        def execute(self, query, params):
            query_str = str(query)
            if "FROM domain_erp.payment_run_items" in query_str:
                return DummyResult(("pay-1", "run-1", "op-1", "ignored", Decimal("50.00")))
            return DummyResult()

        def commit(self):
            captured["committed"] = True

        def rollback(self):
            raise AssertionError("rollback should not be called")

    async def fake_store_payment_run_event_in_outbox(db, *, tenant_id, event_type, run_id, payload):
        captured["tenant_id"] = tenant_id
        captured["event_type"] = event_type
        captured["run_id"] = run_id
        captured["payload"] = payload

    monkeypatch.setattr(payment_runs, "_store_payment_run_event_in_outbox", fake_store_payment_run_event_in_outbox)
    monkeypatch.setattr(payment_runs, "uuid7", lambda: "ret-1")

    response = asyncio.run(
        payment_runs.return_payment(
            "run-1",
            payment_runs.ReturnPaymentRequest(
                payment_id="pay-1",
                return_reason="R01",
                return_date=date(2026, 3, 12),
                notes="bank returned debit",
            ),
            tenant_id="tenant-wave1",
            db=DummyDb(),
        )
    )

    assert response["status"] == "ok"
    assert captured["committed"] is True
    assert captured["event_type"] == "payment_run.returned"
    assert captured["run_id"] == "run-1"
    assert captured["payload"]["return_id"] == "ret-1"


def test_payment_return_amount_accepts_current_and_legacy_row_shapes():
    assert payment_runs._payment_return_amount(
        ("pay-1", "run-1", "op-1", Decimal("42.50"), "cred-1")
    ) == Decimal("42.50")
    assert payment_runs._payment_return_amount(
        ("pay-1", "run-1", "op-1", "cred-1", Decimal("42.50"))
    ) == Decimal("42.50")


def test_pos_tagesabschluss_enqueues_cash_closing_outbox_event(monkeypatch):
    captured: dict[str, Any] = {}
    from app.services.fiscalization import service as fiscal_service_module

    async def fake_enqueue(db, *, event_type, aggregate_id, payload, tenant_id=None):
        captured["event_type"] = event_type
        captured["aggregate_id"] = aggregate_id
        captured["payload"] = payload
        captured["tenant_id"] = tenant_id

    class FakeDb:
        def __init__(self):
            self.commands: list[tuple[str, Any]] = []

        def execute(self, statement, params=None):
            self.commands.append((str(statement), params))
            return self

        def commit(self):
            self.commands.append(("COMMIT", None))

    class FakeFiscalizationService:
        def __init__(self, db, tenant_id):
            self.db = db
            self.tenant_id = tenant_id

        def get_config(self):
            return {
                "configured": True,
                "cash_register_id": "register-1",
                "client_id": "client-1",
                "settings": {"terminal_id": "terminal-1"},
            }

        def daily_summary(self, business_date):
            return {
                "incomplete_count": 0,
                "gross_total": 407.0,
                "cash_total": 119.0,
                "card_total": 238.0,
                "transaction_count": 5,
            }

        def close_cash_point(self, command):
            return fiscal_service_module.ProviderResult(
                provider="fiskaly",
                operation="cash_point_closing",
                provider_reference="closing-1",
                status="completed",
                simulated=False,
            )

    monkeypatch.setattr(compat, "_enqueue_event", fake_enqueue)
    monkeypatch.setattr(compat, "_ensure_chart_account", lambda db, tenant_id, account_number, account_name: account_number)
    monkeypatch.setattr(fiscal_service_module, "FiscalizationService", FakeFiscalizationService)

    payload = compat.TagesabschlussIn(
        datum=date(2026, 3, 11),
        kassierer="Kasse 1",
        tse_transaktionen=5,
        umsatz_bar=119.0,
        umsatz_ec=238.0,
        umsatz_paypal=0.0,
        umsatz_b2b=0.0,
        umsatz_gutschein=50.0,
        gutschein_ausgabe=100.0,
        barentnahme=80.0,
        umsatz_gesamt=407.0,
        bargeld_gezaehlt=139.0,
        ec_abrechnung=238.0,
        paypal_abrechnung=0.0,
        differenz_bar=0.0,
    )

    db = FakeDb()
    response = asyncio.run(compat.create_tagesabschluss(payload, tenant_id="tenant-wave1", db=db))

    assert response.status == "gebucht"
    assert captured["event_type"] == "cash_closing.posted"
    assert captured["tenant_id"] == "tenant-wave1"
    assert captured["payload"]["cash_closing_id"] == response.id
    assert captured["payload"]["belegnummer"] == response.belegnummer
    journal_lines = [
        params
        for statement, params in db.commands
        if "INSERT INTO domain_erp.journal_entry_lines" in statement
    ]
    assert {
        (line["acc_id"], line["debit"], line["credit"]) for line in journal_lines
    } == {
        ("1000", Decimal("219.00"), Decimal("0.00")),
        ("1200", Decimal("238.00"), Decimal("0.00")),
        ("1600", Decimal("50.00"), Decimal("0.00")),
        ("8400", Decimal("0.00"), Decimal("407.00")),
        ("1600", Decimal("0.00"), Decimal("100.00")),
        ("1800", Decimal("80.00"), Decimal("0.00")),
        ("1000", Decimal("0.00"), Decimal("80.00")),
    }


def test_closing_checklist_response_returns_structured_approval_snapshot():
    row = (
        "cls-1",
        "2026-03",
        "monthly",
        None,
        "approved",
        100.0,
        5,
        5,
        4,
        4,
        [],
        datetime(2026, 3, 11, 9, 0, 0),
        datetime(2026, 3, 11, 9, 0, 0),
        None,
        None,
    )
    response = closing_checklists.build_closing_checklist_response(row, items_data=[])

    assert response.approval_status == "approved"
    assert response.approval_can_close is True
    assert response.approval_override_resolution.rule_id == "finance.closing.period"
    assert response.approval_explainability.status == "allowed"


def test_finance_actions_closing_approve_delegates_to_checklist_workspace(monkeypatch):
    captured: dict[str, object] = {}

    async def fake_approve_closing_workspace(request, db):
        captured["tenant_id"] = request.tenant_id
        captured["period"] = request.period
        captured["closing_type"] = request.closing_type
        captured["actor"] = request.actor
        return {"status": "approved", "approval_status": "approved"}

    endpoint_gateways.register_closing_workspace_gateway(
        endpoint_gateways.ClosingWorkspaceGateway(
            calculate=closing_checklists.calculate_closing_workspace,
            approve=fake_approve_closing_workspace,
            close=closing_checklists.close_closing_workspace,
            lock=closing_checklists.lock_closing_workspace,
        )
    )

    response = asyncio.run(
        finance_actions.approve_closing(
            finance_actions.ClosingActionRequest(
                period="2026-03",
                closing_type="monatsabschluss",
                actor="controller@example.com",
            ),
            tenant_id="tenant-wave1",
            db=None,
        )
    )

    assert captured == {
        "tenant_id": "tenant-wave1",
        "period": "2026-03",
        "closing_type": "monatsabschluss",
        "actor": "controller@example.com",
    }
    assert response["approval_status"] == "approved"


def test_vat_return_response_returns_structured_approval_snapshot():
    row = (
        "vat-1",
        "2026-03",
        "monthly",
        "Valero GmbH",
        None,
        "DE123",
        1000.0,
        190.0,
        190.0,
        0.0,
        [],
        "approved",
        datetime(2026, 3, 11, 9, 0, 0),
        datetime(2026, 3, 11, 10, 0, 0),
        None,
        None,
        datetime(2026, 3, 11, 8, 0, 0),
        datetime(2026, 3, 11, 10, 0, 0),
    )
    response = vat_return_export._build_vat_return_response(row, positions_data=[])

    assert response.approval_status == "approved"
    assert response.approval_can_submit is True
    assert response.approval_override_resolution.rule_id == "finance.vat_return.submission"
    assert response.approval_explainability.status == "allowed"


def test_vat_return_approve_promotes_validated_return(monkeypatch):
    async def fake_get_vat_return(return_id, tenant_id, db):
        status = getattr(db, "status", "validated")
        return vat_return_export.VATReturnResponse(
            id=return_id,
            period="2026-03",
            return_type="monthly",
            taxpayer_name="Valero GmbH",
            tax_id=None,
            vat_id="DE123",
            total_sales_net=1000,
            total_input_tax=190,
            total_output_tax=190,
            vat_payable=0,
            positions=[],
            status=status,
            calculated_at=None,
            validated_at=datetime(2026, 3, 11, 9, 0, 0),
            approved_at=None,
            approved_by=None,
            submitted_at=None,
            elster_reference=None,
            approval_status=status,
            approval_can_submit=status == "approved",
            approval_override_resolution=vat_return_export.PolicyOverrideResolution(rule_id="finance.vat_return.submission"),
            approval_explainability=vat_return_export.ExplainabilityView(status="approval-required", summary="pending"),
            notes=None,
            created_at=datetime(2026, 3, 11, 8, 0, 0),
            updated_at=datetime(2026, 3, 11, 9, 0, 0),
        )

    class DummyDb:
        status = "validated"

        def execute(self, _query, _params):
            self.status = "approved"
            return None

        def commit(self):
            return None

        def rollback(self):
            raise AssertionError("rollback should not be called")

    monkeypatch.setattr(vat_return_export, "get_vat_return", fake_get_vat_return)
    response = asyncio.run(
        vat_return_export.approve_vat_return(
            "vat-1",
            vat_return_export.VATReturnApprovalRequest(approved_by="tax@example.com"),
            tenant_id="tenant-wave1",
            db=DummyDb(),
        )
    )

    assert response.status == "approved"
    assert response.approved_by == "tax@example.com"


def test_ap_invoice_semantic_status_normalizes_document_and_workflow_status():
    """semantic_status berechnet das einheitliche deutsche Freigabevokabular."""
    compute = ap_invoices._compute_ap_invoice_semantic_status

    # VERBUCHT überschreibt alles
    assert compute({"status": "VERBUCHT", "approval_status": "pending"}) == "VERBUCHT"

    # Workflow-Status hat Vorrang vor Document-Status wenn nicht VERBUCHT
    assert compute({"status": "ENTWURF", "approval_status": "pending"}) == "ZUR_FREIGABE"
    assert compute({"status": "ENTWURF", "approval_status": "partially_approved"}) == "TEILWEISE_FREIGEGEBEN"
    assert compute({"status": "ENTWURF", "approval_status": "approved"}) == "FREIGEGEBEN"
    assert compute({"status": "ENTWURF", "approval_status": "rejected"}) == "ABGELEHNT"

    # not_requested fällt auf Document-Status zurück
    assert compute({"status": "ENTWURF", "approval_status": "not_requested"}) == "ENTWURF"
    assert compute({"status": "FREIGEGEBEN", "approval_status": "not_requested"}) == "FREIGEGEBEN"

    # Fehlender approval_status fällt auf Document-Status zurück
    assert compute({"status": "ENTWURF"}) == "ENTWURF"


def test_ap_invoice_detail_carries_semantic_status(monkeypatch):
    """get_ap_invoice gibt semantic_status im Response mit aus."""
    monkeypatch.setattr(ap_invoices, "get_repository", lambda db: object())
    monkeypatch.setattr(
        ap_invoices,
        "get_from_store",
        lambda doc_type, invoice_id, repo: {
            "number": invoice_id,
            "tenantId": "tenant-wave1",
            "status": "ENTWURF",
        },
    )

    async def fake_get_approval_status(invoice_id, tenant_id, db):
        return build_approval_status_response(
            invoice_id=invoice_id,
            tenant_id=tenant_id,
            status="partially_approved",
            required_approvals=2,
            approvals=[{"approved_by": "lead"}],
            rejections=[],
            applicable_rule={"id": "rule.ap", "name": "AP Rule", "required_approvals": 2, "approval_roles": ["manager"]},
        )

    endpoint_gateways.register_approval_workflow_gateway(
        endpoint_gateways.ApprovalWorkflowGateway(
            get_status=fake_get_approval_status,
            request_approval=lambda invoice_id, tenant_id, requested_by, comment, db: ap_approval_workflow.request_approval(
                ap_approval_workflow.ApprovalRequest(
                    invoice_id=invoice_id,
                    requested_by=requested_by,
                    comment=comment,
                ),
                tenant_id=tenant_id,
                db=db,
            ),
            approve_invoice=lambda invoice_id, tenant_id, approved_by, action, comment, db: ap_approval_workflow.approve_invoice(
                ap_approval_workflow.ApprovalAction(
                    invoice_id=invoice_id,
                    approved_by=approved_by,
                    action=action,
                    comment=comment,
                ),
                tenant_id=tenant_id,
                db=db,
            ),
        )
    )

    response = asyncio.run(ap_invoices.get_ap_invoice("inv-semantic", db=None))

    assert response["semantic_status"] == "TEILWEISE_FREIGEGEBEN"


def test_ap_invoice_list_filter_uses_semantic_status(monkeypatch):
    """Listenfilter FREIGEGEBEN matcht auf semantic_status, nicht nur auf approval_status-String."""
    monkeypatch.setattr(ap_invoices, "get_repository", lambda db: object())
    monkeypatch.setattr(
        ap_invoices,
        "list_from_store",
        lambda doc_type, skip, limit, tenant_id, repo: {
            "data": [
                {"number": "inv-approved", "tenantId": "tenant-wave1", "status": "ENTWURF", "customerId": "s1"},
                {"number": "inv-draft", "tenantId": "tenant-wave1", "status": "ENTWURF", "customerId": "s2"},
            ]
        },
    )

    async def fake_get_approval_status(invoice_id, tenant_id, db):
        if invoice_id == "inv-approved":
            return build_approval_status_response(
                invoice_id=invoice_id,
                tenant_id=tenant_id,
                status="approved",
                required_approvals=1,
                approvals=[{"approved_by": "lead"}],
                rejections=[],
                applicable_rule=None,
            )
        return build_approval_status_response(
            invoice_id=invoice_id,
            tenant_id=tenant_id,
            status="not_requested",
            required_approvals=0,
            approvals=[],
            rejections=[],
            applicable_rule=None,
        )

    endpoint_gateways.register_approval_workflow_gateway(
        endpoint_gateways.ApprovalWorkflowGateway(
            get_status=fake_get_approval_status,
            request_approval=lambda invoice_id, tenant_id, requested_by, comment, db: ap_approval_workflow.request_approval(
                ap_approval_workflow.ApprovalRequest(
                    invoice_id=invoice_id,
                    requested_by=requested_by,
                    comment=comment,
                ),
                tenant_id=tenant_id,
                db=db,
            ),
            approve_invoice=lambda invoice_id, tenant_id, approved_by, action, comment, db: ap_approval_workflow.approve_invoice(
                ap_approval_workflow.ApprovalAction(
                    invoice_id=invoice_id,
                    approved_by=approved_by,
                    action=action,
                    comment=comment,
                ),
                tenant_id=tenant_id,
                db=db,
            ),
        )
    )

    response = asyncio.run(ap_invoices.list_ap_invoices(status="FREIGEGEBEN", db=None))

    assert len(response) == 1
    assert response[0]["number"] == "inv-approved"
    assert response[0]["semantic_status"] == "FREIGEGEBEN"


def test_vat_return_submit_requires_and_returns_submitted_snapshot(monkeypatch):
    async def fake_get_vat_return(return_id, tenant_id, db):
        status = getattr(db, "status", "approved")
        return vat_return_export.VATReturnResponse(
            id=return_id,
            period="2026-03",
            return_type="monthly",
            taxpayer_name="Valero GmbH",
            tax_id=None,
            vat_id="DE123",
            total_sales_net=1000,
            total_input_tax=190,
            total_output_tax=190,
            vat_payable=0,
            positions=[],
            status=status,
            calculated_at=None,
            validated_at=datetime(2026, 3, 11, 9, 0, 0),
            approved_at=datetime(2026, 3, 11, 10, 0, 0),
            approved_by="tax@example.com",
            submitted_at=None,
            elster_reference=None,
            approval_status=status,
            approval_can_submit=status == "approved",
            approval_override_resolution=vat_return_export.PolicyOverrideResolution(rule_id="finance.vat_return.submission"),
            approval_explainability=vat_return_export.ExplainabilityView(status="allowed", summary="ready"),
            notes=None,
            created_at=datetime(2026, 3, 11, 8, 0, 0),
            updated_at=datetime(2026, 3, 11, 10, 0, 0),
        )

    class DummyDb:
        status = "approved"

        def execute(self, _query, _params):
            self.status = "submitted"
            return None

        def commit(self):
            return None

        def rollback(self):
            raise AssertionError("rollback should not be called")

    monkeypatch.setattr(vat_return_export, "get_vat_return", fake_get_vat_return)
    response = asyncio.run(
        vat_return_export.submit_vat_return(
            "vat-1",
            vat_return_export.VATReturnSubmitRequest(submitted_by="tax@example.com"),
            tenant_id="tenant-wave1",
            db=DummyDb(),
        )
    )

    assert response.status == "submitted"
    assert response.elster_reference == "ELSTER-2026-03-vat-1"


def test_ap_invoice_semantic_status_preserves_extended_document_states():
    compute = ap_invoices._compute_ap_invoice_semantic_status

    assert compute({"status": "TEILWEISE_FREIGEGEBEN", "approval_status": "not_requested"}) == "TEILWEISE_FREIGEGEBEN"
    assert compute({"status": "BEZAHLT", "approval_status": "not_requested"}) == "BEZAHLT"


def test_ap_approval_status_fallback_reads_document_semantics_without_request(monkeypatch):
    monkeypatch.setattr(router_helpers, "get_repository", lambda db: object())
    monkeypatch.setattr(
        router_helpers,
        "get_from_store",
        lambda doc_type, invoice_id, repo: {"number": invoice_id, "tenantId": "tenant-wave1", "status": "ABGELEHNT"},
    )

    class DummyDb:
        def execute(self, _query, _params):
            return type("Result", (), {"fetchone": lambda self: None})()

    response = asyncio.run(ap_approval_workflow.get_approval_status("inv-fallback", tenant_id="tenant-wave1", db=DummyDb()))

    assert response.status == "rejected"
    assert response.can_post is False


def test_cash_closings_read_model_returns_structured_snapshot():
    closing_rows = [
        {
            "id": "cash-close-1",
            "periode": "2026-03-11",
            "status": "gebucht",
            "verantwortlicher": "M. Muster",
            "abschluss_datum": date(2026, 3, 11),
            "items": {
                "tse_transaktionen": 42,
                "umsatz_bar": 2450.0,
                "umsatz_ec": 3200.0,
                "umsatz_paypal": 400.0,
                "umsatz_b2b": 150.0,
                "umsatz_gesamt": 6200.0,
                "bargeld_gezaehlt": 2450.0,
                "ec_abrechnung": 3200.0,
                "paypal_abrechnung": 400.0,
                "differenz_bar": 0.0,
                "belegnummer": "KA-2026-03-11",
            },
            "created_at": datetime(2026, 3, 11, 18, 15, 0),
        }
    ]
    journal_row = {
        "id": "je-1",
        "entry_number": "KA-2026-03-11",
        "posting_date": datetime(2026, 3, 11, 18, 15, 0),
        "status": "posted",
    }

    class DummyResult:
        def __init__(self, value):
            self.value = value

        def mappings(self):
            return self

        def all(self):
            return self.value

        def fetchone(self):
            return self.value

        def scalar(self):
            return self.value

    class DummyDb:
        def execute(self, query, params):
            query_str = str(query)
            if "FROM abschluss_checklisten" in query_str:
                return DummyResult(closing_rows)
            if "FROM domain_erp.journal_entries" in query_str:
                return DummyResult([journal_row])
            if "FROM domain_erp.cash_movements" in query_str:
                return DummyResult(3)
            raise AssertionError(query_str)

    response = asyncio.run(finance_read_models.get_cash_closings(tenant_id="tenant-wave1-posted", db=DummyDb()))

    assert response.total_count == 1
    assert response.items[0].workflow_status == "posted"
    assert response.items[0].totals.cash_expected == 2450.0
    assert response.items[0].posting.journal_entry_number == "KA-2026-03-11"
    assert response.items[0].reference_context.tse_transaction_count == 42
    assert "abschluss_checklisten:cash-close-1" in response.items[0].reference_context.source_document_refs


def test_cash_closings_read_model_marks_missing_posting_as_exception():
    closing_rows = [
        {
            "id": "cash-close-2",
            "periode": "2026-03-12",
            "status": "gebucht",
            "verantwortlicher": "A. Beispiel",
            "abschluss_datum": date(2026, 3, 12),
            "items": {
                "tse_transaktionen": 12,
                "umsatz_bar": 100.0,
                "umsatz_ec": 0.0,
                "umsatz_paypal": 0.0,
                "umsatz_b2b": 0.0,
                "umsatz_gesamt": 100.0,
                "bargeld_gezaehlt": 98.0,
                "ec_abrechnung": 0.0,
                "paypal_abrechnung": 0.0,
                "differenz_bar": -2.0,
                "belegnummer": "KA-2026-03-12",
            },
            "created_at": datetime(2026, 3, 12, 19, 0, 0),
        }
    ]

    class DummyResult:
        def __init__(self, value):
            self.value = value

        def mappings(self):
            return self

        def all(self):
            return self.value

        def fetchone(self):
            return self.value

        def scalar(self):
            return self.value

    class DummyDb:
        def execute(self, query, params):
            query_str = str(query)
            if "FROM abschluss_checklisten" in query_str:
                return DummyResult(closing_rows)
            if "FROM domain_erp.journal_entries" in query_str:
                return DummyResult(None)
            if "FROM domain_erp.cash_movements" in query_str:
                raise Exception("cash_movements missing")
            raise AssertionError(query_str)

    response = asyncio.run(finance_read_models.get_cash_closings(tenant_id="tenant-wave1-exc", db=DummyDb()))

    assert response.total_count == 1
    assert response.items[0].workflow_status == "exception"
    assert response.items[0].exception_flags.has_missing_posting is True
    assert response.items[0].exception_flags.has_difference is True
    assert response.items[0].posting.journal_entry_id is None


def test_cash_closing_analysis_read_model_aggregates_exceptions():
    snapshot = finance_read_models.CashClosingReadModel(
        tenant_id="tenant-wave1",
        total_count=3,
        schema_version=1,
        items=[
            finance_read_models.CashClosingSnapshot(
                id="c1",
                closing_date="2026-03-11",
                operator_name="M. Muster",
                workflow_status="exception",
                totals=finance_read_models.CashClosingTotals(cash_difference=2.0, gross_total=100.0),
                posting=finance_read_models.CashClosingPosting(),
                import_context=finance_read_models.CashClosingImportContext(import_source_label="cash_movements"),
                reference_context=finance_read_models.CashClosingReferenceContext(),
                exception_flags=finance_read_models.CashClosingExceptionFlags(
                    has_difference=True,
                    has_missing_posting=True,
                    has_import_gap=False,
                ),
            ),
            finance_read_models.CashClosingSnapshot(
                id="c2",
                closing_date="2026-03-11",
                operator_name="M. Muster",
                workflow_status="posted",
                totals=finance_read_models.CashClosingTotals(cash_difference=0.0, gross_total=90.0),
                posting=finance_read_models.CashClosingPosting(journal_entry_number="KA-2"),
                import_context=finance_read_models.CashClosingImportContext(),
                reference_context=finance_read_models.CashClosingReferenceContext(),
                exception_flags=finance_read_models.CashClosingExceptionFlags(),
            ),
            finance_read_models.CashClosingSnapshot(
                id="c3",
                closing_date="2026-03-12",
                operator_name="A. Beispiel",
                workflow_status="exception",
                totals=finance_read_models.CashClosingTotals(cash_difference=1.0, gross_total=80.0),
                posting=finance_read_models.CashClosingPosting(),
                import_context=finance_read_models.CashClosingImportContext(),
                reference_context=finance_read_models.CashClosingReferenceContext(),
                exception_flags=finance_read_models.CashClosingExceptionFlags(
                    has_difference=True,
                    has_missing_posting=False,
                    has_import_gap=False,
                ),
            ),
        ],
    )

    response = finance_read_models.project_cash_closing_analysis(snapshot)

    assert response.total_count == 3
    assert response.exception_count == 2
    assert response.balanced_count == 1
    assert response.missing_posting_count == 1
    assert response.difference_count == 2
    assert response.import_context_count == 1
    assert response.top_exception_operators[0].key == "A. Beispiel"
    assert response.top_exception_operators[0].count == 1
    assert response.top_exception_dates[0].key == "2026-03-11"
    assert response.top_exception_dates[0].count == 1


def test_cash_closing_reporting_read_model_groups_by_period():
    snapshot = finance_read_models.CashClosingReadModel(
        tenant_id="tenant-wave1",
        total_count=3,
        schema_version=1,
        items=[
            finance_read_models.CashClosingSnapshot(
                id="c1",
                closing_date="2026-03-11",
                operator_name="M. Muster",
                workflow_status="posted",
                totals=finance_read_models.CashClosingTotals(
                    cash_difference=0.0,
                    card_difference=0.0,
                    paypal_difference=0.0,
                    gross_total=100.0,
                ),
                posting=finance_read_models.CashClosingPosting(journal_entry_number="KA-1"),
                import_context=finance_read_models.CashClosingImportContext(),
                reference_context=finance_read_models.CashClosingReferenceContext(),
                exception_flags=finance_read_models.CashClosingExceptionFlags(),
            ),
            finance_read_models.CashClosingSnapshot(
                id="c2",
                closing_date="2026-03-12",
                operator_name="A. Beispiel",
                workflow_status="exception",
                totals=finance_read_models.CashClosingTotals(
                    cash_difference=-2.0,
                    card_difference=1.0,
                    paypal_difference=0.0,
                    gross_total=80.0,
                ),
                posting=finance_read_models.CashClosingPosting(),
                import_context=finance_read_models.CashClosingImportContext(),
                reference_context=finance_read_models.CashClosingReferenceContext(),
                exception_flags=finance_read_models.CashClosingExceptionFlags(
                    has_difference=True,
                    has_missing_posting=True,
                ),
            ),
            finance_read_models.CashClosingSnapshot(
                id="c3",
                closing_date="2026-02-28",
                operator_name="B. Beispiel",
                workflow_status="booked",
                totals=finance_read_models.CashClosingTotals(
                    cash_difference=0.5,
                    card_difference=0.0,
                    paypal_difference=0.0,
                    gross_total=50.0,
                ),
                posting=finance_read_models.CashClosingPosting(),
                import_context=finance_read_models.CashClosingImportContext(import_source_label="cash_movements"),
                reference_context=finance_read_models.CashClosingReferenceContext(),
                exception_flags=finance_read_models.CashClosingExceptionFlags(has_difference=True),
            ),
        ],
    )

    response = finance_read_models.project_cash_closing_reporting(snapshot)

    assert response.total_count == 3
    assert response.total_gross == 230.0
    assert response.total_difference == 3.5
    assert response.periods[0].period_key == "2026-03"
    assert response.periods[0].closing_count == 2
    assert response.periods[0].gross_total == 180.0
    assert response.periods[0].exception_count == 1
    assert response.periods[0].missing_posting_count == 1
    assert response.periods[0].difference_total == 3.0
    assert response.periods[1].period_key == "2026-02"
    assert response.periods[1].closing_count == 1


def test_cash_closing_detail_read_model_returns_single_snapshot():
    snapshot = finance_read_models.CashClosingReadModel(
        tenant_id="tenant-wave1",
        total_count=2,
        schema_version=1,
        items=[
            finance_read_models.CashClosingSnapshot(
                id="c1",
                closing_date="2026-03-11",
                operator_name="M. Muster",
                workflow_status="posted",
                totals=finance_read_models.CashClosingTotals(gross_total=100.0),
                posting=finance_read_models.CashClosingPosting(journal_entry_number="KA-1"),
                import_context=finance_read_models.CashClosingImportContext(),
                reference_context=finance_read_models.CashClosingReferenceContext(),
                exception_flags=finance_read_models.CashClosingExceptionFlags(),
            ),
            finance_read_models.CashClosingSnapshot(
                id="c2",
                closing_date="2026-03-12",
                operator_name="A. Beispiel",
                workflow_status="exception",
                totals=finance_read_models.CashClosingTotals(gross_total=80.0),
                posting=finance_read_models.CashClosingPosting(),
                import_context=finance_read_models.CashClosingImportContext(),
                reference_context=finance_read_models.CashClosingReferenceContext(),
                exception_flags=finance_read_models.CashClosingExceptionFlags(has_missing_posting=True),
            ),
        ],
    )

    response = finance_read_models.project_cash_closing_detail(snapshot, "c2")

    assert response is not None
    assert response.id == "c2"
    assert response.workflow_status == "exception"
    assert response.exception_flags.has_missing_posting is True
