"""
Fuhrpark API Endpoints - zvoove style master data mask.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.inspection import inspect as sa_inspect
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.operations.repository import FahrzeugRepository

router = APIRouter(prefix="/fuhrpark", tags=["Fuhrpark"])


def _serialize_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def _to_dict(model: Any) -> dict:
    mapper = sa_inspect(model.__class__)
    data = {}
    for column in mapper.columns:
        key = column.key
        data[key] = _serialize_value(getattr(model, key))
    return data


class FuhrparkFahrzeugPayload(BaseModel):
    ro_nummer: Optional[str] = None
    is_neu: bool = False
    betrieb: Optional[str] = None
    bereich: Optional[str] = None
    pol_kennzeichen: Optional[str] = None
    kennzeichen: str = Field(..., min_length=2, max_length=20)
    typ: str = Field(..., min_length=2, max_length=50)
    marke: Optional[str] = None
    modell: Optional[str] = None
    baujahr: Optional[int] = None
    verwendung: Optional[str] = None
    kfz_brief_nummer: Optional[str] = None
    schadstoffgruppe: Optional[str] = None
    leistung_kw: Optional[float] = None
    kraftstoff: Optional[str] = None
    fahrgestellnummer: Optional[str] = None
    erstzulassung: Optional[datetime] = None
    ausstattung: Optional[str] = None
    fahrtenschreiber_vorhanden: bool = False
    ahk_vorhanden: bool = False
    ladekran_vorhanden: bool = False
    fahrer_name: Optional[str] = None
    fahrer_vorname: Optional[str] = None
    kilometerstand: float = 0
    km_stand_alle_eintraege: bool = False
    bestellnummer: Optional[str] = None
    bestelldatum: Optional[datetime] = None
    haendler: Optional[str] = None
    zustand: Optional[str] = "neu"
    kaufsumme_eur: Optional[float] = None
    kaufdatum: Optional[datetime] = None
    verkaufsdatum: Optional[datetime] = None
    abmeldedatum: Optional[datetime] = None
    kostenstelle: Optional[str] = None
    abschreibungsart: Optional[str] = None
    afa_jahre: Optional[int] = None
    afa_eur_jaehrlich: Optional[float] = None
    afa_eur_monatlich: Optional[float] = None
    leasingdauer_monate: Optional[int] = None
    leasinggesellschaft: Optional[str] = None
    leasingrate_eur: Optional[float] = None
    kfz_steuer_eur: Optional[float] = None
    kfz_steuernummer: Optional[str] = None
    kontierung: Optional[str] = None
    finanzamt: Optional[str] = None
    versicherungs_gesellschaft: Optional[str] = None
    versicherungsschein_nr: Optional[str] = None
    versicherung_satz_eur_monat: Optional[float] = None
    versicherung_haftpflicht: bool = False
    versicherung_kasko: bool = False
    naechster_tuev_termin: Optional[datetime] = None
    naechster_asu_termin: Optional[datetime] = None
    naechste_inspektion: Optional[datetime] = None
    leergewicht_kg: Optional[float] = None
    nutzlast_kg: Optional[float] = None
    gesamtgewicht_kg: Optional[float] = None
    anhaengerlast_kg: Optional[float] = None
    winterreifen_vorhanden: bool = False
    winterreifen_eingelagert: bool = False
    handy_freisprecheinrichtung: bool = False
    handy_fabrikat: Optional[str] = None
    handy_rufnummer: Optional[str] = None
    status: Optional[str] = "verfuegbar"


class DruckerSetupPayload(BaseModel):
    drucker_name: str = Field(..., min_length=2, max_length=255)


class UnfallAnzeigePayload(BaseModel):
    datum: datetime
    ort: str = Field(..., min_length=2, max_length=255)
    beschreibung: str = Field(..., min_length=3)


@router.get("/fahrzeuge", response_model=list[dict])
async def list_fahrzeuge(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    repo = FahrzeugRepository(db)
    if status:
        return [_to_dict(x) for x in repo.get_by_status(status)]
    return [_to_dict(x) for x in repo.get_all(skip=skip, limit=limit)]


@router.get("/fahrzeuge/{fahrzeug_id}", response_model=dict)
async def get_fahrzeug(fahrzeug_id: str, db: Session = Depends(get_db)):
    repo = FahrzeugRepository(db)
    fahrzeug = repo.get_by_id(fahrzeug_id)
    if not fahrzeug:
        raise HTTPException(status_code=404, detail=f"Fahrzeug {fahrzeug_id} not found")
    return _to_dict(fahrzeug)


@router.post("/fahrzeuge", response_model=dict, status_code=201)
async def create_fahrzeug(payload: FuhrparkFahrzeugPayload, db: Session = Depends(get_db)):
    repo = FahrzeugRepository(db)
    existing = repo.get_by_kennzeichen(payload.kennzeichen)
    if existing:
        raise HTTPException(status_code=409, detail="Kennzeichen already exists")
    fahrzeug = repo.create(payload.model_dump(exclude_none=True))
    return _to_dict(fahrzeug)


@router.patch("/fahrzeuge/{fahrzeug_id}", response_model=dict)
async def update_fahrzeug(
    fahrzeug_id: str,
    payload: FuhrparkFahrzeugPayload,
    db: Session = Depends(get_db),
):
    repo = FahrzeugRepository(db)
    existing = repo.get_by_id(fahrzeug_id)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Fahrzeug {fahrzeug_id} not found")
    if payload.kennzeichen and payload.kennzeichen != existing.kennzeichen:
        duplicate = repo.get_by_kennzeichen(payload.kennzeichen)
        if duplicate:
            raise HTTPException(status_code=409, detail="Kennzeichen already exists")
    fahrzeug = repo.update(fahrzeug_id, payload.model_dump(exclude_none=True))
    return _to_dict(fahrzeug)


@router.delete("/fahrzeuge/{fahrzeug_id}", status_code=204)
async def delete_fahrzeug(fahrzeug_id: str, db: Session = Depends(get_db)):
    repo = FahrzeugRepository(db)
    if not repo.delete(fahrzeug_id):
        raise HTTPException(status_code=404, detail=f"Fahrzeug {fahrzeug_id} not found")


@router.post("/fahrzeuge/{fahrzeug_id}/drucker-einrichten", response_model=dict)
async def setup_fahrzeug_printer(
    fahrzeug_id: str,
    payload: DruckerSetupPayload,
    db: Session = Depends(get_db),
):
    repo = FahrzeugRepository(db)
    fahrzeug = repo.get_by_id(fahrzeug_id)
    if not fahrzeug:
        raise HTTPException(status_code=404, detail=f"Fahrzeug {fahrzeug_id} not found")
    return {"ok": True, "fahrzeug_id": fahrzeug_id, "drucker_name": payload.drucker_name}


@router.post("/fahrzeuge/{fahrzeug_id}/drucken", response_model=dict)
async def print_fahrzeugakte(fahrzeug_id: str, db: Session = Depends(get_db)):
    repo = FahrzeugRepository(db)
    fahrzeug = repo.get_by_id(fahrzeug_id)
    if not fahrzeug:
        raise HTTPException(status_code=404, detail=f"Fahrzeug {fahrzeug_id} not found")
    return {"ok": True, "fahrzeug_id": fahrzeug_id, "aktion": "fahrzeugakte_gedruckt"}


@router.post("/fahrzeuge/{fahrzeug_id}/unfall-anzeige", response_model=dict)
async def create_unfall_anzeige(
    fahrzeug_id: str,
    payload: UnfallAnzeigePayload,
    db: Session = Depends(get_db),
):
    repo = FahrzeugRepository(db)
    fahrzeug = repo.get_by_id(fahrzeug_id)
    if not fahrzeug:
        raise HTTPException(status_code=404, detail=f"Fahrzeug {fahrzeug_id} not found")
    return {
        "ok": True,
        "fahrzeug_id": fahrzeug_id,
        "datum": payload.datum.isoformat(),
        "ort": payload.ort,
        "beschreibung": payload.beschreibung,
    }
