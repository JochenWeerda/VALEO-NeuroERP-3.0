"""Kunden-Kontakte (Kontakthistorie + Wiedervorlage) — Kunden-Cockpit."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.crm_kontakt_service import CrmKontaktService

router = APIRouter(prefix="/crm/kunden-kontakte", tags=["crm", "kontakte"])


class KontaktIn(BaseModel):
    kunden_nr: str
    richtung: str = "aus"
    art: str = "telefon"
    kurzinfo: Optional[str] = None
    notiz: Optional[str] = None
    wiedervorlage: Optional[str] = None
    weiterleitung_an: Optional[str] = None
    bediener: Optional[str] = None
    verweis: Optional[str] = None


@router.get("/wiedervorlagen", summary="Offene Wiedervorlagen")
def wiedervorlagen(
    tage: int = Query(14, ge=0, le=365),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    return CrmKontaktService(db, tenant_id).wiedervorlagen_offen(tage)


@router.get("/{kunden_nr}", summary="Kontakthistorie eines Kunden")
def list_kontakte(
    kunden_nr: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    return CrmKontaktService(db, tenant_id).list_by_kunde(kunden_nr)


@router.post("", summary="Kontakt anlegen")
def create_kontakt(
    body: KontaktIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return CrmKontaktService(db, tenant_id).create(body.model_dump())


class ErledigtIn(BaseModel):
    ergebnis: Optional[str] = None  # Serviceabschluss-Ergebnis (optional)


@router.post("/{kontakt_id}/erledigt", summary="Wiedervorlage erledigen (mit optionalem Ergebnis)")
def erledigt(
    kontakt_id: str,
    body: ErledigtIn | None = None,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return CrmKontaktService(db, tenant_id).set_erledigt(
        kontakt_id, True, ergebnis=(body.ergebnis if body else None)
    )
