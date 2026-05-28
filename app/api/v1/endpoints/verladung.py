"""Verladung — vollständiges CRUD."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from fastapi import Response, APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.operations.models import Verladung, VerladungStatus

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class CompatFlexOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


router = APIRouter(prefix="/verladung", tags=["Verladung"])


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


class VerladungPayload(BaseModel):
    kennzeichen: str = Field(..., min_length=2)
    fahrzeug_id: Optional[str] = None
    fahrer: Optional[str] = None
    artikel: str = Field(..., min_length=2)
    artikel_id: Optional[str] = None
    menge: float = Field(..., gt=0)
    einheit: str = "t"
    lieferschein_nr: Optional[str] = None
    lieferschein_id: Optional[str] = None
    kunde: Optional[str] = None
    kunde_id: Optional[str] = None
    ladeort: Optional[str] = None
    zielort: Optional[str] = None
    geplanter_zeitslot: Optional[datetime] = None
    datum: datetime
    status: str = VerladungStatus.GEPLANT.value
    notiz: Optional[str] = None
    tenant_id: str = "default"


class VerladungPatch(BaseModel):
    kennzeichen: Optional[str] = None
    fahrer: Optional[str] = None
    menge: Optional[float] = None
    status: Optional[str] = None
    geplanter_zeitslot: Optional[datetime] = None
    beginn_verladung: Optional[datetime] = None
    ende_verladung: Optional[datetime] = None
    notiz: Optional[str] = None


@router.get("", summary="Verladungen auflisten",
    response_model=list[CompatFlexOut]
)
def list_verladungen(
    status: Optional[str] = None,
    datum_von: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
):
    q = db.query(Verladung)
    if status:
        q = q.filter(Verladung.status == status)
    return [_to_dict(v) for v in q.order_by(Verladung.datum.desc()).offset(skip).limit(limit).all()]


@router.get("/{verladung_id}", summary="Verladung abrufen",
    response_model=CompatFlexOut
)
def get_verladung(verladung_id: str, db: Session = Depends(get_db)):
    obj = db.query(Verladung).filter(Verladung.id == verladung_id).first()
    if not obj:
        raise HTTPException(404, "Verladung nicht gefunden")
    return _to_dict(obj)


@router.post("", status_code=201, summary="Verladung anlegen",
    response_model=CompatFlexOut
)
def create_verladung(payload: VerladungPayload, db: Session = Depends(get_db)):
    obj = Verladung(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return _to_dict(obj)


@router.patch("/{verladung_id}", summary="Verladung aktualisieren",
    response_model=CompatFlexOut
)
def update_verladung(verladung_id: str, payload: VerladungPatch, db: Session = Depends(get_db)):
    obj = db.query(Verladung).filter(Verladung.id == verladung_id).first()
    if not obj:
        raise HTTPException(404, "Verladung nicht gefunden")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    obj.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(obj)
    return _to_dict(obj)


@router.delete("/{verladung_id}", status_code=204, response_class=Response, response_model=None, summary="Verladung löschen")
def delete_verladung(verladung_id: str, db: Session = Depends(get_db)):
    obj = db.query(Verladung).filter(Verladung.id == verladung_id).first()
    if not obj:
        raise HTTPException(404, "Verladung nicht gefunden")
    db.delete(obj)
    db.commit()
