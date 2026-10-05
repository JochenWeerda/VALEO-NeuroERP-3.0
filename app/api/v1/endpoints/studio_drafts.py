"""ScreenDefinition Studio API — catalog, validate, propose, drafts."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field

from app.api.v1.endpoints.mask_screen_definition import _check_readiness
from app.core.screen_definitions import SCREEN_DEFINITION_BUILDERS
from app.core.tenant import get_tenant_id
from app.services.studio_draft_store import get_draft, list_drafts, save_draft, set_status, studio_run_route
from app.services.studio_propose import propose_studio_draft
from app.services.studio_validation import load_studio_catalog, validate_studio_draft

router = APIRouter(prefix="/studio", tags=["ui", "studio", "screen-definition"])

_FIELD_TYPES = [
    "text", "number", "date", "datetime", "boolean", "select", "multiselect",
    "textarea", "file", "lookup", "table", "currency", "percentage",
]
_FLOORPLANS = ["worklist", "objectPage", "transaction", "cockpit", "wizard", "analyticalList"]


class StudioDefinitionIn(BaseModel):
    definition: dict[str, Any]


class StudioProposeIn(BaseModel):
    intent: str = Field(min_length=1)


def _actor(x_actor_id: str | None) -> str:
    actor = (x_actor_id or "").strip()
    return actor or "studio-user"


def _native_ids() -> set[str]:
    return set(SCREEN_DEFINITION_BUILDERS)


def _report(definition: dict[str, Any]) -> dict[str, Any]:
    violations = validate_studio_draft(definition, native_screen_ids=_native_ids())
    readiness = _check_readiness(definition)
    blocking = [error for error in readiness.get("errors") or [] if "non_temporary" not in error]
    return {
        "violations": violations,
        "readiness": readiness,
        "canPublish": not violations and not blocking,
        "definition": definition,
    }


@router.get("/catalog", summary="Studio-Katalog für Floorplans, Datenquellen und Actions")
def studio_catalog() -> dict[str, Any]:
    catalog = load_studio_catalog()
    return {
        "version": catalog["version"],
        "floorplans": _FLOORPLANS,
        "fieldTypes": _FIELD_TYPES,
        "columnNavigation": ["single", "listDetail", "listDetailDetail"],
        "dataSources": catalog["data_sources"],
        "actions": catalog["command_actions"],
    }


@router.post("/validate", summary="Studio-ScreenDefinition gegen Katalog und Gates prüfen")
def studio_validate(body: StudioDefinitionIn) -> dict[str, Any]:
    return _report(body.definition)


@router.post("/propose", summary="Studio-ScreenDefinition aus einer Absicht vorschlagen")
def studio_propose(body: StudioProposeIn) -> dict[str, Any]:
    definition = propose_studio_draft(body.intent)
    return _report(definition)


@router.get("/drafts", summary="Studio-Entwürfe des Mandanten auflisten")
def studio_list_drafts(tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    return {"drafts": list_drafts(tenant_id)}


@router.post("/drafts", summary="Studio-Entwurf anlegen")
def studio_create_draft(
    body: StudioDefinitionIn,
    tenant_id: str = Depends(get_tenant_id),
    x_actor_id: str | None = Header(default=None, alias="X-Actor-ID"),
) -> dict[str, Any]:
    report = _report(body.definition)
    if report["violations"]:
        raise HTTPException(status_code=400, detail={"violations": report["violations"]})
    record = save_draft(tenant_id, _actor(x_actor_id), body.definition, readiness=report["readiness"])
    return {**record, **report}


@router.put("/drafts/{draft_id}", summary="Studio-Entwurf aktualisieren")
def studio_update_draft(
    draft_id: str,
    body: StudioDefinitionIn,
    tenant_id: str = Depends(get_tenant_id),
    x_actor_id: str | None = Header(default=None, alias="X-Actor-ID"),
) -> dict[str, Any]:
    report = _report(body.definition)
    if report["violations"]:
        raise HTTPException(status_code=400, detail={"violations": report["violations"]})
    try:
        record = save_draft(
            tenant_id,
            _actor(x_actor_id),
            body.definition,
            draft_id=draft_id,
            readiness=report["readiness"],
        )
    except KeyError as error:
        raise HTTPException(status_code=404, detail="draft_nicht_gefunden") from error
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return {**record, **report}


@router.post("/drafts/{draft_id}/submit-review", summary="Studio-Entwurf zur Vier-Augen-Prüfung geben")
def studio_submit_review(
    draft_id: str,
    tenant_id: str = Depends(get_tenant_id),
    x_actor_id: str | None = Header(default=None, alias="X-Actor-ID"),
) -> dict[str, Any]:
    return _transition(draft_id, tenant_id, _actor(x_actor_id), "review")


@router.post("/drafts/{draft_id}/publish", summary="Studio-Entwurf als published_temp freigeben")
def studio_publish(
    draft_id: str,
    tenant_id: str = Depends(get_tenant_id),
    x_actor_id: str | None = Header(default=None, alias="X-Actor-ID"),
) -> dict[str, Any]:
    item = get_draft(tenant_id, draft_id)
    if item is None:
        raise HTTPException(status_code=404, detail="draft_nicht_gefunden")
    report = _report(item["definition"])
    if not report["canPublish"]:
        raise HTTPException(status_code=400, detail={"violations": report["violations"], "readiness": report["readiness"]})
    try:
        record = set_status(tenant_id, draft_id, _actor(x_actor_id), "published_temp")
    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    screen_id = str(record.get("screen_id") or (record.get("definition") or {}).get("id") or "")
    return {**record, **report, "route": studio_run_route(screen_id) if screen_id else None}


@router.post("/drafts/{draft_id}/retire", summary="Freigegebene Studio-Maske zurückziehen")
def studio_retire(
    draft_id: str,
    tenant_id: str = Depends(get_tenant_id),
    x_actor_id: str | None = Header(default=None, alias="X-Actor-ID"),
) -> dict[str, Any]:
    return _transition(draft_id, tenant_id, _actor(x_actor_id), "retired")


def _transition(draft_id: str, tenant_id: str, actor: str, status: str) -> dict[str, Any]:
    try:
        return set_status(tenant_id, draft_id, actor, status)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="draft_nicht_gefunden") from error
    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
