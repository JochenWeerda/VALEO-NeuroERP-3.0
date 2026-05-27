"""
Fuhrpark API Endpoints - zvoove style master data mask.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from fastapi import Response, APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.inspection import inspect as sa_inspect
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.operations.repository import (
    FahrzeugRepository,
    FuhrparkAusgehendesDokumentRepository,
    FuhrparkRechnungRepository,
    FuhrparkTerminartRepository,
)

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


class FuhrparkTerminartPayload(BaseModel):
    terminart: str = Field(..., min_length=2, max_length=120)
    intervall_monate: int = Field(0, ge=0, le=1200)
    intervall_km: int = Field(0, ge=0, le=2_000_000)


class FuhrparkRechnungPayload(BaseModel):
    rechnungs_nr: str = Field(..., min_length=3, max_length=80)
    datum: datetime
    fahrzeug_id: Optional[str] = None
    fahrzeug_kennzeichen: Optional[str] = None
    sachkonto: Optional[str] = None
    kostenart: Optional[str] = None
    betrag_eur: float = Field(..., ge=0)
    notiz: Optional[str] = None


class FuhrparkAusgehendesDokumentPayload(BaseModel):
    beleg_typ: str = Field(..., min_length=2, max_length=120)
    formular: Optional[str] = Field(default=None, max_length=80)
    ziel_modul: Optional[str] = Field(default=None, max_length=255)
    beschreibung: Optional[str] = None
    aktiv: bool = True
    letzter_druck: Optional[datetime] = None


@router.get("/fahrzeuge", response_model=list[dict], summary="Fahrzeuge auflisten")
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


@router.get("/fahrzeuge/{fahrzeug_id}", response_model=dict, summary="Fahrzeug abrufen")
async def get_fahrzeug(fahrzeug_id: str, db: Session = Depends(get_db)):
    repo = FahrzeugRepository(db)
    fahrzeug = repo.get_by_id(fahrzeug_id)
    if not fahrzeug:
        raise HTTPException(status_code=404, detail=f"Fahrzeug {fahrzeug_id} not found")
    return _to_dict(fahrzeug)


@router.post("/fahrzeuge", response_model=dict, status_code=201, summary="Fahrzeug anlegen")
async def create_fahrzeug(payload: FuhrparkFahrzeugPayload, db: Session = Depends(get_db)):
    repo = FahrzeugRepository(db)
    existing = repo.get_by_kennzeichen(payload.kennzeichen)
    if existing:
        raise HTTPException(status_code=409, detail="Kennzeichen already exists")
    fahrzeug = repo.create(payload.model_dump(exclude_none=True))
    return _to_dict(fahrzeug)


@router.patch("/fahrzeuge/{fahrzeug_id}", response_model=dict, summary="Fahrzeug aktualisieren")
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


@router.delete("/fahrzeuge/{fahrzeug_id}", status_code=204, response_class=Response, response_model=None, summary="Fahrzeug löschen")
async def delete_fahrzeug(fahrzeug_id: str, db: Session = Depends(get_db)):
    repo = FahrzeugRepository(db)
    if not repo.delete(fahrzeug_id):
        raise HTTPException(status_code=404, detail=f"Fahrzeug {fahrzeug_id} not found")


@router.post("/fahrzeuge/{fahrzeug_id}/drucker-einrichten", response_model=dict, summary="Fahrzeug printer setup")
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


@router.post("/fahrzeuge/{fahrzeug_id}/drucken", response_model=dict, summary="Fahrzeugakte drucken")
async def print_fahrzeugakte(fahrzeug_id: str, db: Session = Depends(get_db)):
    repo = FahrzeugRepository(db)
    fahrzeug = repo.get_by_id(fahrzeug_id)
    if not fahrzeug:
        raise HTTPException(status_code=404, detail=f"Fahrzeug {fahrzeug_id} not found")
    return {"ok": True, "fahrzeug_id": fahrzeug_id, "aktion": "fahrzeugakte_gedruckt"}


@router.post("/fahrzeuge/{fahrzeug_id}/unfall-anzeige", response_model=dict, summary="Unfall anzeige anlegen")
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


@router.get("/terminarten", response_model=list[dict], summary="Terminarten auflisten")
async def list_terminarten(db: Session = Depends(get_db)):
    repo = FuhrparkTerminartRepository(db)
    return [_to_dict(row) for row in repo.get_all()]


@router.post("/terminarten", response_model=dict, status_code=201, summary="Terminart anlegen")
async def create_terminart(payload: FuhrparkTerminartPayload, db: Session = Depends(get_db)):
    repo = FuhrparkTerminartRepository(db)
    duplicate = repo.get_by_name(payload.terminart)
    if duplicate:
        raise HTTPException(status_code=409, detail="Terminart already exists")
    row = repo.create(payload.model_dump())
    return _to_dict(row)


@router.patch("/terminarten/{terminart_id}", response_model=dict, summary="Terminart aktualisieren")
async def update_terminart(
    terminart_id: str,
    payload: FuhrparkTerminartPayload,
    db: Session = Depends(get_db),
):
    repo = FuhrparkTerminartRepository(db)
    existing = repo.get_by_id(terminart_id)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Terminart {terminart_id} not found")
    if payload.terminart != existing.terminart:
        duplicate = repo.get_by_name(payload.terminart)
        if duplicate:
            raise HTTPException(status_code=409, detail="Terminart already exists")
    updated = repo.update(terminart_id, payload.model_dump())
    return _to_dict(updated)


@router.delete("/terminarten/{terminart_id}", status_code=204, response_class=Response, response_model=None, summary="Terminart löschen")
async def delete_terminart(terminart_id: str, db: Session = Depends(get_db)):
    repo = FuhrparkTerminartRepository(db)
    if not repo.delete(terminart_id):
        raise HTTPException(status_code=404, detail=f"Terminart {terminart_id} not found")


@router.get("/rechnungen", response_model=list[dict], summary="Rechnungen auflisten")
async def list_rechnungen(
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    repo = FuhrparkRechnungRepository(db)
    return [_to_dict(row) for row in repo.get_all(skip=skip, limit=limit)]


@router.post("/rechnungen", response_model=dict, status_code=201, summary="Rechnung anlegen")
async def create_rechnung(payload: FuhrparkRechnungPayload, db: Session = Depends(get_db)):
    repo = FuhrparkRechnungRepository(db)
    duplicate = repo.get_by_rechnungs_nr(payload.rechnungs_nr)
    if duplicate:
        raise HTTPException(status_code=409, detail="Rechnungsnummer already exists")
    row = repo.create(payload.model_dump())
    return _to_dict(row)


@router.patch("/rechnungen/{rechnung_id}", response_model=dict, summary="Rechnung aktualisieren")
async def update_rechnung(
    rechnung_id: str,
    payload: FuhrparkRechnungPayload,
    db: Session = Depends(get_db),
):
    repo = FuhrparkRechnungRepository(db)
    existing = repo.get_by_id(rechnung_id)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Rechnung {rechnung_id} not found")
    if payload.rechnungs_nr != existing.rechnungs_nr:
        duplicate = repo.get_by_rechnungs_nr(payload.rechnungs_nr)
        if duplicate:
            raise HTTPException(status_code=409, detail="Rechnungsnummer already exists")
    updated = repo.update(rechnung_id, payload.model_dump())
    return _to_dict(updated)


@router.delete("/rechnungen/{rechnung_id}", status_code=204, response_class=Response, response_model=None, summary="Rechnung löschen")
async def delete_rechnung(rechnung_id: str, db: Session = Depends(get_db)):
    repo = FuhrparkRechnungRepository(db)
    if not repo.delete(rechnung_id):
        raise HTTPException(status_code=404, detail=f"Rechnung {rechnung_id} not found")


@router.get("/ausgehende-dokumente", response_model=list[dict], summary="Ausgehende dokumente auflisten")
async def list_ausgehende_dokumente(
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    repo = FuhrparkAusgehendesDokumentRepository(db)
    return [_to_dict(row) for row in repo.get_all(skip=skip, limit=limit)]


@router.post("/ausgehende-dokumente", response_model=dict, status_code=201, summary="Ausgehendes dokument anlegen")
async def create_ausgehendes_dokument(
    payload: FuhrparkAusgehendesDokumentPayload,
    db: Session = Depends(get_db),
):
    repo = FuhrparkAusgehendesDokumentRepository(db)
    row = repo.create(payload.model_dump())
    return _to_dict(row)


@router.patch("/ausgehende-dokumente/{dokument_id}", response_model=dict, summary="Ausgehendes dokument aktualisieren")
async def update_ausgehendes_dokument(
    dokument_id: str,
    payload: FuhrparkAusgehendesDokumentPayload,
    db: Session = Depends(get_db),
):
    repo = FuhrparkAusgehendesDokumentRepository(db)
    existing = repo.get_by_id(dokument_id)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Ausgehendes Dokument {dokument_id} not found")
    updated = repo.update(dokument_id, payload.model_dump())
    return _to_dict(updated)


@router.delete("/ausgehende-dokumente/{dokument_id}", status_code=204, response_class=Response, response_model=None, summary="Ausgehendes dokument löschen")
async def delete_ausgehendes_dokument(dokument_id: str, db: Session = Depends(get_db)):
    repo = FuhrparkAusgehendesDokumentRepository(db)
    if not repo.delete(dokument_id):
        raise HTTPException(status_code=404, detail=f"Ausgehendes Dokument {dokument_id} not found")
