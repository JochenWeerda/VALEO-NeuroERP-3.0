"""
SLA-Eskalation — Wave 12 AP1/AP2

Batch-SLA-Scanner und Eskalationsereignis-Erzeugung auf Basis von
process_sla.py-Contracts (Wave 4 AP3).
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from app.core.process_sla import (
    EscalationEvent,
    EscalationTarget,
    ProcessSLAPolicy,
    SLASeverity,
    SLAViolation,
    evaluate_sla,
)


def scan_all_sla_violations(
    instances: list[dict[str, Any]],
    policies: list[ProcessSLAPolicy],
) -> list[SLAViolation]:
    """Prueft alle uebergebenen Workflow-Instanzen gegen die SLA-Policies.

    Jeder Eintrag in ``instances`` muss folgende Felder besitzen:
    - ``instance_id`` (str)
    - ``tenant_id`` (str)
    - ``process_key`` (str)
    - ``step_name`` (str)
    - ``started_at`` (datetime | str ISO-8601)
    """
    violations: list[SLAViolation] = []
    for inst in instances:
        started = inst.get("started_at")
        if isinstance(started, str):
            started = datetime.fromisoformat(started)
        if started is None:
            continue
        violation = evaluate_sla(
            instance_id=inst.get("instance_id", ""),
            tenant_id=inst.get("tenant_id", ""),
            process_key=inst.get("process_key", ""),
            step_name=inst.get("step_name", ""),
            started_at=started,
            policies=policies,
        )
        if violation is not None:
            violations.append(violation)
    return violations


def create_escalation_event(
    violation: SLAViolation,
    *,
    override_target: EscalationTarget | None = None,
) -> EscalationEvent:
    """Erzeugt ein Eskalationsereignis fuer eine kritische SLA-Verletzung.

    Nur bei ``severity == CRITICAL`` oder explizit gesetztem ``override_target``
    sinnvoll aufzurufen; bei reinen Warnungen wird trotzdem ein Ereignis erzeugt.
    """
    target = override_target or violation.escalation_target or EscalationTarget.PROCESS_OWNER
    return EscalationEvent(
        escalation_id=f"esc-{uuid.uuid4().hex[:8]}",
        violation_id=violation.violation_id,
        tenant_id=violation.tenant_id,
        target=target,
        message=(
            f"SLA-Verletzung fuer Prozess '{violation.process_key}' "
            f"Schritt '{violation.step_name}': {violation.elapsed_hours:.1f}h "
            f"({violation.severity.value})"
        ),
    )


def acknowledge_escalation(event: EscalationEvent) -> EscalationEvent:
    """Setzt ``acknowledged=True`` auf dem Eskalationsereignis."""
    return event.model_copy(update={"acknowledged": True})


def escalation_summary(violations: list[SLAViolation]) -> dict[str, int]:
    """Zaehlt Verletzungen nach Schweregrad."""
    summary: dict[str, int] = {
        SLASeverity.INFO.value: 0,
        SLASeverity.WARNING.value: 0,
        SLASeverity.CRITICAL.value: 0,
    }
    for v in violations:
        summary[v.severity.value] = summary.get(v.severity.value, 0) + 1
    return summary
