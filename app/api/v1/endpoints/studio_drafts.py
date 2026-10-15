"""ScreenDefinition Studio API — catalog, validate, propose, drafts."""

from __future__ import annotations

from typing import Any
from datetime import datetime
from uuid import UUID
from collections.abc import Callable

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.api.v1.endpoints.mask_screen_definition import _check_readiness
from app.core.screen_definitions import SCREEN_DEFINITION_BUILDERS
from app.core.tenant import get_tenant_id
from app.auth.deps import get_current_user
from app.auth.finance_roles import beleg_write
from app.services.studio_draft_store import StudioStorageUnavailable, list_history, get_status_replay, get_draft, list_drafts, save_draft, set_status, studio_run_route
from app.services.studio_propose import propose_studio_draft
from app.services.studio_validation import load_studio_catalog, validate_studio_draft
from app.services.studio_semantic import DialogueTurn, HarvestPreviewIn, HarvestPreviewOut, StudioDialogueIn, StudioDialogueOut, dialogue, preview, semantic_catalog
from app.core.database import get_db
from sqlalchemy.orm import Session

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


class StudioSaveIn(StudioDefinitionIn):
    idempotency_key: UUID


class StudioUpdateIn(StudioSaveIn):
    expected_revision: str = Field(pattern=r"^[0-9a-f]{64}$")


class StudioRevisionIn(BaseModel):
    idempotency_key: UUID
    expected_revision: str = Field(pattern=r"^[0-9a-f]{64}$")


class StudioHistoryRow(BaseModel):
    id: str
    actor: str
    recorded_at: datetime
    action: str
    revision: str
    status: str | None
    active: bool
    simulation_result: str | None = None
    simulation_profile: str | None = None
    simulation_failures: str | None = None


class StudioHistoryViewOut(BaseModel):
    items: list[StudioHistoryRow]
    total: int


class StudioDiffRow(BaseModel):
    id: str
    path: str
    before: str
    after: str


class StudioHistoryDiffOut(BaseModel):
    items: list[StudioDiffRow]
    total: int
    revision: str
    previous_revision: str | None
    actor: str
    action: str


class StudioSimulationEvidenceOut(BaseModel):
    profile: str | None = None
    artifact_hash: str | None = None
    checks: dict[str, bool]
    passed: bool
    tenant_id: str
    draft_id: str
    candidate_revision: str
    definition_hash: str
    business_effect: str = "not_verified"
    external_effect: str = "not_verified"
    failed_checks: list[str] = Field(default_factory=list)
    error: str | None = None
    error_location: str | None = None


class StudioSimulationOut(BaseModel):
    id: str
    tenant_id: str
    screen_id: str
    base_screen_id: str | None = None
    definition: dict[str, Any]
    status: str
    readiness: dict[str, Any] | None = None
    created_by: str
    updated_by: str
    updated_at: datetime
    revision: str
    simulation: StudioSimulationEvidenceOut


def _storage_call(operation: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    try:
        return operation(*args, **kwargs)
    except StudioStorageUnavailable as error:
        raise HTTPException(503, "Studio-Persistenz derzeit nicht verfuegbar") from error


def _replay(tenant: str, draft: str, actor: str, action: str, revision: str, key: str):
    try:
        return _storage_call(get_status_replay, tenant, draft, actor, action, revision, key)
    except ValueError as error:
        raise HTTPException(409, str(error)) from error


def _actor(user: dict[str, Any]) -> str:
    subject = user.get("sub")
    if not isinstance(subject, str) or not subject.strip():
        raise HTTPException(403, "Gepruefter Studio-Urheber fehlt")
    return subject.strip()


def _may_design(user: dict[str, Any]) -> bool:
    if not isinstance(user.get("sub"), str) or not user["sub"].strip():
        return False
    try:
        beleg_write(user=user)
        return True
    except HTTPException as error:
        if error.status_code != 403:
            raise
        return False


def _may_publish(user: dict[str, Any]) -> bool:
    claims = user.get("raw") or {}
    return claims.get("identity_type") == "human" and "admin" in (user.get("roles") or [])


def _publisher(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    # Same verified identity_type/admin boundary as identity administration.
    if not _may_publish(user):
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
        "definitionReady": not violations and not blocking,
        "canPublish": False,
        "requiresSimulation": True,
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
        "semantic": semantic_catalog(),
        "permissions": {"canDesign": _may_design(user), "canPublish": _may_publish(user)},
    }


@router.post("/validate", summary="Studio-ScreenDefinition gegen Katalog und Gates prüfen")
def studio_validate(body: StudioDefinitionIn, user: dict = Depends(get_current_user)) -> dict[str, Any]:
    return _report(body.definition)


@router.post("/propose", summary="Studio-ScreenDefinition aus einer Absicht vorschlagen")
def studio_propose(body: StudioProposeIn, user: dict = Depends(get_current_user)) -> dict[str, Any]:
    definition = propose_studio_draft(body.intent)
    return _report(definition)


@router.post("/dialogue", response_model=StudioDialogueOut, summary="Fachsprachlichen Studio-Entwurf kataloggebunden klaeren")
def studio_dialogue(body: StudioDialogueIn, user: dict = Depends(beleg_write),
                    tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> StudioDialogueOut:
    _actor(user)
    if not body.use_language_model:
        return dialogue(body)
    from app.services.studio_semantic_model import interpret
    from app.services.llm_gateway import LLMGateway
    interpreted = interpret(body, LLMGateway(db, tenant_id))
    if interpreted.contract is None or interpreted.unsupported or interpreted.question:
        return StudioDialogueOut(mode="llm_assisted", message=" ".join(filter(None, [
            interpreted.summary, interpreted.question, *interpreted.unsupported])), limitations=semantic_catalog()["limitations"])
    # The model chooses neither fields nor actions. A recognized process is
    # resolved through the same deterministic catalog and human decisions.
    recognized = body.model_copy(update={"turns": [*body.turns, DialogueTurn(role="user", content="Getreide-Kalkulationsprobe")]})
    result = dialogue(recognized)
    if result.definition:
        result.definition["studioSemantic"]["dialogue"] = [turn.model_dump() for turn in body.turns]
        result.definition["studioSemantic"]["interpretation"] = interpreted.model_dump()
    return result.model_copy(update={"mode": "llm_assisted"})


@router.post("/harvest-preview", response_model=HarvestPreviewOut, summary="Isolierte manuelle Getreidekalkulation ohne Fachwirkung")
def studio_harvest_preview(body: HarvestPreviewIn, user: dict = Depends(beleg_write)) -> HarvestPreviewOut:
    _actor(user)
    try:
        return HarvestPreviewOut(**preview(body))
    except ValueError as error:
        raise HTTPException(400, str(error)) from error


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


@router.get("/drafts/{draft_id}/history", summary="Unveraenderliche Studio-Revisionshistorie lesen")
def studio_history(
    draft_id: str, skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500),
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    if _storage_call(get_draft, tenant_id, draft_id) is None:
        raise HTTPException(404, "draft_nicht_gefunden")
    entries = _storage_call(list_history, tenant_id, draft_id, skip=skip, limit=limit + 1)
    return {"history": entries[:limit], "has_more": len(entries) > limit,
            "next_skip": skip + limit if len(entries) > limit else None}


@router.post("/drafts", summary="Studio-Entwurf anlegen")
def studio_create_draft(
    body: StudioSaveIn,
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(beleg_write),
) -> dict[str, Any]:
    report = _report(body.definition)
    if report["violations"]:
        raise HTTPException(status_code=400, detail={"violations": report["violations"]})
    try:
        record = _storage_call(save_draft, tenant_id, _actor(user), body.definition, readiness=report["readiness"], idempotency_key=str(body.idempotency_key))
    except ValueError as error:
        raise HTTPException(409, str(error)) from error
    return {**record, **report}


@router.put("/drafts/{draft_id}", summary="Studio-Entwurf aktualisieren")
def studio_update_draft(
    draft_id: str,
    body: StudioUpdateIn,
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(beleg_write),
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
            expected_revision=body.expected_revision,
            idempotency_key=str(body.idempotency_key),
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
    user: dict = Depends(beleg_write),
) -> dict[str, Any]:
    return _transition(draft_id, tenant_id, _actor(user), "review", body.expected_revision, str(body.idempotency_key))


@router.post("/drafts/{draft_id}/publish", summary="Studio-Entwurf als published_temp freigeben")
def studio_publish(
    draft_id: str,
    body: StudioRevisionIn,
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(_publisher),
) -> dict[str, Any]:
    actor, key = _actor(user), str(body.idempotency_key)
    cached = _replay(tenant_id, draft_id, actor, "published_temp", body.expected_revision, key)
    item = cached or _storage_call(get_draft, tenant_id, draft_id)
    if item is None:
        raise HTTPException(status_code=404, detail="draft_nicht_gefunden")
    if not cached and body.expected_revision != item["revision"]:
        cached = _replay(tenant_id, draft_id, actor, "published_temp", body.expected_revision, key)
        if cached is None:
            raise HTTPException(409, "entwurf_seit_anzeige_geaendert")
        item = cached
    report = _report(item["definition"])
    if not report["definitionReady"]:
        raise HTTPException(status_code=400, detail={"violations": report["violations"], "readiness": report["readiness"]})
    try:
        record = cached or _storage_call(set_status, tenant_id, draft_id, actor, "published_temp", expected_snapshot=item, idempotency_key=key, request_revision=body.expected_revision)
    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except KeyError as error:
        raise HTTPException(status_code=404, detail="draft_nicht_gefunden") from error
    screen_id = str(record.get("screen_id") or (record.get("definition") or {}).get("id") or "")
    return {**record, **report, "canPublish": True, "route": studio_run_route(screen_id) if screen_id else None}


@router.post("/drafts/{draft_id}/retire", summary="Freigegebene Studio-Maske zurückziehen")
def studio_retire(
    draft_id: str,
    body: StudioRevisionIn,
    tenant_id: str = Depends(get_tenant_id),
    user: dict = Depends(_publisher),
) -> dict[str, Any]:
    return _transition(draft_id, tenant_id, _actor(user), "retired", body.expected_revision, str(body.idempotency_key))


def _transition(draft_id: str, tenant_id: str, actor: str, status: str, revision: str, key: str) -> dict[str, Any]:
    cached = _replay(tenant_id, draft_id, actor, status, revision, key)
    if cached is not None:
        return cached
    item = _storage_call(get_draft, tenant_id, draft_id)
    if item is None:
        raise HTTPException(404, "draft_nicht_gefunden")
    if item["revision"] != revision:
        cached = _replay(tenant_id, draft_id, actor, status, revision, key)
        if cached is not None:
            return cached
        raise HTTPException(409, "entwurf_seit_anzeige_geaendert")
    try:
        return _storage_call(set_status, tenant_id, draft_id, actor, status, expected_snapshot=item, idempotency_key=key, request_revision=revision)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="draft_nicht_gefunden") from error
    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.get("/drafts/{draft_id}/history-view", response_model=StudioHistoryViewOut, summary="Studio-Fassungen fuer native Auditmaske")
def studio_history_view(draft_id: str, skip: int = Query(0, ge=0), limit: int = Query(25, ge=1, le=100),
                        tenant_id: str = Depends(get_tenant_id), user: dict = Depends(get_current_user)) -> dict[str, Any]:
    from app.services.studio_draft_store import count_history
    item = _storage_call(get_draft, tenant_id, draft_id)
    if item is None: raise HTTPException(404, "draft_nicht_gefunden")
    entries = _storage_call(list_history, tenant_id, draft_id, skip=skip, limit=limit)
    rows = [{"id": entry["id"], "actor": entry["actor"], "recorded_at": entry["recorded_at"],
             "action": entry["action"], "revision": entry["revision"],
             "status": entry["snapshot"].get("status"),
             "simulation_result": ("bestanden" if entry["snapshot"]["simulation"].get("passed") is True else "fehlgeschlagen") if "simulation" in entry["snapshot"] else None,
             "simulation_profile": entry["snapshot"].get("simulation", {}).get("profile"),
             "simulation_failures": ", ".join(entry["snapshot"].get("simulation", {}).get("failed_checks", [])) or None,
             "active": item["status"] == "published_temp" and entry["revision"] == item["revision"]} for entry in entries]
    return {"items": rows, "total": _storage_call(count_history, tenant_id, draft_id)}


@router.get("/drafts/{draft_id}/history-diff", response_model=StudioHistoryDiffOut, summary="Unveraenderliche Studio-Aenderung vergleichen")
def studio_history_diff(draft_id: str, entry_id: str, skip: int = Query(0, ge=0), limit: int = Query(25, ge=1, le=100),
                        tenant_id: str = Depends(get_tenant_id), user: dict = Depends(get_current_user)) -> dict[str, Any]:
    from app.services.studio_draft_store import history_event
    from app.services.studio_history_view import definition_diff
    item = _storage_call(get_draft, tenant_id, draft_id)
    entry = _storage_call(history_event, tenant_id, draft_id, event_id=entry_id) if item else None
    if entry is None: raise HTTPException(404, "historie_nicht_gefunden")
    previous = _storage_call(history_event, tenant_id, draft_id, revision=entry["previous_revision"]) if entry["previous_revision"] else None
    if entry["previous_revision"] and previous is None:
        raise HTTPException(409, "historischer_ausgangsstand_nicht_verfuegbar")
    rows = definition_diff(previous["snapshot"]["definition"] if previous else {}, entry["snapshot"]["definition"])
    return {"items": rows[skip:skip+limit], "total": len(rows), "revision": entry["revision"],
            "previous_revision": entry["previous_revision"], "actor": entry["actor"], "action": entry["action"]}


@router.get("/history-events/{entry_id}/diff", response_model=StudioHistoryDiffOut, summary="Studio-Ereignis fuer native Vergleichsmaske")
def studio_event_diff(entry_id: str, skip: int = Query(0, ge=0), limit: int = Query(25, ge=1, le=100),
                      tenant_id: str = Depends(get_tenant_id), user: dict = Depends(get_current_user)) -> dict[str, Any]:
    from app.services.studio_draft_store import history_event
    entry = _storage_call(history_event, tenant_id, None, event_id=entry_id)
    if entry is None: raise HTTPException(404, "historie_nicht_gefunden")
    return studio_history_diff(entry["draft_id"], entry_id, skip, limit, tenant_id, user)


@router.post("/drafts/{draft_id}/simulate", response_model=StudioSimulationOut, summary="Reale Prozesskette fuer unveraenderliche Review-Fassung pruefen")
def studio_simulate(draft_id: str, body: StudioRevisionIn,
                    tenant_id: str = Depends(get_tenant_id),
                    user: dict = Depends(beleg_write)) -> dict[str, Any]:
    from app.services.studio_draft_store import simulate_draft
    from app.core.studio_release import SimulationBusy
    try:
        return _storage_call(simulate_draft, tenant_id, draft_id, _actor(user), body.expected_revision, str(body.idempotency_key))
    except SimulationBusy as error:
        raise HTTPException(429, "Gemeinsamer Simulationspruefstand belegt; spaeter erneut versuchen", headers={"Retry-After": "5"}) from error
    except KeyError as error:
        raise HTTPException(404, "draft_nicht_gefunden") from error
    except ValueError as error:
        raise HTTPException(409, str(error)) from error
