"""
Saga-bezogene Endpunkte.
"""

from __future__ import annotations

from typing import Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from ....core.saga import SagaCoordinator, SagaDefinition, SagaStep
from ....dependencies import get_saga_coordinator


router = APIRouter()


class SagaRegistrationPayload(Dict[str, List[Dict[str, str]]]):
    """Hilfsdefinition für dynamische Saga-Registrierung."""


@router.post("/definitions/{saga_name}", status_code=status.HTTP_201_CREATED)
async def register_saga(
    saga_name: str,
    payload: Dict[str, List[Dict[str, str]]],
    coordinator: SagaCoordinator = Depends(get_saga_coordinator),
) -> Dict[str, str]:
    """
    Registriert eine Saga über deklarative JSON-Strukturen.
    Aktionen/Kompensationen werden als Log-Placeholder ausgeführt.
    """

    steps: List[SagaStep] = []
    for step_payload in payload.get("steps", []):
        step_name = step_payload["name"]

        async def action(context: Dict[str, str], _name: str = step_name) -> None:
            context.setdefault("log", []).append(f"action:{_name}")

        async def compensation(context: Dict[str, str], _name: str = step_name) -> None:
            context.setdefault("log", []).append(f"compensation:{_name}")

        steps.append(
            SagaStep(
                name=step_name,
                action=action,
                compensation=compensation if step_payload.get("compensation", True) else None,
            )
        )

    saga_definition = SagaDefinition(name=saga_name, steps=steps)
    await coordinator.register(saga_definition)
    return {"status": "registered", "saga": saga_name}


@router.post("/instances/{saga_name}", status_code=status.HTTP_202_ACCEPTED)
async def start_saga(
    saga_name: str,
    context: Dict[str, str],
    coordinator: SagaCoordinator = Depends(get_saga_coordinator),
) -> Dict[str, str]:
    try:
        instance = await coordinator.start(saga_name, dict(context))
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return {"status": "started", "saga": saga_name, "instance_id": str(instance.id)}


@router.get("/instances/{instance_id}")
async def saga_status(
    instance_id: UUID,
    coordinator: SagaCoordinator = Depends(get_saga_coordinator),
) -> Dict[str, str]:
    try:
        instance = await coordinator.status(instance_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return {
        "saga": instance.definition.name,
        "instance_id": str(instance.id),
        "status": instance.status,
        "completed_steps": instance.completed_steps,
        "error": instance.error,
    }


