"""
Agrar Feldbuch — ERP-interne Endpoints (Landhandel-Mitarbeiter)

Schläge: CRUD per Kunde
Maßnahmen: CRUD (Spritztagebuch / Ackerschlagkartei)
from-lieferschein: Maßnahme aus Lieferschein erzeugen
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.uuid7 import uuid7
from app.infrastructure.models.agrar_models import FeldbuchMassnahme, FeldbuchSchlag
from modules.agrar.services.feldbuch_service import create_massnahme_from_lieferschein

router = APIRouter(tags=["agrar", "feldbuch"])


# ────────────────────────────────────────────────────────────────────────────
# Pydantic Schemas
# ────────────────────────────────────────────────────────────────────────────

class SchlagCreate(BaseModel):
    customer_id: str
    name: str
    flik: Optional[str] = None
    flaeche: float
    kultur: Optional[str] = None
    vorkultur: Optional[str] = None
    gemeinde: Optional[str] = None
    gemarkung: Optional[str] = None
    bodenart: Optional[str] = None
    ackerzahl: Optional[float] = None
    status: str = "aktiv"
    created_by: Optional[str] = None


class SchlagUpdate(BaseModel):
    name: Optional[str] = None
    flik: Optional[str] = None
    flaeche: Optional[float] = None
    kultur: Optional[str] = None
    vorkultur: Optional[str] = None
    gemeinde: Optional[str] = None
    gemarkung: Optional[str] = None
    bodenart: Optional[str] = None
    ackerzahl: Optional[float] = None
    status: Optional[str] = None


class MassnahmeCreate(BaseModel):
    customer_id: str
    schlag_id: Optional[str] = None
    datum: datetime
    uhrzeit: Optional[str] = None
    typ: str
    bezeichnung: Optional[str] = None
    mittel: Optional[str] = None
    mittel_id: Optional[str] = None
    mittel_typ: Optional[str] = None
    menge: Optional[float] = None
    einheit: Optional[str] = None
    flaeche: Optional[float] = None
    anwender: Optional[str] = None
    quelle: str = "erp_service"
    lieferschein_id: Optional[str] = None
    auflagen: Optional[list[str]] = None
    wartezeit_tage: Optional[int] = None
    windgeschwindigkeit: Optional[float] = None
    temperatur: Optional[float] = None
    compliant: bool = True
    bemerkung: Optional[str] = None


class MassnahmeUpdate(BaseModel):
    schlag_id: Optional[str] = None
    datum: Optional[datetime] = None
    uhrzeit: Optional[str] = None
    typ: Optional[str] = None
    bezeichnung: Optional[str] = None
    mittel: Optional[str] = None
    menge: Optional[float] = None
    einheit: Optional[str] = None
    flaeche: Optional[float] = None
    anwender: Optional[str] = None
    auflagen: Optional[list[str]] = None
    wartezeit_tage: Optional[int] = None
    windgeschwindigkeit: Optional[float] = None
    temperatur: Optional[float] = None
    compliant: Optional[bool] = None
    bemerkung: Optional[str] = None


class FromLieferscheinCreate(BaseModel):
    lieferschein_id: str
    lieferschein_datum: datetime
    customer_id: str
    schlag_id: str
    artikel_name: str
    menge: float
    einheit: str
    flaeche: float
    anwender: str = "VALEO GmbH"


# ────────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────────

def _schlag_to_dict(s: FeldbuchSchlag) -> dict[str, Any]:
    return {
        "id": s.id,
        "tenant_id": s.tenant_id,
        "customer_id": s.customer_id,
        "name": s.name,
        "flik": s.flik,
        "flaeche": s.flaeche,
        "kultur": s.kultur,
        "vorkultur": s.vorkultur,
        "gemeinde": s.gemeinde,
        "gemarkung": s.gemarkung,
        "bodenart": s.bodenart,
        "ackerzahl": s.ackerzahl,
        "status": s.status,
        "created_at": s.created_at.isoformat() if s.created_at else None,
        "created_by": s.created_by,
    }


def _massnahme_to_dict(m: FeldbuchMassnahme) -> dict[str, Any]:
    schlag_name = m.schlag.name if m.schlag else None
    return {
        "id": m.id,
        "tenant_id": m.tenant_id,
        "schlag_id": m.schlag_id,
        "schlag_name": schlag_name,
        "customer_id": m.customer_id,
        "datum": m.datum.date().isoformat() if m.datum else None,
        "uhrzeit": m.uhrzeit,
        "typ": m.typ,
        "bezeichnung": m.bezeichnung,
        "mittel": m.mittel,
        "mittel_id": m.mittel_id,
        "mittel_typ": m.mittel_typ,
        "menge": m.menge,
        "einheit": m.einheit,
        "flaeche": m.flaeche,
        "anwender": m.anwender,
        "quelle": m.quelle,
        "lieferschein_id": m.lieferschein_id,
        "auflagen": m.auflagen,
        "wartezeit_tage": m.wartezeit_tage,
        "windgeschwindigkeit": m.windgeschwindigkeit,
        "temperatur": m.temperatur,
        "compliant": m.compliant,
        "exportiert": m.exportiert,
        "exportiert_am": m.exportiert_am.isoformat() if m.exportiert_am else None,
        "bemerkung": m.bemerkung,
        "created_at": m.created_at.isoformat() if m.created_at else None,
    }


# ────────────────────────────────────────────────────────────────────────────
# Schläge Endpoints
# ────────────────────────────────────────────────────────────────────────────

@router.get("/schlaege")
async def list_schlaege(
    customer_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    q = db.query(FeldbuchSchlag).filter(FeldbuchSchlag.tenant_id == tenant_id)
    if customer_id:
        q = q.filter(FeldbuchSchlag.customer_id == customer_id)
    if status:
        q = q.filter(FeldbuchSchlag.status == status)
    return [_schlag_to_dict(s) for s in q.order_by(FeldbuchSchlag.name).all()]


@router.post("/schlaege", status_code=201)
async def create_schlag(
    data: SchlagCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    schlag = FeldbuchSchlag(
        id=uuid7(),
        tenant_id=tenant_id,
        **data.model_dump(),
    )
    db.add(schlag)
    db.commit()
    db.refresh(schlag)
    return _schlag_to_dict(schlag)


@router.get("/schlaege/{schlag_id}")
async def get_schlag(
    schlag_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    schlag = (
        db.query(FeldbuchSchlag)
        .filter(FeldbuchSchlag.id == schlag_id, FeldbuchSchlag.tenant_id == tenant_id)
        .first()
    )
    if not schlag:
        raise HTTPException(status_code=404, detail="Schlag nicht gefunden")
    return _schlag_to_dict(schlag)


@router.put("/schlaege/{schlag_id}")
async def update_schlag(
    schlag_id: str,
    data: SchlagUpdate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    schlag = (
        db.query(FeldbuchSchlag)
        .filter(FeldbuchSchlag.id == schlag_id, FeldbuchSchlag.tenant_id == tenant_id)
        .first()
    )
    if not schlag:
        raise HTTPException(status_code=404, detail="Schlag nicht gefunden")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(schlag, field, value)
    db.commit()
    db.refresh(schlag)
    return _schlag_to_dict(schlag)


@router.delete("/schlaege/{schlag_id}", status_code=204)
async def deactivate_schlag(
    schlag_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> None:
    schlag = (
        db.query(FeldbuchSchlag)
        .filter(FeldbuchSchlag.id == schlag_id, FeldbuchSchlag.tenant_id == tenant_id)
        .first()
    )
    if not schlag:
        raise HTTPException(status_code=404, detail="Schlag nicht gefunden")
    schlag.status = "stillgelegt"
    db.commit()


# ────────────────────────────────────────────────────────────────────────────
# Maßnahmen Endpoints
# ────────────────────────────────────────────────────────────────────────────

@router.get("/feldbuch/massnahmen")
async def list_massnahmen(
    schlag_id: Optional[str] = Query(None),
    customer_id: Optional[str] = Query(None),
    typ: Optional[str] = Query(None),
    von: Optional[str] = Query(None),   # ISO date string
    bis: Optional[str] = Query(None),   # ISO date string
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    q = (
        db.query(FeldbuchMassnahme)
        .filter(FeldbuchMassnahme.tenant_id == tenant_id)
    )
    if schlag_id:
        q = q.filter(FeldbuchMassnahme.schlag_id == schlag_id)
    if customer_id:
        q = q.filter(FeldbuchMassnahme.customer_id == customer_id)
    if typ:
        q = q.filter(FeldbuchMassnahme.typ == typ)
    if von:
        q = q.filter(FeldbuchMassnahme.datum >= datetime.fromisoformat(von))
    if bis:
        q = q.filter(FeldbuchMassnahme.datum <= datetime.fromisoformat(bis))
    return [_massnahme_to_dict(m) for m in q.order_by(FeldbuchMassnahme.datum.desc()).all()]


@router.post("/feldbuch/massnahmen", status_code=201)
async def create_massnahme(
    data: MassnahmeCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    massnahme = FeldbuchMassnahme(
        id=uuid7(),
        tenant_id=tenant_id,
        **data.model_dump(),
    )
    db.add(massnahme)
    db.commit()
    db.refresh(massnahme)
    return _massnahme_to_dict(massnahme)


@router.put("/feldbuch/massnahmen/{massnahme_id}")
async def update_massnahme(
    massnahme_id: str,
    data: MassnahmeUpdate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    massnahme = (
        db.query(FeldbuchMassnahme)
        .filter(FeldbuchMassnahme.id == massnahme_id, FeldbuchMassnahme.tenant_id == tenant_id)
        .first()
    )
    if not massnahme:
        raise HTTPException(status_code=404, detail="Maßnahme nicht gefunden")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(massnahme, field, value)
    db.commit()
    db.refresh(massnahme)
    return _massnahme_to_dict(massnahme)


@router.delete("/feldbuch/massnahmen/{massnahme_id}", status_code=204)
async def delete_massnahme(
    massnahme_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> None:
    massnahme = (
        db.query(FeldbuchMassnahme)
        .filter(FeldbuchMassnahme.id == massnahme_id, FeldbuchMassnahme.tenant_id == tenant_id)
        .first()
    )
    if not massnahme:
        raise HTTPException(status_code=404, detail="Maßnahme nicht gefunden")
    db.delete(massnahme)
    db.commit()


@router.post("/feldbuch/massnahmen/from-lieferschein", status_code=201)
async def massnahme_from_lieferschein(
    data: FromLieferscheinCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """
    Erzeugt eine Feldbuch-Maßnahme aus einem Lieferschein mit PSM-Dienstleistung.
    Verhindert Duplikate (lieferschein_id unique per tenant).
    """
    massnahme = create_massnahme_from_lieferschein(
        db,
        lieferschein_id=data.lieferschein_id,
        lieferschein_datum=data.lieferschein_datum,
        customer_id=data.customer_id,
        schlag_id=data.schlag_id,
        artikel_name=data.artikel_name,
        menge=data.menge,
        einheit=data.einheit,
        flaeche=data.flaeche,
        anwender=data.anwender,
        tenant_id=tenant_id,
    )
    db.commit()
    db.refresh(massnahme)
    return _massnahme_to_dict(massnahme)
