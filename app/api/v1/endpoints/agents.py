"""
AI Agents API
Endpoints for triggering and managing agent workflows
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from uuid import uuid4

from ....agents.langgraph_server import (
    invoke_bestellvorschlag,
    resume_bestellvorschlag
)
from ....core.logging import set_correlation_id

logger = logging.getLogger(__name__)

router = APIRouter()


class WorkflowTriggerRequest(BaseModel):
    """Request to trigger a workflow."""
    tenant_id: str = "system"
    parameters: dict = {}


class WorkflowTriggerResponse(BaseModel):
    """Response from triggering a workflow."""
    workflow_id: str
    correlation_id: str
    status: str
    started_at: str


@router.post("/bestellvorschlag/trigger", response_model=WorkflowTriggerResponse)
async def trigger_bestellvorschlag(request: WorkflowTriggerRequest):
    """
    Trigger the Bestellvorschlag (Purchase Order Proposal) workflow.
    
    This workflow:
    1. Analyzes stock levels
    2. Checks sales history
    3. Generates purchase proposal
    4. Waits for approval
    5. Creates purchase order if approved
    """
    correlation_id = str(uuid4())
    set_correlation_id(correlation_id)
    
    logger.info(f"Triggering Bestellvorschlag workflow (tenant: {request.tenant_id})")
    
    try:
        # Invoke LangGraph workflow (pauses at approval checkpoint)
        result = await invoke_bestellvorschlag(request.tenant_id, correlation_id)
        
        return WorkflowTriggerResponse(
            workflow_id=correlation_id,
            correlation_id=correlation_id,
            status="pending_approval",  # Always pauses at checkpoint
            started_at=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Workflow failed: {str(e)}")


class ApprovalRequest(BaseModel):
    """Request to approve or reject a workflow."""
    approved: bool
    rejection_reason: str | None = None


@router.post("/bestellvorschlag/approve/{workflow_id}")
async def approve_workflow(workflow_id: str, request: ApprovalRequest):
    """
    Approve or reject a pending Bestellvorschlag workflow.
    
    If approved, workflow continues to create purchase order.
    If rejected, workflow ends without creating order.
    """
    logger.info(f"Processing approval for workflow {workflow_id}: approved={request.approved}")
    
    try:
        result = await resume_bestellvorschlag(
            workflow_id,
            request.approved,
            request.rejection_reason
        )
        
        return {
            "workflow_id": workflow_id,
            "approved": request.approved,
            "order_id": result.get("order_id"),
            "status": "completed" if result.get("order_id") else "rejected"
        }
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Approval processing failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Approval failed: {str(e)}")


@router.get("/bestellvorschlag/status/{workflow_id}")
async def get_workflow_status(workflow_id: str):
    """
    Get status of a running workflow from LangGraph checkpointer.
    """
    from ....agents.langgraph_server import get_bestellvorschlag_workflow
    
    workflow = get_bestellvorschlag_workflow()
    config = {"configurable": {"thread_id": workflow_id}}
    
    try:
        state = await workflow.aget_state(config)
        
        if state is None:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return {
            "workflow_id": workflow_id,
            "status": "pending_approval" if not state.values.get("approved") else "completed",
            "proposal": state.values.get("proposal"),
            "order_id": state.values.get("order_id"),
            "created_at": state.values.get("created_at")
        }
    
    except Exception as e:
        logger.error(f"Failed to get workflow status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

