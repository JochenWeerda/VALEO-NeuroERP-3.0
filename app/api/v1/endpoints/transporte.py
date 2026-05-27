"""Transporte — Fahrerverwaltung, vollständiges CRUD."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from fastapi import Response, APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.operations.models import Fahrer, FahrerStatus

router = APIRouter(prefix="/transporte", tags=["Transporte"])


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


class FahrerPayload(BaseModel):
    personalnummer: Optional[str] = None
    name: str = Field(..., min_length=2)
    vorname: Optional[str] = None
    geburtsdatum: Optional[datetime] = None
    telefon: Optional[str] = None
    email: Optional[str] = None
    fuehrerschein: str = Field(..., min_length=1)
    fuehrerschein_gueltig_bis: Optional[datetime] = None
    adr_bescheinigung: bool = False
    adr_gueltig_bis: Optional[datetime] = None
    status: str = FahrerStatus.VERFUEGBAR.value
    aktuelles_fahrzeug_id: Optional[str] = None


class FahrerPatch(BaseModel):
    name: Optional[str] = None
    vorname: Optional[str] = None
    telefon: Optional[str] = None
    email: Optional[str] = None
    fuehrerschein: Optional[str] = None
    fuehrerschein_gueltig_bis: Optional[datetime] = None
    status: Optional[str] = None
    aktuelles_fahrzeug_id: Optional[str] = None
    touren_heute: Optional[int] = None


@router.get("/fahrer", summary="Fahrer auflisten",
    response_model=dict
)
def list_fahrer(
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
):
    q = db.query(Fahrer)
    if status:
        q = q.filter(Fahrer.status == status)
    rows = q.order_by(Fahrer.name).offset(skip).limit(limit).all()
    result = []
    for f in rows:
        d = _to_dict(f)
        d["fahrzeug"] = f.fahrzeug.kennzeichen if f.fahrzeug else None
        result.append(d)
    return result


@router.get("/fahrer/{fahrer_id}", summary="Fahrer abrufen",
    response_model=dict
)
def get_fahrer(fahrer_id: str, db: Session = Depends(get_db)):
    obj = db.query(Fahrer).filter(Fahrer.id == fahrer_id).first()
    if not obj:
        raise HTTPException(404, "Fahrer nicht gefunden")
    data = _to_dict(obj)
    data["fahrzeug"] = obj.fahrzeug.kennzeichen if obj.fahrzeug else None
    return data


@router.post("/fahrer", status_code=201, summary="Fahrer anlegen",
    response_model=dict
)
def create_fahrer(payload: FahrerPayload, db: Session = Depends(get_db)):
    obj = Fahrer(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return _to_dict(obj)


@router.patch("/fahrer/{fahrer_id}", summary="Fahrer aktualisieren",
    response_model=dict
)
def update_fahrer(fahrer_id: str, payload: FahrerPatch, db: Session = Depends(get_db)):
    obj = db.query(Fahrer).filter(Fahrer.id == fahrer_id).first()
    if not obj:
        raise HTTPException(404, "Fahrer nicht gefunden")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    obj.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(obj)
    return _to_dict(obj)


@router.delete("/fahrer/{fahrer_id}", status_code=204, response_class=Response, response_model=None, summary="Fahrer löschen")
def delete_fahrer(fahrer_id: str, db: Session = Depends(get_db)):
    obj = db.query(Fahrer).filter(Fahrer.id == fahrer_id).first()
    if not obj:
        raise HTTPException(404, "Fahrer nicht gefunden")
    db.delete(obj)
    db.commit()
