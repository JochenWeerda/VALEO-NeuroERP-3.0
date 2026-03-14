"""
SLA/Timeout/Eskalationsbeobachtung — Wave 4 AP3

Definiert SLA-Policies fuer Kernprozesse und bewertet Verletzungen
anhand von Laufzeiten und Eskalationsstufen.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class SLASeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class EscalationTarget(str, Enum):
    PROCESS_OWNER = "process_owner"
    TEAM_LEAD = "team_lead"
    MANAGEMENT = "management"


class ProcessSLAPolicy(BaseModel):
    """SLA-Richtlinie fuer einen Kernprozessschritt."""

    policy_id: str
    process_key: str           # z.B. "ap_invoice_approval"
    process_definition_key: str | None = None
    workflow_key: str | None = None
    workflow_version_number: int | None = None
    step_name: str             # z.B. "waiting_approval"
    warning_after_hours: float
    critical_after_hours: float
    escalation_target: EscalationTarget = EscalationTarget.PROCESS_OWNER
    active: bool = True
    schema_version: int = 1


class SLAViolation(BaseModel):
    """Gemessene SLA-Verletzung einer Workflow-Instanz."""

    violation_id: str
    instance_id: str
    tenant_id: str
    process_key: str
    process_definition_key: str | None = None
    workflow_key: str | None = None
    workflow_version_number: int | None = None
    step_name: str
    started_at: datetime
    violation_detected_at: datetime
    elapsed_hours: float
    severity: SLASeverity
    escalated: bool = False
    escalation_target: Optional[EscalationTarget] = None
    schema_version: int = 1


class EscalationEvent(BaseModel):
    """Ausgeloestes Eskalationsereignis."""

    escalation_id: str
    violation_id: str
    tenant_id: str
    target: EscalationTarget
    message: str
    triggered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    acknowledged: bool = False
    schema_version: int = 1


def build_default_sla_policies() -> list[ProcessSLAPolicy]:
    """Standard-SLAs fuer Kernprozesse."""
    return [
        ProcessSLAPolicy(
            policy_id="sla-ap-approval",
            process_key="ap_invoice_approval",
            process_definition_key="settlement_to_finance",
            workflow_key="ap_invoice_approval",
            workflow_version_number=1,
            step_name="waiting_approval",
            warning_after_hours=24.0,
            critical_after_hours=72.0,
        ),
        ProcessSLAPolicy(
            policy_id="sla-harvest-acceptance",
            process_key="harvest_acceptance",
            process_definition_key="contract_to_intake",
            workflow_key="annahme",
            workflow_version_number=1,
            step_name="pending",
            warning_after_hours=4.0,
            critical_after_hours=8.0,
        ),
        ProcessSLAPolicy(
            policy_id="sla-quality-protocol",
            process_key="quality_protocol",
            process_definition_key="intake_to_quality",
            workflow_key="annahme",
            workflow_version_number=1,
            step_name="pending",
            warning_after_hours=8.0,
            critical_after_hours=24.0,
        ),
        ProcessSLAPolicy(
            policy_id="sla-payment-run",
            process_key="payment_run",
            step_name="waiting_approval",
            warning_after_hours=48.0,
            critical_after_hours=96.0,
            escalation_target=EscalationTarget.MANAGEMENT,
        ),
        # Wave 19: agrar_settlement SLA-Policies
        ProcessSLAPolicy(
            policy_id="sla-agrar-settlement",
            process_key="agrar_settlement",
            process_definition_key="agrar_settlement",
            workflow_key="agrar_settlement",
            workflow_version_number=1,
            step_name="waiting_approval",
            warning_after_hours=24.0,
            critical_after_hours=48.0,
            escalation_target=EscalationTarget.TEAM_LEAD,
        ),
        ProcessSLAPolicy(
            policy_id="sla-agrar-settlement-approval",
            process_key="agrar_settlement_approval",
            process_definition_key="agrar_settlement",
            workflow_key="agrar_settlement",
            workflow_version_number=1,
            step_name="zur_freigabe",
            warning_after_hours=8.0,
            critical_after_hours=24.0,
            escalation_target=EscalationTarget.TEAM_LEAD,
        ),
        ProcessSLAPolicy(
            policy_id="sla-agrar-settlement-posting",
            process_key="agrar_settlement",
            process_definition_key="agrar_settlement",
            workflow_key="agrar_settlement",
            workflow_version_number=1,
            step_name="freigegeben_pending_verbuchung",
            warning_after_hours=4.0,
            critical_after_hours=12.0,
            escalation_target=EscalationTarget.MANAGEMENT,
        ),
    ]


def evaluate_sla(
    instance_id: str,
    tenant_id: str,
    process_key: str,
    step_name: str,
    started_at: datetime,
    policies: list[ProcessSLAPolicy],
    *,
    process_definition_key: str | None = None,
    workflow_key: str | None = None,
    workflow_version_number: int | None = None,
) -> Optional[SLAViolation]:
    """Prueft ob eine Workflow-Instanz eine SLA verletzt."""
    policy = next(
        (
            p
            for p in policies
            if p.process_key == process_key
            and p.step_name == step_name
            and p.active
            and (
                process_definition_key is None
                or p.process_definition_key is None
                or p.process_definition_key == process_definition_key
            )
            and (
                workflow_key is None
                or p.workflow_key is None
                or p.workflow_key == workflow_key
            )
            and (
                workflow_version_number is None
                or p.workflow_version_number is None
                or p.workflow_version_number == workflow_version_number
            )
        ),
        None,
    )
    if policy is None:
        return None

    # Sicherstellen, dass started_at timezone-aware ist
    if started_at.tzinfo is None:
        started_at = started_at.replace(tzinfo=timezone.utc)

    elapsed = (datetime.now(timezone.utc) - started_at).total_seconds() / 3600

    if elapsed >= policy.critical_after_hours:
        severity = SLASeverity.CRITICAL
    elif elapsed >= policy.warning_after_hours:
        severity = SLASeverity.WARNING
    else:
        return None

    return SLAViolation(
        violation_id=f"viol-{instance_id}-{step_name}",
        instance_id=instance_id,
        tenant_id=tenant_id,
        process_key=process_key,
        process_definition_key=(
            process_definition_key or policy.process_definition_key
        ),
        workflow_key=workflow_key or policy.workflow_key,
        workflow_version_number=(
            workflow_version_number or policy.workflow_version_number
        ),
        step_name=step_name,
        started_at=started_at,
        violation_detected_at=datetime.now(timezone.utc),
        elapsed_hours=elapsed,
        severity=severity,
        escalated=severity == SLASeverity.CRITICAL,
        escalation_target=(
            policy.escalation_target if severity == SLASeverity.CRITICAL else None
        ),
    )
