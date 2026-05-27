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
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Column, DateTime, String, Text, func
from sqlalchemy.orm import Session

from app.core.database import Base, get_db
from app.core.tenant import get_tenant_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/gdpr/requests", tags=["gdpr"])

# ---------------------------------------------------------------------------
# SQLAlchemy models
# ---------------------------------------------------------------------------

class GdprRequest(Base):
    __tablename__ = "gdpr_requests"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    subject_id = Column(String(36), nullable=False)
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
    subject_id: str = Field(..., description="ID of the data subject")
    subject_email: str = Field(..., description="E-mail of the data subject")
    request_type: str = Field(..., description="ACCESS | ERASURE | PORTABILITY | RECTIFICATION")
    notes: Optional[str] = None


class GdprRequestResponse(BaseModel):
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


def _get_request_or_404(request_id: str, tenant_id: str, db: Session) -> GdprRequest:
    obj = (
        db.query(GdprRequest)
        .filter(GdprRequest.id == request_id, GdprRequest.tenant_id == tenant_id)
        .first()
    )
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
    return request.headers.get("X-User-ID")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("", response_model=GdprRequestResponse, status_code=status.HTTP_201_CREATED, summary="Gdpr request anlegen")
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
    obj = GdprRequest(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        subject_id=payload.subject_id,
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


@router.get("/{request_id}", response_model=GdprRequestResponse, summary="Gdpr request abrufen")
async def get_gdpr_request(
    request_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> GdprRequestResponse:
    """Fetch a single GDPR request by ID."""
    obj = _get_request_or_404(request_id, tenant_id, db)
    return GdprRequestResponse.model_validate(obj)


@router.get("/{request_id}/history", response_model=List[GdprHistoryEntry], summary="Gdpr request history abrufen")
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


@router.post("/{request_id}/verify", response_model=GdprRequestResponse, summary="Gdpr request verifizieren")
async def verify_gdpr_request(
    request_id: str,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> GdprRequestResponse:
    """Mark identity as verified (PENDING -> VERIFIED)."""
    obj = _get_request_or_404(request_id, tenant_id, db)
    if obj.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot verify request in status '{obj.status}'",
        )
    user = _current_user(request)
    old_status = obj.status
    obj.status = "VERIFIED"
    obj.verified_at = datetime.now(timezone.utc)
    _record_history(db, obj.id, tenant_id, old_status, "VERIFIED", user)
    try:
        db.commit()
        db.refresh(obj)
    except Exception as exc:
        db.rollback()
        logger.error("gdpr_requests verify failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Could not verify GDPR request")
    return GdprRequestResponse.model_validate(obj)


@router.post("/{request_id}/export", response_model=GdprRequestResponse, summary="Gdpr request exportieren")
async def export_gdpr_request(
    request_id: str,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> GdprRequestResponse:
    """Trigger data export (Art. 15/20). VERIFIED -> PROCESSING -> COMPLETED."""
    obj = _get_request_or_404(request_id, tenant_id, db)
    if obj.status != "VERIFIED":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot export request in status '{obj.status}'. Must be VERIFIED first.",
        )
    user = _current_user(request)
    old_status = obj.status
    obj.status = "PROCESSING"
    _record_history(db, obj.id, tenant_id, old_status, "PROCESSING", user, "Export started")

    export_data: Dict[str, Any] = {
        "subject_id": obj.subject_id,
        "subject_email": obj.subject_email,
        "request_type": obj.request_type,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "tenant_id": tenant_id,
        "data": {},
    }
    # Best-effort: pull user-level data; failure is non-blocking (subject may be a customer)
    try:
        from app.infrastructure.models import User  # type: ignore[attr-defined]
        user_rec = (
            db.query(User)
            .filter(User.id == obj.subject_id, User.tenant_id == tenant_id)
            .first()
        )
        if user_rec:
            export_data["data"]["user"] = {
                "id": user_rec.id,
                "username": getattr(user_rec, "username", None),
                "email": getattr(user_rec, "email", None),
                "first_name": getattr(user_rec, "first_name", None),
                "last_name": getattr(user_rec, "last_name", None),
                "created_at": user_rec.created_at.isoformat() if getattr(user_rec, "created_at", None) else None,
            }
    except Exception as exc:  # noqa: BLE001 — best-effort secondary data, non-blocking
        logger.warning("GDPR export: could not load User record for %s: %s", obj.subject_id, exc)

    obj.export_payload = json.dumps(export_data, ensure_ascii=False, default=str)
    obj.status = "COMPLETED"
    obj.completed_at = datetime.now(timezone.utc)
    _record_history(db, obj.id, tenant_id, "PROCESSING", "COMPLETED", user, "Export completed")
    try:
        db.commit()
        db.refresh(obj)
    except Exception as exc:
        db.rollback()
        logger.error("gdpr_requests export failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Could not complete GDPR export")
    return GdprRequestResponse.model_validate(obj)


@router.post("/{request_id}/delete", response_model=GdprRequestResponse, summary="Subject data löschen")
async def delete_subject_data(
    request_id: str,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> GdprRequestResponse:
    """Execute erasure (Art. 17). Only for ERASURE requests in VERIFIED status."""
    obj = _get_request_or_404(request_id, tenant_id, db)
    if obj.request_type != "ERASURE":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This endpoint only processes ERASURE requests",
        )
    if obj.status != "VERIFIED":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot erase request in status '{obj.status}'. Must be VERIFIED first.",
        )
    user = _current_user(request)
    old_status = obj.status
    obj.status = "PROCESSING"
    _record_history(db, obj.id, tenant_id, old_status, "PROCESSING", user, "Erasure started")

    anon_suffix = f"deleted-{obj.subject_id[:8]}"
    # Anonymise system user if found (non-fatal — subject may be a customer, not a system user)
    try:
        from app.infrastructure.models import User  # type: ignore[attr-defined]
        user_rec = (
            db.query(User)
            .filter(User.id == obj.subject_id, User.tenant_id == tenant_id)
            .first()
        )
        if user_rec:
            user_rec.email = f"{anon_suffix}@anonymized.local"
            user_rec.first_name = "Geloescht"
            user_rec.last_name = "Nutzer"
            if hasattr(user_rec, "is_active"):
                user_rec.is_active = False
            if hasattr(user_rec, "deleted_at"):
                user_rec.deleted_at = datetime.now(timezone.utc)
            logger.info("GDPR erasure: anonymised User %s", obj.subject_id)
    except Exception as exc:  # noqa: BLE001 — best-effort, subject may not be a system User
        logger.warning("GDPR erasure: could not anonymise User %s: %s", obj.subject_id, exc)

    obj.status = "COMPLETED"
    obj.completed_at = datetime.now(timezone.utc)
    _record_history(db, obj.id, tenant_id, "PROCESSING", "COMPLETED", user, "Erasure completed (anonymised)")
    try:
        db.commit()
        db.refresh(obj)
    except Exception as exc:
        db.rollback()
        logger.error("gdpr_requests delete failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Could not complete GDPR erasure")
    return GdprRequestResponse.model_validate(obj)


@router.post("/{request_id}/reject", response_model=GdprRequestResponse, summary="Gdpr request ablehnen")
async def reject_gdpr_request(
    request_id: str,
    request: Request,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> GdprRequestResponse:
    """Reject a GDPR request (e.g. identity not verifiable, legal hold)."""
    obj = _get_request_or_404(request_id, tenant_id, db)
    if obj.status in ("COMPLETED", "REJECTED"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Request is already in terminal status '{obj.status}'",
        )
    user = _current_user(request)
    old_status = obj.status
    obj.status = "REJECTED"
    obj.rejection_reason = reason
    obj.completed_at = datetime.now(timezone.utc)
    _record_history(db, obj.id, tenant_id, old_status, "REJECTED", user, reason)
    try:
        db.commit()
        db.refresh(obj)
    except Exception as exc:
        db.rollback()
        logger.error("gdpr_requests reject failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Could not reject GDPR request")
    return GdprRequestResponse.model_validate(obj)


@router.get("/{request_id}/download", summary="Gdpr export herunterladen")
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
    if obj.status != "COMPLETED":
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
