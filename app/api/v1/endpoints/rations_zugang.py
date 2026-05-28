"""
Rationsoptimierung – DSGVO-Zugangsverwaltung

Steuert, wer auf betriebseigene Grundfutterdaten und Rationen eines
bestimmten Mandanten (tenant_id) zugreifen darf.

Rollen:
  admin              – VALEO-interner Admin (alle Rechte)
  vertriebsberater   – dem Betrieb zugeordneter Berater
  portal_user        – vom Betrieb selbst eingeladen
  share_link         – temporärer Lesezugang über Token-Link

Berechtigungen (granular):
  darf_lesen               – Grundfutter + Rationen einsehen
  darf_rationen_anlegen    – eigene Rationen speichern
  darf_grundfutter_anlegen – eigene Analysen anlegen/bearbeiten
  darf_zugang_verwalten    – diese Liste bearbeiten
"""
from __future__ import annotations

import secrets
import string
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Header, Query, status
from pydantic import BaseModel, ConfigDict, EmailStr
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.infrastructure.models.futtermittel_models import RationsZugang

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.rations_zugang_schemas import (
    ShareLinkCreate,
    ShareLinkOut,
    ZugangCreate,
    ZugangOut,
)


router = APIRouter()

# ---------------------------------------------------------------------------
# Pydantic-Schemas
# ---------------------------------------------------------------------------

class ZugangBase(BaseModel):
    empfaenger_email: EmailStr
    empfaenger_name: Optional[str] = None
    zugang_typ: str = "portal_user"  # admin|vertriebsberater|portal_user|share_link
    gueltig_ab: Optional[datetime] = None
    gueltig_bis: Optional[datetime] = None
    darf_lesen: bool = True
    darf_rationen_anlegen: bool = False
    darf_grundfutter_anlegen: bool = False
    darf_zugang_verwalten: bool = False
    notizen: Optional[str] = None

class ZugangPatch(BaseModel):
    empfaenger_name: Optional[str] = None
    gueltig_bis: Optional[datetime] = None
    darf_lesen: Optional[bool] = None
    darf_rationen_anlegen: Optional[bool] = None
    darf_grundfutter_anlegen: Optional[bool] = None
    darf_zugang_verwalten: Optional[bool] = None
    ist_aktiv: Optional[bool] = None
    sperrgrund: Optional[str] = None
    notizen: Optional[str] = None

class ShareTokenValidation(BaseModel):
    valid: bool
    tenant_id: Optional[str] = None
    darf_lesen: bool = False
    darf_rationen_anlegen: bool = False
    darf_grundfutter_anlegen: bool = False
    reason: Optional[str] = None


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def _gen_token(length: int = 48) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def _caller_info(
    x_user_email: Optional[str] = None,
    x_user_name: Optional[str] = None,
) -> tuple[str, Optional[str]]:
    """Liest Caller-Identität aus Dev-/Auth-Headern."""
    return (x_user_email or "system@valeo.local", x_user_name)


def _require_manage_access(
    tenant_id: str,
    caller_email: str,
    db: Session,
) -> None:
    """Wirft 403, wenn der Caller keine Verwaltungsrechte für tenant_id hat."""
    entry = db.query(RationsZugang).filter(
        RationsZugang.tenant_id == tenant_id,
        RationsZugang.empfaenger_email == caller_email,
        RationsZugang.ist_aktiv.is_(True),
        RationsZugang.darf_zugang_verwalten.is_(True),
    ).first()
    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Keine Berechtigung zur Zugangsverwaltung für diesen Mandanten.",
        )


# ---------------------------------------------------------------------------
# Endpunkte
# ---------------------------------------------------------------------------

@router.get(
    "/{tenant_id}/zugang",
    response_model=List[ZugangOut],
    summary="Zugangs-Liste eines Mandanten abrufen",
)
def list_zugang(
    tenant_id: str,
    aktiv_only: bool = Query(True),
    x_user_email: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
):
    caller_email, _ = _caller_info(x_user_email)
    _require_manage_access(tenant_id, caller_email, db)

    q = db.query(RationsZugang).filter(RationsZugang.tenant_id == tenant_id)
    if aktiv_only:
        q = q.filter(RationsZugang.ist_aktiv.is_(True))
    return q.order_by(RationsZugang.created_at.desc()).all()


@router.post(
    "/{tenant_id}/zugang",
    response_model=ZugangOut,
    status_code=status.HTTP_201_CREATED,
    summary="Zugang anlegen",
)
def create_zugang(
    tenant_id: str,
    payload: ZugangCreate,
    x_user_email: Optional[str] = Header(default=None),
    x_user_name: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
):
    import uuid
    caller_email, caller_name = _caller_info(x_user_email, x_user_name)
    _require_manage_access(tenant_id, caller_email, db)

    entry = RationsZugang(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        empfaenger_email=str(payload.empfaenger_email),
        empfaenger_name=payload.empfaenger_name,
        zugang_typ=payload.zugang_typ,
        gueltig_ab=payload.gueltig_ab or datetime.now(timezone.utc),
        gueltig_bis=payload.gueltig_bis,
        darf_lesen=payload.darf_lesen,
        darf_rationen_anlegen=payload.darf_rationen_anlegen,
        darf_grundfutter_anlegen=payload.darf_grundfutter_anlegen,
        darf_zugang_verwalten=payload.darf_zugang_verwalten,
        ist_aktiv=True,
        erstellt_von_email=caller_email,
        erstellt_von_name=caller_name,
        notizen=payload.notizen,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.patch(
    "/{tenant_id}/zugang/{eintrag_id}",
    response_model=ZugangOut,
    summary="Zugang bearbeiten / sperren / entsperren",
)
def patch_zugang(
    tenant_id: str,
    eintrag_id: str,
    payload: ZugangPatch,
    x_user_email: Optional[str] = Header(default=None),
    x_user_name: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
):
    caller_email, caller_name = _caller_info(x_user_email, x_user_name)
    _require_manage_access(tenant_id, caller_email, db)

    entry = db.query(RationsZugang).filter(
        RationsZugang.id == eintrag_id,
        RationsZugang.tenant_id == tenant_id,
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Eintrag nicht gefunden.")

    for field, val in payload.model_dump(exclude_none=True).items():
        setattr(entry, field, val)

    if payload.ist_aktiv is False and entry.gesperrt_am is None:
        entry.gesperrt_am = datetime.now(timezone.utc)
        entry.gesperrt_durch = caller_email
    elif payload.ist_aktiv is True:
        entry.gesperrt_am = None
        entry.gesperrt_durch = None

    db.commit()
    db.refresh(entry)
    return entry


@router.delete(
    "/{tenant_id}/zugang/{eintrag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Zugang widerrufen (löschen)",
    response_model=None,
)
def delete_zugang(
    tenant_id: str,
    eintrag_id: str,
    x_user_email: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
):
    caller_email, _ = _caller_info(x_user_email)
    _require_manage_access(tenant_id, caller_email, db)

    entry = db.query(RationsZugang).filter(
        RationsZugang.id == eintrag_id,
        RationsZugang.tenant_id == tenant_id,
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Eintrag nicht gefunden.")

    db.delete(entry)
    db.commit()
    from fastapi.responses import Response
    return Response(status_code=204)


@router.post(
    "/{tenant_id}/zugang/share-link",
    response_model=ShareLinkOut,
    status_code=status.HTTP_201_CREATED,
    summary="Share-Link mit einmaligem Token generieren",
)
def create_share_link(
    tenant_id: str,
    payload: ShareLinkCreate,
    x_user_email: Optional[str] = Header(default=None),
    x_user_name: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
):
    import uuid
    caller_email, caller_name = _caller_info(x_user_email, x_user_name)
    _require_manage_access(tenant_id, caller_email, db)

    token = _gen_token(48)
    entry = RationsZugang(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        empfaenger_email=f"sharelink_{token[:8]}@valeo.link",
        empfaenger_name=payload.empfaenger_name,
        zugang_typ="share_link",
        share_token=token,
        gueltig_ab=datetime.now(timezone.utc),
        gueltig_bis=payload.gueltig_bis,
        darf_lesen=True,
        darf_rationen_anlegen=False,
        darf_grundfutter_anlegen=False,
        darf_zugang_verwalten=False,
        ist_aktiv=True,
        erstellt_von_email=caller_email,
        erstellt_von_name=caller_name,
        notizen=payload.notizen,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    return ShareLinkOut(
        id=entry.id,
        share_token=token,
        share_url_suffix=f"/portal/rations/share/{token}",
        gueltig_bis=entry.gueltig_bis,
    )


@router.get(
    "/portal/share/{token}",
    response_model=ShareTokenValidation,
    summary="Share-Token validieren (öffentlich, kein Auth nötig)",
)
def validate_share_token(
    token: str,
    db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    entry = db.query(RationsZugang).filter(
        RationsZugang.share_token == token,
        RationsZugang.ist_aktiv.is_(True),
    ).first()
    if not entry:
        return ShareTokenValidation(valid=False, reason="Token unbekannt oder gesperrt.")
    if entry.gueltig_bis and entry.gueltig_bis < now:
        return ShareTokenValidation(valid=False, reason="Token abgelaufen.")

    return ShareTokenValidation(
        valid=True,
        tenant_id=entry.tenant_id,
        darf_lesen=entry.darf_lesen,
        darf_rationen_anlegen=entry.darf_rationen_anlegen,
        darf_grundfutter_anlegen=entry.darf_grundfutter_anlegen,
    )
