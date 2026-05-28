"""
Price List management endpoints.
SALES-PRC-01: Preislisten und Preisfindung
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from fastapi import Response, APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.read_model_cache import cached_read_model, invalidate_tenant_prefix
from app.core.uuid7 import uuid7

logger = logging.getLogger(__name__)

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.base import CompatFlexOut


router = APIRouter(prefix="/price-lists", tags=["sales", "pricing"])

DEFAULT_TENANT = settings.DEFAULT_TENANT_ID


class PriceListItemInput(BaseModel):
    article_id: str
    article_number: Optional[str] = None
    unit_price: Decimal = Field(ge=Decimal("0"))
    min_quantity: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    max_quantity: Optional[Decimal] = None
    discount_percent: Decimal = Field(default=Decimal("0"), ge=Decimal("0"), le=Decimal("100"))
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None


class PriceListItemOut(PriceListItemInput):
    id: str
    price_list_id: str


class PriceListBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    currency: str = "EUR"
    price_list_type: str = "standard"
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    is_active: bool = True
    items: List[PriceListItemInput] = Field(default_factory=list)


class PriceListCreate(PriceListBase):
    tenant_id: Optional[str] = None


class PriceListUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    currency: Optional[str] = None
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    is_active: Optional[bool] = None
    items: Optional[List[PriceListItemInput]] = None


class PriceList(PriceListBase):
    id: str
    tenant_id: str
    item_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


def _ensure_schema(db: Session) -> None:
    db.execute(text("CREATE SCHEMA IF NOT EXISTS domain_pricing"))


@router.post("/", response_model=PriceList, status_code=201, summary="Price list anlegen")
async def create_price_list(
    payload: PriceListCreate,
    tenant_id: str = Query(DEFAULT_TENANT),
    db: Session = Depends(get_db),
):
    """Create a new price list with optional items."""
    _ensure_schema(db)
    tid = payload.tenant_id or tenant_id
    pl_id = uuid7()

    db.execute(
        text("""
            INSERT INTO domain_pricing.price_lists
            (id, tenant_id, name, description, currency, price_list_type,
             valid_from, valid_until, is_active, created_at, updated_at)
            VALUES (:id, :tid, :name, :desc, :cur, :plt,
                    :vf, :vu, :active, NOW(), NOW())
        """),
        {
            "id": pl_id, "tid": tid, "name": payload.name,
            "desc": payload.description, "cur": payload.currency,
            "plt": payload.price_list_type,
            "vf": payload.valid_from, "vu": payload.valid_until,
            "active": payload.is_active,
        },
    )

    for item in payload.items:
        item_id = uuid7()
        db.execute(
            text("""
                INSERT INTO domain_pricing.price_list_items
                (id, price_list_id, article_id, article_number, unit_price,
                 min_quantity, max_quantity, discount_percent, valid_from, valid_until)
                VALUES (:id, :plid, :aid, :anr, :up,
                        :minq, :maxq, :dp, :vf, :vu)
            """),
            {
                "id": item_id, "plid": pl_id,
                "aid": item.article_id, "anr": item.article_number,
                "up": item.unit_price, "minq": item.min_quantity,
                "maxq": item.max_quantity, "dp": item.discount_percent,
                "vf": item.valid_from, "vu": item.valid_until,
            },
        )

    db.commit()
    invalidate_tenant_prefix("price_lists", tid)
    return PriceList(
        id=pl_id, tenant_id=tid, name=payload.name,
        description=payload.description, currency=payload.currency,
        price_list_type=payload.price_list_type,
        valid_from=payload.valid_from, valid_until=payload.valid_until,
        is_active=payload.is_active, item_count=len(payload.items),
        items=payload.items,
    )


@router.get("/", response_model=List[PriceList], summary="Price lists auflisten")
@cached_read_model("price_lists", ttl=300)
async def list_price_lists(
    tenant_id: str = Query(DEFAULT_TENANT),
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """List all price lists."""
    _ensure_schema(db)
    where = ["tenant_id = :tid"]
    params: dict = {"tid": tenant_id}
    if is_active is not None:
        where.append("is_active = :active")
        params["active"] = is_active

    rows = db.execute(
        # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
        text(f"""
            SELECT id, tenant_id, name, description, currency, price_list_type,
                   valid_from, valid_until, is_active, created_at, updated_at,
                   (SELECT COUNT(*) FROM domain_pricing.price_list_items WHERE price_list_id = pl.id) AS item_count
            FROM domain_pricing.price_lists pl
            WHERE {' AND '.join(where)}
            ORDER BY name
        """),
        params,
    ).fetchall()
    return [
        PriceList(
            id=str(r[0]), tenant_id=r[1], name=r[2], description=r[3],
            currency=r[4], price_list_type=r[5],
            valid_from=r[6], valid_until=r[7], is_active=r[8],
            created_at=r[9], updated_at=r[10], item_count=r[11] or 0,
        )
        for r in rows
    ]


@router.get("/{pl_id}", response_model=PriceList, summary="Price list abrufen")
async def get_price_list(
    pl_id: str,
    db: Session = Depends(get_db),
):
    """Get price list by ID with items."""
    _ensure_schema(db)
    row = db.execute(
        text("""
            SELECT id, tenant_id, name, description, currency, price_list_type,
                   valid_from, valid_until, is_active, created_at, updated_at
            FROM domain_pricing.price_lists WHERE id = :id
        """),
        {"id": pl_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Preisliste nicht gefunden")

    items = db.execute(
        text("""
            SELECT id, price_list_id, article_id, article_number, unit_price,
                   min_quantity, max_quantity, discount_percent, valid_from, valid_until
            FROM domain_pricing.price_list_items WHERE price_list_id = :plid
            ORDER BY article_number
        """),
        {"plid": pl_id},
    ).fetchall()

    item_list = [
        PriceListItemInput(
            article_id=i[2], article_number=i[3],
            unit_price=Decimal(str(i[4])), min_quantity=Decimal(str(i[5])),
            max_quantity=Decimal(str(i[6])) if i[6] else None,
            discount_percent=Decimal(str(i[7])),
            valid_from=i[8], valid_until=i[9],
        )
        for i in items
    ]

    return PriceList(
        id=str(row[0]), tenant_id=row[1], name=row[2], description=row[3],
        currency=row[4], price_list_type=row[5],
        valid_from=row[6], valid_until=row[7], is_active=row[8],
        created_at=row[9], updated_at=row[10],
        item_count=len(item_list), items=item_list,
    )


@router.put("/{pl_id}", response_model=PriceList, summary="Price list aktualisieren")
async def update_price_list(
    pl_id: str,
    payload: PriceListUpdate,
    db: Session = Depends(get_db),
):
    """Update price list (header + items)."""
    existing = db.execute(
        text("SELECT id FROM domain_pricing.price_lists WHERE id = :id"),
        {"id": pl_id},
    ).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Preisliste nicht gefunden")

    set_parts = ["updated_at = NOW()"]
    params: dict = {"id": pl_id}
    for field in ("name", "description", "currency", "valid_from", "valid_until", "is_active"):
        val = getattr(payload, field, None)
        if val is not None:
            set_parts.append(f"{field} = :{field}")
            params[field] = val

    db.execute(
        text(f"UPDATE domain_pricing.price_lists SET {', '.join(set_parts)} WHERE id = :id"),  # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
        params,
    )

    if payload.items is not None:
        db.execute(
            text("DELETE FROM domain_pricing.price_list_items WHERE price_list_id = :plid"),
            {"plid": pl_id},
        )
        for item in payload.items:
            item_id = uuid7()
            db.execute(
                text("""
                    INSERT INTO domain_pricing.price_list_items
                    (id, price_list_id, article_id, article_number, unit_price,
                     min_quantity, max_quantity, discount_percent, valid_from, valid_until)
                    VALUES (:id, :plid, :aid, :anr, :up, :minq, :maxq, :dp, :vf, :vu)
                """),
                {
                    "id": item_id, "plid": pl_id,
                    "aid": item.article_id, "anr": item.article_number,
                    "up": item.unit_price, "minq": item.min_quantity,
                    "maxq": item.max_quantity, "dp": item.discount_percent,
                    "vf": item.valid_from, "vu": item.valid_until,
                },
            )

    db.commit()
    return await get_price_list(pl_id, db)


@router.delete("/{pl_id}", status_code=204, response_class=Response, response_model=None, summary="Price list löschen")
async def delete_price_list(pl_id: str, db: Session = Depends(get_db)):
    """Delete price list and its items."""
    existing = db.execute(
        text("SELECT id FROM domain_pricing.price_lists WHERE id = :id"),
        {"id": pl_id},
    ).fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Preisliste nicht gefunden")
    db.execute(text("DELETE FROM domain_pricing.price_list_items WHERE price_list_id = :id"), {"id": pl_id})
    db.execute(text("DELETE FROM domain_pricing.price_lists WHERE id = :id"), {"id": pl_id})
    db.commit()
