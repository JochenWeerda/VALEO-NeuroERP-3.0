"""
AI Agents API
Endpoints for triggering and managing agent workflows
"""

from datetime import datetime
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ....agents import get_neuroassist_service
from ....core.logging import set_correlation_id

logger = logging.getLogger(__name__)

router = APIRouter()
neuroassist_service = get_neuroassist_service()


class CapabilityResponse(BaseModel):
    capability_key: str
    title: str
    kind: str
    domain: str
    role_key: str
    orchestration_pattern: str
    default_stage_sequence: list[str]
    readiness: str
    workflow_module: str
    workflow_builder: str
    workflow_entrypoint: str
    description: str
    process_scopes: list[str]


class NeuroAssistRunRequest(BaseModel):
    capability_key: str
    tenant_id: str = "system"
    parameters: dict = Field(default_factory=dict)


class NeuroAssistRunResponse(BaseModel):
    run_id: str
    correlation_id: str
    capability_key: str
    status: str
    started_at: str
    runtime: dict
    result: dict = Field(default_factory=dict)


class NeuroAssistGateActionRequest(BaseModel):
    gate_type: str
    decision: str
    rejection_reason: str | None = None


class NeuroAssistGateActionResponse(BaseModel):
    run_id: str
    correlation_id: str
    capability_key: str
    started_at: str
    status: str
    runtime: dict
    result: dict = Field(default_factory=dict)


def _list_capability_responses(productive_only: bool) -> list[CapabilityResponse]:
    capabilities = neuroassist_service.list_capabilities(productive_only=productive_only)
    return [
        CapabilityResponse(
            capability_key=cap.capability_key,
            title=cap.title,
            kind=cap.kind,
            domain=cap.domain,
            role_key=cap.role_key,
            orchestration_pattern=cap.orchestration_pattern,
            default_stage_sequence=list(cap.default_stage_sequence),
            readiness=cap.readiness,
            workflow_module=cap.workflow_module,
            workflow_builder=cap.workflow_builder,
            workflow_entrypoint=cap.workflow_entrypoint,
            description=cap.description,
            process_scopes=list(cap.process_scopes),
        )
        for cap in capabilities
    ]


@router.get("/neuroassist/capabilities", response_model=list[CapabilityResponse])
async def list_neuroassist_capabilities(productive_only: bool = True):
    return _list_capability_responses(productive_only)


@router.post("/neuroassist/runs", response_model=NeuroAssistRunResponse)
async def run_neuroassist_capability(request: NeuroAssistRunRequest):
    logger.info(
        "Running NeuroASSIST capability '%s' (tenant: %s)",
        request.capability_key,
        request.tenant_id,
    )

    try:
        result = await neuroassist_service.run_capability(
            request.capability_key,
            tenant_id=request.tenant_id,
            parameters=request.parameters,
        )
        set_correlation_id(result["correlation_id"])
        return NeuroAssistRunResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.error("NeuroASSIST capability run failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"NeuroASSIST run failed: {str(exc)}")


@router.get("/neuroassist/runs/{run_id}", response_model=NeuroAssistRunResponse)
async def get_neuroassist_run_status(run_id: str):
    try:
        return NeuroAssistRunResponse(**(await neuroassist_service.get_run_status(run_id)))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.error("NeuroASSIST run status lookup failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"NeuroASSIST status lookup failed: {str(exc)}")


@router.post("/neuroassist/runs/{run_id}/gates", response_model=NeuroAssistGateActionResponse)
async def apply_neuroassist_gate_action(run_id: str, request: NeuroAssistGateActionRequest):
    try:
        return NeuroAssistGateActionResponse(
            **(
                await neuroassist_service.apply_gate_action(
                    run_id,
                    gate_type=request.gate_type,
                    decision=request.decision,
                    rejection_reason=request.rejection_reason,
                )
            )
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.error("NeuroASSIST gate action failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"NeuroASSIST gate action failed: {str(exc)}")

