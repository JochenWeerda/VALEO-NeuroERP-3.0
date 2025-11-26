"""
REST-Endpunkte für Workflow-Verwaltung.
"""

from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from ....core.workflow_engine import WorkflowEngine
from ....core.event_router import EventRouter
from ....schemas.workflow import (
    WorkflowDefinition,
    WorkflowInstance,
    CreateInstanceRequest,
    TransitionRequest,
    EventPayload,
    SimulationRequest,
    SimulationResult,
)
from ....dependencies import get_engine, get_event_router


router = APIRouter()


@router.post("/definitions", response_model=WorkflowDefinition, status_code=status.HTTP_201_CREATED)
async def register_definition(
    definition: WorkflowDefinition,
    engine: WorkflowEngine = Depends(get_engine),
) -> WorkflowDefinition:
    try:
        return await engine.register_definition(definition)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/definitions", response_model=List[WorkflowDefinition])
async def list_definitions(
    name: str | None = None,
    tenant: str | None = None,
    engine: WorkflowEngine = Depends(get_engine),
) -> List[WorkflowDefinition]:
    definitions = await engine.list_definitions(name=name, tenant=tenant)
    return list(definitions)


@router.post("/instances", response_model=WorkflowInstance, status_code=status.HTTP_201_CREATED)
async def create_instance(
    payload: CreateInstanceRequest,
    engine: WorkflowEngine = Depends(get_engine),
) -> WorkflowInstance:
    try:
        definition = await engine.get_definition(payload.workflow_name, payload.workflow_version, payload.tenant)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return await engine.create_instance(definition, payload.context)


@router.get("/instances/{instance_id}", response_model=WorkflowInstance)
async def fetch_instance(
    instance_id: UUID,
    engine: WorkflowEngine = Depends(get_engine),
) -> WorkflowInstance:
    try:
        return await engine.get_instance(instance_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/instances/{instance_id}/transitions", response_model=WorkflowInstance)
async def trigger_transition(
    instance_id: UUID,
    request: TransitionRequest,
    engine: WorkflowEngine = Depends(get_engine),
) -> WorkflowInstance:
    try:
        return await engine.trigger_transition(instance_id, request.transition_name, request.payload)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.post("/events", status_code=status.HTTP_202_ACCEPTED)
async def handle_event(
    payload: EventPayload,
    event_router: EventRouter = Depends(get_event_router),
) -> dict:
    return await event_router.route_event(payload)


@router.post("/simulate", response_model=SimulationResult)
async def simulate_workflow(
    payload: SimulationRequest,
    engine: WorkflowEngine = Depends(get_engine),
) -> SimulationResult:
    try:
        definition = await engine.get_definition(payload.workflow_name, payload.workflow_version, payload.tenant)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    result = await engine.simulate(definition, payload.context, payload.transitions)
    return SimulationResult(**result)


