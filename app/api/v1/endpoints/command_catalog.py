"""
Command Catalog API — Wave 5 Paket A.

Endpoints fuer den Business-Command-Katalog, Agent-Manifest und Command-Dispatch.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from app.core.tenant import get_tenant_id
from app.core.business_commands import (
    BusinessCommand,
    build_core_command_catalog,
)
from app.core.command_dispatcher import CommandDispatcher
from app.core.agent_command_manifest import build_agent_command_manifest
from app.core.ui_density_manifest import build_ui_density_manifest

router = APIRouter(prefix="/commands", tags=["commands", "process-kernel"])


class DispatchRequest(BaseModel):
    command: BusinessCommand
    aggregate_state: dict[str, Any] = Field(default_factory=dict)


@router.get("/catalog", summary="Vollstaendiger Command-Katalog",
    response_model=list
)
def get_command_catalog(
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict]:
    """Gibt den vollstaendigen CommandDefinition-Katalog zurueck."""
    catalog = build_core_command_catalog()
    return [cd.model_dump() for cd in catalog]


@router.get("/agent-manifest", summary="Agent-Command-Manifest",
    response_model=dict
)
def get_agent_manifest(
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    """Gibt das AgentCommandManifest zurueck (welche Commands Agenten ausfuehren duerfen)."""
    manifest = build_agent_command_manifest()
    return manifest.model_dump()


@router.get("/ui-density-manifest", summary="UI-Density-Manifest aus produktiven Command-Contracts",
    response_model=dict
)
def get_ui_density_manifest(
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    manifest = build_ui_density_manifest()
    return manifest.model_dump()


@router.post("/dispatch", summary="Command dispatchen und validieren",
    response_model=dict
)
def dispatch_command(
    body: DispatchRequest,
    issuer_role: Optional[str] = Query(default=None, description="Rolle des Ausstellers"),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    """
    Prueft Rolle und Preconditions und gibt CommandResult zurueck.
    Kein tatsaechlicher DB-Schreibvorgang — der Aufrufer fuehrt die Aktion aus.
    """
    dispatcher = CommandDispatcher()
    result = dispatcher.dispatch(body.command, body.aggregate_state, issuer_role)
    return result.model_dump()
