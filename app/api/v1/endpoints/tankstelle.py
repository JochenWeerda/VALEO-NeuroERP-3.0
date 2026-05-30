"""Tankstelle — Zapfungen und Tankbestand, vollständiges CRUD."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from fastapi import Response, APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.operations.models import Zapfung, TankBestand

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.tankstelle_schemas import TankstelleOut


router = APIRouter(prefix="/tankstelle", tags=["Tankstelle"])


def _to_dict(obj: Any) -> dict:
    from sqlalchemy.inspection import inspect as sa_inspect
    mapper = sa_inspect(obj.__class__)
    result = {}
    for col in mapper.columns:
        val = getattr(obj, col.key)
        if isinstance(val, datetime):
            val = val.isoformat()
        if isinstance(val, Decimal):
            val = float(val)
        result[col.key] = val
    return result


# ── Zapfungen ──────────────────────────────────────────────────────────────

class ZapfungPayload(BaseModel):
    kennzeichen: str = Field(..., min_length=2)
    fahrzeug_id: Optional[str] = None
    fahrer: Optional[str] = None
    fahrer_id: Optional[str] = None
    artikel: str = Field(..., min_length=2)
    menge: float = Field(..., gt=0)
    kilometer_stand: Optional[float] = None
    zapfsaeule: Optional[str] = None
    preis_liter: Optional[float] = None
    gesamtpreis: Optional[float] = None
    zeitstempel: datetime
    notiz: Optional[str] = None
    tenant_id: str = "default"


@router.get("/zapfungen", summary="Zapfungen auflisten",
    response_model=list[TankstelleOut]
)
def list_zapfungen(
    kennzeichen: Optional[str] = None,
    artikel: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
):
    q = db.query(Zapfung)
    if kennzeichen:
        q = q.filter(Zapfung.kennzeichen.ilike(f"%{kennzeichen}%"))
    if artikel:
        q = q.filter(Zapfung.artikel == artikel)
    return [_to_dict(z) for z in q.order_by(Zapfung.zeitstempel.desc()).offset(skip).limit(limit).all()]


@router.get("/zapfungen/{zapfung_id}", summary="Zapfung abrufen",
    response_model=TankstelleOut
)
def get_zapfung(zapfung_id: str, db: Session = Depends(get_db)):
    obj = db.query(Zapfung).filter(Zapfung.id == zapfung_id).first()
    if not obj:
        raise HTTPException(404, "Zapfung nicht gefunden")
    return _to_dict(obj)


@router.post("/zapfungen", status_code=201, summary="Zapfung anlegen",
    response_model=TankstelleOut
)
def create_zapfung(payload: ZapfungPayload, db: Session = Depends(get_db)):
    obj = Zapfung(**payload.model_dump())
    db.add(obj)
    # Tankbestand reduzieren
    bestand = db.query(TankBestand).filter(TankBestand.artikel == payload.artikel).first()
    if bestand:
        bestand.bestand_liter = max(0, bestand.bestand_liter - payload.menge)
    db.commit()
    db.refresh(obj)
    return _to_dict(obj)


@router.delete("/zapfungen/{zapfung_id}", status_code=204, response_class=Response, response_model=None, summary="Zapfung löschen")
def delete_zapfung(zapfung_id: str, db: Session = Depends(get_db)):
    obj = db.query(Zapfung).filter(Zapfung.id == zapfung_id).first()
    if not obj:
        raise HTTPException(404, "Zapfung nicht gefunden")
    db.delete(obj)
    db.commit()


# ── Tankbestand ────────────────────────────────────────────────────────────

class TankBestandPatch(BaseModel):
    bestand_liter: Optional[float] = None
    kapazitaet_liter: Optional[float] = None
    min_bestand: Optional[float] = None


@router.get("/bestand", summary="Bestand auflisten",
    response_model=list[TankstelleOut]
)
def list_bestand(db: Session = Depends(get_db)):
    return [_to_dict(b) for b in db.query(TankBestand).all()]


@router.patch("/bestand/{artikel}", summary="Bestand aktualisieren",
    response_model=TankstelleOut
)
def update_bestand(artikel: str, payload: TankBestandPatch, db: Session = Depends(get_db)):
    obj = db.query(TankBestand).filter(TankBestand.artikel == artikel).first()
    if not obj:
        obj = TankBestand(artikel=artikel)
        db.add(obj)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    obj.letzte_befuellung = datetime.utcnow()
    db.commit()
    db.refresh(obj)
    return _to_dict(obj)
