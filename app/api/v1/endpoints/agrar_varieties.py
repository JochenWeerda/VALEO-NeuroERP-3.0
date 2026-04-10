"""
Agrar Sorten/Varieties API fuer Ernte-Annahme.

Vollstaendiges CRUD gegen domain_shared.agrar_sorten.
Beim ersten Aufruf ohne Daten werden Standard-Sorten als Seed angelegt.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.uuid7 import uuid7
from app.infrastructure.models.futtermittel_models import AgrarSorte

router = APIRouter()


class VarietyIn(BaseModel):
    variety_number: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    crop_type: Optional[str] = None
    zuechter: Optional[str] = None
    zulassungsjahr: Optional[int] = None
    reifezahl: Optional[str] = None
    qualitaetsgruppe: Optional[str] = None


class VarietyOut(VarietyIn):
    id: str
    aktiv: bool = True

    class Config:
        from_attributes = True


# Standard seed data — inserted once per tenant on first list call
_STANDARD_SEED = [
    {"variety_number": "245", "name": "Weizen", "description": "Standard-Weizen", "crop_type": "WHEAT"},
    {"variety_number": "100", "name": "Mais", "description": "Standard-Mais", "crop_type": "MAIZE"},
    {"variety_number": "200", "name": "Gerste", "description": "Standard-Gerste", "crop_type": "BARLEY"},
    {"variety_number": "300", "name": "Hafer", "description": "Standard-Hafer", "crop_type": "OATS"},
    {"variety_number": "400", "name": "Raps", "description": "Standard-Raps", "crop_type": "RAPESEED"},
]


def _ensure_seed(db: Session, tenant_id: str) -> None:
    """Insert standard varieties for tenant if table is empty for that tenant."""
    count = db.query(AgrarSorte).filter(AgrarSorte.tenant_id == tenant_id).count()
    if count == 0:
        for seed in _STANDARD_SEED:
            db.add(AgrarSorte(id=uuid7(), tenant_id=tenant_id, **seed))
        db.commit()


@router.get("/", response_model=list[VarietyOut])
async def list_varieties(
    crop_type: Optional[str] = Query(None, description="Filtern nach Kulturart"),
    aktiv: bool = Query(True),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Liste der Sorten fuer Ernte-Annahme."""
    _ensure_seed(db, tenant_id)
    q = db.query(AgrarSorte).filter(AgrarSorte.tenant_id == tenant_id)
    if aktiv:
        q = q.filter(AgrarSorte.aktiv.is_(True))
    if crop_type:
        q = q.filter(AgrarSorte.crop_type == crop_type)
    return q.order_by(AgrarSorte.name).all()


@router.get("/{sorte_id}", response_model=VarietyOut)
async def get_variety(
    sorte_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Einzelne Sorte abrufen."""
    item = db.query(AgrarSorte).filter(
        and_(AgrarSorte.id == sorte_id, AgrarSorte.tenant_id == tenant_id)
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Sorte '{sorte_id}' nicht gefunden")
    return item


@router.post("/", response_model=VarietyOut, status_code=201)
async def create_variety(
    payload: VarietyIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Neue Sorte anlegen."""
    item = AgrarSorte(id=uuid7(), tenant_id=tenant_id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{sorte_id}", response_model=VarietyOut)
async def update_variety(
    sorte_id: str,
    payload: VarietyIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Sorte aktualisieren."""
    item = db.query(AgrarSorte).filter(
        and_(AgrarSorte.id == sorte_id, AgrarSorte.tenant_id == tenant_id)
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Sorte '{sorte_id}' nicht gefunden")
    for k, v in payload.model_dump().items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{sorte_id}", status_code=204)
async def delete_variety(
    sorte_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Sorte deaktivieren (soft delete)."""
    item = db.query(AgrarSorte).filter(
        and_(AgrarSorte.id == sorte_id, AgrarSorte.tenant_id == tenant_id)
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Sorte '{sorte_id}' nicht gefunden")
    item.aktiv = False
    db.commit()
    return Response(status_code=204)
