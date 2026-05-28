"""
Verträge API - Rahmenverträge (SQLAlchemy)
"""

from datetime import datetime
from typing import Optional
from fastapi import Response, APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.operations.repository import RahmenvertragRepository

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.base import CompatFlexOut


router = APIRouter(prefix="/vertrag", tags=["Verträge"])


class VertragCreate(BaseModel):
    nummer: str
    partner: str
    partner_id: str
    typ: str
    artikel: str
    artikel_id: str
    menge: float = Field(..., ge=0)
    restmenge: float = Field(..., ge=0)
    preis: float = Field(..., ge=0)
    laufzeit_bis: str
    status: str = "aktiv"


class VertragUpdate(BaseModel):
    partner: Optional[str] = None
    partner_id: Optional[str] = None
    typ: Optional[str] = None
    artikel: Optional[str] = None
    artikel_id: Optional[str] = None
    menge: Optional[float] = Field(None, ge=0)
    restmenge: Optional[float] = Field(None, ge=0)
    preis: Optional[float] = Field(None, ge=0)
    laufzeit_bis: Optional[str] = None
    status: Optional[str] = None


def _to_dict(vertrag) -> dict:
    return {
        "id": vertrag.id,
        "nummer": vertrag.nummer,
        "partner": vertrag.partner,
        "partnerId": vertrag.partner_id,
        "typ": vertrag.typ,
        "artikel": vertrag.artikel,
        "artikelId": vertrag.artikel_id,
        "menge": float(vertrag.menge),
        "restmenge": float(vertrag.restmenge),
        "preis": float(vertrag.preis),
        "laufzeitBis": vertrag.laufzeit_bis.date().isoformat() if vertrag.laufzeit_bis else None,
        "status": vertrag.status,
        "createdAt": vertrag.created_at.isoformat() if vertrag.created_at else None,
        "updatedAt": vertrag.updated_at.isoformat() if vertrag.updated_at else None,
    }


@router.get("/rahmenvertraege", response_model=CompatFlexOut, summary="Rahmenvertraege auflisten")
async def list_rahmenvertraege(
    status: Optional[str] = Query(None, description="Filter by status"),
    typ: Optional[str] = Query(None, description="Filter by type"),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> dict:
    repo = RahmenvertragRepository(db)
    items = repo.get_all(limit=limit, status=status, typ=typ)
    gesamt_menge = sum(float(v.menge) for v in items)
    rest_menge = sum(float(v.restmenge) for v in items)
    return {
        "items": [_to_dict(v) for v in items],
        "total": len(items),
        "menge_gesamt": gesamt_menge,
        "menge_rest": rest_menge,
    }


@router.get("/rahmenvertraege/{vertrag_id}", response_model=CompatFlexOut, summary="Rahmenvertrag abrufen")
async def get_rahmenvertrag(vertrag_id: str, db: Session = Depends(get_db)) -> dict:
    repo = RahmenvertragRepository(db)
    vertrag = repo.get_by_id(vertrag_id)
    if not vertrag:
        raise HTTPException(status_code=404, detail="Rahmenvertrag not found")
    return _to_dict(vertrag)


@router.post("/rahmenvertraege", response_model=CompatFlexOut, status_code=201, summary="Rahmenvertrag anlegen")
async def create_rahmenvertrag(data: VertragCreate, db: Session = Depends(get_db)) -> dict:
    repo = RahmenvertragRepository(db)
    if repo.get_by_nummer(data.nummer):
        raise HTTPException(status_code=409, detail="Vertragsnummer already exists")

    payload = data.model_dump()
    payload["laufzeit_bis"] = datetime.fromisoformat(payload["laufzeit_bis"])
    vertrag = repo.create(payload)
    return _to_dict(vertrag)


@router.patch("/rahmenvertraege/{vertrag_id}", response_model=CompatFlexOut, summary="Rahmenvertrag aktualisieren")
async def update_rahmenvertrag(vertrag_id: str, data: VertragUpdate, db: Session = Depends(get_db)) -> dict:
    repo = RahmenvertragRepository(db)
    payload = data.model_dump(exclude_unset=True)
    if "laufzeit_bis" in payload and payload["laufzeit_bis"]:
        payload["laufzeit_bis"] = datetime.fromisoformat(payload["laufzeit_bis"])
    vertrag = repo.update(vertrag_id, payload)
    if not vertrag:
        raise HTTPException(status_code=404, detail="Rahmenvertrag not found")
    return _to_dict(vertrag)


@router.delete("/rahmenvertraege/{vertrag_id}", status_code=204, response_class=Response, response_model=None, summary="Rahmenvertrag löschen")
async def delete_rahmenvertrag(vertrag_id: str, db: Session = Depends(get_db)):
    repo = RahmenvertragRepository(db)
    if not repo.delete(vertrag_id):
        raise HTTPException(status_code=404, detail="Rahmenvertrag not found")
