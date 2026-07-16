"""Integration monitor API: preview, quarantine and controlled acceptance (FEED-INT-034)."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.agrar.rations.authz import READ_ROLES, WRITE_ROLES, require_roles
from app.auth.deps import User, get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.feeding_import_monitor_service import (
    FeedingImportMonitorService,
    ImportJobStateError,
)

router = APIRouter(prefix="/feeding", tags=["feeding-import-monitor"])

AdapterName = Literal["agrirouter", "icar-ade", "laboratory"]
# Anzeige-Label umfasst auch extern quarantinierte Quellen (FEED-INT-035).
JobAdapterLabel = Literal["agrirouter", "icar-ade", "laboratory", "mixer-feedback"]
JobStatus = Literal["validated", "quarantined", "accepted", "rejected"]


class ImportPreviewIn(BaseModel):
    adapter: AdapterName
    payload: dict[str, Any]


class ImportFindingOut(BaseModel):
    severity: str
    message: str


class ImportPreviewOut(BaseModel):
    model_config = ConfigDict(extra="ignore")

    adapter: AdapterName
    valid: bool
    findings: list[ImportFindingOut]
    mapped: dict[str, Any] | None = None


class ImportJobOut(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    tenant_id: str
    adapter: JobAdapterLabel
    status: JobStatus
    findings: list[ImportFindingOut]
    mapped_excerpt: dict[str, Any]
    result_ref: str | None = None
    decision_reason: str | None = None
    decided_by: str | None = None
    decided_at: datetime | None = None
    created_by: str
    created_at: datetime


class ImportRejectIn(BaseModel):
    reason: str = Field(min_length=3, max_length=2000,
                        description="Quarantaene-/Ablehnungsbegruendung ist pflichtig")


class EmptyBody(BaseModel):
    model_config = ConfigDict(extra="forbid")


def _service(db: Session, tenant_id: str, user: User) -> FeedingImportMonitorService:
    return FeedingImportMonitorService(db, tenant_id, str(user.get("sub") or "unknown"))


@router.post("/imports/preview", response_model=ImportPreviewOut,
             summary="Provider-Payload validieren und Zuordnung zeigen — ohne Persistenz")
async def preview_import(body: ImportPreviewIn, db: Session = Depends(get_db),
                         tenant_id: str = Depends(get_tenant_id),
                         user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, READ_ROLES, detail="Keine Berechtigung fuer die Importvorschau.")
    try:
        return _service(db, tenant_id, user).preview(body.adapter, body.payload)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/imports", response_model=ImportJobOut, status_code=201,
             summary="Importauftrag anlegen (fehlerhafte Payloads landen in Quarantaene)")
async def create_import_job(body: ImportPreviewIn, db: Session = Depends(get_db),
                            tenant_id: str = Depends(get_tenant_id),
                            user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, WRITE_ROLES, detail="Keine Berechtigung fuer Importe.")
    try:
        return _service(db, tenant_id, user).create_job(body.adapter, body.payload)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/imports", response_model=list[ImportJobOut],
            summary="Integrationsmonitor: Importauftraege mit Status")
async def list_import_jobs(status: JobStatus | None = None, db: Session = Depends(get_db),
                           tenant_id: str = Depends(get_tenant_id),
                           user: User = Depends(get_current_user)) -> list[dict[str, Any]]:
    require_roles(user, READ_ROLES, detail="Keine Berechtigung fuer den Integrationsmonitor.")
    return _service(db, tenant_id, user).list_jobs(status=status)


@router.post("/imports/{job_id}/accept", response_model=ImportJobOut,
             summary="Validierten Import kontrolliert uebernehmen (idempotenter Importpfad)")
async def accept_import_job(job_id: str, body: EmptyBody, db: Session = Depends(get_db),
                            tenant_id: str = Depends(get_tenant_id),
                            user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, WRITE_ROLES, detail="Keine Berechtigung fuer die Import-Uebernahme.")
    try:
        return _service(db, tenant_id, user).accept(job_id)
    except ImportJobStateError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/imports/{job_id}/reject", response_model=ImportJobOut,
             summary="Import mit Pflicht-Begruendung verwerfen")
async def reject_import_job(job_id: str, body: ImportRejectIn, db: Session = Depends(get_db),
                            tenant_id: str = Depends(get_tenant_id),
                            user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, WRITE_ROLES, detail="Keine Berechtigung fuer die Import-Entscheidung.")
    try:
        return _service(db, tenant_id, user).reject(job_id, body.reason)
    except ImportJobStateError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
