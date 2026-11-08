"""
Strecke – Speditionen / Frachttarife nach PLZ
Full CRUD for freight price table.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from fastapi import Response, APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.inspection import inspect as sa_inspect
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.domains.operations.repository import SpeditionFrachttarifRepository

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.strecke_speditionen_schemas import StreckeSpeditionenOut
from app.auth.bereich_roles import SCHREIBEN  # Schreibrecht je Bereich (WRITE-ROLES)


router = APIRouter(prefix="/strecke/speditionen", tags=["Strecke - Speditionen"])


def _serialize_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def _to_dict(model: Any) -> dict:
    mapper = sa_inspect(model.__class__)
    return {col.key: _serialize_value(getattr(model, col.key)) for col in mapper.columns}


class FrachttarifPayload(BaseModel):
    plz_von: str = Field(..., min_length=1, max_length=10)
    plz_bis: str = Field(..., min_length=1, max_length=10)
    spediteur: str = Field(..., min_length=2, max_length=255)
    preis_eur_t: float = Field(..., ge=0)
    aktiv: bool = True
    notiz: Optional[str] = None


@router.get("/frachttarife", response_model=list[StreckeSpeditionenOut], summary="Frachttarife auflisten")
async def list_frachttarife(
    skip: int = Query(0, ge=0),
    limit: int = Query(500, ge=1, le=2000),
    aktiv_only: bool = Query(False),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    repo = SpeditionFrachttarifRepository(db, tenant_id)
    return [_to_dict(row) for row in repo.get_all(skip=skip, limit=limit, aktiv_only=aktiv_only)]


@router.get("/frachttarife/{tarif_id}", response_model=StreckeSpeditionenOut, summary="Frachttarif abrufen")
async def get_frachttarif(tarif_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    repo = SpeditionFrachttarifRepository(db, tenant_id)
    row = repo.get_by_id(tarif_id)
    if not row:
        raise HTTPException(status_code=404, detail=f"Frachttarif {tarif_id} not found")
    return _to_dict(row)


@router.post("/frachttarife", response_model=StreckeSpeditionenOut, status_code=201, summary="Frachttarif anlegen", dependencies=SCHREIBEN["LOGISTIK"])
async def create_frachttarif(payload: FrachttarifPayload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    repo = SpeditionFrachttarifRepository(db, tenant_id)
    row = repo.create(payload.model_dump())
    return _to_dict(row)


@router.patch("/frachttarife/{tarif_id}", response_model=StreckeSpeditionenOut, summary="Frachttarif aktualisieren", dependencies=SCHREIBEN["LOGISTIK"])
async def update_frachttarif(
    tarif_id: str,
    payload: FrachttarifPayload,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    repo = SpeditionFrachttarifRepository(db, tenant_id)
    existing = repo.get_by_id(tarif_id)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Frachttarif {tarif_id} not found")
    updated = repo.update(tarif_id, payload.model_dump())
    return _to_dict(updated)


@router.delete("/frachttarife/{tarif_id}", status_code=204, response_class=Response, response_model=None, summary="Frachttarif löschen", dependencies=SCHREIBEN["LOGISTIK"])
async def delete_frachttarif(tarif_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    repo = SpeditionFrachttarifRepository(db, tenant_id)
    if not repo.delete(tarif_id):
        raise HTTPException(status_code=404, detail=f"Frachttarif {tarif_id} not found")
