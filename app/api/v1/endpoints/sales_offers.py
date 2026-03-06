"""Domain sales offers (Angebote) CRUD endpoints."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from ....core.config import settings
from ....core.database import get_db
from ..schemas.base import PaginatedResponse

router = APIRouter()

DEFAULT_TENANT = settings.DEFAULT_TENANT_ID


class SalesOfferItemInput(BaseModel):
    article_number: str = Field(..., min_length=1, max_length=80)
    description: Optional[str] = None
    quantity: float = Field(..., ge=0)
    unit: str = "kg"
    unit_price: float = Field(..., ge=0)
    ek_price: Optional[float] = None
    discount_percent: float = Field(default=0.0, ge=0, le=100)


class SalesOfferItemOut(SalesOfferItemInput):
    id: str
    line_number: int
    line_total: float


class SalesOfferBase(BaseModel):
    offer_number: str = Field(..., min_length=1, max_length=64)
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    subject: str = Field(..., min_length=1, max_length=255)
    description: str = ""
    total_amount: float = 0.0
    currency: str = "EUR"
    status: str = "offen"
    contact_person: Optional[str] = None
    valid_until: Optional[datetime] = None
    notes: Optional[str] = None
    is_pauschale: bool = False
    items: list[SalesOfferItemInput] = Field(default_factory=list)


class SalesOfferCreate(SalesOfferBase):
    tenant_id: Optional[str] = None


class SalesOfferUpdate(BaseModel):
    offer_number: Optional[str] = None
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    subject: Optional[str] = None
    description: Optional[str] = None
    total_amount: Optional[float] = None
    currency: Optional[str] = None
    status: Optional[str] = None
    contact_person: Optional[str] = None
    valid_until: Optional[datetime] = None
    notes: Optional[str] = None
    is_pauschale: Optional[bool] = None
    items: Optional[list[SalesOfferItemInput]] = None


class SalesOffer(SalesOfferBase):
    id: str
    tenant_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    version: int = 1
    items: list[SalesOfferItemOut] = Field(default_factory=list)


def _line_total(quantity: float, unit_price: float, discount_percent: float) -> Decimal:
    qty = Decimal(str(quantity))
    price = Decimal(str(unit_price))
    discount = Decimal(str(discount_percent))
    base = qty * price
    discounted = base * (Decimal("100") - discount) / Decimal("100")
    return discounted.quantize(Decimal("0.01"))


def _fetch_items(db: Session, offer_id: str) -> list[SalesOfferItemOut]:
    rows = db.execute(
        text(
            """
            SELECT id, line_number, article_number, description,
                   quantity, unit, unit_price, ek_price, discount_percent, line_total
            FROM domain_crm.sales_offer_items
            WHERE offer_id = :offer_id
            ORDER BY line_number ASC
            """
        ),
        {"offer_id": offer_id},
    ).mappings().all()
    return [
        SalesOfferItemOut(
            id=str(row["id"]),
            line_number=int(row["line_number"]),
            article_number=str(row["article_number"]),
            description=row.get("description"),
            quantity=float(row.get("quantity") or 0),
            unit=str(row.get("unit") or "kg"),
            unit_price=float(row.get("unit_price") or 0),
            ek_price=float(row["ek_price"]) if row.get("ek_price") is not None else None,
            discount_percent=float(row.get("discount_percent") or 0),
            line_total=float(row.get("line_total") or 0),
        )
        for row in rows
    ]


def _row_to_offer(row: dict, items: Optional[list[SalesOfferItemOut]] = None) -> SalesOffer:
    return SalesOffer(
        id=str(row["id"]),
        tenant_id=str(row["tenant_id"]),
        offer_number=row["offer_number"],
        customer_id=str(row["customer_id"]) if row.get("customer_id") else None,
        customer_name=row.get("customer_name"),
        subject=row.get("subject") or "",
        description=row.get("description") or "",
        total_amount=float(row.get("total_amount") or Decimal("0")),
        currency=row.get("currency") or "EUR",
        status=row.get("status") or "offen",
        contact_person=row.get("contact_person"),
        valid_until=row.get("valid_until"),
        notes=row.get("notes"),
        is_pauschale=bool(row.get("is_pauschale") or False),
        items=items or [],
        created_at=row.get("created_at"),
        updated_at=row.get("updated_at"),
        deleted_at=row.get("deleted_at"),
        version=int(row.get("version") or 1),
    )


@router.get("/", response_model=PaginatedResponse[SalesOffer])
async def list_sales_offers(
    tenant_id: Optional[str] = Query(None),
    customer_id: Optional[str] = Query(None, description="Filter by customer ID"),
    search: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=200),
    db: Session = Depends(get_db),
):
    effective_tenant = tenant_id or DEFAULT_TENANT
    params: dict[str, object] = {
        "tenant_id": effective_tenant,
        "skip": skip,
        "limit": limit,
    }

    where = ["tenant_id = :tenant_id", "deleted_at IS NULL"]
    if customer_id:
        where.append("customer_id = :customer_id")
        params["customer_id"] = customer_id
    if search:
        where.append("(offer_number ILIKE :search OR subject ILIKE :search OR customer_name ILIKE :search)")
        params["search"] = f"%{search}%"
    if status_filter:
        where.append("status = :status")
        params["status"] = status_filter

    where_sql = " AND ".join(where)
    total = (
        db.execute(
            text(f"SELECT COUNT(*) FROM domain_crm.sales_offers WHERE {where_sql}"), params
        ).scalar()
        or 0
    )
    rows = db.execute(
        text(
            f"""
            SELECT *
            FROM domain_crm.sales_offers
            WHERE {where_sql}
            ORDER BY created_at DESC
            OFFSET :skip LIMIT :limit
            """
        ),
        params,
    ).mappings()
    offer_list = []
    for row in rows:
        row_dict = dict(row)
        offer_items = _fetch_items(db, str(row_dict["id"]))
        offer_list.append(_row_to_offer(row_dict, offer_items))

    page = (skip // limit) + 1
    pages = (total + limit - 1) // limit if total else 1
    return PaginatedResponse[SalesOffer](
        items=offer_list,
        total=int(total),
        page=page,
        size=limit,
        pages=pages,
        has_next=(skip + limit) < int(total),
        has_prev=skip > 0,
    )


@router.get("/{offer_id}", response_model=SalesOffer)
async def get_sales_offer(
    offer_id: str,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    effective_tenant = tenant_id or DEFAULT_TENANT
    row = db.execute(
        text(
            """
            SELECT *
            FROM domain_crm.sales_offers
            WHERE id = :id AND tenant_id = :tenant_id AND deleted_at IS NULL
            """
        ),
        {"id": offer_id, "tenant_id": effective_tenant},
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Sales offer not found")
    return _row_to_offer(dict(row), _fetch_items(db, offer_id))


@router.post("/", response_model=SalesOffer, status_code=status.HTTP_201_CREATED)
async def create_sales_offer(payload: SalesOfferCreate, db: Session = Depends(get_db)):
    effective_tenant = payload.tenant_id or DEFAULT_TENANT
    offer_id = str(uuid4())
    now = datetime.now(timezone.utc)

    duplicate = db.execute(
        text(
            """
            SELECT 1
            FROM domain_crm.sales_offers
            WHERE tenant_id = :tenant_id
              AND offer_number = :offer_number
              AND deleted_at IS NULL
            """
        ),
        {"tenant_id": effective_tenant, "offer_number": payload.offer_number},
    ).first()
    if duplicate:
        raise HTTPException(status_code=409, detail="offer_number already exists")

    # Compute totals from items
    computed_total = Decimal("0")
    for item in payload.items:
        computed_total += _line_total(item.quantity, item.unit_price, item.discount_percent)
    total_amount = float(computed_total) if payload.items else payload.total_amount

    db.execute(
        text(
            """
            INSERT INTO domain_crm.sales_offers
                (id, tenant_id, offer_number, customer_id, customer_name, subject, description,
                 total_amount, currency, status, contact_person, valid_until,
                 notes, is_pauschale, created_at, updated_at, version)
            VALUES
                (:id, :tenant_id, :offer_number, :customer_id, :customer_name, :subject, :description,
                 :total_amount, :currency, :status, :contact_person, :valid_until,
                 :notes, :is_pauschale, :created_at, :updated_at, 1)
            """
        ),
        {
            "id": offer_id,
            "tenant_id": effective_tenant,
            "offer_number": payload.offer_number,
            "customer_id": payload.customer_id,
            "customer_name": payload.customer_name,
            "subject": payload.subject,
            "description": payload.description,
            "total_amount": total_amount,
            "currency": payload.currency,
            "status": payload.status,
            "contact_person": payload.contact_person,
            "valid_until": payload.valid_until,
            "notes": payload.notes,
            "is_pauschale": payload.is_pauschale,
            "created_at": now,
            "updated_at": now,
        },
    )

    for idx, item in enumerate(payload.items, start=1):
        lt = _line_total(item.quantity, item.unit_price, item.discount_percent)
        db.execute(
            text(
                """
                INSERT INTO domain_crm.sales_offer_items
                    (id, tenant_id, offer_id, line_number, article_number, description,
                     quantity, unit, unit_price, ek_price, discount_percent, line_total, created_at, updated_at)
                VALUES
                    (:id, :tenant_id, :offer_id, :line_number, :article_number, :description,
                     :quantity, :unit, :unit_price, :ek_price, :discount_percent, :line_total, :now, :now)
                """
            ),
            {
                "id": str(uuid4()),
                "tenant_id": effective_tenant,
                "offer_id": offer_id,
                "line_number": idx,
                "article_number": item.article_number,
                "description": item.description,
                "quantity": item.quantity,
                "unit": item.unit,
                "unit_price": item.unit_price,
                "ek_price": item.ek_price,
                "discount_percent": item.discount_percent,
                "line_total": float(lt),
                "now": now,
            },
        )

    db.commit()
    return _row_to_offer(
        {
            "id": offer_id,
            "tenant_id": effective_tenant,
            "offer_number": payload.offer_number,
            "customer_id": payload.customer_id,
            "customer_name": payload.customer_name,
            "subject": payload.subject,
            "description": payload.description,
            "total_amount": total_amount,
            "currency": payload.currency,
            "status": payload.status,
            "contact_person": payload.contact_person,
            "valid_until": payload.valid_until,
            "notes": payload.notes,
            "is_pauschale": payload.is_pauschale,
            "created_at": now,
            "updated_at": now,
            "deleted_at": None,
            "version": 1,
        },
        _fetch_items(db, offer_id),
    )


@router.patch("/{offer_id}", response_model=SalesOffer)
async def update_sales_offer(
    offer_id: str,
    payload: SalesOfferUpdate,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    effective_tenant = tenant_id or DEFAULT_TENANT
    row = db.execute(
        text(
            """
            SELECT * FROM domain_crm.sales_offers
            WHERE id = :id AND tenant_id = :tenant_id AND deleted_at IS NULL
            """
        ),
        {"id": offer_id, "tenant_id": effective_tenant},
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Sales offer not found")

    update_data = payload.model_dump(exclude_unset=True, exclude={"items"})
    now = datetime.now(timezone.utc)

    if update_data:
        set_clauses = ", ".join(f"{k} = :{k}" for k in update_data)
        update_data["offer_id"] = offer_id
        update_data["tenant_id"] = effective_tenant
        update_data["updated_at"] = now
        db.execute(
            text(
                f"""
                UPDATE domain_crm.sales_offers
                SET {set_clauses}, updated_at = :updated_at, version = version + 1
                WHERE id = :offer_id AND tenant_id = :tenant_id
                """
            ),
            update_data,
        )

    if payload.items is not None:
        db.execute(
            text("DELETE FROM domain_crm.sales_offer_items WHERE offer_id = :offer_id"),
            {"offer_id": offer_id},
        )
        computed_total = Decimal("0")
        for idx, item in enumerate(payload.items, start=1):
            lt = _line_total(item.quantity, item.unit_price, item.discount_percent)
            computed_total += lt
            db.execute(
                text(
                    """
                    INSERT INTO domain_crm.sales_offer_items
                        (id, tenant_id, offer_id, line_number, article_number, description,
                         quantity, unit, unit_price, ek_price, discount_percent, line_total, created_at, updated_at)
                    VALUES
                        (:id, :tenant_id, :offer_id, :line_number, :article_number, :description,
                         :quantity, :unit, :unit_price, :ek_price, :discount_percent, :line_total, :now, :now)
                    """
                ),
                {
                    "id": str(uuid4()),
                    "tenant_id": effective_tenant,
                    "offer_id": offer_id,
                    "line_number": idx,
                    "article_number": item.article_number,
                    "description": item.description,
                    "quantity": item.quantity,
                    "unit": item.unit,
                    "unit_price": item.unit_price,
                    "ek_price": item.ek_price,
                    "discount_percent": item.discount_percent,
                    "line_total": float(lt),
                    "now": now,
                },
            )
        # update total_amount on the offer
        db.execute(
            text(
                """
                UPDATE domain_crm.sales_offers
                SET total_amount = :total, updated_at = :now
                WHERE id = :offer_id
                """
            ),
            {"total": float(computed_total), "now": now, "offer_id": offer_id},
        )

    db.commit()

    updated_row = db.execute(
        text("SELECT * FROM domain_crm.sales_offers WHERE id = :id"),
        {"id": offer_id},
    ).mappings().first()
    return _row_to_offer(dict(updated_row), _fetch_items(db, offer_id))


@router.delete("/{offer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sales_offer(
    offer_id: str,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    effective_tenant = tenant_id or DEFAULT_TENANT
    row = db.execute(
        text(
            """
            SELECT 1 FROM domain_crm.sales_offers
            WHERE id = :id AND tenant_id = :tenant_id AND deleted_at IS NULL
            """
        ),
        {"id": offer_id, "tenant_id": effective_tenant},
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="Sales offer not found")
    db.execute(
        text(
            """
            UPDATE domain_crm.sales_offers
            SET deleted_at = :now, updated_at = :now
            WHERE id = :id
            """
        ),
        {"now": datetime.now(timezone.utc), "id": offer_id},
    )
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{offer_id}/convert-to-order", status_code=status.HTTP_200_OK)
async def convert_offer_to_order(
    offer_id: str,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Mark offer as accepted and return the offer data ready for order creation."""
    effective_tenant = tenant_id or DEFAULT_TENANT
    row = db.execute(
        text(
            """
            SELECT * FROM domain_crm.sales_offers
            WHERE id = :id AND tenant_id = :tenant_id AND deleted_at IS NULL
            """
        ),
        {"id": offer_id, "tenant_id": effective_tenant},
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Sales offer not found")

    now = datetime.now(timezone.utc)
    db.execute(
        text("UPDATE domain_crm.sales_offers SET status = 'angenommen', updated_at = :now WHERE id = :id"),
        {"now": now, "id": offer_id},
    )

    order_id = str(uuid4())
    order_number = f"SO-{row['offer_number']}"
    offer_items = _fetch_items(db, offer_id)
    total = sum(Decimal(str(i.line_total)) for i in offer_items)

    db.execute(
        text("""
            INSERT INTO domain_crm.sales_orders
            (id, tenant_id, sales_offer_id, customer_id, order_number, subject,
             description, total_amount, currency, status, contact_person, notes,
             created_at, updated_at, version)
            VALUES (:id, :tid, :offer_id, :cid, :on, :subj, :desc, :total,
                    :cur, 'open', :cp, :notes, :now, :now, 1)
        """),
        {
            "id": order_id, "tid": effective_tenant, "offer_id": offer_id,
            "cid": row.get("customer_id") or "", "on": order_number,
            "subj": row["subject"], "desc": row.get("description") or "",
            "total": float(total), "cur": row.get("currency") or "EUR",
            "cp": row.get("contact_person"), "notes": row.get("notes"),
            "now": now,
        },
    )

    for item in offer_items:
        db.execute(
            text("""
                INSERT INTO domain_crm.sales_order_items
                (id, tenant_id, order_id, line_number, article_number, description,
                 quantity, unit_price, discount_percent, line_total, created_at, updated_at)
                VALUES (:id, :tid, :oid, :ln, :an, :desc, :qty, :up, :dp, :lt, :now, :now)
            """),
            {
                "id": str(uuid4()), "tid": effective_tenant, "oid": order_id,
                "ln": item.line_number, "an": item.article_number,
                "desc": item.description, "qty": item.quantity,
                "up": item.unit_price, "dp": item.discount_percent,
                "lt": item.line_total, "now": now,
            },
        )

    db.commit()

    updated = db.execute(
        text("SELECT * FROM domain_crm.sales_offers WHERE id = :id"),
        {"id": offer_id},
    ).mappings().first()
    offer_out = _row_to_offer(dict(updated), offer_items)
    return {
        "offer": offer_out.model_dump() if hasattr(offer_out, "model_dump") else offer_out,
        "created_order_id": order_id,
        "created_order_number": order_number,
    }
