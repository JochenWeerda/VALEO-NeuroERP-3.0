"""
GDPR Data-Subject Requests API
Implements the request lifecycle: create → verify → export/delete/reject → download
GDPR Articles 15 (access), 17 (erasure), 20 (portability)
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Literal

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field, AliasChoices, field_validator
from sqlalchemy import Column, DateTime, String, Text, Integer, UniqueConstraint, func, text
from sqlalchemy.orm import Session

from app.core.database import Base, get_db
from app.core.tenant import get_tenant_id
from app.core.business_time import business_now
from app.services import gdpr_request_processor as processor

logger = logging.getLogger(__name__)

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.gdpr_requests_schemas import GdprRequestsOut
from app.core.akteur import akteur_aus_request
from app.auth.bereich_roles import SCHREIBEN  # Schreibrecht je Bereich (WRITE-ROLES)


router = APIRouter(prefix="/gdpr/requests", tags=["gdpr"])

# ---------------------------------------------------------------------------
# SQLAlchemy models
# ---------------------------------------------------------------------------

class GdprRequest(Base):
    __tablename__ = "gdpr_requests"
    __table_args__ = (UniqueConstraint("tenant_id", "creation_key", name="uq_gdpr_request_creation_key"),)

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    subject_id = Column(String(36), nullable=False)
    subject_type = Column(String(20), nullable=True)
    data_scope = Column(String(32), nullable=True)
    version = Column(Integer, nullable=False, default=1)
    creation_key = Column(String(128), nullable=True)
    creation_digest = Column(String(64), nullable=True)
    processing_result = Column(Text, nullable=True)
    subject_email = Column(String(255), nullable=False)
    # ACCESS | ERASURE | PORTABILITY | RECTIFICATION
    request_type = Column(String(40), nullable=False)
    # PENDING -> VERIFIED -> PROCESSING -> COMPLETED | REJECTED
    status = Column(String(40), nullable=False, default="PENDING")
    notes = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    # Stored JSON export payload (small payloads only)
    export_payload = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    created_by = Column(String(36), nullable=True)


class GdprRequestHistory(Base):
    """Status-change log for a GdprRequest."""
    __tablename__ = "gdpr_request_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id = Column(String(36), nullable=False, index=True)
    tenant_id = Column(String(36), nullable=False, index=True)
    old_status = Column(String(40), nullable=True)
    new_status = Column(String(40), nullable=False)
    changed_by = Column(String(36), nullable=True)
    note = Column(Text, nullable=True)
    changed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class GdprRequestCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True, str_strip_whitespace=True)
    subject_type: Literal["CUSTOMER", "LEAD"]
    data_scope: Literal["LOCAL_CRM_SUBJECT"]
    idempotency_key: str | None = Field(default=None, min_length=1, max_length=128, validation_alias=AliasChoices("idempotency_key", "_idempotencyKey"))
    subject_id: str = Field(..., min_length=1, max_length=36, description="ID of the data subject")
    subject_email: str = Field(..., min_length=3, max_length=255, description="E-mail of the data subject")
    request_type: str = Field(..., description="ACCESS | ERASURE | PORTABILITY | RECTIFICATION")
    notes: Optional[str] = None


class GdprRequestResponse(BaseModel):
    subject_type: Optional[str] = None
    version: int = 1
    data_scope: Optional[str] = None
    processing_result: Optional[dict] = None

    @field_validator("processing_result", mode="before")
    @classmethod
    def parse_processing_result(cls, value):
        return json.loads(value) if isinstance(value, str) else value
    id: str
    tenant_id: str
    subject_id: str
    subject_email: str
    request_type: str
    status: str
    notes: Optional[str]
    rejection_reason: Optional[str]
    created_at: datetime
    verified_at: Optional[datetime]
    completed_at: Optional[datetime]
    updated_at: Optional[datetime]
    created_by: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class GdprHistoryEntry(BaseModel):
    id: str
    request_id: str
    old_status: Optional[str]
    new_status: str
    changed_by: Optional[str]
    note: Optional[str]
    changed_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

VALID_REQUEST_TYPES = {"ACCESS", "ERASURE", "PORTABILITY", "RECTIFICATION"}


def _get_request_or_404(request_id: str, tenant_id: str, db: Session, *, lock=False) -> GdprRequest:
    query = db.query(GdprRequest).filter(GdprRequest.id == request_id, GdprRequest.tenant_id == tenant_id)
    obj = (query.with_for_update() if lock else query).first()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="GDPR request not found")
    return obj


def _record_history(
    db: Session,
    request_id: str,
    tenant_id: str,
    old_status: Optional[str],
    new_status: str,
    changed_by: Optional[str],
    note: Optional[str] = None,
) -> None:
    entry = GdprRequestHistory(
        id=str(uuid.uuid4()),
        request_id=request_id,
        tenant_id=tenant_id,
        old_status=old_status,
        new_status=new_status,
        changed_by=changed_by,
        note=note,
    )
    db.add(entry)


def _current_user(request: Request) -> Optional[str]:
    """Urheber aus dem geprueften Token (bis 19.10.2026 zuerst aus dem Client-Header ``X-User-ID``)."""
    return akteur_aus_request(request)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("", response_model=GdprRequestResponse, status_code=status.HTTP_201_CREATED, summary="Gdpr request anlegen", dependencies=SCHREIBEN["QUALITAET"])
async def create_gdpr_request(
    payload: GdprRequestCreate,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> GdprRequestResponse:
    """Create a new GDPR data-subject request (Art. 15 / 17 / 20)."""
    if payload.request_type not in VALID_REQUEST_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"request_type must be one of {sorted(VALID_REQUEST_TYPES)}",
        )
    user = _current_user(request)
    if not user:
        raise HTTPException(401, "Verifizierter Urheber erforderlich")
    import hashlib
    creation_digest = hashlib.sha256(json.dumps({"actor": user, **payload.model_dump(exclude={'idempotency_key'})}, sort_keys=True).encode()).hexdigest()
    if payload.idempotency_key:
        db.execute(text('SELECT pg_advisory_xact_lock(hashtextextended(:key,0))'), {'key': 'gdpr-create:' + tenant_id + ':' + payload.idempotency_key})
        existing = db.query(GdprRequest).filter(GdprRequest.tenant_id == tenant_id, GdprRequest.creation_key == payload.idempotency_key).first()
        if existing is not None:
            if existing.creation_digest != creation_digest:
                raise HTTPException(409, 'Wiederholungsschluessel gehoert zu einem anderen Antrag')
            return GdprRequestResponse.model_validate(existing)
    processor.subject_rows(db, payload.subject_type, payload.subject_id, tenant_id, email=payload.subject_email)
    obj = GdprRequest(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        subject_id=payload.subject_id,
        subject_type=payload.subject_type, data_scope=payload.data_scope, version=1, creation_key=payload.idempotency_key, creation_digest=creation_digest,
        subject_email=payload.subject_email,
        request_type=payload.request_type,
        status="PENDING",
        notes=payload.notes,
        created_by=user,
    )
    db.add(obj)
    _record_history(db, obj.id, tenant_id, None, "PENDING", user, "Request created")
    try:
        db.commit()
        db.refresh(obj)
    except Exception as exc:
        db.rollback()
        logger.error("gdpr_requests create failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Could not create GDPR request")
    logger.info("GDPR request created: %s type=%s tenant=%s", obj.id, obj.request_type, tenant_id)
    return GdprRequestResponse.model_validate(obj)


@router.get("", response_model=List[GdprRequestResponse], summary="Gdpr requests auflisten",
            dependencies=SCHREIBEN["QUALITAET"])
async def list_gdpr_requests(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> List[GdprRequestResponse]:
    """Anfragen des Mandanten, neueste zuerst. Bis 20.10.2026 fehlte der Weg; die Liste blieb immer leer.

    Die Liste zeigt E-Mail-Adressen der Betroffenen; deshalb dieselbe Rolle wie die Bearbeitung.
    """
    rows = (db.query(GdprRequest).filter(GdprRequest.tenant_id == tenant_id)
            .order_by(GdprRequest.created_at.desc()).limit(500).all())
    return [GdprRequestResponse.model_validate(row) for row in rows]


@router.get("/{request_id}", response_model=GdprRequestResponse, summary="Gdpr request abrufen", dependencies=SCHREIBEN["QUALITAET"])
async def get_gdpr_request(
    request_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> GdprRequestResponse:
    """Fetch a single GDPR request by ID."""
    obj = _get_request_or_404(request_id, tenant_id, db)
    return GdprRequestResponse.model_validate(obj)


@router.get("/{request_id}/history", response_model=List[GdprHistoryEntry], summary="Gdpr request history abrufen", dependencies=SCHREIBEN["QUALITAET"])
async def get_gdpr_request_history(
    request_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> List[GdprHistoryEntry]:
    """Return the status-change log for a GDPR request."""
    _get_request_or_404(request_id, tenant_id, db)
    entries = (
        db.query(GdprRequestHistory)
        .filter(
            GdprRequestHistory.request_id == request_id,
            GdprRequestHistory.tenant_id == tenant_id,
        )
        .order_by(GdprRequestHistory.changed_at.asc())
        .all()
    )
    return [GdprHistoryEntry.model_validate(e) for e in entries]


@router.post("/{request_id}/verify", response_model=GdprRequestResponse, summary="Gdpr request verifizieren", dependencies=SCHREIBEN["QUALITAET"])
async def verify_gdpr_request(
    request_id: str,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> GdprRequestResponse:
    """Mark identity as verified (PENDING -> VERIFIED)."""
    obj = _get_request_or_404(request_id, tenant_id, db, lock=True)
    if obj.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot verify request in status '{obj.status}'",
        )
    user = _current_user(request)
    old_status = obj.status
    obj.version = (obj.version or 1) + 1
    obj.status = "VERIFIED"
    obj.verified_at = business_now()
    _record_history(db, obj.id, tenant_id, old_status, "VERIFIED", user)
    try:
        db.commit()
        db.refresh(obj)
    except Exception as exc:
        db.rollback()
        logger.error("gdpr_requests verify failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Could not verify GDPR request")
    return GdprRequestResponse.model_validate(obj)


async def _process_request(request_id, request, payload, db, tenant_id, action):
    initial = _get_request_or_404(request_id, tenant_id, db)
    db.execute(text('SELECT pg_advisory_xact_lock(hashtextextended(:key,0))'), {'key': 'gdpr-subject:' + tenant_id + ':' + initial.subject_id})
    obj = _get_request_or_404(request_id, tenant_id, db, lock=True)
    actor = _current_user(request)
    if not actor:
        raise HTTPException(401, 'Verifizierter Urheber erforderlich')
    before = obj.status
    try:
        processor.process(db, obj, payload, actor, action)
        if before != obj.status:
            _record_history(db, obj.id, tenant_id, before, obj.status, actor, payload.reason)
        db.commit()
        db.refresh(obj)
        return GdprRequestResponse.model_validate(obj)
    except Exception:
        db.rollback()
        raise


@router.post("/{request_id}/export", response_model=GdprRequestResponse, summary="CRM-Betroffenendaten exportieren", dependencies=SCHREIBEN["QUALITAET"])
async def export_gdpr_request(request_id: str, request: Request, payload: processor.ProcessPayload,
    db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await _process_request(request_id, request, payload, db, tenant_id, 'export')


@router.post("/{request_id}/delete", response_model=GdprRequestResponse, summary="CRM-Personendaten anonymisieren", dependencies=SCHREIBEN["QUALITAET"])
async def delete_subject_data(request_id: str, request: Request, payload: processor.ProcessPayload,
    db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return await _process_request(request_id, request, payload, db, tenant_id, 'erase')


@router.post("/{request_id}/reject", response_model=GdprRequestResponse, summary="Gdpr request ablehnen", dependencies=SCHREIBEN["QUALITAET"])
async def reject_gdpr_request(
    request_id: str,
    request: Request,
    reason: Optional[str] = None,
    body: Optional[dict] = Body(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> GdprRequestResponse:
    """Reject a GDPR request (e.g. identity not verifiable, legal hold)."""
    # Maske, CLI und MCP schicken die Begruendung im Body (``_auditReason``); vorher ging sie dort verloren.
    reason = reason or (body or {}).get("reason") or (body or {}).get("_auditReason")
    obj = _get_request_or_404(request_id, tenant_id, db, lock=True)
    if obj.status in ("COMPLETED", "PARTIALLY_COMPLETED", "REJECTED"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Request is already in terminal status '{obj.status}'",
        )
    user = _current_user(request)
    old_status = obj.status
    obj.version = (obj.version or 1) + 1
    obj.status = "REJECTED"
    obj.rejection_reason = reason
    obj.completed_at = business_now()
    _record_history(db, obj.id, tenant_id, old_status, "REJECTED", user, reason)
    try:
        db.commit()
        db.refresh(obj)
    except Exception as exc:
        db.rollback()
        logger.error("gdpr_requests reject failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Could not reject GDPR request")
    return GdprRequestResponse.model_validate(obj)


@router.get("/{request_id}/download", summary="Gdpr export herunterladen", dependencies=SCHREIBEN["QUALITAET"],
    response_model=GdprRequestsOut
)
async def download_gdpr_export(
    request_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> StreamingResponse:
    """
    Download the JSON export package for a COMPLETED ACCESS/PORTABILITY request.
    Returns 404 if the export is not yet ready.
    """
    obj = _get_request_or_404(request_id, tenant_id, db)
    if obj.status not in ("COMPLETED", "PARTIALLY_COMPLETED"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export not ready. Request must be in COMPLETED status.",
        )
    if not obj.export_payload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No export file available (ERASURE or REJECTED requests have no download).",
        )
    filename = f"gdpr_export_{obj.subject_id}_{obj.id[:8]}.json"
    payload_bytes = obj.export_payload.encode("utf-8")
    return StreamingResponse(
        iter([payload_bytes]),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
