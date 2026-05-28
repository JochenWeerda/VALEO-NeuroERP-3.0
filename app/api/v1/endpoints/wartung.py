"""Wartung / Anlagenverwaltung — vollständiges CRUD."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from fastapi import Response, APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.operations.models import WartungAnlage, WartungsProtokoll, WartungStatus

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class CompatFlexOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


router = APIRouter(prefix="/wartung", tags=["Wartung"])


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


# ── Anlagen ───────────────────────────────────────────────────────────────────

class AnlagePayload(BaseModel):
    name: str = Field(..., min_length=2)
    typ: str = Field(..., min_length=2)
    standort: str = Field(..., min_length=2)
    hersteller: Optional[str] = None
    seriennummer: Optional[str] = None
    baujahr: Optional[int] = None
    letzte_wartung: Optional[datetime] = None
    naechste_wartung: Optional[datetime] = None
    wartungsintervall_monate: int = 6
    verantwortlicher: Optional[str] = None
    notiz: Optional[str] = None
    status: str = WartungStatus.AKTIV.value
    tenant_id: str = "default"


class AnlagePatch(BaseModel):
    name: Optional[str] = None
    typ: Optional[str] = None
    standort: Optional[str] = None
    letzte_wartung: Optional[datetime] = None
    naechste_wartung: Optional[datetime] = None
    status: Optional[str] = None
    verantwortlicher: Optional[str] = None
    notiz: Optional[str] = None


@router.get("/anlagen", summary="Anlagen auflisten",
    response_model=list[CompatFlexOut]
)
def list_anlagen(
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
):
    q = db.query(WartungAnlage)
    if status:
        q = q.filter(WartungAnlage.status == status)
    return [_to_dict(a) for a in q.order_by(WartungAnlage.name).offset(skip).limit(limit).all()]


@router.get("/anlagen/{anlage_id}", summary="Anlage abrufen",
    response_model=CompatFlexOut
)
def get_anlage(anlage_id: str, db: Session = Depends(get_db)):
    obj = db.query(WartungAnlage).filter(WartungAnlage.id == anlage_id).first()
    if not obj:
        raise HTTPException(404, "Anlage nicht gefunden")
    data = _to_dict(obj)
    data["protokolle"] = [_to_dict(p) for p in obj.protokolle]
    return data


@router.post("/anlagen", status_code=201, summary="Anlage anlegen",
    response_model=CompatFlexOut
)
def create_anlage(payload: AnlagePayload, db: Session = Depends(get_db)):
    obj = WartungAnlage(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return _to_dict(obj)


@router.patch("/anlagen/{anlage_id}", summary="Anlage aktualisieren",
    response_model=CompatFlexOut
)
def update_anlage(anlage_id: str, payload: AnlagePatch, db: Session = Depends(get_db)):
    obj = db.query(WartungAnlage).filter(WartungAnlage.id == anlage_id).first()
    if not obj:
        raise HTTPException(404, "Anlage nicht gefunden")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    obj.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(obj)
    return _to_dict(obj)


@router.delete("/anlagen/{anlage_id}", status_code=204, response_class=Response, response_model=None, summary="Anlage löschen")
def delete_anlage(anlage_id: str, db: Session = Depends(get_db)):
    obj = db.query(WartungAnlage).filter(WartungAnlage.id == anlage_id).first()
    if not obj:
        raise HTTPException(404, "Anlage nicht gefunden")
    db.delete(obj)
    db.commit()


# ── Wartungsprotokolle ────────────────────────────────────────────────────────

class ProtokollPayload(BaseModel):
    datum: datetime
    art: str
    beschreibung: Optional[str] = None
    techniker: Optional[str] = None
    kosten: Optional[float] = None
    naechste_faellig: Optional[datetime] = None
    tenant_id: str = "default"


@router.get("/anlagen/{anlage_id}/protokolle", summary="Protokolle auflisten",
    response_model=None
)
def list_protokolle(anlage_id: str, db: Session = Depends(get_db)):
    return [
        _to_dict(p)
        for p in db.query(WartungsProtokoll)
        .filter(WartungsProtokoll.anlage_id == anlage_id)
        .order_by(WartungsProtokoll.datum.desc())
        .all()
    ]


@router.post("/anlagen/{anlage_id}/protokolle", status_code=201, summary="Protokoll anlegen",
    response_model=CompatFlexOut
)
def create_protokoll(anlage_id: str, payload: ProtokollPayload, db: Session = Depends(get_db)):
    anlage = db.query(WartungAnlage).filter(WartungAnlage.id == anlage_id).first()
    if not anlage:
        raise HTTPException(404, "Anlage nicht gefunden")
    proto = WartungsProtokoll(anlage_id=anlage_id, **payload.model_dump())
    db.add(proto)
    # Letzte Wartung + nächste Fälligkeit aktualisieren
    anlage.letzte_wartung = payload.datum
    if payload.naechste_faellig:
        anlage.naechste_wartung = payload.naechste_faellig
    db.commit()
    db.refresh(proto)
    return _to_dict(proto)
