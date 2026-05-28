"""Versicherungen — vollständiges CRUD."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from fastapi import Response, APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.operations.models import Versicherung, VersicherungStatus

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class CompatFlexOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


router = APIRouter(prefix="/versicherungen", tags=["Versicherungen"])


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


class VersicherungPayload(BaseModel):
    art: str = Field(..., min_length=2)
    versicherer: str = Field(..., min_length=2)
    vertragsnummer: str = Field(..., min_length=2)
    praemie: float = 0.0
    waehrung: str = "EUR"
    zahlungsweise: str = "jaehrlich"
    ablauf: Optional[datetime] = None
    beginn: Optional[datetime] = None
    selbstbehalt: Optional[float] = None
    versicherungssumme: Optional[float] = None
    ansprechpartner: Optional[str] = None
    telefon: Optional[str] = None
    email: Optional[str] = None
    notiz: Optional[str] = None
    status: str = VersicherungStatus.AKTIV.value
    tenant_id: str = "default"


class VersicherungPatch(BaseModel):
    art: Optional[str] = None
    versicherer: Optional[str] = None
    praemie: Optional[float] = None
    ablauf: Optional[datetime] = None
    status: Optional[str] = None
    notiz: Optional[str] = None
    ansprechpartner: Optional[str] = None
    telefon: Optional[str] = None
    email: Optional[str] = None


@router.get("", summary="Versicherungen auflisten",
    response_model=list[CompatFlexOut]
)
def list_versicherungen(
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
):
    q = db.query(Versicherung)
    if status:
        q = q.filter(Versicherung.status == status)
    return [_to_dict(v) for v in q.order_by(Versicherung.art).offset(skip).limit(limit).all()]


@router.get("/{versicherung_id}", summary="Versicherung abrufen",
    response_model=CompatFlexOut
)
def get_versicherung(versicherung_id: str, db: Session = Depends(get_db)):
    obj = db.query(Versicherung).filter(Versicherung.id == versicherung_id).first()
    if not obj:
        raise HTTPException(404, "Versicherung nicht gefunden")
    return _to_dict(obj)


@router.post("", status_code=201, summary="Versicherung anlegen",
    response_model=CompatFlexOut
)
def create_versicherung(payload: VersicherungPayload, db: Session = Depends(get_db)):
    obj = Versicherung(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return _to_dict(obj)


@router.patch("/{versicherung_id}", summary="Versicherung aktualisieren",
    response_model=CompatFlexOut
)
def update_versicherung(versicherung_id: str, payload: VersicherungPatch, db: Session = Depends(get_db)):
    obj = db.query(Versicherung).filter(Versicherung.id == versicherung_id).first()
    if not obj:
        raise HTTPException(404, "Versicherung nicht gefunden")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    obj.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(obj)
    return _to_dict(obj)


@router.delete("/{versicherung_id}", status_code=204, response_class=Response, response_model=None, summary="Versicherung löschen")
def delete_versicherung(versicherung_id: str, db: Session = Depends(get_db)):
    obj = db.query(Versicherung).filter(Versicherung.id == versicherung_id).first()
    if not obj:
        raise HTTPException(404, "Versicherung nicht gefunden")
    db.delete(obj)
    db.commit()
