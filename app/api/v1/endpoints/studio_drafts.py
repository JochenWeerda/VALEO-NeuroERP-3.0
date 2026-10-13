"""ScreenDefinition Studio API — catalog, validate, propose, drafts."""

from __future__ import annotations

from typing import Any
from collections.abc import Callable

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.v1.endpoints.mask_screen_definition import _check_readiness
from app.core.screen_definitions import SCREEN_DEFINITION_BUILDERS
from app.core.tenant import get_tenant_id
from app.auth.deps import get_current_user
from app.services.studio_draft_store import StudioStorageUnavailable, get_draft, list_drafts, save_draft, set_status, studio_run_route
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


class StudioRevisionIn(BaseModel):
    expected_revision: str = Field(pattern=r"^[0-9a-f]{64}$")


def _storage_call(operation: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    try:
        return operation(*args, **kwargs)
    except StudioStorageUnavailable as error:
        raise HTTPException(503, "Studio-Persistenz derzeit nicht verfuegbar") from error


def _actor(user: dict[str, Any]) -> str:
    subject = user.get("sub")
    if not isinstance(subject, str) or not subject.strip():
        raise HTTPException(403, "Gepruefter Studio-Urheber fehlt")
    return subject.strip()


def _publisher(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    # Same verified identity_type/admin boundary as identity administration.
    claims = user.get("raw") or {}
    if claims.get("identity_type") != "human" or "admin" not in (user.get("roles") or []):
        raise HTTPException(403, "Menschliche Administration fuer Studio-Publikation erforderlich")
    _actor(user)
    return user


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
def studio_catalog(user: dict = Depends(get_current_user)) -> dict[str, Any]:
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
def studio_validate(body: StudioDefinitionIn, user: dict = Depends(get_current_user)) -> dict[str, Any]:
    return _report(body.definition)


@router.post("/propose", summary="Studio-ScreenDefinition aus einer Absicht vorschlagen")
def studio_propose(body: StudioProposeIn, user: dict = Depends(get_current_user)) -> dict[str, Any]:
    definition = propose_studio_draft(body.intent)
    return _report(definition)


@router.get("/drafts", summary="Studio-Entwürfe des Mandanten auflisten")
def studio_list_drafts(tenant_id: str = Depends(get_tenant_id), user: dict = Depends(get_current_user)) -> dict[str, Any]:
    return {"drafts": _storage_call(list_drafts, tenant_id)}


@router.get("/drafts/{draft_id}", summary="Gespeicherten Studio-Entwurf zur Pruefung abrufen")
def studio_get_draft(
    draft_id: str, tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    item = _storage_call(get_draft, tenant_id, draft_id)
    if item is None:
        raise HTTPException(404, "draft_nicht_gefunden")
    return item


@router.post("/drafts", summary="Studio-Entwurf anlegen")
def studio_create_draft(
    body: StudioDefinitionIn,
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    report = _report(body.definition)
    if report["violations"]:
        raise HTTPException(status_code=400, detail={"violations": report["violations"]})
    record = _storage_call(save_draft, tenant_id, _actor(user), body.definition, readiness=report["readiness"])
    return {**record, **report}


@router.put("/drafts/{draft_id}", summary="Studio-Entwurf aktualisieren")
def studio_update_draft(
    draft_id: str,
    body: StudioDefinitionIn,
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    report = _report(body.definition)
    if report["violations"]:
        raise HTTPException(status_code=400, detail={"violations": report["violations"]})
    try:
        record = _storage_call(save_draft,
            tenant_id,
            _actor(user),
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
    body: StudioRevisionIn,
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    return _transition(draft_id, tenant_id, _actor(user), "review", body.expected_revision)


@router.post("/drafts/{draft_id}/publish", summary="Studio-Entwurf als published_temp freigeben")
def studio_publish(
    draft_id: str,
    body: StudioRevisionIn,
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(_publisher),
) -> dict[str, Any]:
    item = _storage_call(get_draft, tenant_id, draft_id)
    if item is None:
        raise HTTPException(status_code=404, detail="draft_nicht_gefunden")
    if body.expected_revision != item["revision"]:
        raise HTTPException(409, "entwurf_seit_anzeige_geaendert")
    report = _report(item["definition"])
    if not report["canPublish"]:
        raise HTTPException(status_code=400, detail={"violations": report["violations"], "readiness": report["readiness"]})
    try:
        record = _storage_call(set_status, tenant_id, draft_id, _actor(user), "published_temp", expected_snapshot=item)
    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except KeyError as error:
        raise HTTPException(status_code=404, detail="draft_nicht_gefunden") from error
    screen_id = str(record.get("screen_id") or (record.get("definition") or {}).get("id") or "")
    return {**record, **report, "route": studio_run_route(screen_id) if screen_id else None}


@router.post("/drafts/{draft_id}/retire", summary="Freigegebene Studio-Maske zurückziehen")
def studio_retire(
    draft_id: str,
    body: StudioRevisionIn,
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(_publisher),
) -> dict[str, Any]:
    return _transition(draft_id, tenant_id, _actor(user), "retired", body.expected_revision)


def _transition(draft_id: str, tenant_id: str, actor: str, status: str, revision: str) -> dict[str, Any]:
    item = _storage_call(get_draft, tenant_id, draft_id)
    if item is None:
        raise HTTPException(404, "draft_nicht_gefunden")
    if item["revision"] != revision:
        raise HTTPException(409, "entwurf_seit_anzeige_geaendert")
    try:
        return _storage_call(set_status, tenant_id, draft_id, actor, status, expected_snapshot=item)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="draft_nicht_gefunden") from error
    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
