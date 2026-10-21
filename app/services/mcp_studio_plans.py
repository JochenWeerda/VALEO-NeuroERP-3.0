"""Versioned Studio-authoring capability; only the registered HTTP command writes."""
import json
import os
from uuid import UUID

import httpx
from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.api.v1.schemas.studio_migration import StudioSavedMigrationIn, StudioSchemaChangeIn
from app.services.mcp_tool_registry_service import mcp_tool_registry_service
from app.services.mask_data_read import _json_object, _json_constant

TOOL = "studio.migration.plan"
COMMAND = "studio.migration_plan.prepare"


class StudioPlanParameters(BaseModel):
    model_config = ConfigDict(extra="forbid")
    draft_id: UUID
    expected_revision: str = Field(pattern=r"^[0-9a-f]{64}$")
    schema_changes: list[StudioSchemaChangeIn] = Field(default_factory=list, max_length=20)


def execute(request, authorization, *, transport=None):
    try:
        parameters = StudioPlanParameters.model_validate(request.parameters)
    except ValidationError as error:
        raise HTTPException(422, "Ungueltiger Studio-Planauftrag") from error
    if request.mode != "execute":
        return {"success": True, "mode": request.mode, "persisted": False,
                "validation_only": True, "command": COMMAND, "command_version": 1,
                "authorization_checked_by_target_on_execute": True}
    capability = mcp_tool_registry_service.get_tool(TOOL)
    if (capability.get("agent_write_enabled") is not True or capability.get("domain_command") != COMMAND
            or capability.get("command_version") != 1 or capability.get("role_policy") != "beleg_write"):
        raise HTTPException(403, "Studio-Plan-Capability ist nicht freigeschaltet")
    try:
        body = StudioSavedMigrationIn(expected_revision=parameters.expected_revision,
            idempotency_key=request.idempotency_key, schema_changes=parameters.schema_changes)
    except ValidationError as error:
        raise HTTPException(422, "Gueltiger Wiederholungsschluessel ist erforderlich") from error
    if not authorization or not authorization.startswith("Bearer ") or not authorization[7:].strip():
        raise HTTPException(401, "Bearer-Token des Aufrufers fehlt")
    path = f"/api/v1/studio/drafts/{parameters.draft_id}/migration-plan"
    base = os.environ.get("MASK_ACTION_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    try:
        with httpx.Client(base_url=base, timeout=30, transport=transport, follow_redirects=False) as client:
            with client.stream("POST", path, headers={"Authorization":authorization}, json=body.model_dump(mode="json")) as response:
                if response.status_code >= 400:
                    raise HTTPException(response.status_code, "Studio-Planauftrag vom Server abgelehnt")
                if response.status_code != 200:
                    raise HTTPException(502, "Ungueltige Studio-Antwort")
                data=bytearray()
                for chunk in response.iter_bytes():
                    data.extend(chunk)
                    if len(data)>2*1024*1024:
                        raise HTTPException(502,"Studio-Antwort ueberschreitet das Limit")
                try:
                    result=json.loads(data, object_pairs_hook=_json_object, parse_constant=_json_constant)
                except (ValueError, UnicodeError) as error:
                    raise HTTPException(502,"Ungueltige Studio-Antwort") from error
                if not isinstance(result,dict):
                    raise HTTPException(502,"Ungueltige Studio-Antwort")
                return result
    except httpx.HTTPError as error:
        raise HTTPException(503,"Studio derzeit nicht erreichbar") from error
