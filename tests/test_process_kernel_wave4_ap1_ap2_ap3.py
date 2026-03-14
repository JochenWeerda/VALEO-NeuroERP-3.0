"""
Wave-4 Contract-Tests: AP1 Workflow-Runtime + AP2 Projektions-Consumer + AP3 Process-SLA
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

# ---------------------------------------------------------------------------
# AP1 Imports
# ---------------------------------------------------------------------------
from app.core.workflow_runtime import (
    WorkflowCheckpoint,
    WorkflowInstance,
    WorkflowRuntimeStatus,
    WorkflowRuntimeStore,
)

# ---------------------------------------------------------------------------
# AP2 Imports
# ---------------------------------------------------------------------------
from app.core.projection_consumer import (
    ProjectionConsumer,
    ProjectionRegistry,
    ProjectionStatus,
    RebuildRequest,
    build_default_projection_registry,
)

# ---------------------------------------------------------------------------
# AP3 Imports
# ---------------------------------------------------------------------------
from app.core.process_sla import (
    EscalationTarget,
    ProcessSLAPolicy,
    SLASeverity,
    SLAViolation,
    build_default_sla_policies,
    evaluate_sla,
)


# ===========================================================================
# AP1: Persistente Workflow-Laufzeit
# ===========================================================================


def _make_instance(
    instance_id: str = "inst-1",
    tenant_id: str = "tenant-test",
    process_key: str = "ap_invoice_approval",
    aggregate_type: str = "ap_invoice",
    aggregate_id: str = "inv-42",
    status: WorkflowRuntimeStatus = WorkflowRuntimeStatus.PENDING,
) -> WorkflowInstance:
    return WorkflowInstance(
        instance_id=instance_id,
        tenant_id=tenant_id,
        process_key=process_key,
        definition_version="1.0.0",
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        status=status,
    )


def test_workflow_instance_add_checkpoint_updates_step():
    """add_checkpoint() muss current_step und checkpoints aktualisieren."""
    inst = _make_instance()
    assert inst.current_step is None
    assert len(inst.checkpoints) == 0

    cp = inst.add_checkpoint("review", {"reviewer": "user-1"})

    assert inst.current_step == "review"
    assert len(inst.checkpoints) == 1
    assert cp.step_name == "review"
    assert cp.state_snapshot == {"reviewer": "user-1"}
    assert cp.checkpoint_id == "cp-1"
    assert cp.schema_version == 1


def test_workflow_instance_is_resumable_waiting_approval():
    """WAITING_APPROVAL-Instanzen sind resumierbar."""
    inst = _make_instance(status=WorkflowRuntimeStatus.WAITING_APPROVAL)
    assert inst.is_resumable() is True


def test_workflow_instance_is_resumable_failed():
    """FAILED-Instanzen sind resumierbar."""
    inst = _make_instance(status=WorkflowRuntimeStatus.FAILED)
    assert inst.is_resumable() is True


def test_workflow_instance_is_resumable_completed_false():
    """COMPLETED-Instanzen sind NICHT resumierbar."""
    inst = _make_instance(status=WorkflowRuntimeStatus.COMPLETED)
    assert inst.is_resumable() is False


def test_workflow_instance_is_resumable_running_false():
    """RUNNING-Instanzen sind NICHT resumierbar."""
    inst = _make_instance(status=WorkflowRuntimeStatus.RUNNING)
    assert inst.is_resumable() is False


def test_workflow_runtime_store_upsert_and_get():
    """Store.upsert() und Store.get() funktionieren korrekt."""
    store = WorkflowRuntimeStore()
    inst = _make_instance("inst-upsert-1")

    # Noch nicht im Store
    assert store.get("inst-upsert-1") is None

    # Einfuegen
    store.upsert(inst)
    retrieved = store.get("inst-upsert-1")
    assert retrieved is not None
    assert retrieved.instance_id == "inst-upsert-1"

    # Update (Upsert)
    inst.status = WorkflowRuntimeStatus.RUNNING
    store.upsert(inst)
    updated = store.get("inst-upsert-1")
    assert updated is not None
    assert updated.status == WorkflowRuntimeStatus.RUNNING
    assert len(store.instances) == 1  # Kein Duplikat


def test_workflow_runtime_store_get_by_aggregate():
    """Store.get_by_aggregate() filtert korrekt nach Aggregat-Typ und -ID."""
    store = WorkflowRuntimeStore()
    inst1 = _make_instance("inst-agg-1", aggregate_type="ap_invoice", aggregate_id="inv-1")
    inst2 = _make_instance("inst-agg-2", aggregate_type="ap_invoice", aggregate_id="inv-1")
    inst3 = _make_instance("inst-agg-3", aggregate_type="ap_invoice", aggregate_id="inv-2")
    inst4 = _make_instance("inst-agg-4", aggregate_type="payment_run", aggregate_id="inv-1")

    for i in [inst1, inst2, inst3, inst4]:
        store.upsert(i)

    result = store.get_by_aggregate("ap_invoice", "inv-1")
    assert len(result) == 2
    ids = {i.instance_id for i in result}
    assert ids == {"inst-agg-1", "inst-agg-2"}


def test_workflow_runtime_store_get_by_status():
    """Store.get_by_status() filtert korrekt nach Status."""
    store = WorkflowRuntimeStore()
    pending1 = _make_instance("inst-st-1", status=WorkflowRuntimeStatus.PENDING)
    pending2 = _make_instance("inst-st-2", status=WorkflowRuntimeStatus.PENDING)
    running = _make_instance("inst-st-3", status=WorkflowRuntimeStatus.RUNNING)
    completed = _make_instance("inst-st-4", status=WorkflowRuntimeStatus.COMPLETED)

    for i in [pending1, pending2, running, completed]:
        store.upsert(i)

    pending_list = store.get_by_status(WorkflowRuntimeStatus.PENDING)
    assert len(pending_list) == 2

    running_list = store.get_by_status(WorkflowRuntimeStatus.RUNNING)
    assert len(running_list) == 1

    cancelled_list = store.get_by_status(WorkflowRuntimeStatus.CANCELLED)
    assert cancelled_list == []


def test_workflow_instance_latest_checkpoint():
    """latest_checkpoint() gibt den letzten Checkpoint zurueck."""
    inst = _make_instance()

    # Kein Checkpoint
    assert inst.latest_checkpoint() is None

    # Einen Checkpoint hinzufuegen
    inst.add_checkpoint("step-1", {"data": 1})
    cp2 = inst.add_checkpoint("step-2", {"data": 2})

    latest = inst.latest_checkpoint()
    assert latest is not None
    assert latest.checkpoint_id == cp2.checkpoint_id
    assert latest.step_name == "step-2"


def test_workflow_checkpoint_schema_version():
    """WorkflowCheckpoint hat schema_version == 1."""
    cp = WorkflowCheckpoint(
        checkpoint_id="cp-test",
        step_name="test-step",
        state_snapshot={"key": "value"},
    )
    assert cp.schema_version == 1


def test_workflow_instance_schema_version():
    """WorkflowInstance hat schema_version == 1."""
    inst = _make_instance()
    assert inst.schema_version == 1


def test_workflow_runtime_store_schema_version():
    """WorkflowRuntimeStore hat schema_version == 1."""
    store = WorkflowRuntimeStore()
    assert store.schema_version == 1


# ===========================================================================
# AP2: Asynchrone Projektionen und Consumer
# ===========================================================================


def test_projection_registry_build_default_has_cockpits():
    """build_default_projection_registry() muss alle drei Standard-Cockpits enthalten."""
    registry = build_default_projection_registry()

    assert registry.get("ap_invoice_cockpit") is not None
    assert registry.get("payment_run_cockpit") is not None
    assert registry.get("process_observation") is not None
    assert len(registry.consumers) >= 3


def test_projection_consumer_mark_stale_updates_lag():
    """mark_stale() setzt Status auf STALE und aktualisiert lag_count."""
    consumer = ProjectionConsumer(
        consumer_id="c-1",
        projection_name="test_projection",
        event_subjects=["*.test.*"],
        status=ProjectionStatus.CURRENT,
        lag_count=0,
    )
    consumer.mark_stale(42)
    assert consumer.status == ProjectionStatus.STALE
    assert consumer.lag_count == 42


def test_projection_consumer_mark_current():
    """mark_current() setzt Status auf CURRENT und setzt lag_count auf 0."""
    consumer = ProjectionConsumer(
        consumer_id="c-2",
        projection_name="test_projection",
        event_subjects=["*.test.*"],
        status=ProjectionStatus.STALE,
        lag_count=15,
    )
    consumer.mark_current("event-xyz-999")
    assert consumer.status == ProjectionStatus.CURRENT
    assert consumer.lag_count == 0
    assert consumer.last_event_id == "event-xyz-999"
    assert consumer.last_updated is not None


def test_projection_registry_get_stale():
    """get_stale() gibt alle Consumer mit Status STALE zurueck."""
    registry = build_default_projection_registry()

    # Initial sind alle STALE (Default)
    stale = registry.get_stale()
    assert len(stale) == len(registry.consumers)

    # Einen Consumer als CURRENT markieren
    ap_consumer = registry.get("ap_invoice_cockpit")
    assert ap_consumer is not None
    ap_consumer.mark_current("event-100")

    stale_after = registry.get_stale()
    assert len(stale_after) == len(registry.consumers) - 1
    assert all(c.projection_name != "ap_invoice_cockpit" for c in stale_after)


def test_projection_registry_get_returns_none_for_unknown():
    """get() gibt None zurueck fuer unbekannte Projektion."""
    registry = build_default_projection_registry()
    result = registry.get("nonexistent_projection")
    assert result is None


def test_projection_consumer_schema_version():
    """ProjectionConsumer hat schema_version == 1."""
    consumer = ProjectionConsumer(
        consumer_id="c-schema",
        projection_name="schema_test",
        event_subjects=["*.test.*"],
    )
    assert consumer.schema_version == 1


def test_rebuild_request_schema_version():
    """RebuildRequest hat schema_version == 1."""
    req = RebuildRequest(
        projection_name="ap_invoice_cockpit",
        requested_by="admin@test.de",
        tenant_id="tenant-1",
        reason="Dateninkonsistenz nach Migration",
    )
    assert req.schema_version == 1
    assert req.status == "accepted"


def test_projection_registry_schema_version():
    """ProjectionRegistry hat schema_version == 1."""
    registry = ProjectionRegistry()
    assert registry.schema_version == 1


# ===========================================================================
# AP3: SLA/Timeout/Eskalationsbeobachtung
# ===========================================================================


def test_build_default_sla_policies_covers_ap_invoice():
    """build_default_sla_policies() muss ap_invoice_approval enthalten."""
    policies = build_default_sla_policies()
    ap_policy = next(
        (p for p in policies if p.process_key == "ap_invoice_approval"), None
    )
    assert ap_policy is not None
    assert ap_policy.policy_id == "sla-ap-approval"
    assert ap_policy.warning_after_hours == 24.0
    assert ap_policy.critical_after_hours == 72.0
    assert ap_policy.escalation_target == EscalationTarget.PROCESS_OWNER
    assert ap_policy.schema_version == 1


def test_build_default_sla_policies_covers_all_four():
    """build_default_sla_policies() muss alle vier Kernprozesse abdecken."""
    policies = build_default_sla_policies()
    keys = {p.process_key for p in policies}
    assert "ap_invoice_approval" in keys
    assert "harvest_acceptance" in keys
    assert "quality_protocol" in keys
    assert "payment_run" in keys


def test_evaluate_sla_no_violation_within_warning():
    """Keine Verletzung wenn elapsed < warning_after_hours."""
    policies = build_default_sla_policies()
    # started_at 1 Stunde in der Vergangenheit (warning bei 24h)
    started_at = datetime.now(timezone.utc) - timedelta(hours=1)

    violation = evaluate_sla(
        instance_id="inst-ok",
        tenant_id="t1",
        process_key="ap_invoice_approval",
        step_name="waiting_approval",
        started_at=started_at,
        policies=policies,
    )
    assert violation is None


def test_evaluate_sla_warning_after_threshold():
    """WARNING-Verletzung wenn 24h <= elapsed < 72h fuer ap_invoice_approval."""
    policies = build_default_sla_policies()
    # Genau 30 Stunden verstrichen
    started_at = datetime.now(timezone.utc) - timedelta(hours=30)

    violation = evaluate_sla(
        instance_id="inst-warn",
        tenant_id="t1",
        process_key="ap_invoice_approval",
        step_name="waiting_approval",
        started_at=started_at,
        policies=policies,
    )
    assert violation is not None
    assert violation.severity == SLASeverity.WARNING
    assert violation.escalated is False
    assert violation.escalation_target is None
    assert violation.elapsed_hours >= 30.0
    assert violation.schema_version == 1


def test_evaluate_sla_critical_after_threshold():
    """CRITICAL-Verletzung wenn elapsed >= 72h fuer ap_invoice_approval."""
    policies = build_default_sla_policies()
    # 80 Stunden verstrichen
    started_at = datetime.now(timezone.utc) - timedelta(hours=80)

    violation = evaluate_sla(
        instance_id="inst-crit",
        tenant_id="t1",
        process_key="ap_invoice_approval",
        step_name="waiting_approval",
        started_at=started_at,
        policies=policies,
    )
    assert violation is not None
    assert violation.severity == SLASeverity.CRITICAL
    assert violation.elapsed_hours >= 80.0


def test_evaluate_sla_critical_sets_escalated_true():
    """Kritische SLA-Verletzung setzt escalated=True und escalation_target."""
    policies = build_default_sla_policies()
    started_at = datetime.now(timezone.utc) - timedelta(hours=100)

    violation = evaluate_sla(
        instance_id="inst-esc",
        tenant_id="t1",
        process_key="ap_invoice_approval",
        step_name="waiting_approval",
        started_at=started_at,
        policies=policies,
    )
    assert violation is not None
    assert violation.escalated is True
    assert violation.escalation_target == EscalationTarget.PROCESS_OWNER


def test_evaluate_sla_payment_run_escalates_to_management():
    """payment_run kritische Verletzung eskaliert an MANAGEMENT."""
    policies = build_default_sla_policies()
    # 100 Stunden (kritisch bei 96h)
    started_at = datetime.now(timezone.utc) - timedelta(hours=100)

    violation = evaluate_sla(
        instance_id="inst-pay",
        tenant_id="t1",
        process_key="payment_run",
        step_name="waiting_approval",
        started_at=started_at,
        policies=policies,
    )
    assert violation is not None
    assert violation.severity == SLASeverity.CRITICAL
    assert violation.escalation_target == EscalationTarget.MANAGEMENT


def test_evaluate_sla_no_matching_policy_returns_none():
    """Keine passende Policy → evaluate_sla gibt None zurueck."""
    policies = build_default_sla_policies()
    started_at = datetime.now(timezone.utc) - timedelta(hours=999)

    violation = evaluate_sla(
        instance_id="inst-no-policy",
        tenant_id="t1",
        process_key="unknown_process",
        step_name="unknown_step",
        started_at=started_at,
        policies=policies,
    )
    assert violation is None


def test_evaluate_sla_violation_id_format():
    """violation_id folgt dem Format 'viol-{instance_id}-{step_name}'."""
    policies = build_default_sla_policies()
    started_at = datetime.now(timezone.utc) - timedelta(hours=30)

    violation = evaluate_sla(
        instance_id="inst-42",
        tenant_id="t1",
        process_key="ap_invoice_approval",
        step_name="waiting_approval",
        started_at=started_at,
        policies=policies,
    )
    assert violation is not None
    assert violation.violation_id == "viol-inst-42-waiting_approval"


def test_process_sla_policy_schema_version():
    """ProcessSLAPolicy hat schema_version == 1."""
    policy = ProcessSLAPolicy(
        policy_id="sla-test",
        process_key="test_process",
        step_name="test_step",
        warning_after_hours=1.0,
        critical_after_hours=2.0,
    )
    assert policy.schema_version == 1


def test_sla_violation_schema_version():
    """SLAViolation hat schema_version == 1."""
    now = datetime.now(timezone.utc)
    violation = SLAViolation(
        violation_id="viol-test",
        instance_id="inst-test",
        tenant_id="t1",
        process_key="ap_invoice_approval",
        step_name="waiting_approval",
        started_at=now - timedelta(hours=30),
        violation_detected_at=now,
        elapsed_hours=30.0,
        severity=SLASeverity.WARNING,
    )
    assert violation.schema_version == 1
