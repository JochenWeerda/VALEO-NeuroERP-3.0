"""
LangGraph Server
Real workflow execution with state persistence and checkpoints
"""

import logging

from app.core.human_approval_gate import (
    ApprovalDecision,
    ApprovalRisikostufe,
    record_approval_decision,
)

from .workflows.bestellvorschlag import (
    BestellvorschlagState,
    BESTELLVORSCHLAG_AKTIONSTYP,
    build_bestellvorschlag_workflow,
    run_bestellvorschlag_workflow
)

logger = logging.getLogger(__name__)


def build_bestellvorschlag_graph():
    """
    Build the productive Bestellvorschlag workflow.
    """
    logger.info("Bestellvorschlag workflow compiled with shared builder")
    return build_bestellvorschlag_workflow()


# Global workflow instance
_bestellvorschlag_workflow = None


def get_bestellvorschlag_workflow():
    """Get the global Bestellvorschlag workflow instance."""
    global _bestellvorschlag_workflow
    if _bestellvorschlag_workflow is None:
        _bestellvorschlag_workflow = build_bestellvorschlag_graph()
    return _bestellvorschlag_workflow


async def invoke_bestellvorschlag(tenant_id: str, correlation_id: str) -> BestellvorschlagState:
    """
    Invoke Bestellvorschlag workflow using the new LangGraph implementation.

    Returns state at checkpoint (before approval).
    """
    # Use the new LangGraph-based workflow
    result = await run_bestellvorschlag_workflow(tenant_id, correlation_id)

    logger.info(f"Bestellvorschlag workflow paused at approval checkpoint: {correlation_id}")
    return result


async def resume_bestellvorschlag(
    workflow_id: str, 
    approved: bool, 
    rejection_reason: str | None = None
) -> BestellvorschlagState:
    """
    Resume Bestellvorschlag workflow after approval/rejection.
    """
    workflow = get_bestellvorschlag_workflow()
    
    config = {"configurable": {"thread_id": workflow_id}}
    
    # Get current state from checkpoint
    state = await workflow.aget_state(config)
    
    if state is None:
        raise ValueError(f"Workflow {workflow_id} not found")

    approval_requirement = state.values.get("approval_requirement") or {}
    # Update state with approval decision
    state.values["approved"] = approved
    state.values["rejection_reason"] = rejection_reason
    if approval_requirement.get("requires_human_approval"):
        record = record_approval_decision(
            aktions_typ=approval_requirement.get("aktions_typ", BESTELLVORSCHLAG_AKTIONSTYP),
            instanz_id=workflow_id,
            agent_id="neuroassist.bestellvorschlag",
            risiko_stufe=ApprovalRisikostufe(approval_requirement["risiko_stufe"]),
            decision=ApprovalDecision.GENEHMIGT if approved else ApprovalDecision.ABGELEHNT,
            entschieden_von="human_operator",
            begruendung=rejection_reason or ("Human approval granted" if approved else "Human approval rejected"),
            kontext={
                "tenant_id": state.values.get("tenant_id"),
                "proposal": state.values.get("proposal"),
                "approval_requirement": approval_requirement,
            },
        )
        state.values["approval_record"] = record.as_dict()
        existing_gate_decisions = [
            entry
            for entry in state.values.get("gate_decisions", [])
            if entry.get("gate_type") != "approval_gate"
        ]
        existing_gate_decisions.append(
            {
                "gate_type": "approval_gate",
                "status": "allowed" if approved else "blocked",
                "reason": (
                    "Human approval granted for the proposed action."
                    if approved
                    else "Human approval rejected the proposed action."
                ),
                "required_role": "human_operator",
                "schema_version": 1,
            }
        )
        state.values["gate_decisions"] = existing_gate_decisions
        state.values["current_stage_key"] = "execution" if approved else "closure"
        state.values.setdefault("stage_transition_log", []).append(
            {
                "stage_key": state.values["current_stage_key"],
                "timestamp": record.entschieden_am.isoformat() if approval_requirement.get("requires_human_approval") and record else None,
                "detail": "Approval decision applied",
            }
        )

    # Resume from checkpoint
    result = await workflow.ainvoke(None, config)
    
    logger.info(f"Workflow {workflow_id} resumed: approved={approved}")
    return result

