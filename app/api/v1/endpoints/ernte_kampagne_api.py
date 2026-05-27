from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.ernte_kampagne import ErnteArt
from app.domains.operations.models import ErnteKampagneDB

router = APIRouter(prefix="/ernte-kampagnen", tags=["ernte-kampagnen"])


class SchlagErntezielRequest(BaseModel):
    schlag_id: str
    sorte: str
    flaeche_ha: float
    ziel_ertrag_t_ha: float


class ErnteKampagneCreateRequest(BaseModel):
    tenant_id: str
    wirtschaftsjahr: int
    ernte_art: str
    bezeichnung: str
    schlag_ziele: list[SchlagErntezielRequest] = Field(default_factory=list)


def _to_dict(row: ErnteKampagneDB) -> dict:
    return {
        "kampagne_id": row.kampagne_id,
        "tenant_id": row.tenant_id,
        "wirtschaftsjahr": row.wirtschaftsjahr,
        "ernte_art": row.ernte_art,
        "bezeichnung": row.bezeichnung,
        "status": row.status,
        "schlag_ziele": row.schlag_ziele or [],
        "erstellt_am": row.erstellt_am.isoformat() if row.erstellt_am else None,
    }


@router.post("", status_code=201, summary="Kampagne anlegen")
def create_kampagne(req: ErnteKampagneCreateRequest, db: Session = Depends(get_db)):
    ErnteArt(req.ernte_art)  # validate enum value
    row = ErnteKampagneDB(
        kampagne_id=str(uuid.uuid4()),
        tenant_id=req.tenant_id,
        wirtschaftsjahr=req.wirtschaftsjahr,
        ernte_art=req.ernte_art,
        bezeichnung=req.bezeichnung,
        status="geplant",
        schlag_ziele=[z.model_dump() for z in req.schlag_ziele],
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _to_dict(row)


@router.get("/tenant/{tenant_id}", summary="Kampagnen abrufen")
def get_kampagnen(tenant_id: str, wirtschaftsjahr: Optional[int] = None, db: Session = Depends(get_db)):
    q = db.query(ErnteKampagneDB).filter(ErnteKampagneDB.tenant_id == tenant_id)
    if wirtschaftsjahr is not None:
        q = q.filter(ErnteKampagneDB.wirtschaftsjahr == wirtschaftsjahr)
    return [_to_dict(r) for r in q.all()]


@router.get("/{kampagne_id}", summary="Kampagne abrufen")
def get_kampagne(kampagne_id: str, db: Session = Depends(get_db)):
    row = db.query(ErnteKampagneDB).filter(ErnteKampagneDB.kampagne_id == kampagne_id).first()
    if not row:
        raise HTTPException(404, "Kampagne nicht gefunden")
    return _to_dict(row)


@router.delete("/{kampagne_id}", status_code=204, response_class=Response, response_model=None, summary="Kampagne löschen")
def delete_kampagne(kampagne_id: str, db: Session = Depends(get_db)):
    row = db.query(ErnteKampagneDB).filter(ErnteKampagneDB.kampagne_id == kampagne_id).first()
    if not row:
        raise HTTPException(404, "Kampagne nicht gefunden")
    if row.status != "geplant":
        raise HTTPException(400, "Nur geplante Kampagnen können gelöscht werden")
    db.delete(row)
    db.commit()
    return Response(status_code=204)


@router.post("/{kampagne_id}/start", summary="Kampagne starten")
def start_kampagne(kampagne_id: str, db: Session = Depends(get_db)):
    row = db.query(ErnteKampagneDB).filter(ErnteKampagneDB.kampagne_id == kampagne_id).first()
    if not row:
        raise HTTPException(404, "Kampagne nicht gefunden")
    if row.status != "geplant":
        raise HTTPException(400, "Kampagne ist nicht im Status 'geplant'")
    row.status = "aktiv"
    db.commit()
    db.refresh(row)
    return _to_dict(row)


@router.post("/{kampagne_id}/abschliessen", summary="Kampagne abschliessen")
def abschliessen_kampagne(kampagne_id: str, db: Session = Depends(get_db)):
    row = db.query(ErnteKampagneDB).filter(ErnteKampagneDB.kampagne_id == kampagne_id).first()
    if not row:
        raise HTTPException(404, "Kampagne nicht gefunden")
    if row.status != "aktiv":
        raise HTTPException(400, "Kampagne ist nicht im Status 'aktiv'")
    row.status = "abgeschlossen"
    db.commit()
    db.refresh(row)
    return _to_dict(row)
