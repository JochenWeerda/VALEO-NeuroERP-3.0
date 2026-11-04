"""Foerderantraege (Agrarfoerderung) im Mandanten.

Bis 03.11.2026 (Batch 8) legte jeder Lesezugriff per ``_seed`` zwei erfundene Antraege an (FA-2026-001 Greening,
FA-2026-002 Junglandwirte), kein Weg kannte einen Mandanten, und Aendern nahm die Kennung als Zahl an - die
Kennungen sind Texte (``FA-...``), jedes Aendern scheiterte mit 422. Jetzt: Mandant aus der Anmeldung, RLS auf
``domain_ops.ops_foerderantraege`` (Migration ``scheinwege_mandant_20261103``), Antragsnummer je Mandant eindeutig.
"""

from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.v1.schemas.foerderung_schemas import FoerderAntragListOut, FoerderAntragOut, FoerderungStatsOut
from app.auth.bereich_roles import SCHREIBEN  # Schreibrecht je Bereich (WRITE-ROLES)
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.domains.operations.models import FoerderAntrag

router = APIRouter(prefix="/foerderung", tags=["Foerderung"])

STATUS = ("entwurf", "eingereicht", "bewilligt", "abgelehnt")


class FoerderAntragCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    nummer: str = Field(min_length=1, max_length=80)
    programm: str = Field(min_length=1, max_length=120)
    antragsdatum: date
    flaeche: float = Field(default=0, ge=0)
    betrag: float = Field(default=0, ge=0)
    status: str = "entwurf"


class FoerderAntragUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    programm: Optional[str] = Field(default=None, min_length=1, max_length=120)
    antragsdatum: Optional[date] = None
    flaeche: Optional[float] = Field(default=None, ge=0)
    betrag: Optional[float] = Field(default=None, ge=0)
    status: Optional[str] = None


def _dt(v: Optional[datetime]) -> Optional[str]:
    return v.date().isoformat() if v else None


def _out(a: FoerderAntrag) -> dict:
    return {"id": a.id, "nummer": a.nummer, "programm": a.programm, "antragsdatum": _dt(a.antragsdatum),
            "flaeche": float(a.flaeche or 0), "betrag": float(a.betrag or 0), "status": a.status}


def _status(wert: Optional[str]) -> None:
    if wert is not None and wert not in STATUS:
        raise HTTPException(status_code=422, detail=f"status muss einer von {', '.join(STATUS)} sein")


def _eigener(db: Session, tenant_id: str, antrag_id: str) -> FoerderAntrag:
    antrag = db.query(FoerderAntrag).filter(FoerderAntrag.tenant_id == tenant_id, FoerderAntrag.id == antrag_id).first()
    if not antrag:
        raise HTTPException(status_code=404, detail="Antrag nicht gefunden")
    return antrag


def _speichern(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Antragsnummer ist im Mandanten schon vergeben") from exc


@router.get("/antraege", response_model=FoerderAntragListOut, summary="Antraege auflisten")
async def list_antraege(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(500, ge=1, le=2000),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    query = db.query(FoerderAntrag).filter(FoerderAntrag.tenant_id == tenant_id)
    if status:
        query = query.filter(FoerderAntrag.status == status)
    payload = [_out(a) for a in query.order_by(FoerderAntrag.antragsdatum.desc()).limit(limit).all()]
    return {"items": payload, "total": len(payload), "sum_betrag": sum(i["betrag"] for i in payload)}


@router.get("/stats", response_model=FoerderungStatsOut, summary="Foerderung stats abrufen")
async def get_foerderung_stats(tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> dict:
    items = db.query(FoerderAntrag.status, FoerderAntrag.betrag).filter(FoerderAntrag.tenant_id == tenant_id).limit(10000).all()
    return {
        "bewilligt": sum(1 for s, _ in items if s == "bewilligt"),
        "eingereicht": sum(1 for s, _ in items if s == "eingereicht"),
        "entwurf": sum(1 for s, _ in items if s == "entwurf"),
        "betrag_bewilligt": sum(float(b or 0) for s, b in items if s == "bewilligt"),
    }


@router.post("/antraege", response_model=FoerderAntragOut, status_code=201, summary="Antrag anlegen", dependencies=SCHREIBEN["AGRAR"])
async def create_antrag(body: FoerderAntragCreate, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> dict:
    _status(body.status)
    antrag = FoerderAntrag(
        tenant_id=tenant_id, nummer=body.nummer, programm=body.programm,
        antragsdatum=datetime.combine(body.antragsdatum, datetime.min.time()),
        flaeche=body.flaeche, betrag=body.betrag, status=body.status,
    )
    db.add(antrag)
    _speichern(db)
    db.refresh(antrag)
    return _out(antrag)


@router.get("/antraege/{antrag_id}", response_model=FoerderAntragOut, summary="Antrag abrufen")
async def get_antrag(antrag_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> dict:
    return _out(_eigener(db, tenant_id, antrag_id))


@router.put("/antraege/{antrag_id}", response_model=FoerderAntragOut, summary="Antrag aktualisieren", dependencies=SCHREIBEN["AGRAR"])
async def update_antrag(
    antrag_id: str, body: FoerderAntragUpdate, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db),
) -> dict:
    antrag = _eigener(db, tenant_id, antrag_id)
    update_data = body.model_dump(exclude_unset=True)
    _status(update_data.get("status"))
    if update_data.get("antragsdatum") is not None:
        update_data["antragsdatum"] = datetime.combine(update_data["antragsdatum"], datetime.min.time())
    for field, value in update_data.items():
        setattr(antrag, field, value)
    _speichern(db)
    db.refresh(antrag)
    return _out(antrag)


@router.delete("/antraege/{antrag_id}", status_code=204, response_class=Response, response_model=None, summary="Antrag löschen", dependencies=SCHREIBEN["AGRAR"])
async def delete_antrag(antrag_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> Response:
    """Nur Entwuerfe; ein eingereichter Antrag ist ein Vorgang gegenueber der Behoerde."""
    antrag = _eigener(db, tenant_id, antrag_id)
    if antrag.status != "entwurf":
        raise HTTPException(status_code=409, detail="Nur Entwürfe können gelöscht werden")
    db.delete(antrag)
    db.commit()
    return Response(status_code=204)
