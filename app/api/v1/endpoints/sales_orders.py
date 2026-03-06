"""Domain sales orders CRUD endpoints."""

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


class SalesOrderBase(BaseModel):
    order_number: str = Field(..., min_length=1, max_length=64)
    customer_id: str = Field(..., min_length=1)
    subject: str = Field(..., min_length=1, max_length=255)
    description: str = ""
    total_amount: float = 0.0
    currency: str = "EUR"
    status: str = "open"
    contact_person: Optional[str] = None
    delivery_date: Optional[datetime] = None
    delivery_address: Optional[str] = None
    shipping_method: Optional[str] = None
    payment_terms: Optional[str] = None
    notes: Optional[str] = None
    items: list["SalesOrderItemInput"] = Field(default_factory=list)


class SalesOrderCreate(SalesOrderBase):
    tenant_id: Optional[str] = None


class SalesOrderUpdate(BaseModel):
    order_number: Optional[str] = None
    customer_id: Optional[str] = None
    subject: Optional[str] = None
    description: Optional[str] = None
    total_amount: Optional[float] = None
    currency: Optional[str] = None
    status: Optional[str] = None
    contact_person: Optional[str] = None
    delivery_date: Optional[datetime] = None
    delivery_address: Optional[str] = None
    shipping_method: Optional[str] = None
    payment_terms: Optional[str] = None
    notes: Optional[str] = None
    items: Optional[list["SalesOrderItemInput"]] = None


class SalesOrderItemInput(BaseModel):
    article_number: str = Field(..., min_length=1, max_length=80)
    description: Optional[str] = None
    quantity: float = Field(..., ge=0)
    unit_price: float = Field(..., ge=0)
    discount_percent: float = Field(default=0.0, ge=0, le=100)


class SalesOrderItemOut(SalesOrderItemInput):
    id: str
    line_number: int
    line_total: float


class SalesOrder(SalesOrderBase):
    id: str
    tenant_id: str
    sales_offer_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    version: int = 1
    items: list[SalesOrderItemOut] = Field(default_factory=list)


def _line_total(quantity: float, unit_price: float, discount_percent: float) -> Decimal:
    qty = Decimal(str(quantity))
    price = Decimal(str(unit_price))
    discount = Decimal(str(discount_percent))
    base = qty * price
    discounted = base * (Decimal("100") - discount) / Decimal("100")
    return discounted.quantize(Decimal("0.01"))


def _fetch_items(db: Session, order_id: str) -> list[SalesOrderItemOut]:
    rows = db.execute(
        text(
            """
            SELECT id, line_number, article_number, description, quantity, unit_price, discount_percent, line_total
            FROM domain_crm.sales_order_items
            WHERE order_id = :order_id
            ORDER BY line_number ASC
            """
        ),
        {"order_id": order_id},
    ).mappings().all()
    return [
        SalesOrderItemOut(
            id=str(row["id"]),
            line_number=int(row["line_number"]),
            article_number=str(row["article_number"]),
            description=row.get("description"),
            quantity=float(row.get("quantity") or 0),
            unit_price=float(row.get("unit_price") or 0),
            discount_percent=float(row.get("discount_percent") or 0),
            line_total=float(row.get("line_total") or 0),
        )
        for row in rows
    ]


def _row_to_order(row: dict, items: Optional[list[SalesOrderItemOut]] = None) -> SalesOrder:
    return SalesOrder(
        id=str(row["id"]),
        tenant_id=str(row["tenant_id"]),
        sales_offer_id=str(row["sales_offer_id"]) if row.get("sales_offer_id") else None,
        order_number=row["order_number"],
        customer_id=str(row["customer_id"]) if row.get("customer_id") else None,
        subject=row.get("subject"),
        description=row.get("description"),
        total_amount=float(row.get("total_amount") or Decimal("0")),
        currency=row.get("currency") or "EUR",
        status=row.get("status") or "open",
        contact_person=row.get("contact_person"),
        delivery_date=row.get("delivery_date"),
        delivery_address=row.get("delivery_address"),
        shipping_method=row.get("shipping_method"),
        payment_terms=row.get("payment_terms"),
        notes=row.get("notes"),
        items=items or [],
        created_at=row.get("created_at"),
        updated_at=row.get("updated_at"),
        deleted_at=row.get("deleted_at"),
        version=int(row.get("version") or 1),
    )


@router.get("/", response_model=PaginatedResponse[SalesOrder])
async def list_sales_orders(
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
        where.append("(order_number ILIKE :search OR subject ILIKE :search)")
        params["search"] = f"%{search}%"
    if status_filter:
        where.append("status = :status")
        params["status"] = status_filter

    where_sql = " AND ".join(where)
    total = db.execute(text(f"SELECT COUNT(*) FROM domain_crm.sales_orders WHERE {where_sql}"), params).scalar() or 0
    rows = db.execute(
        text(
            f"""
            SELECT *
            FROM domain_crm.sales_orders
            WHERE {where_sql}
            ORDER BY created_at DESC
            OFFSET :skip LIMIT :limit
            """
        ),
        params,
    ).mappings()
    items = []
    for row in rows:
        row_dict = dict(row)
        order_items = _fetch_items(db, str(row_dict["id"]))
        items.append(_row_to_order(row_dict, order_items))

    page = (skip // limit) + 1
    pages = (total + limit - 1) // limit if total else 1
    return PaginatedResponse[SalesOrder](
        items=items,
        total=int(total),
        page=page,
        size=limit,
        pages=pages,
        has_next=(skip + limit) < int(total),
        has_prev=skip > 0,
    )


@router.get("/{order_id}", response_model=SalesOrder)
async def get_sales_order(order_id: str, tenant_id: Optional[str] = Query(None), db: Session = Depends(get_db)):
    effective_tenant = tenant_id or DEFAULT_TENANT
    row = db.execute(
        text(
            """
            SELECT *
            FROM domain_crm.sales_orders
            WHERE id = :id AND tenant_id = :tenant_id AND deleted_at IS NULL
            """
        ),
        {"id": order_id, "tenant_id": effective_tenant},
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Sales order not found")
    return _row_to_order(dict(row), _fetch_items(db, order_id))


@router.post("/", response_model=SalesOrder, status_code=status.HTTP_201_CREATED)
async def create_sales_order(payload: SalesOrderCreate, db: Session = Depends(get_db)):
    effective_tenant = payload.tenant_id or DEFAULT_TENANT
    order_id = str(uuid4())
    now = datetime.now(timezone.utc)

    duplicate = db.execute(
        text(
            """
            SELECT 1
            FROM domain_crm.sales_orders
            WHERE tenant_id = :tenant_id
              AND order_number = :order_number
              AND deleted_at IS NULL
            """
        ),
        {"tenant_id": effective_tenant, "order_number": payload.order_number},
    ).first()
    if duplicate:
        raise HTTPException(status_code=409, detail="order_number already exists")

    customer_exists = db.execute(
        text(
            """
            SELECT 1
            FROM domain_crm.customers
            WHERE id = :customer_id AND tenant_id = :tenant_id
            """
        ),
        {"customer_id": payload.customer_id, "tenant_id": effective_tenant},
    ).first()
    if not customer_exists:
        raise HTTPException(status_code=400, detail="customer_id does not exist")

    items_total = sum(
        (_line_total(i.quantity, i.unit_price, i.discount_percent) for i in payload.items),
        Decimal("0.00"),
    )
    total_amount = payload.total_amount if payload.total_amount > 0 else float(items_total)

    db.execute(
        text(
            """
            INSERT INTO domain_crm.sales_orders (
                id, tenant_id, sales_offer_id, customer_id, order_number, subject, description,
                total_amount, currency, status, contact_person, delivery_date, delivery_address, shipping_method,
                payment_terms, notes, created_at, updated_at, version
            ) VALUES (
                :id, :tenant_id, NULL, :customer_id, :order_number, :subject, :description,
                :total_amount, :currency, :status, :contact_person, :delivery_date, :delivery_address, :shipping_method,
                :payment_terms, :notes, :created_at, :updated_at, :version
            )
            """
        ),
        {
            "id": order_id,
            "tenant_id": effective_tenant,
            "customer_id": payload.customer_id,
            "order_number": payload.order_number,
            "subject": payload.subject,
            "description": payload.description or "",
            "total_amount": total_amount,
            "currency": payload.currency,
            "status": payload.status,
            "contact_person": payload.contact_person,
            "delivery_date": payload.delivery_date,
            "delivery_address": payload.delivery_address,
            "shipping_method": payload.shipping_method,
            "payment_terms": payload.payment_terms,
            "notes": payload.notes,
            "created_at": now,
            "updated_at": now,
            "version": 1,
        },
    )
    for index, item in enumerate(payload.items, start=1):
        db.execute(
            text(
                """
                INSERT INTO domain_crm.sales_order_items (
                    id, tenant_id, order_id, line_number, article_number, description,
                    quantity, unit_price, discount_percent, line_total, created_at, updated_at
                ) VALUES (
                    :id, :tenant_id, :order_id, :line_number, :article_number, :description,
                    :quantity, :unit_price, :discount_percent, :line_total, :created_at, :updated_at
                )
                """
            ),
            {
                "id": str(uuid4()),
                "tenant_id": effective_tenant,
                "order_id": order_id,
                "line_number": index,
                "article_number": item.article_number,
                "description": item.description,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "discount_percent": item.discount_percent,
                "line_total": _line_total(item.quantity, item.unit_price, item.discount_percent),
                "created_at": now,
                "updated_at": now,
            },
        )
    db.commit()

    row = db.execute(
        text("SELECT * FROM domain_crm.sales_orders WHERE id = :id"),
        {"id": order_id},
    ).mappings().first()
    return _row_to_order(dict(row), _fetch_items(db, order_id))


@router.put("/{order_id}", response_model=SalesOrder)
async def update_sales_order(
    order_id: str,
    payload: SalesOrderUpdate,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    effective_tenant = tenant_id or DEFAULT_TENANT
    current = db.execute(
        text(
            """
            SELECT *
            FROM domain_crm.sales_orders
            WHERE id = :id AND tenant_id = :tenant_id AND deleted_at IS NULL
            """
        ),
        {"id": order_id, "tenant_id": effective_tenant},
    ).mappings().first()
    if not current:
        raise HTTPException(status_code=404, detail="Sales order not found")

    data = payload.model_dump(exclude_unset=True)
    if not data:
        return _row_to_order(dict(current), _fetch_items(db, order_id))

    if "order_number" in data and data["order_number"] != current["order_number"]:
        duplicate = db.execute(
            text(
                """
                SELECT 1
                FROM domain_crm.sales_orders
                WHERE tenant_id = :tenant_id
                  AND order_number = :order_number
                  AND id != :id
                  AND deleted_at IS NULL
                """
            ),
            {"tenant_id": effective_tenant, "order_number": data["order_number"], "id": order_id},
        ).first()
        if duplicate:
            raise HTTPException(status_code=409, detail="order_number already exists")

    if "customer_id" in data:
        customer_exists = db.execute(
            text(
                """
                SELECT 1
                FROM domain_crm.customers
                WHERE id = :customer_id AND tenant_id = :tenant_id
                """
            ),
            {"customer_id": data["customer_id"], "tenant_id": effective_tenant},
        ).first()
        if not customer_exists:
            raise HTTPException(status_code=400, detail="customer_id does not exist")

    replace_items = None
    if "items" in data:
        replace_items = payload.items or []
        del data["items"]
    if replace_items is not None and "total_amount" not in data:
        items_total = sum(
            (_line_total(i.quantity, i.unit_price, i.discount_percent) for i in replace_items),
            Decimal("0.00"),
        )
        data["total_amount"] = float(items_total)

    set_fields = []
    params: dict[str, object] = {"id": order_id, "tenant_id": effective_tenant}
    for key, value in data.items():
        if key in {"subject", "description"} and value is None:
            value = ""
        set_fields.append(f"{key} = :{key}")
        params[key] = value
    set_fields.append("updated_at = :updated_at")
    set_fields.append("version = COALESCE(version, 1) + 1")
    params["updated_at"] = datetime.now(timezone.utc)

    db.execute(
        text(
            f"""
            UPDATE domain_crm.sales_orders
            SET {", ".join(set_fields)}
            WHERE id = :id AND tenant_id = :tenant_id AND deleted_at IS NULL
            """
        ),
        params,
    )
    if replace_items is not None:
        now = datetime.now(timezone.utc)
        db.execute(
            text("DELETE FROM domain_crm.sales_order_items WHERE order_id = :order_id"),
            {"order_id": order_id},
        )
        for index, item in enumerate(replace_items, start=1):
            db.execute(
                text(
                    """
                    INSERT INTO domain_crm.sales_order_items (
                        id, tenant_id, order_id, line_number, article_number, description,
                        quantity, unit_price, discount_percent, line_total, created_at, updated_at
                    ) VALUES (
                        :id, :tenant_id, :order_id, :line_number, :article_number, :description,
                        :quantity, :unit_price, :discount_percent, :line_total, :created_at, :updated_at
                    )
                    """
                ),
                {
                    "id": str(uuid4()),
                    "tenant_id": effective_tenant,
                    "order_id": order_id,
                    "line_number": index,
                    "article_number": item.article_number,
                    "description": item.description,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "discount_percent": item.discount_percent,
                    "line_total": _line_total(item.quantity, item.unit_price, item.discount_percent),
                    "created_at": now,
                    "updated_at": now,
                },
            )
    db.commit()

    row = db.execute(
        text("SELECT * FROM domain_crm.sales_orders WHERE id = :id"),
        {"id": order_id},
    ).mappings().first()
    return _row_to_order(dict(row), _fetch_items(db, order_id))


@router.post("/{order_id}/create-delivery-note", response_model=dict, status_code=201)
async def create_delivery_from_order(
    order_id: str,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Create a delivery note from a sales order (document flow)."""
    effective_tenant = tenant_id or DEFAULT_TENANT
    order_row = db.execute(
        text("SELECT * FROM domain_crm.sales_orders WHERE id = :id AND tenant_id = :tid AND deleted_at IS NULL"),
        {"id": order_id, "tid": effective_tenant},
    ).mappings().first()
    if not order_row:
        raise HTTPException(status_code=404, detail="Sales order not found")
    if order_row["status"] in ("cancelled", "completed"):
        raise HTTPException(status_code=400, detail=f"Auftrag hat Status '{order_row['status']}' und kann nicht geliefert werden")

    from app.core.uuid7 import uuid7
    dn_id = uuid7()
    dn_nr = f"LS-{order_row['order_number']}"

    db.execute(text("CREATE SCHEMA IF NOT EXISTS domain_sales"))
    db.execute(
        text("""
            INSERT INTO domain_sales.delivery_notes
            (id, tenant_id, ls_nummer, status, lieferdatum, kunde_nr, kunde_name,
             auftrags_nr, notizen, versandart, created_at, updated_at)
            VALUES (:id, :tid, :ls, 'offen', NOW()::date, :kid, :kname,
                    :anr, :notizen, :versand, NOW(), NOW())
        """),
        {
            "id": dn_id, "tid": effective_tenant, "ls": dn_nr,
            "kid": order_row["customer_id"], "kname": order_row.get("subject", ""),
            "anr": order_row["order_number"],
            "notizen": order_row.get("notes", ""),
            "versand": order_row.get("shipping_method", ""),
        },
    )

    items = _fetch_items(db, order_id)
    for i, item in enumerate(items, 1):
        pos_id = uuid7()
        db.execute(
            text("""
                INSERT INTO domain_sales.delivery_note_positions
                (id, delivery_note_id, pos_nr, artikel_nr, bezeichnung,
                 menge, einheit, listenpreis, netto_preis, netto_betrag, created_at, updated_at)
                VALUES (:id, :dnid, :pos, :anr, :desc,
                        :menge, 'Stk', :lp, :np, :nb, NOW(), NOW())
            """),
            {
                "id": pos_id, "dnid": dn_id, "pos": i,
                "anr": item.article_number, "desc": item.description or "",
                "menge": item.quantity, "lp": item.unit_price,
                "np": item.unit_price, "nb": item.line_total,
            },
        )

    db.execute(
        text("UPDATE domain_crm.sales_orders SET status = 'in_delivery', updated_at = NOW() WHERE id = :id"),
        {"id": order_id},
    )
    db.commit()
    return {"ok": True, "delivery_note_id": dn_id, "delivery_note_number": dn_nr, "order_id": order_id}


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def delete_sales_order(order_id: str, tenant_id: Optional[str] = Query(None), db: Session = Depends(get_db)) -> Response:
    effective_tenant = tenant_id or DEFAULT_TENANT
    db.execute(
        text("DELETE FROM domain_crm.sales_order_items WHERE order_id = :id"),
        {"id": order_id},
    )
    updated = db.execute(
        text(
            """
            UPDATE domain_crm.sales_orders
            SET deleted_at = :deleted_at, updated_at = :updated_at
            WHERE id = :id AND tenant_id = :tenant_id AND deleted_at IS NULL
            """
        ),
        {
            "id": order_id,
            "tenant_id": effective_tenant,
            "deleted_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        },
    )
    if updated.rowcount == 0:
        raise HTTPException(status_code=404, detail="Sales order not found")
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
