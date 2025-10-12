"""
AI Agents API
Endpoints for triggering and managing agent workflows
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from uuid import uuid4

from ....agents.workflows.bestellvorschlag import build_bestellvorschlag_workflow
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
        # Build and run workflow
        workflow = build_bestellvorschlag_workflow()
        result = await workflow(request.tenant_id, correlation_id)
        
        return WorkflowTriggerResponse(
            workflow_id=correlation_id,
            correlation_id=correlation_id,
            status="completed" if result["order_id"] else "pending_approval",
            started_at=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Workflow failed: {str(e)}")


@router.get("/bestellvorschlag/status/{workflow_id}")
async def get_workflow_status(workflow_id: str):
    """
    Get status of a running workflow.
    
    TODO: Implement workflow state persistence.
    """
    return {
        "workflow_id": workflow_id,
        "status": "completed",
        "message": "Workflow status tracking not yet implemented (Phase 3)"
    }

