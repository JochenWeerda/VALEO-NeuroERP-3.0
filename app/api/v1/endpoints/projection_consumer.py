"""
Projektions-Consumer API — Wave 4 AP2

Endpoints fuer die Verwaltung von Read-Model-Consumers und Rebuild-Anforderungen.
"""

from __future__ import annotations


from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette.responses import JSONResponse

from app.core.tenant import get_tenant_id
from app.core.projection_consumer import (
    ProjectionRegistry,
    RebuildRequest,
    build_default_projection_registry,
)

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.base import CompatFlexOut
from app.api.v1.schemas.projection_consumer_schemas import ProjectionConsumerOut


router = APIRouter(prefix="/projections", tags=["projections", "read-models"])

# ---------------------------------------------------------------------------
# In-Memory State
# ---------------------------------------------------------------------------

_REGISTRY: ProjectionRegistry = build_default_projection_registry()
_REBUILD_REQUESTS: dict[str, RebuildRequest] = {}


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------


class RebuildRequestBody(BaseModel):
    requested_by: str
    rebuild_from: str = "beginning"
    reason: str
    schema_version: int = 1


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("", summary="Projections auflisten",
    response_model=ProjectionConsumerOut
)
async def list_projections(
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    """Gibt die vollstaendige Projektion-Registry zurueck."""
    return _REGISTRY.model_dump()


@router.get("/stale", summary="Stale projections auflisten",
    response_model=list[ProjectionConsumerOut]
)
async def list_stale_projections(
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict]:
    """Gibt alle veralteten Consumer zurueck."""
    stale = _REGISTRY.get_stale()
    return [c.model_dump() for c in stale]


@router.get("/{projection_name}", summary="Projection abrufen",
    response_model=ProjectionConsumerOut
)
async def get_projection(
    projection_name: str,
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    """Gibt einen einzelnen Consumer anhand des Projektion-Namens zurueck."""
    consumer = _REGISTRY.get(projection_name)
    if consumer is None:
        raise HTTPException(
            status_code=404,
            detail=f"Projektion '{projection_name}' nicht gefunden.",
        )
    return consumer.model_dump()


@router.post("/{projection_name}/rebuild", status_code=202, summary="Rebuild request",
    response_model=ProjectionConsumerOut
)
async def request_rebuild(
    projection_name: str,
    body: RebuildRequestBody,
    tenant_id: str = Depends(get_tenant_id),
) -> JSONResponse:
    """Erstellt eine Rebuild-Anforderung fuer eine Projektion (accepted: 202)."""
    consumer = _REGISTRY.get(projection_name)
    if consumer is None:
        raise HTTPException(
            status_code=404,
            detail=f"Projektion '{projection_name}' nicht gefunden.",
        )
    rebuild_request = RebuildRequest(
        projection_name=projection_name,
        requested_by=body.requested_by,
        tenant_id=tenant_id,
        rebuild_from=body.rebuild_from,
        reason=body.reason,
    )
    _REBUILD_REQUESTS[projection_name] = rebuild_request

    # Consumer als "rebuilding" markieren
    consumer.status = __import__(
        "app.core.projection_consumer", fromlist=["ProjectionStatus"]
    ).ProjectionStatus.REBUILDING
    _REGISTRY.upsert = lambda c: None  # Registry ist immutable in-memory; Consumer direkt mutiert

    return JSONResponse(
        status_code=202,
        content=rebuild_request.model_dump(mode="json"),
    )


@router.get("/{projection_name}/rebuild-status", summary="Rebuild status abrufen",
    response_model=ProjectionConsumerOut
)
async def get_rebuild_status(
    projection_name: str,
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    """Gibt den letzten Rebuild-Request fuer eine Projektion zurueck."""
    consumer = _REGISTRY.get(projection_name)
    if consumer is None:
        raise HTTPException(
            status_code=404,
            detail=f"Projektion '{projection_name}' nicht gefunden.",
        )
    rebuild = _REBUILD_REQUESTS.get(projection_name)
    if rebuild is None:
        raise HTTPException(
            status_code=404,
            detail=f"Kein Rebuild-Request fuer Projektion '{projection_name}' gefunden.",
        )
    return rebuild.model_dump()
