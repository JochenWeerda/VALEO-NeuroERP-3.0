"""
AI Agents API
Endpoints for triggering and managing agent workflows
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime

from ....agents import get_genxais_service
from ....core.logging import set_correlation_id

logger = logging.getLogger(__name__)

router = APIRouter()
genxais_service = get_genxais_service()


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
    capability_key: str


class CapabilityResponse(BaseModel):
    capability_key: str
    title: str
    kind: str
    domain: str
    readiness: str
    workflow_module: str
    workflow_builder: str
    workflow_entrypoint: str
    description: str
    process_scopes: list[str]


@router.get("/genxais/capabilities", response_model=list[CapabilityResponse])
async def list_genxais_capabilities(productive_only: bool = True):
    capabilities = genxais_service.list_capabilities(productive_only=productive_only)
    return [
        CapabilityResponse(
            capability_key=cap.capability_key,
            title=cap.title,
            kind=cap.kind,
            domain=cap.domain,
            readiness=cap.readiness,
            workflow_module=cap.workflow_module,
            workflow_builder=cap.workflow_builder,
            workflow_entrypoint=cap.workflow_entrypoint,
            description=cap.description,
            process_scopes=list(cap.process_scopes),
        )
        for cap in capabilities
    ]


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
    logger.info(f"Triggering Bestellvorschlag workflow (tenant: {request.tenant_id})")
    
    try:
        result = await genxais_service.trigger_bestellvorschlag(request.tenant_id)
        set_correlation_id(result["correlation_id"])
        return WorkflowTriggerResponse(**result)
    
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
        result = await genxais_service.approve_bestellvorschlag(
            workflow_id,
            request.approved,
            request.rejection_reason,
        )
        return result
    
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
    try:
        return await genxais_service.get_bestellvorschlag_status(workflow_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get workflow status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

