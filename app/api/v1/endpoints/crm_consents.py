"""CRM-Einwilligungen (DSGVO) fuer Maskengenerator und Consent-Masken."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from pydantic import Field
from sqlalchemy.orm import Session

from app.api.v1.schemas.base import BaseSchema, TypedObjectOut
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.uuid7 import uuid7
from app.infrastructure.models.crm_consent import CrmConsent, CrmConsentHistory

router = APIRouter(prefix="/crm/consents", tags=["crm", "dsgvo"])

_CHANNELS = {"email", "sms", "phone", "postal"}
_TYPES = {"marketing", "service", "required"}
_STATUSES = {"pending", "granted", "denied", "revoked"}
_SOURCES = {"web_form", "api", "import", "manual"}


class ConsentCreate(BaseSchema):
    contact_id: str = Field(..., min_length=1)
    channel: str = Field(..., min_length=1)
    consent_type: str = Field(..., min_length=1)
    source: str = "manual"
    expires_at: Optional[datetime] = None
    tenant_id: Optional[str] = None


class ConsentUpdate(BaseSchema):
    status: Optional[str] = None
    expires_at: Optional[datetime] = None
    reason: Optional[str] = None


def _iso(value: Optional[datetime]) -> Optional[str]:
    return value.isoformat() if value is not None else None


def _to_dict(row: CrmConsent) -> dict:
    return {
        "id": row.id,
        "tenant_id": row.tenant_id,
        "contact_id": row.contact_id,
        "channel": row.channel,
        "consent_type": row.consent_type,
        "status": row.status,
        "source": row.source,
        "granted_at": _iso(row.granted_at),
        "denied_at": _iso(row.denied_at),
        "revoked_at": _iso(row.revoked_at),
        "expires_at": _iso(row.expires_at),
        "double_opt_in_token": row.double_opt_in_token,
        "created_at": _iso(row.created_at),
        "updated_at": _iso(row.updated_at),
    }


def _history_dict(row: CrmConsentHistory) -> dict:
    return {
        "id": row.id,
        "consent_id": row.consent_id,
        "action": row.action,
        "old_status": row.old_status,
        "new_status": row.new_status,
        "reason": row.reason,
        "changed_by": row.changed_by,
        "changed_at": _iso(row.changed_at),
    }


def _load(db: Session, consent_id: str, tenant_id: str) -> CrmConsent:
    row = (
        db.query(CrmConsent)
        .filter(CrmConsent.id == consent_id, CrmConsent.tenant_id == tenant_id)
        .first()
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Einwilligung nicht gefunden")
    return row


def _audit(
    db: Session,
    consent: CrmConsent,
    action: str,
    old_status: Optional[str],
    new_status: str,
    *,
    reason: Optional[str] = None,
    changed_by: str = "system",
    request: Optional[Request] = None,
) -> None:
    ip = request.client.host if request and request.client else None
    ua = request.headers.get("user-agent") if request else None
    db.add(
        CrmConsentHistory(
            id=uuid7(),
            consent_id=consent.id,
            action=action,
            old_status=old_status,
            new_status=new_status,
            reason=reason,
            changed_by=changed_by,
            ip_address=ip,
            user_agent=ua,
        )
    )


@router.get("", response_model=list[TypedObjectOut], summary="Einwilligungen auflisten")
@router.get("/", response_model=list[TypedObjectOut], summary="Einwilligungen auflisten")
async def list_consents(
    contact_id: Optional[str] = Query(None),
    channel: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict]:
    q = db.query(CrmConsent).filter(CrmConsent.tenant_id == tenant_id)
    if contact_id:
        q = q.filter(CrmConsent.contact_id == contact_id)
    if channel:
        q = q.filter(CrmConsent.channel == channel)
    if status:
        q = q.filter(CrmConsent.status == status)
    return [_to_dict(row) for row in q.order_by(CrmConsent.created_at.desc()).all()]


@router.get("/contact/{contact_id}", response_model=list[TypedObjectOut], summary="Einwilligungen eines Kontakts")
async def list_contact_consents(
    contact_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict]:
    rows = (
        db.query(CrmConsent)
        .filter(CrmConsent.tenant_id == tenant_id, CrmConsent.contact_id == contact_id)
        .order_by(CrmConsent.created_at.desc())
        .all()
    )
    return [_to_dict(row) for row in rows]


@router.post("", response_model=TypedObjectOut, status_code=201, summary="Einwilligung anlegen")
@router.post("/", response_model=TypedObjectOut, status_code=201, summary="Einwilligung anlegen")
async def create_consent(
    payload: ConsentCreate,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    channel = payload.channel.strip().lower()
    consent_type = payload.consent_type.strip().lower()
    source = (payload.source or "manual").strip().lower()
    if channel not in _CHANNELS:
        raise HTTPException(status_code=422, detail=f"Ungueltiger Kanal: {payload.channel}")
    if consent_type not in _TYPES:
        raise HTTPException(status_code=422, detail=f"Ungueltiger Einwilligungstyp: {payload.consent_type}")
    if source not in _SOURCES:
        raise HTTPException(status_code=422, detail=f"Ungueltige Quelle: {payload.source}")
    now = datetime.now(timezone.utc)
    row = CrmConsent(
        id=uuid7(),
        tenant_id=payload.tenant_id or tenant_id,
        contact_id=payload.contact_id,
        channel=channel,
        consent_type=consent_type,
        status="pending",
        source=source,
        expires_at=payload.expires_at,
        double_opt_in_token=uuid7(),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        created_at=now,
        updated_at=now,
        created_by="system",
    )
    db.add(row)
    db.flush()
    _audit(db, row, "granted", None, "pending", request=request)
    db.commit()
    db.refresh(row)
    return _to_dict(row)


@router.get("/{consent_id}", response_model=TypedObjectOut, summary="Einwilligung abrufen")
async def get_consent(
    consent_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    return _to_dict(_load(db, consent_id, tenant_id))


@router.put("/{consent_id}", response_model=TypedObjectOut, summary="Einwilligung aktualisieren")
async def update_consent(
    consent_id: str,
    payload: ConsentUpdate,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    row = _load(db, consent_id, tenant_id)
    old_status = row.status
    if payload.status:
        status = payload.status.strip().lower()
        if status not in _STATUSES:
            raise HTTPException(status_code=422, detail=f"Ungueltiger Status: {payload.status}")
        row.status = status
        now = datetime.now(timezone.utc)
        if status == "granted":
            row.granted_at = now
        elif status == "denied":
            row.denied_at = now
        elif status == "revoked":
            row.revoked_at = now
    if payload.expires_at is not None:
        row.expires_at = payload.expires_at
    row.updated_at = datetime.now(timezone.utc)
    if old_status != row.status:
        _audit(db, row, "updated", old_status, row.status, reason=payload.reason, request=request)
    db.commit()
    db.refresh(row)
    return _to_dict(row)


@router.delete("/{consent_id}", status_code=204, response_class=Response, response_model=None, summary="Einwilligung loeschen")
async def delete_consent(
    consent_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> Response:
    row = _load(db, consent_id, tenant_id)
    db.delete(row)
    db.commit()
    return Response(status_code=204)


@router.get("/{consent_id}/history", response_model=list[TypedObjectOut], summary="Einwilligungshistorie")
async def get_consent_history(
    consent_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict]:
    _load(db, consent_id, tenant_id)
    rows = (
        db.query(CrmConsentHistory)
        .filter(CrmConsentHistory.consent_id == consent_id)
        .order_by(CrmConsentHistory.changed_at.desc())
        .all()
    )
    return [_history_dict(row) for row in rows]


@router.post("/{consent_id}/confirm", response_model=TypedObjectOut, summary="Double-Opt-In bestaetigen")
async def confirm_consent(
    consent_id: str,
    request: Request,
    token: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    row = _load(db, consent_id, tenant_id)
    if row.double_opt_in_token != token:
        raise HTTPException(status_code=400, detail="Ungueltiges Bestaetigungstoken")
    if row.created_at and datetime.now(timezone.utc) > row.created_at + timedelta(hours=48):
        raise HTTPException(status_code=400, detail="Bestaetigungstoken abgelaufen")
    old_status = row.status
    now = datetime.now(timezone.utc)
    row.status = "granted"
    row.granted_at = now
    row.double_opt_in_confirmed_at = now
    row.double_opt_in_token = None
    row.updated_at = now
    _audit(db, row, "granted", old_status, "granted", changed_by="contact", request=request)
    db.commit()
    db.refresh(row)
    return _to_dict(row)


@router.post("/{consent_id}/revoke", response_model=TypedObjectOut, summary="Einwilligung widerrufen")
async def revoke_consent(
    consent_id: str,
    request: Request,
    reason: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    row = _load(db, consent_id, tenant_id)
    if row.status != "granted":
        raise HTTPException(status_code=400, detail="Nur erteilte Einwilligungen koennen widerrufen werden")
    old_status = row.status
    now = datetime.now(timezone.utc)
    row.status = "revoked"
    row.revoked_at = now
    row.updated_at = now
    _audit(db, row, "revoked", old_status, "revoked", reason=reason, changed_by="contact", request=request)
    db.commit()
    db.refresh(row)
    return _to_dict(row)


@router.post(
    "/{consent_id}/resend-confirmation",
    response_model=TypedObjectOut,
    summary="Double-Opt-In erneut senden",
)
async def resend_confirmation(
    consent_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    row = _load(db, consent_id, tenant_id)
    if row.status not in {"pending", "denied"}:
        raise HTTPException(status_code=400, detail="Bestaetigung nur fuer offene Einwilligungen")
    row.double_opt_in_token = uuid7()
    row.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(row)
    payload = _to_dict(row)
    payload["message"] = "Bestaetigung erneut ausgestellt"
    return payload
