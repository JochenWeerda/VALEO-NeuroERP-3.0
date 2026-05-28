"""Ernte-Planungsübersicht — CRUD für Ernteplanung (Schlag, Kultur, Menge, Status)."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.operations.models import ErnteDB

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.base import CompatFlexOut


router = APIRouter(prefix="/agrar/ernte", tags=["agrar", "ernte", "ernteplanung"])


class ErntePayload(BaseModel):
    schlag: str
    kultur: str
    datum: str
    menge: float = 0
    ertrag: float = 0
    status: str = "geplant"
    tenant_id: str = "default"


class ErntePatch(BaseModel):
    schlag: Optional[str] = None
    kultur: Optional[str] = None
    datum: Optional[str] = None
    menge: Optional[float] = None
    ertrag: Optional[float] = None
    status: Optional[str] = None


def _to_dict(row: ErnteDB) -> dict:
    return {
        "id": row.id,
        "schlag": row.schlag,
        "kultur": row.kultur,
        "datum": row.datum.isoformat() if row.datum else None,
        "menge": row.menge or 0,
        "ertrag": row.ertrag or 0,
        "status": row.status,
        "tenant_id": row.tenant_id,
    }


@router.get("", summary="Ernten auflisten",
    response_model=list[CompatFlexOut]
)
def list_ernten(
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(200, le=500),
    db: Session = Depends(get_db),
):
    q = db.query(ErnteDB)
    if status:
        q = q.filter(ErnteDB.status == status)
    return [_to_dict(r) for r in q.order_by(ErnteDB.datum.desc()).offset(skip).limit(limit).all()]


@router.get("/{ernte_id}", summary="Ernte abrufen",
    response_model=CompatFlexOut
)
def get_ernte(ernte_id: str, db: Session = Depends(get_db)):
    row = db.query(ErnteDB).filter(ErnteDB.id == ernte_id).first()
    if not row:
        raise HTTPException(404, "Ernte nicht gefunden")
    return _to_dict(row)


@router.post("", status_code=201, summary="Ernte anlegen",
    response_model=CompatFlexOut
)
def create_ernte(payload: ErntePayload, db: Session = Depends(get_db)):
    datum = date.fromisoformat(payload.datum) if payload.datum else date.today()
    row = ErnteDB(
        tenant_id=payload.tenant_id,
        schlag=payload.schlag,
        kultur=payload.kultur,
        datum=datum,
        menge=payload.menge,
        ertrag=payload.ertrag,
        status=payload.status,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _to_dict(row)


@router.patch("/{ernte_id}", summary="Ernte aktualisieren",
    response_model=CompatFlexOut
)
def update_ernte(ernte_id: str, payload: ErntePatch, db: Session = Depends(get_db)):
    row = db.query(ErnteDB).filter(ErnteDB.id == ernte_id).first()
    if not row:
        raise HTTPException(404, "Ernte nicht gefunden")
    data = payload.model_dump(exclude_unset=True)
    if "datum" in data and data["datum"]:
        data["datum"] = date.fromisoformat(data["datum"])
    for k, v in data.items():
        setattr(row, k, v)
    row.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(row)
    return _to_dict(row)


@router.delete("/{ernte_id}", status_code=204, response_class=Response, response_model=None, summary="Ernte löschen")
def delete_ernte(ernte_id: str, db: Session = Depends(get_db)):
    row = db.query(ErnteDB).filter(ErnteDB.id == ernte_id).first()
    if not row:
        raise HTTPException(404, "Ernte nicht gefunden")
    db.delete(row)
    db.commit()
    return Response(status_code=204)
