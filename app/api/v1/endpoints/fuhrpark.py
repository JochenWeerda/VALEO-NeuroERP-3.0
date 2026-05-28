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

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.fuhrpark_schemas import (
    DruckerSetupPayload,
    FuhrparkAusgehendesDokumentPayload,
    FuhrparkFahrzeugPayload,
    FuhrparkOut,
    FuhrparkRechnungPayload,
    FuhrparkTerminartPayload,
    UnfallAnzeigePayload,
)
from pydantic import ConfigDict as _ConfigDict

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

@router.get("/fahrzeuge", response_model=list[FuhrparkOut], summary="Fahrzeuge auflisten")
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


@router.get("/fahrzeuge/{fahrzeug_id}", response_model=FuhrparkOut, summary="Fahrzeug abrufen")
async def get_fahrzeug(fahrzeug_id: str, db: Session = Depends(get_db)):
    repo = FahrzeugRepository(db)
    fahrzeug = repo.get_by_id(fahrzeug_id)
    if not fahrzeug:
        raise HTTPException(status_code=404, detail=f"Fahrzeug {fahrzeug_id} not found")
    return _to_dict(fahrzeug)


@router.post("/fahrzeuge", response_model=FuhrparkOut, status_code=201, summary="Fahrzeug anlegen")
async def create_fahrzeug(payload: FuhrparkFahrzeugPayload, db: Session = Depends(get_db)):
    repo = FahrzeugRepository(db)
    existing = repo.get_by_kennzeichen(payload.kennzeichen)
    if existing:
        raise HTTPException(status_code=409, detail="Kennzeichen already exists")
    fahrzeug = repo.create(payload.model_dump(exclude_none=True))
    return _to_dict(fahrzeug)


@router.patch("/fahrzeuge/{fahrzeug_id}", response_model=FuhrparkOut, summary="Fahrzeug aktualisieren")
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


@router.post("/fahrzeuge/{fahrzeug_id}/drucker-einrichten", response_model=FuhrparkOut, summary="Fahrzeug printer setup")
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


@router.post("/fahrzeuge/{fahrzeug_id}/drucken", response_model=FuhrparkOut, summary="Fahrzeugakte drucken")
async def print_fahrzeugakte(fahrzeug_id: str, db: Session = Depends(get_db)):
    repo = FahrzeugRepository(db)
    fahrzeug = repo.get_by_id(fahrzeug_id)
    if not fahrzeug:
        raise HTTPException(status_code=404, detail=f"Fahrzeug {fahrzeug_id} not found")
    return {"ok": True, "fahrzeug_id": fahrzeug_id, "aktion": "fahrzeugakte_gedruckt"}


@router.post("/fahrzeuge/{fahrzeug_id}/unfall-anzeige", response_model=FuhrparkOut, summary="Unfall anzeige anlegen")
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


@router.get("/terminarten", response_model=list[FuhrparkOut], summary="Terminarten auflisten")
async def list_terminarten(db: Session = Depends(get_db)):
    repo = FuhrparkTerminartRepository(db)
    return [_to_dict(row) for row in repo.get_all()]


@router.post("/terminarten", response_model=FuhrparkOut, status_code=201, summary="Terminart anlegen")
async def create_terminart(payload: FuhrparkTerminartPayload, db: Session = Depends(get_db)):
    repo = FuhrparkTerminartRepository(db)
    duplicate = repo.get_by_name(payload.terminart)
    if duplicate:
        raise HTTPException(status_code=409, detail="Terminart already exists")
    row = repo.create(payload.model_dump())
    return _to_dict(row)


@router.patch("/terminarten/{terminart_id}", response_model=FuhrparkOut, summary="Terminart aktualisieren")
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


@router.get("/rechnungen", response_model=list[FuhrparkOut], summary="Rechnungen auflisten")
async def list_rechnungen(
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    repo = FuhrparkRechnungRepository(db)
    return [_to_dict(row) for row in repo.get_all(skip=skip, limit=limit)]


@router.post("/rechnungen", response_model=FuhrparkOut, status_code=201, summary="Rechnung anlegen")
async def create_rechnung(payload: FuhrparkRechnungPayload, db: Session = Depends(get_db)):
    repo = FuhrparkRechnungRepository(db)
    duplicate = repo.get_by_rechnungs_nr(payload.rechnungs_nr)
    if duplicate:
        raise HTTPException(status_code=409, detail="Rechnungsnummer already exists")
    row = repo.create(payload.model_dump())
    return _to_dict(row)


@router.patch("/rechnungen/{rechnung_id}", response_model=FuhrparkOut, summary="Rechnung aktualisieren")
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


@router.get("/ausgehende-dokumente", response_model=list[FuhrparkOut], summary="Ausgehende dokumente auflisten")
async def list_ausgehende_dokumente(
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    repo = FuhrparkAusgehendesDokumentRepository(db)
    return [_to_dict(row) for row in repo.get_all(skip=skip, limit=limit)]


@router.post("/ausgehende-dokumente", response_model=FuhrparkOut, status_code=201, summary="Ausgehendes dokument anlegen")
async def create_ausgehendes_dokument(
    payload: FuhrparkAusgehendesDokumentPayload,
    db: Session = Depends(get_db),
):
    repo = FuhrparkAusgehendesDokumentRepository(db)
    row = repo.create(payload.model_dump())
    return _to_dict(row)


@router.patch("/ausgehende-dokumente/{dokument_id}", response_model=FuhrparkOut, summary="Ausgehendes dokument aktualisieren")
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
