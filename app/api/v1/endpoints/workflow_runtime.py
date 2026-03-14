"""
Workflow Runtime API — Wave 4 AP1

Endpoints fuer die persistente Workflow-Laufzeit:
Instanzen abfragen, Checkpoints schreiben, Resume/Cancel/Replay.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.tenant import get_tenant_id
from app.core.workflow_runtime import (
    WorkflowInstance,
    WorkflowRuntimeStatus,
    WorkflowRuntimeStore,
)

router = APIRouter(prefix="/workflow/runtime", tags=["workflow", "runtime"])

# ---------------------------------------------------------------------------
# In-Memory Store (Produktiv: persistente DB)
# ---------------------------------------------------------------------------

_STORE: WorkflowRuntimeStore = WorkflowRuntimeStore()


# ---------------------------------------------------------------------------
# Request / Response Schemas
# ---------------------------------------------------------------------------


class CreateInstanceRequest(BaseModel):
    instance_id: str
    process_key: str
    definition_version: str
    aggregate_type: str
    aggregate_id: str
    context: dict[str, Any] = {}
    schema_version: int = 1


class CheckpointRequest(BaseModel):
    step_name: str
    state_snapshot: dict[str, Any]
    schema_version: int = 1


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("/instances")
async def list_instances(
    status: Optional[str] = None,
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict]:
    """Listet alle Workflow-Instanzen des Tenants, optional nach Status gefiltert."""
    if status is not None:
        try:
            status_enum = WorkflowRuntimeStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Ungueltiger Status: {status}. Erlaubt: {[s.value for s in WorkflowRuntimeStatus]}",
            )
        instances = _STORE.get_by_status(status_enum)
    else:
        instances = _STORE.instances

    # Tenant-Filterung
    instances = [i for i in instances if i.tenant_id == tenant_id]
    return [i.model_dump() for i in instances]


@router.post("/instances")
async def create_instance(
    request: CreateInstanceRequest,
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    """Erstellt eine neue Workflow-Instanz."""
    existing = _STORE.get(request.instance_id)
    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail=f"Instanz '{request.instance_id}' existiert bereits.",
        )
    instance = WorkflowInstance(
        instance_id=request.instance_id,
        tenant_id=tenant_id,
        process_key=request.process_key,
        definition_version=request.definition_version,
        aggregate_type=request.aggregate_type,
        aggregate_id=request.aggregate_id,
        context=request.context,
    )
    _STORE.upsert(instance)
    return instance.model_dump()


@router.get("/instances/{instance_id}")
async def get_instance(
    instance_id: str,
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    """Gibt eine einzelne Workflow-Instanz zurueck."""
    instance = _STORE.get(instance_id)
    if instance is None:
        raise HTTPException(status_code=404, detail=f"Instanz '{instance_id}' nicht gefunden.")
    if instance.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Zugriff verweigert.")
    return instance.model_dump()


@router.post("/instances/{instance_id}/checkpoint")
async def add_checkpoint(
    instance_id: str,
    request: CheckpointRequest,
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    """Schreibt einen neuen Checkpoint fuer die angegebene Instanz."""
    instance = _STORE.get(instance_id)
    if instance is None:
        raise HTTPException(status_code=404, detail=f"Instanz '{instance_id}' nicht gefunden.")
    if instance.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Zugriff verweigert.")
    if instance.status in (
        WorkflowRuntimeStatus.COMPLETED,
        WorkflowRuntimeStatus.CANCELLED,
    ):
        raise HTTPException(
            status_code=409,
            detail=f"Instanz '{instance_id}' ist bereits abgeschlossen (Status: {instance.status}).",
        )
    cp = instance.add_checkpoint(request.step_name, request.state_snapshot)
    _STORE.upsert(instance)
    return cp.model_dump()


@router.post("/instances/{instance_id}/resume")
async def resume_instance(
    instance_id: str,
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    """Setzt den Status auf RUNNING wenn die Instanz resumierbar ist."""
    instance = _STORE.get(instance_id)
    if instance is None:
        raise HTTPException(status_code=404, detail=f"Instanz '{instance_id}' nicht gefunden.")
    if instance.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Zugriff verweigert.")
    if not instance.is_resumable():
        raise HTTPException(
            status_code=409,
            detail=f"Instanz '{instance_id}' kann nicht wiederaufgenommen werden (Status: {instance.status}).",
        )
    instance.status = WorkflowRuntimeStatus.RUNNING
    instance.error_message = None
    instance.updated_at = datetime.now(timezone.utc)
    _STORE.upsert(instance)
    return instance.model_dump()


@router.post("/instances/{instance_id}/cancel")
async def cancel_instance(
    instance_id: str,
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    """Setzt den Status der Instanz auf CANCELLED."""
    instance = _STORE.get(instance_id)
    if instance is None:
        raise HTTPException(status_code=404, detail=f"Instanz '{instance_id}' nicht gefunden.")
    if instance.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Zugriff verweigert.")
    if instance.status in (
        WorkflowRuntimeStatus.COMPLETED,
        WorkflowRuntimeStatus.CANCELLED,
    ):
        raise HTTPException(
            status_code=409,
            detail=f"Instanz '{instance_id}' ist bereits im Endzustand (Status: {instance.status}).",
        )
    instance.status = WorkflowRuntimeStatus.CANCELLED
    instance.updated_at = datetime.now(timezone.utc)
    _STORE.upsert(instance)
    return instance.model_dump()


@router.get("/instances/{instance_id}/replay")
async def get_replay(
    instance_id: str,
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    """Gibt alle Checkpoints der Instanz fuer Replay-Analysen zurueck."""
    instance = _STORE.get(instance_id)
    if instance is None:
        raise HTTPException(status_code=404, detail=f"Instanz '{instance_id}' nicht gefunden.")
    if instance.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Zugriff verweigert.")
    return {
        "instance_id": instance_id,
        "process_key": instance.process_key,
        "status": instance.status,
        "current_step": instance.current_step,
        "checkpoints": [cp.model_dump() for cp in instance.checkpoints],
        "total_checkpoints": len(instance.checkpoints),
    }
