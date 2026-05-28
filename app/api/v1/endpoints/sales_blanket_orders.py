"""Rahmenaufträge / Abrufe (Blanket Orders) — thin-router, sqlalchemy.text()."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....core.tenant import get_tenant_id

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.base import CompatFlexOut


router = APIRouter()


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class BlanketOrderCreate(BaseModel):
    customer_id: str = Field(..., min_length=1)
    article_id: str = Field(..., min_length=1)
    total_quantity: float = Field(..., gt=0)
    unit_price: float = Field(..., ge=0)
    valid_from: datetime
    valid_to: datetime


class BlanketOrderUpdate(BaseModel):
    unit_price: Optional[float] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None


class BlanketOrderOut(BaseModel):
    id: str
    tenant_id: str
    customer_id: str
    article_id: str
    total_quantity: float
    unit_price: float
    valid_from: datetime
    valid_to: datetime
    status: str
    created_at: Optional[datetime] = None


class ReleaseCreate(BaseModel):
    quantity: float = Field(..., gt=0)
    requested_delivery_date: datetime


class ReleaseOut(BaseModel):
    id: str
    blanket_order_id: str
    release_quantity: float
    release_date: datetime
    sales_order_ref: Optional[str] = None
    status: str


class RemainingOut(BaseModel):
    blanket_order_id: str
    total_quantity: float
    released_quantity: float
    remaining_quantity: float
    unit_price: float
    remaining_amount: float


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_blanket_order(db: Session, order_id: str, tenant_id: str) -> dict:
    row = db.execute(
        text(
            """
            SELECT * FROM domain_sales.blanket_orders
            WHERE id = :id AND tenant_id = :tenant_id
            """
        ),
        {"id": order_id, "tenant_id": tenant_id},
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Rahmenauftrag nicht gefunden")
    return dict(row)


def _released_total(db: Session, blanket_order_id: str, tenant_id: str) -> float:
    val = db.execute(
        text(
            """
            SELECT COALESCE(SUM(release_quantity), 0)
            FROM domain_sales.blanket_order_releases
            WHERE blanket_order_id = :bid AND tenant_id = :tid
              AND status != 'STORNIERT'
            """
        ),
        {"bid": blanket_order_id, "tid": tenant_id},
    ).scalar()
    return float(val or 0)


def _row_to_blanket(row: dict) -> BlanketOrderOut:
    return BlanketOrderOut(
        id=str(row["id"]),
        tenant_id=str(row["tenant_id"]),
        customer_id=str(row["customer_id"]),
        article_id=str(row["article_id"]),
        total_quantity=float(row["total_quantity"]),
        unit_price=float(row["unit_price"]),
        valid_from=row["valid_from"],
        valid_to=row["valid_to"],
        status=str(row["status"]),
        created_at=row.get("created_at"),
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/", response_model=list[BlanketOrderOut], summary="Blanket orders auflisten")
async def list_blanket_orders(
    customer_id: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=200),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    where = ["tenant_id = :tenant_id"]
    params: dict = {"tenant_id": tenant_id, "skip": skip, "limit": limit}
    if customer_id:
        where.append("customer_id = :customer_id")
        params["customer_id"] = customer_id
    if status_filter:
        where.append("status = :status")
        params["status"] = status_filter
    where_sql = " AND ".join(where)
    try:
        rows = db.execute(
            text(
                f"SELECT * FROM domain_sales.blanket_orders WHERE {where_sql} "
                "ORDER BY created_at DESC OFFSET :skip LIMIT :limit"
            ),
            params,
        ).mappings().all()
    except Exception:
        raise HTTPException(status_code=503, detail="Datenbankfehler")
    return [_row_to_blanket(dict(r)) for r in rows]


@router.post("/", response_model=BlanketOrderOut, status_code=status.HTTP_201_CREATED, summary="Blanket order anlegen")
async def create_blanket_order(
    payload: BlanketOrderCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    oid = str(uuid4())
    try:
        db.execute(
            text(
                """
                INSERT INTO domain_sales.blanket_orders
                  (id, tenant_id, customer_id, article_id, total_quantity, unit_price,
                   valid_from, valid_to, status, created_at)
                VALUES
                  (:id, :tenant_id, :customer_id, :article_id, :total_quantity, :unit_price,
                   :valid_from, :valid_to, 'AKTIV', :now)
                """
            ),
            {
                "id": oid,
                "tenant_id": tenant_id,
                "customer_id": payload.customer_id,
                "article_id": payload.article_id,
                "total_quantity": payload.total_quantity,
                "unit_price": payload.unit_price,
                "valid_from": payload.valid_from,
                "valid_to": payload.valid_to,
                "now": now,
            },
        )
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="Datenbankfehler")
    return _row_to_blanket(_get_blanket_order(db, oid, tenant_id))


@router.get("/{order_id}", response_model=CompatFlexOut, summary="Blanket order abrufen")
async def get_blanket_order(
    order_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    row = _get_blanket_order(db, order_id, tenant_id)
    try:
        releases = db.execute(
            text(
                "SELECT * FROM domain_sales.blanket_order_releases "
                "WHERE blanket_order_id = :bid AND tenant_id = :tid ORDER BY release_date"
            ),
            {"bid": order_id, "tid": tenant_id},
        ).mappings().all()
    except Exception:
        raise HTTPException(status_code=503, detail="Datenbankfehler")
    return {
        **_row_to_blanket(row).model_dump(),
        "releases": [dict(r) for r in releases],
    }


@router.patch("/{order_id}", response_model=BlanketOrderOut, summary="Blanket order aktualisieren")
async def update_blanket_order(
    order_id: str,
    payload: BlanketOrderUpdate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    row = _get_blanket_order(db, order_id, tenant_id)
    if row["status"] != "AKTIV":
        raise HTTPException(status_code=422, detail="Nur AKTIV-Rahmenaufträge können geändert werden")
    data = payload.model_dump(exclude_unset=True)
    if not data:
        return _row_to_blanket(row)
    sets = ", ".join(f"{k} = :{k}" for k in data)
    data["id"] = order_id
    data["tenant_id"] = tenant_id
    try:
        db.execute(
            text(f"UPDATE domain_sales.blanket_orders SET {sets} WHERE id = :id AND tenant_id = :tenant_id"),  # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
            data,
        )
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="Datenbankfehler")
    return _row_to_blanket(_get_blanket_order(db, order_id, tenant_id))


@router.post("/{order_id}/release", response_model=ReleaseOut, status_code=status.HTTP_201_CREATED, summary="Release anlegen")
async def create_release(
    order_id: str,
    payload: ReleaseCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    row = _get_blanket_order(db, order_id, tenant_id)
    if row["status"] != "AKTIV":
        raise HTTPException(status_code=422, detail="Rahmenauftrag ist nicht aktiv")

    already_released = _released_total(db, order_id, tenant_id)
    total_qty = float(row["total_quantity"])
    if payload.quantity > (total_qty - already_released):
        raise HTTPException(
            status_code=422,
            detail=f"Abrufmenge {payload.quantity} überschreitet Restmenge {total_qty - already_released:.2f}",
        )

    rid = str(uuid4())
    now = datetime.now(timezone.utc)
    try:
        db.execute(
            text(
                """
                INSERT INTO domain_sales.blanket_order_releases
                  (id, blanket_order_id, release_quantity, release_date, sales_order_ref, status, tenant_id)
                VALUES
                  (:id, :bid, :qty, :date, NULL, 'OFFEN', :tid)
                """
            ),
            {"id": rid, "bid": order_id, "qty": payload.quantity, "date": payload.requested_delivery_date, "tid": tenant_id},
        )
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="Datenbankfehler")

    rel_row = db.execute(
        text("SELECT * FROM domain_sales.blanket_order_releases WHERE id = :id AND tenant_id = :tid"),
        {"id": rid, "tid": tenant_id},
    ).mappings().first()
    r = dict(rel_row)
    return ReleaseOut(
        id=str(r["id"]),
        blanket_order_id=str(r["blanket_order_id"]),
        release_quantity=float(r["release_quantity"]),
        release_date=r["release_date"],
        sales_order_ref=r.get("sales_order_ref"),
        status=str(r["status"]),
    )


@router.get("/{order_id}/remaining", response_model=RemainingOut, summary="Remaining abrufen")
async def get_remaining(
    order_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    row = _get_blanket_order(db, order_id, tenant_id)
    released = _released_total(db, order_id, tenant_id)
    total = float(row["total_quantity"])
    remaining = total - released
    unit_price = float(row["unit_price"])
    return RemainingOut(
        blanket_order_id=order_id,
        total_quantity=total,
        released_quantity=released,
        remaining_quantity=remaining,
        unit_price=unit_price,
        remaining_amount=round(remaining * unit_price, 2),
    )


@router.post("/{order_id}/close", response_model=BlanketOrderOut, summary="Blanket order abschließen")
async def close_blanket_order(
    order_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    row = _get_blanket_order(db, order_id, tenant_id)
    if row["status"] == "ABGESCHLOSSEN":
        return _row_to_blanket(row)
    if row["status"] == "STORNIERT":
        raise HTTPException(status_code=422, detail="Stornierte Rahmenaufträge können nicht abgeschlossen werden")
    try:
        db.execute(
            text(
                "UPDATE domain_sales.blanket_orders SET status = 'ABGESCHLOSSEN' "
                "WHERE id = :id AND tenant_id = :tid"
            ),
            {"id": order_id, "tid": tenant_id},
        )
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="Datenbankfehler")
    return _row_to_blanket(_get_blanket_order(db, order_id, tenant_id))
