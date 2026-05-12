"""
Process SLA API — Wave 4 AP3

Endpoints fuer SLA-Beobachtung, Verletzungsbewertung und Eskalationsquittierung.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.tenant import get_tenant_id
from app.core.process_sla import (
    EscalationEvent,
    ProcessSLAPolicy,
    SLASeverity,
    SLAViolation,
    build_default_sla_policies,
    evaluate_sla,
)

router = APIRouter(prefix="/process/sla", tags=["process", "sla"])

# ---------------------------------------------------------------------------
# In-Memory State
# ---------------------------------------------------------------------------

_VIOLATIONS: list[SLAViolation] = []
_ESCALATION_EVENTS: list[EscalationEvent] = []
_POLICIES: list[ProcessSLAPolicy] = build_default_sla_policies()


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------


class EvaluateSLARequest(BaseModel):
    instance_id: str
    tenant_id: str
    process_key: str
    step_name: str
    started_at: datetime
    schema_version: int = 1


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("/policies")
async def list_sla_policies(
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict]:
    """Gibt alle Standard-SLA-Policies zurueck."""
    return [p.model_dump() for p in _POLICIES]


@router.post("/evaluate")
async def evaluate_sla_endpoint(
    request: EvaluateSLARequest,
    tenant_id: str = Depends(get_tenant_id),
) -> Optional[dict]:
    """
    Bewertet ob eine Workflow-Instanz eine SLA verletzt.
    Gibt die Verletzung zurueck oder null wenn keine Verletzung vorliegt.
    """
    violation = evaluate_sla(
        instance_id=request.instance_id,
        tenant_id=request.tenant_id or tenant_id,
        process_key=request.process_key,
        step_name=request.step_name,
        started_at=request.started_at,
        policies=_POLICIES,
    )
    if violation is None:
        return None

    # Verletzung speichern (Deduplizierung nach violation_id)
    existing_ids = {v.violation_id for v in _VIOLATIONS}
    if violation.violation_id not in existing_ids:
        _VIOLATIONS.append(violation)

        # Bei kritischer Verletzung automatisch Eskalationsereignis erstellen
        if violation.severity == SLASeverity.CRITICAL and violation.escalation_target is not None:
            escalation = EscalationEvent(
                escalation_id=f"esc-{violation.violation_id}",
                violation_id=violation.violation_id,
                tenant_id=violation.tenant_id,
                target=violation.escalation_target,
                message=(
                    f"Kritische SLA-Verletzung: Prozess '{violation.process_key}', "
                    f"Schritt '{violation.step_name}', Instanz '{violation.instance_id}'. "
                    f"Verstrichen: {violation.elapsed_hours:.1f}h."
                ),
            )
            _ESCALATION_EVENTS.append(escalation)

    return violation.model_dump()


@router.get("/violations")
async def list_violations(
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict]:
    """Gibt alle bekannten SLA-Verletzungen des Tenants zurueck."""
    tenant_violations = [
        v for v in _VIOLATIONS if v.tenant_id == tenant_id
    ]
    return [v.model_dump() for v in tenant_violations]


@router.post("/violations/{violation_id}/acknowledge")
async def acknowledge_violation(
    violation_id: str,
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    """
    Quittiert eine Eskalation: setzt acknowledged=True und escalated=False
    auf dem zugehoerigen EscalationEvent.
    """
    # Verletzung pruefen
    violation = next((v for v in _VIOLATIONS if v.violation_id == violation_id), None)
    if violation is None:
        raise HTTPException(
            status_code=404,
            detail=f"Verletzung '{violation_id}' nicht gefunden.",
        )
    if violation.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Zugriff verweigert.")

    # Zugehoerigen Eskalationsevent quittieren
    escalation = next(
        (e for e in _ESCALATION_EVENTS if e.violation_id == violation_id), None
    )
    if escalation is None:
        raise HTTPException(
            status_code=404,
            detail=f"Kein Eskalationsevent fuer Verletzung '{violation_id}' gefunden.",
        )

    escalation.acknowledged = True
    violation.escalated = False

    return {
        "violation_id": violation_id,
        "acknowledged": True,
        "escalation_id": escalation.escalation_id,
        "acknowledged_at": datetime.now(timezone.utc).isoformat(),
    }
