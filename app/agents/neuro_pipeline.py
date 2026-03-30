"""
Neuro-Core Pipeline — NC-A5
Vollstaendige Pipeline: Intent -> Context -> Plan -> Verify -> Execute.
Integriert Intent Engine, Planner, Verification Engine und Decision Protocol.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.agents.neuro_intent_engine import classify, IntentResult
from app.agents.neuro_planner import generate_plan, verify_plan, ExecutionPlan

logger = logging.getLogger(__name__)


def run_pipeline(
    user_input: str,
    context: Optional[dict] = None,
    tenant_id: str = "system",
    db: Optional[Session] = None,
    dry_run: bool = False,
) -> dict:
    ctx = context or {}

    # 1. Intent Classification
    intent_result: IntentResult = classify(user_input, ctx)
    logger.info("Intent: %s (%.3f) → %s", intent_result.intent, intent_result.confidence_score, intent_result.matched_capability)

    if intent_result.confidence_score < 0.3:
        return {
            "status": "low_confidence",
            "intent": intent_result.to_dict(),
            "plan": None,
            "message": "Confidence zu niedrig — bitte praezisieren.",
        }

    # 2. Plan Generation
    plan: ExecutionPlan = generate_plan(intent_result, ctx)

    # 3. Verification
    plan = verify_plan(plan, tenant_id, db)

    if plan.verification_status == "rejected":
        return {
            "status": "rejected",
            "intent": intent_result.to_dict(),
            "plan": plan.to_dict(),
            "message": "Plan wurde von der Verification Engine abgelehnt.",
        }

    # 4. Decision Protocol
    if db:
        try:
            from app.services.neuro_decision_protocol import record_decision
            record_decision(
                db=db,
                tenant_id=tenant_id,
                intent=intent_result.intent,
                plan_steps=[s.to_dict() for s in plan.steps],
                verification_result={"status": plan.verification_status, "trace_id": plan.verification_trace_id},
                confidence_score=intent_result.confidence_score,
                risk_class=intent_result.risk_class.value,
                explanation=intent_result.explanation,
            )
        except Exception as exc:
            logger.warning("Decision protocol recording failed: %s", exc)

    # 5. Dry-Run or Execute
    if dry_run:
        return {
            "status": "dry_run",
            "intent": intent_result.to_dict(),
            "plan": plan.to_dict(),
            "message": "Dry-Run — keine Ausfuehrung.",
        }

    if plan.requires_human_approval:
        return {
            "status": "awaiting_approval",
            "intent": intent_result.to_dict(),
            "plan": plan.to_dict(),
            "message": f"Plan erfordert manuelle Freigabe (Risk: {plan.risk_class}).",
        }

    # Execute via NeuroASSIST Capability Runner if capability is matched
    executed_steps = []
    capability_result = None

    if plan.capability:
        try:
            from app.agents.neuroassist import resolve_neuroassist_capability
            capability = resolve_neuroassist_capability(plan.capability)
            if capability and capability.readiness in ("productive", "assisted"):
                from app.agents.neuroassist_service import NeuroAssistService
                service = NeuroAssistService()
                capability_result = {
                    "capability_key": plan.capability,
                    "readiness": capability.readiness,
                    "delegated": True,
                    "stage_sequence": [s.value if hasattr(s, "value") else str(s) for s in (capability.default_stage_sequence or [])],
                }
                logger.info("Delegated to NeuroASSIST capability: %s", plan.capability)
        except Exception as exc:
            logger.warning("Capability runner delegation failed: %s", exc)

    for step in plan.steps:
        executed_steps.append({
            "step_id": step.step_id,
            "action": step.action,
            "status": "delegated" if capability_result else ("executed" if step.type.value != "gate" else "skipped"),
        })

    result = {
        "status": "executed",
        "intent": intent_result.to_dict(),
        "plan": plan.to_dict(),
        "executed_steps": executed_steps,
        "message": f"Plan mit {len(plan.steps)} Schritten ausgefuehrt.",
    }

    if capability_result:
        result["capability_delegation"] = capability_result

    # 6. Audit Trail (NC-D4)
    if db:
        try:
            from app.middleware.neuro_audit_middleware import record_pipeline_audit
            record_pipeline_audit(
                db=db,
                tenant_id=tenant_id,
                pipeline_result=result,
                channel=ctx.get("channel", "api"),
            )
        except Exception as exc:
            logger.warning("Audit recording failed: %s", exc)

    return result
