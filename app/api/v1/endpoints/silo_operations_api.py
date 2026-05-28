from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.operations.models import SiloBewegungDB, SiloZelleDB

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.base import CompatFlexOut


router = APIRouter(prefix="/silo", tags=["silo-operations"])


class SiloZelleCreateRequest(BaseModel):
    tenant_id: str
    bezeichnung: str
    kapazitaet_t: float


class EinlagerungRequest(BaseModel):
    tenant_id: str
    silo_id: str
    menge_t: float
    sorte: str
    beleg_nr: Optional[str] = None


class AuslagerungRequest(BaseModel):
    tenant_id: str
    silo_id: str
    menge_t: float
    beleg_nr: Optional[str] = None


def _zelle_to_dict(row: SiloZelleDB) -> dict:
    return {
        "silo_id": row.silo_id,
        "tenant_id": row.tenant_id,
        "bezeichnung": row.bezeichnung,
        "kapazitaet_t": float(row.kapazitaet_t),
        "bestand_t": float(row.bestand_t),
        "sorte": row.sorte,
        "gesperrt": row.gesperrt,
    }


@router.post("/zellen", status_code=201, summary="Silo zelle anlegen",
    response_model=CompatFlexOut
)
def create_silo_zelle(req: SiloZelleCreateRequest, db: Session = Depends(get_db)):
    row = SiloZelleDB(
        silo_id=str(uuid.uuid4()),
        tenant_id=req.tenant_id,
        bezeichnung=req.bezeichnung,
        kapazitaet_t=req.kapazitaet_t,
        bestand_t=0,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _zelle_to_dict(row)


@router.get("/zellen/{zelle_id}", summary="Silo zelle abrufen",
    response_model=CompatFlexOut
)
def get_silo_zelle(zelle_id: str, db: Session = Depends(get_db)):
    row = db.query(SiloZelleDB).filter(SiloZelleDB.silo_id == zelle_id).first()
    if not row:
        raise HTTPException(404, "Silo-Zelle nicht gefunden")
    return _zelle_to_dict(row)


@router.get("/by-tenant/{tenant_id}", summary="Zellen auflisten",
    response_model=list[CompatFlexOut]
)
def list_zellen(tenant_id: str, db: Session = Depends(get_db)):
    rows = db.query(SiloZelleDB).filter(SiloZelleDB.tenant_id == tenant_id).all()
    return [_zelle_to_dict(r) for r in rows]


@router.post("/einlagern", status_code=201, summary="Einlagern",
    response_model=CompatFlexOut
)
def einlagern(req: EinlagerungRequest, db: Session = Depends(get_db)):
    zelle = db.query(SiloZelleDB).filter(
        SiloZelleDB.silo_id == req.silo_id,
        SiloZelleDB.tenant_id == req.tenant_id,
    ).first()
    if not zelle:
        raise HTTPException(404, "Silo-Zelle nicht gefunden")
    if zelle.gesperrt:
        raise HTTPException(422, "Silo-Zelle ist gesperrt")
    if float(zelle.bestand_t) + req.menge_t > float(zelle.kapazitaet_t):
        raise HTTPException(422, "Kapazität überschritten")
    bewegung = SiloBewegungDB(
        bewegung_id=str(uuid.uuid4()),
        silo_id=req.silo_id,
        typ="einlagerung",
        menge_t=req.menge_t,
        sorte=req.sorte,
        beleg_nr=req.beleg_nr,
    )
    zelle.bestand_t = float(zelle.bestand_t) + req.menge_t
    zelle.sorte = req.sorte
    db.add(bewegung)
    db.commit()
    db.refresh(bewegung)
    return {"bewegung_id": bewegung.bewegung_id, "typ": "einlagerung", "menge_t": req.menge_t, "silo_id": req.silo_id}


@router.post("/auslagern", status_code=201, summary="Auslagern",
    response_model=CompatFlexOut
)
def auslagern(req: AuslagerungRequest, db: Session = Depends(get_db)):
    zelle = db.query(SiloZelleDB).filter(
        SiloZelleDB.silo_id == req.silo_id,
        SiloZelleDB.tenant_id == req.tenant_id,
    ).first()
    if not zelle:
        raise HTTPException(404, "Silo-Zelle nicht gefunden")
    if float(zelle.bestand_t) < req.menge_t:
        raise HTTPException(422, "Nicht genügend Bestand für Auslagerung")
    bewegung = SiloBewegungDB(
        bewegung_id=str(uuid.uuid4()),
        silo_id=req.silo_id,
        typ="auslagerung",
        menge_t=req.menge_t,
        beleg_nr=req.beleg_nr,
    )
    zelle.bestand_t = float(zelle.bestand_t) - req.menge_t
    db.add(bewegung)
    db.commit()
    db.refresh(bewegung)
    return {"bewegung_id": bewegung.bewegung_id, "typ": "auslagerung", "menge_t": req.menge_t, "silo_id": req.silo_id}


@router.get("/bestand/{tenant_id}", summary="Bestand abrufen",
    response_model=CompatFlexOut
)
def get_bestand(tenant_id: str, db: Session = Depends(get_db)):
    rows = db.query(SiloZelleDB).filter(SiloZelleDB.tenant_id == tenant_id).all()
    gesamtbestand = sum(float(r.bestand_t) for r in rows)
    return {"tenant_id": tenant_id, "gesamtbestand_t": gesamtbestand, "zellen": len(rows), "schema_version": 1}
