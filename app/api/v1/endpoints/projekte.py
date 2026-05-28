"""Projekte — vollständiges CRUD inkl. Aufgaben."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from fastapi import Response, APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.operations.models import Projekt, ProjektAufgabe, ProjektStatus

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.base import CompatFlexOut
from app.api.v1.schemas.projekte_schemas import ProjekteOut


router = APIRouter(prefix="/projekte", tags=["Projekte"])


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


# ── Projekte ──────────────────────────────────────────────────────────────────

class ProjektPayload(BaseModel):
    name: str = Field(..., min_length=2)
    beschreibung: Optional[str] = None
    projektleiter: Optional[str] = None
    kunde: str = "intern"
    kunde_id: Optional[str] = None
    startdatum: Optional[datetime] = None
    enddatum: Optional[datetime] = None
    fortschritt: int = 0
    budget: float = 0.0
    ausgaben: float = 0.0
    kostenstelle: Optional[str] = None
    status: str = ProjektStatus.GEPLANT.value
    prioritaet: str = "normal"
    notiz: Optional[str] = None
    tenant_id: str = "default"


class ProjektPatch(BaseModel):
    name: Optional[str] = None
    beschreibung: Optional[str] = None
    projektleiter: Optional[str] = None
    fortschritt: Optional[int] = None
    budget: Optional[float] = None
    ausgaben: Optional[float] = None
    status: Optional[str] = None
    prioritaet: Optional[str] = None
    enddatum: Optional[datetime] = None
    notiz: Optional[str] = None


@router.get("", summary="Projekte auflisten",
    response_model=list[ProjekteOut]
)
def list_projekte(
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
):
    q = db.query(Projekt)
    if status:
        q = q.filter(Projekt.status == status)
    return [_to_dict(p) for p in q.order_by(Projekt.name).offset(skip).limit(limit).all()]


@router.get("/{projekt_id}", summary="Projekt abrufen",
    response_model=ProjekteOut
)
def get_projekt(projekt_id: str, db: Session = Depends(get_db)):
    obj = db.query(Projekt).filter(Projekt.id == projekt_id).first()
    if not obj:
        raise HTTPException(404, "Projekt nicht gefunden")
    data = _to_dict(obj)
    data["aufgaben"] = [_to_dict(a) for a in obj.aufgaben]
    return data


@router.post("", status_code=201, summary="Projekt anlegen",
    response_model=ProjekteOut
)
def create_projekt(payload: ProjektPayload, db: Session = Depends(get_db)):
    obj = Projekt(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return _to_dict(obj)


@router.patch("/{projekt_id}", summary="Projekt aktualisieren",
    response_model=None
)
def update_projekt(projekt_id: str, payload: ProjektPatch, db: Session = Depends(get_db)):
    obj = db.query(Projekt).filter(Projekt.id == projekt_id).first()
    if not obj:
        raise HTTPException(404, "Projekt nicht gefunden")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    obj.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(obj)
    return _to_dict(obj)


@router.delete("/{projekt_id}", status_code=204, response_class=Response, response_model=None, summary="Projekt löschen")
def delete_projekt(projekt_id: str, db: Session = Depends(get_db)):
    obj = db.query(Projekt).filter(Projekt.id == projekt_id).first()
    if not obj:
        raise HTTPException(404, "Projekt nicht gefunden")
    db.delete(obj)
    db.commit()


# ── Aufgaben ──────────────────────────────────────────────────────────────────

class AufgabePayload(BaseModel):
    titel: str = Field(..., min_length=2)
    beschreibung: Optional[str] = None
    verantwortlicher: Optional[str] = None
    faellig_am: Optional[datetime] = None
    status: str = "offen"
    tenant_id: str = "default"


class AufgabePatch(BaseModel):
    titel: Optional[str] = None
    beschreibung: Optional[str] = None
    verantwortlicher: Optional[str] = None
    faellig_am: Optional[datetime] = None
    erledigt_am: Optional[datetime] = None
    status: Optional[str] = None


@router.get("/{projekt_id}/aufgaben", summary="Aufgaben auflisten",
    response_model=None
)
def list_aufgaben(projekt_id: str, db: Session = Depends(get_db)):
    return [
        _to_dict(a)
        for a in db.query(ProjektAufgabe)
        .filter(ProjektAufgabe.projekt_id == projekt_id)
        .order_by(ProjektAufgabe.faellig_am)
        .all()
    ]


@router.post("/{projekt_id}/aufgaben", status_code=201, summary="Aufgabe anlegen",
    response_model=ProjekteOut
)
def create_aufgabe(projekt_id: str, payload: AufgabePayload, db: Session = Depends(get_db)):
    projekt = db.query(Projekt).filter(Projekt.id == projekt_id).first()
    if not projekt:
        raise HTTPException(404, "Projekt nicht gefunden")
    obj = ProjektAufgabe(projekt_id=projekt_id, **payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return _to_dict(obj)


@router.patch("/{projekt_id}/aufgaben/{aufgabe_id}", summary="Aufgabe aktualisieren",
    response_model=None
)
def update_aufgabe(projekt_id: str, aufgabe_id: str, payload: AufgabePatch, db: Session = Depends(get_db)):
    obj = db.query(ProjektAufgabe).filter(
        ProjektAufgabe.id == aufgabe_id,
        ProjektAufgabe.projekt_id == projekt_id,
    ).first()
    if not obj:
        raise HTTPException(404, "Aufgabe nicht gefunden")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return _to_dict(obj)


@router.delete("/{projekt_id}/aufgaben/{aufgabe_id}", status_code=204, response_class=Response, response_model=None, summary="Aufgabe löschen")
def delete_aufgabe(projekt_id: str, aufgabe_id: str, db: Session = Depends(get_db)):
    obj = db.query(ProjektAufgabe).filter(
        ProjektAufgabe.id == aufgabe_id,
        ProjektAufgabe.projekt_id == projekt_id,
    ).first()
    if not obj:
        raise HTTPException(404, "Aufgabe nicht gefunden")
    db.delete(obj)
    db.commit()
