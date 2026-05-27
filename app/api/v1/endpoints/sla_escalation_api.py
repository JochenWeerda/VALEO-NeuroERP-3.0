"""
SLA-Eskalation API — Wave 12

Batch-SLA-Scan und Eskalationsverwaltung.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from typing import Any

from ....core.process_sla import build_default_sla_policies
from ....core.sla_escalation import (
    scan_all_sla_violations,
    create_escalation_event,
    escalation_summary,
)

router = APIRouter(prefix="/process/sla", tags=["process-kernel", "sla"])


@router.post("/scan", response_model=dict, summary="Sla violations scannen")
def scan_sla_violations(body: dict) -> dict[str, Any]:
    """Prueft eine Liste von Workflow-Instanzen gegen alle aktiven SLA-Policies."""
    instances: list[dict] = body.get("instances", [])
    if not isinstance(instances, list):
        raise HTTPException(status_code=422, detail="instances muss eine Liste sein")
    policies = build_default_sla_policies()
    violations = scan_all_sla_violations(instances, policies)
    summary = escalation_summary(violations)
    return {
        "violations": [v.model_dump(mode="json") for v in violations],
        "violation_count": len(violations),
        "summary": summary,
        "schema_version": 1,
    }


@router.post("/escalate", response_model=dict, status_code=202, summary="Escalation auslösen")
def trigger_escalation(body: dict) -> dict[str, Any]:
    """Erzeugt ein Eskalationsereignis fuer eine SLA-Verletzung."""
    from ....core.process_sla import SLAViolation
    try:
        violation = SLAViolation(**body.get("violation", {}))
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Ungueltige violation: {exc}") from exc
    event = create_escalation_event(violation)
    return {**event.model_dump(mode="json"), "schema_version": 1}
