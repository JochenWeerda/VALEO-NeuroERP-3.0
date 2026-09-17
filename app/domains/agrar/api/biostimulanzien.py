"""Biostimulanzien-Stammdaten — Liste und Kopf fuer die Agrar-Maske."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import ConfigDict
from sqlalchemy import desc, or_
from sqlalchemy.orm import Session

from ....api.v1.schemas.agrar import Biostimulanz, BiostimulanzCreate, BiostimulanzUpdate
from ....api.v1.schemas.base import BaseSchema
from ....core.config import settings
from ....core.database import get_db
from ....infrastructure.models import Biostimulanz as BiostimulanzModel


class BiostimulanzListOut(BaseSchema):
    model_config = ConfigDict(extra="allow")
    items: list[dict[str, Any]]
    total: int
    page: int
    pages: int
    size: int
    has_next: bool
    has_prev: bool

router = APIRouter()

DEFAULT_TENANT = settings.DEFAULT_TENANT_ID


def _item_dict(row: BiostimulanzModel) -> dict[str, Any]:
    bestand = float(row.lagerbestand or 0)
    ablauf = row.ablauf_zulassung.isoformat() if row.ablauf_zulassung else None
    return {
        "id": row.id,
        "artikelnummer": row.artikelnummer,
        "name": row.name,
        "typ": row.typ,
        "hersteller": row.hersteller,
        "eu_zulassung": row.eu_zulassung,
        "ablauf_zulassung": ablauf,
        "vk_preis": float(row.vk_preis) if row.vk_preis is not None else None,
        "ek_preis": float(row.ek_preis) if row.ek_preis is not None else None,
        "lagerbestand": bestand,
        "verfuegbar": bestand,
        "ist_aktiv": bool(row.ist_aktiv),
        "tenant_id": row.tenant_id,
        "dosierung": row.dosierung,
        "waehrung": row.waehrung or "EUR",
    }


@router.get("", response_model=BiostimulanzListOut, summary="Biostimulanzien auflisten")
@router.get("/", response_model=BiostimulanzListOut, summary="Biostimulanzien auflisten", include_in_schema=False)
async def list_biostimulanzien(
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    search: Optional[str] = Query(None, description="Suche in Name, Artikelnummer, Hersteller"),
    typ: Optional[str] = Query(None, description="Filter nach Typ"),
    ist_aktiv: Optional[bool] = Query(None, description="Filter nach Aktiv-Status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=200),
    db: Session = Depends(get_db),
):
    effective_tenant = tenant_id or DEFAULT_TENANT
    query = db.query(BiostimulanzModel).filter(BiostimulanzModel.tenant_id == effective_tenant)
    if ist_aktiv is not None:
        query = query.filter(BiostimulanzModel.ist_aktiv == ist_aktiv)
    if typ:
        query = query.filter(BiostimulanzModel.typ == typ)
    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(
                BiostimulanzModel.name.ilike(like),
                BiostimulanzModel.artikelnummer.ilike(like),
                BiostimulanzModel.hersteller.ilike(like),
            )
        )
    total = query.count()
    items = query.order_by(desc(BiostimulanzModel.created_at)).offset(skip).limit(limit).all()
    page = (skip // limit) + 1
    pages = (total + limit - 1) // limit if total else 1
    return {
        "items": [_item_dict(item) for item in items],
        "total": total,
        "page": page,
        "pages": pages,
        "size": limit,
        "has_next": (skip + limit) < total,
        "has_prev": skip > 0,
    }


@router.get("/search", response_model=list[Biostimulanz], summary="Biostimulanzien suchen")
async def search_biostimulanzien(
    q: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=50),
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    effective_tenant = tenant_id or DEFAULT_TENANT
    like = f"%{q}%"
    rows = (
        db.query(BiostimulanzModel)
        .filter(BiostimulanzModel.ist_aktiv.is_(True))
        .filter(BiostimulanzModel.tenant_id == effective_tenant)
        .filter(
            or_(
                BiostimulanzModel.name.ilike(like),
                BiostimulanzModel.artikelnummer.ilike(like),
                BiostimulanzModel.hersteller.ilike(like),
            )
        )
        .order_by(BiostimulanzModel.name.asc())
        .limit(limit)
        .all()
    )
    return [Biostimulanz.model_validate(item) for item in rows]


@router.get("/{item_id}", summary="Biostimulanz abrufen")
async def get_biostimulanz(
    item_id: str,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    effective_tenant = tenant_id or DEFAULT_TENANT
    row = (
        db.query(BiostimulanzModel)
        .filter(BiostimulanzModel.id == item_id, BiostimulanzModel.tenant_id == effective_tenant)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Biostimulanz nicht gefunden")
    return _item_dict(row)


@router.post("", response_model=Biostimulanz, status_code=201, summary="Biostimulanz anlegen")
@router.post("/", response_model=Biostimulanz, status_code=201, summary="Biostimulanz anlegen", include_in_schema=False)
async def create_biostimulanz(
    body: BiostimulanzCreate,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    effective_tenant = tenant_id or body.tenant_id or DEFAULT_TENANT
    existing = (
        db.query(BiostimulanzModel)
        .filter(
            BiostimulanzModel.artikelnummer == body.artikelnummer,
            BiostimulanzModel.tenant_id == effective_tenant,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Biostimulanz mit Artikelnummer {body.artikelnummer} existiert bereits",
        )
    payload = body.model_dump(exclude={"tenant_id"})
    row = BiostimulanzModel(tenant_id=effective_tenant, **payload)
    db.add(row)
    db.commit()
    db.refresh(row)
    return Biostimulanz.model_validate(row)


@router.patch("/{item_id}", response_model=Biostimulanz, summary="Biostimulanz aktualisieren")
async def update_biostimulanz(
    item_id: str,
    body: BiostimulanzUpdate,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    effective_tenant = tenant_id or DEFAULT_TENANT
    row = (
        db.query(BiostimulanzModel)
        .filter(BiostimulanzModel.id == item_id, BiostimulanzModel.tenant_id == effective_tenant)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Biostimulanz nicht gefunden")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(row, key, value)
    row.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(row)
    return Biostimulanz.model_validate(row)
