"""Safe user query-center API."""

from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.v1.schemas.reporting_bundle_schemas import (
    QueryCatalogOut,
    QueryDefinitionPageOut,
    QueryDefinitionSavedOut,
    QueryExportBundleOut,
    QueryPreviewOut,
)
from app.core.config import settings
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.mask_action_runtime_service import MaskActionResult, parse_action_body
from app.services.query_center_service import QueryCenterError, QueryCenterService

router = APIRouter(prefix="/query-center", tags=["reporting", "query-center"])


class DefinitionIn(BaseModel):
    id: str | None = None
    name: str = Field(min_length=1, max_length=160)
    data_product_id: str
    selected_fields: list[str] = Field(min_length=1, max_length=30)
    filter_spec: dict[str, Any] = Field(default_factory=dict)
    aggregations: list[str] = Field(default_factory=list, max_length=10)
    is_favorite: bool = False


class SaveIn(DefinitionIn):
    reason: str = Field(min_length=5, max_length=500)


class PreviewIn(DefinitionIn):
    limit: int = Field(default=100, ge=1, le=200)


class ReasonIn(BaseModel):
    reason: str = Field(min_length=5, max_length=500)


class ImportIn(BaseModel):
    bundle: dict[str, Any]
    reason: str = Field(min_length=5, max_length=500)


def actor(request: Request) -> str:
    return request.headers.get("X-User-ID") or "query-center-user"


def service(db: Session, tenant_id: str) -> QueryCenterService:
    return QueryCenterService(db, tenant_id, signing_key=settings.SECRET_KEY)


def guarded(call):  # noqa: ANN001, ANN201
    try:
        return call()
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except QueryCenterError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/catalog", response_model=QueryCatalogOut, summary="Abfragekatalog abrufen")
def catalog(
    db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)
) -> dict[str, Any]:
    items = service(db, tenant_id).catalog()
    return {"items": items, "count": len(items)}


@router.get("", response_model=QueryDefinitionPageOut, summary="Abfragedefinitionen auflisten")
def list_definitions(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    favorite: bool | None = None,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return service(db, tenant_id).list_page(
        owner_id=actor(request), page=page, page_size=page_size, favorite=favorite
    )


@router.post("/preview", response_model=QueryPreviewOut, summary="Abfrage als Vorschau ausfuehren")
def preview(
    body: PreviewIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return guarded(
        lambda: service(db, tenant_id).preview(
            body.model_dump(exclude={"limit"}), limit=body.limit
        )
    )


@router.post("", response_model=QueryDefinitionSavedOut, status_code=201, summary="Abfragedefinition speichern")
def save(
    body: SaveIn,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return guarded(
        lambda: service(db, tenant_id).save(
            body.model_dump(exclude={"reason"}),
            actor=actor(request),
            reason=body.reason,
        )
    )


@router.post("/{definition_id}/export", response_model=QueryExportBundleOut, summary="Abfragedefinition signiert exportieren")
def export_definition(
    definition_id: str,
    body: ReasonIn,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return guarded(
        lambda: service(db, tenant_id).export_signed(
            definition_id, actor=actor(request), reason=body.reason
        )
    )


@router.post("/import", response_model=QueryDefinitionSavedOut, status_code=201, summary="Signierte Abfragedefinition importieren")
def import_definition(
    body: ImportIn,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return guarded(
        lambda: service(db, tenant_id).import_signed(
            body.bundle, actor=actor(request), reason=body.reason, commit=True
        )
    )


@router.post(
    "/actions/import",
    response_model=MaskActionResult,
    summary="Signierten Abfrage-Import als Masken-CommandEndpoint",
)
def action_import(
    request: Request,
    body: dict[str, Any] = Body(default_factory=dict),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> MaskActionResult:
    """CE fuer auswertungen/abfrage-center:import — dryRun nur Signaturpruefung."""
    try:
        mode, audit_reason, idempotency_key, payload = parse_action_body(body)
    except ValueError:
        return MaskActionResult(
            actionKey="import",
            mode="invalid",
            success=False,
            error="Unbekannter Aktionsmodus.",
            validationErrors=[
                {"field": "_mode", "message": "Ungueltiger Aktionsmodus", "severity": "blocking"}
            ],
        )

    bundle = payload.get("bundle")
    reason = str(payload.get("reason") or audit_reason or "").strip()
    if not isinstance(bundle, dict):
        return MaskActionResult(
            actionKey="import",
            mode=mode,
            success=False,
            error="bundle ist erforderlich.",
            validationErrors=[
                {"field": "bundle", "message": "Pflichtfeld (signiertes Objekt)", "severity": "blocking"}
            ],
        )
    if len(reason) < 5:
        return MaskActionResult(
            actionKey="import",
            mode=mode,
            success=False,
            error="Audit-Grund ist erforderlich (min. 5 Zeichen).",
            validationErrors=[
                {"field": "reason", "message": "Pflichtfeld", "severity": "blocking"}
            ],
        )

    svc = service(db, tenant_id)
    try:
        preview = svc.preview_import_signed(bundle)
    except QueryCenterError as exc:
        db.rollback()
        return MaskActionResult(
            actionKey="import",
            mode=mode,
            success=False,
            error=str(exc),
            validationErrors=[{"field": "bundle", "message": str(exc), "severity": "blocking"}],
        )
    db.rollback()

    if mode != "execute":
        return MaskActionResult(
            actionKey="import",
            mode=mode,
            success=True,
            summary="Signierter Import wuerde gespeichert — keine Aenderung geschrieben.",
            proposedChanges=[{**preview, "reason": reason}],
        )

    try:
        from app.services.mask_action_runtime_service import _write_audit, _write_outbox

        saved = svc.import_signed(bundle, actor=actor(request), reason=reason)
        def_id = str(saved.get("id") or "")
        audit_id = _write_audit(
            db,
            tenant_id=tenant_id,
            action_key="import",
            entity_type="query_definition",
            entity_id=def_id or tenant_id,
            audit_reason=audit_reason or reason,
            idempotency_key=idempotency_key,
            summary=f"Abfrage importiert: {preview.get('name')}",
        )
        outbox_id = _write_outbox(
            db,
            tenant_id=tenant_id,
            event_type="reporting.query_definition.imported",
            aggregate_id=def_id or tenant_id,
            payload={"definition_id": def_id, "name": preview.get("name"), "tenant_id": tenant_id},
        )
        db.commit()
    except QueryCenterError as exc:
        db.rollback()
        return MaskActionResult(
            actionKey="import", mode=mode, success=False, error=str(exc),
        )
    except Exception:
        db.rollback()
        return MaskActionResult(
            actionKey="import",
            mode=mode,
            success=False,
            error="Abfrage-Import konnte nicht gespeichert werden.",
        )

    return MaskActionResult(
        actionKey="import",
        mode=mode,
        success=True,
        summary=f"Abfrage importiert: {preview.get('name')}.",
        affectedIds=[def_id] if def_id else None,
        auditEntryId=audit_id,
        outboxEventId=outbox_id,
        proposedChanges=[preview],
    )
