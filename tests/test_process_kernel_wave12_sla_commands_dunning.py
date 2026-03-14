"""
Wave-12 Contract Tests: SLA-Eskalation, Settlement-Commands, Dunning-Level-Modell
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import sla_escalation_api
from app.core.process_sla import (
    build_default_sla_policies,
    evaluate_sla,
    EscalationTarget,
    SLASeverity,
    SLAViolation,
)
from app.core.sla_escalation import (
    acknowledge_escalation,
    create_escalation_event,
    escalation_summary,
    scan_all_sla_violations,
)
from app.core.settlement_commands import (
    CommandDispatchLog,
    SettlementCommandDispatchResult,
    SettlementCommandPayload,
    build_command_dispatch_log,
    build_settlement_dispatch_result,
)
from app.core.process_references import build_process_reference_context
from app.core.dunning_model import (
    DEFAULT_DUNNING_RULES,
    DunningLevelAction,
    MahnwesenItem,
    build_dunning_level_counts,
    compute_dunning_level,
)


# ---------------------------------------------------------------------------
# AP1: SLA Batch-Scanner
# ---------------------------------------------------------------------------

def test_scan_sla_violations_detects_critical_ap_invoice():
    old_start = datetime.now(timezone.utc) - timedelta(hours=80)
    instances = [
        {
            "instance_id": "WF-001",
            "tenant_id": "t1",
            "process_key": "ap_invoice_approval",
            "step_name": "waiting_approval",
            "started_at": old_start.isoformat(),
        }
    ]
    policies = build_default_sla_policies()
    violations = scan_all_sla_violations(instances, policies)
    assert len(violations) == 1
    assert violations[0].severity == SLASeverity.CRITICAL
    assert violations[0].instance_id == "WF-001"


def test_scan_sla_violations_returns_empty_for_fresh_instance():
    recent = datetime.now(timezone.utc) - timedelta(hours=1)
    instances = [
        {
            "instance_id": "WF-002",
            "tenant_id": "t1",
            "process_key": "ap_invoice_approval",
            "step_name": "waiting_approval",
            "started_at": recent.isoformat(),
        }
    ]
    violations = scan_all_sla_violations(instances, build_default_sla_policies())
    assert len(violations) == 0


def test_scan_sla_violations_detects_warning_harvest_acceptance():
    old_start = datetime.now(timezone.utc) - timedelta(hours=5)
    instances = [
        {
            "instance_id": "WF-003",
            "tenant_id": "t2",
            "process_key": "harvest_acceptance",
            "step_name": "pending",
            "started_at": old_start.isoformat(),
        }
    ]
    violations = scan_all_sla_violations(instances, build_default_sla_policies())
    assert len(violations) == 1
    assert violations[0].severity == SLASeverity.WARNING


def test_scan_sla_violations_skips_instance_without_started_at():
    instances = [{"instance_id": "WF-004", "tenant_id": "t1", "process_key": "ap_invoice_approval", "step_name": "waiting_approval"}]
    violations = scan_all_sla_violations(instances, build_default_sla_policies())
    assert violations == []


def test_escalation_summary_counts_by_severity():
    policies = build_default_sla_policies()
    now = datetime.now(timezone.utc)
    v1 = evaluate_sla("i1", "t1", "ap_invoice_approval", "waiting_approval", now - timedelta(hours=80), policies)
    v2 = evaluate_sla("i2", "t1", "harvest_acceptance", "pending", now - timedelta(hours=5), policies)
    summary = escalation_summary([v for v in [v1, v2] if v])
    assert summary["critical"] >= 1
    assert summary["warning"] >= 1


# ---------------------------------------------------------------------------
# AP2: Eskalationsereignis
# ---------------------------------------------------------------------------

def test_create_escalation_event_from_critical_violation():
    violation = SLAViolation(
        violation_id="viol-001",
        instance_id="WF-010",
        tenant_id="t1",
        process_key="ap_invoice_approval",
        step_name="waiting_approval",
        started_at=datetime.now(timezone.utc) - timedelta(hours=80),
        violation_detected_at=datetime.now(timezone.utc),
        elapsed_hours=80.0,
        severity=SLASeverity.CRITICAL,
        escalated=True,
        escalation_target=EscalationTarget.MANAGEMENT,
    )
    event = create_escalation_event(violation)
    assert event.violation_id == "viol-001"
    assert event.target == EscalationTarget.MANAGEMENT
    assert "ap_invoice_approval" in event.message
    assert event.acknowledged is False


def test_create_escalation_event_uses_override_target():
    violation = SLAViolation(
        violation_id="viol-002",
        instance_id="WF-011",
        tenant_id="t1",
        process_key="harvest_acceptance",
        step_name="pending",
        started_at=datetime.now(timezone.utc) - timedelta(hours=5),
        violation_detected_at=datetime.now(timezone.utc),
        elapsed_hours=5.0,
        severity=SLASeverity.WARNING,
    )
    event = create_escalation_event(violation, override_target=EscalationTarget.TEAM_LEAD)
    assert event.target == EscalationTarget.TEAM_LEAD


def test_acknowledge_escalation_sets_acknowledged_true():
    violation = SLAViolation(
        violation_id="viol-003",
        instance_id="WF-012",
        tenant_id="t1",
        process_key="payment_run",
        step_name="waiting_approval",
        started_at=datetime.now(timezone.utc) - timedelta(hours=100),
        violation_detected_at=datetime.now(timezone.utc),
        elapsed_hours=100.0,
        severity=SLASeverity.CRITICAL,
        escalated=True,
        escalation_target=EscalationTarget.MANAGEMENT,
    )
    event = create_escalation_event(violation)
    acked = acknowledge_escalation(event)
    assert acked.acknowledged is True
    assert acked.escalation_id == event.escalation_id


def test_sla_scan_api_returns_schema_version():
    app = FastAPI()
    app.include_router(sla_escalation_api.router)
    old = (datetime.now(timezone.utc) - timedelta(hours=80)).isoformat()
    with TestClient(app) as client:
        response = client.post("/process/sla/scan", json={
            "instances": [
                {"instance_id": "WF-API", "tenant_id": "t1", "process_key": "ap_invoice_approval",
                 "step_name": "waiting_approval", "started_at": old},
            ]
        })
    assert response.status_code == 200
    data = response.json()
    assert data["schema_version"] == 1
    assert data["violation_count"] >= 1
    assert "critical" in data["summary"]


# ---------------------------------------------------------------------------
# AP3: Settlement-Command-Payload und Dispatch-Result
# ---------------------------------------------------------------------------

def test_settlement_command_payload_schema_version_is_stable():
    payload = SettlementCommandPayload(
        command_id="settlement.create",
        tenant_id="t1",
        actor="user-42",
        params={"settlement_type": "rohware"},
    )
    assert payload.schema_version == 1
    assert payload.command_id == "settlement.create"


def test_build_settlement_dispatch_result_accepted():
    payload = SettlementCommandPayload(
        command_id="settlement.create",
        tenant_id="t1",
        actor="user-42",
    )
    result = build_settlement_dispatch_result(payload, dispatch_id="disp-001", status="accepted", result_ref="SET-500")
    assert result.status == "accepted"
    assert result.result_ref == "SET-500"
    assert result.schema_version == 1


def test_build_settlement_dispatch_result_rejected_carries_error():
    payload = SettlementCommandPayload(
        command_id="settlement.post",
        tenant_id="t1",
        actor="system",
    )
    result = build_settlement_dispatch_result(
        payload,
        dispatch_id="disp-002",
        status="rejected",
        error_code="MISSING_QUALITY_PROTOCOL",
        error_detail="Kein finalisiertes Qualitätsprotokoll vorhanden.",
    )
    assert result.status == "rejected"
    assert result.error_code == "MISSING_QUALITY_PROTOCOL"


def test_settlement_command_payload_carries_process_ref():
    ref = build_process_reference_context(
        process_key="settlement",
        anchor_entity="settlement",
        anchor_id="SET-99",
        contract_id="KON-1",
    )
    payload = SettlementCommandPayload(
        command_id="settlement.post",
        tenant_id="t1",
        actor="fibu-user",
        process_ref=ref,
    )
    assert payload.process_ref is not None
    assert payload.process_ref.chain.contract_id == "KON-1"


# ---------------------------------------------------------------------------
# AP4: Command Dispatch Log
# ---------------------------------------------------------------------------

def test_build_command_dispatch_log_includes_process_ref_chain():
    ref = build_process_reference_context(
        process_key="settlement",
        anchor_entity="settlement",
        anchor_id="SET-200",
        contract_id="KON-7",
        harvest_acceptance_id="ANH-3",
    )
    payload = SettlementCommandPayload(command_id="settlement.create", tenant_id="t1", actor="user-1")
    result = build_settlement_dispatch_result(payload, dispatch_id="disp-100", result_ref="SET-200")
    log = build_command_dispatch_log(result, actor="user-1", process_ref=ref, outbox_event_id="evt-55")
    assert log.schema_version == 1
    assert log.process_ref_chain is not None
    assert log.process_ref_chain["contract_id"] == "KON-7"
    assert log.outbox_event_id == "evt-55"


def test_build_command_dispatch_log_without_process_ref():
    payload = SettlementCommandPayload(command_id="settlement.preview", tenant_id="t1", actor="user-2")
    result = build_settlement_dispatch_result(payload, dispatch_id="disp-101", status="accepted")
    log = build_command_dispatch_log(result, actor="user-2")
    assert log.process_ref_chain is None
    assert log.outbox_event_id is None


# ---------------------------------------------------------------------------
# AP5: Dunning-Level-Berechnung
# ---------------------------------------------------------------------------

def test_compute_dunning_level_returns_level_2_for_21_days_overdue():
    item = MahnwesenItem(
        item_id="inv-001",
        tenant_id="t1",
        debtor_id="deb-1",
        invoice_id="INV-100",
        invoice_date=date(2026, 1, 1),
        due_date=date(2026, 1, 15),
        open_amount=500.0,
    )
    ref = date(2026, 2, 5)  # 21 days overdue
    level, rule = compute_dunning_level(item, reference_date=ref)
    assert level == 2
    assert rule is not None
    assert rule.action == DunningLevelAction.WARNING


def test_compute_dunning_level_returns_0_for_not_yet_overdue():
    item = MahnwesenItem(
        item_id="inv-002",
        tenant_id="t1",
        debtor_id="deb-2",
        invoice_id="INV-101",
        invoice_date=date(2026, 3, 1),
        due_date=date(2026, 3, 20),
        open_amount=200.0,
    )
    level, rule = compute_dunning_level(item, reference_date=date(2026, 3, 15))
    assert level == 0
    assert rule is None


def test_compute_dunning_level_blocked_item_returns_0():
    item = MahnwesenItem(
        item_id="inv-003",
        tenant_id="t1",
        debtor_id="deb-3",
        invoice_id="INV-102",
        invoice_date=date(2026, 1, 1),
        due_date=date(2026, 1, 10),
        open_amount=750.0,
        blocked=True,
        block_reason="Reklamation offen",
    )
    level, rule = compute_dunning_level(item, reference_date=date(2026, 3, 1))
    assert level == 0


def test_compute_dunning_level_legal_for_50_days_overdue():
    item = MahnwesenItem(
        item_id="inv-004",
        tenant_id="t1",
        debtor_id="deb-4",
        invoice_id="INV-103",
        invoice_date=date(2026, 1, 1),
        due_date=date(2026, 1, 10),
        open_amount=1200.0,
    )
    level, rule = compute_dunning_level(item, reference_date=date(2026, 3, 1))
    assert level == 4
    assert rule.action == DunningLevelAction.LEGAL


# ---------------------------------------------------------------------------
# AP6: Dunning Level Counts für MahnwesenPreview
# ---------------------------------------------------------------------------

def test_build_dunning_level_counts_aggregates_correctly():
    items = [
        MahnwesenItem(item_id="i1", tenant_id="t1", debtor_id="d1", invoice_id="INV-1",
                      invoice_date=date(2026, 1, 1), due_date=date(2026, 1, 15), open_amount=100.0),
        MahnwesenItem(item_id="i2", tenant_id="t1", debtor_id="d2", invoice_id="INV-2",
                      invoice_date=date(2026, 1, 1), due_date=date(2026, 1, 10), open_amount=200.0),
        MahnwesenItem(item_id="i3", tenant_id="t1", debtor_id="d3", invoice_id="INV-3",
                      invoice_date=date(2026, 1, 1), due_date=date(2026, 3, 13), open_amount=50.0),
    ]
    ref = date(2026, 3, 13)
    counts = build_dunning_level_counts(items, reference_date=ref)
    assert sum(counts.values()) == 2   # i3 is not overdue
    assert "1" not in counts or counts.get("1", 0) == 0  # i1: 57 days → level 4


def test_dunning_level_counts_excludes_blocked_items():
    items = [
        MahnwesenItem(item_id="i1", tenant_id="t1", debtor_id="d1", invoice_id="INV-X",
                      invoice_date=date(2026, 1, 1), due_date=date(2026, 1, 10), open_amount=300.0,
                      blocked=True, block_reason="Dispute"),
    ]
    counts = build_dunning_level_counts(items, reference_date=date(2026, 3, 1))
    assert counts == {}


def test_dunning_model_schema_version():
    item = MahnwesenItem(
        item_id="inv-schema",
        tenant_id="t1",
        debtor_id="d1",
        invoice_id="INV-999",
        invoice_date=date(2026, 1, 1),
        due_date=date(2026, 2, 1),
        open_amount=100.0,
    )
    assert item.schema_version == 1
    assert len(DEFAULT_DUNNING_RULES) == 4
