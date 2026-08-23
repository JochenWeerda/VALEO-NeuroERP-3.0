"""Domain sales orders CRUD endpoints."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
import json
from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....core.tenant import get_tenant_id
from ....services.customer_sales_eligibility import assert_customer_allowed_for_delivery
from ....services.customer_sales_eligibility import assert_customer_allowed_for_sales_order
from ....services.numbering_service import get_numbering
from ..schemas.base import PaginatedResponse
from .credit_management import get_credit_status_data

from app.api.v1.schemas.base import BaseSchema, IDResponse
from app.api.v1.schemas.agrar_schemas import DeliveryNoteCreatedOut


router = APIRouter()


class SalesOrderBase(BaseModel):
    order_number: Optional[str] = Field(default=None, min_length=1, max_length=64)
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
    order_number: str
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


def _resolve_order_number(order_number: Optional[str]) -> str:
    cleaned = (order_number or "").strip()
    if cleaned:
        return cleaned
    return get_numbering().next_number("sales_order")


def _resolve_tenant_scope(payload_tenant_id: str | None, tenant_id: str) -> str:
    payload_tenant = (payload_tenant_id or "").strip()
    if payload_tenant and payload_tenant != tenant_id:
        raise HTTPException(status_code=403, detail="tenant_id mismatch")
    return tenant_id


def _fetch_items(db: Session, order_id: str, tenant_id: str) -> list[SalesOrderItemOut]:
    rows = db.execute(
        text(
            """
            SELECT id, line_number, article_number, description, quantity, unit_price, discount_percent, line_total
            FROM domain_crm.sales_order_items
            WHERE order_id = :order_id AND tenant_id = :tenant_id
            ORDER BY line_number ASC
            """
        ),
        {"order_id": order_id, "tenant_id": tenant_id},
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


def _get_sales_order_row(db: Session, order_id: str, tenant_id: str) -> dict:
    row = db.execute(
        text(
            """
            SELECT *
            FROM domain_crm.sales_orders
            WHERE id = :id AND tenant_id = :tenant_id AND deleted_at IS NULL
            """
        ),
        {"id": order_id, "tenant_id": tenant_id},
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Sales order not found")
    return dict(row)


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


@router.get("/", response_model=PaginatedResponse[SalesOrder], summary="Sales orders auflisten")
async def list_sales_orders(
    customer_id: Optional[str] = Query(None, description="Filter by customer ID"),
    search: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=200),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    params: dict[str, object] = {
        "tenant_id": tenant_id,
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
    total = db.execute(text(f"SELECT COUNT(*) FROM domain_crm.sales_orders WHERE {where_sql}"), params).scalar() or 0  # nosec B608  # reviewed-safe: column names code-controlled, values parameterized
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
        order_items = _fetch_items(db, str(row_dict["id"]), tenant_id)
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


@router.get("/{order_id}", response_model=SalesOrder, summary="Sales order abrufen")
async def get_sales_order(
    order_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    row = _get_sales_order_row(db, order_id, tenant_id)
    return _row_to_order(row, _fetch_items(db, order_id, tenant_id))


def _sales_order_tab_endpoint(order_id: str, tab_key: str) -> str:
    return f"/api/v1/sales/orders/{order_id}/tabs/{tab_key}"


def build_sales_order_screen_summary(
    *,
    order_id: str,
    tenant_id: str,
    order: dict[str, Any],
    item_count: int,
    customer_name: str | None = None,
) -> dict[str, Any]:
    delivery_date = order.get("delivery_date")
    delivery_label = delivery_date.isoformat() if hasattr(delivery_date, "isoformat") else (
        str(delivery_date) if delivery_date else None
    )
    return {
        "schema_version": 1,
        "screen_id": "sales/sales-order",
        "order_id": order_id,
        "tenant_id": tenant_id,
        "title": order.get("subject") or order.get("order_number") or "Verkaufsauftrag",
        "subtitle": order.get("order_number"),
        "summary": {
            "total_amount": float(order.get("total_amount") or 0.0),
            "item_count": item_count,
            "status": str(order.get("status") or "open"),
            "delivery_date": delivery_label,
        },
        "available_tabs": ["kopf", "positionen", "lieferung", "dokumente"],
        "tab_endpoints": {
            "positionen": _sales_order_tab_endpoint(order_id, "positionen"),
            "lieferung": _sales_order_tab_endpoint(order_id, "lieferung"),
            "dokumente": _sales_order_tab_endpoint(order_id, "dokumente"),
        },
        "actions": [
            {"key": "edit", "label": "Bearbeiten", "permission": "sales.order.update"},
        ],
        "performance": {
            "initial_payload_budget_kb": 56,
            "tabs_lazy": True,
            "lookup_min_chars": 2,
            "default_table_limit": 25,
        },
        "customer_name": customer_name,
    }


def _fetch_customer_name(db: Session, customer_id: str | None, tenant_id: str) -> str | None:
    if not customer_id:
        return None
    try:
        row = db.execute(
            text(
                """
                SELECT name
                FROM domain_erp.business_partners
                WHERE id = :cid AND tenant_id::text = :tid
                LIMIT 1
                """
            ),
            {"cid": customer_id, "tid": tenant_id},
        ).mappings().first()
        return str(row["name"]) if row and row.get("name") else None
    except Exception:
        db.rollback()
        return None


def _fetch_delivery_notes_for_order(db: Session, order_id: str, tenant_id: str) -> list[dict[str, Any]]:
    try:
        rows = db.execute(
            text(
                """
                SELECT id::text AS id,
                       delivery_note_number,
                       status,
                       delivery_date::text AS delivery_date,
                       COALESCE(invoice_number, '') AS invoice_number,
                       is_delivered
                FROM domain_sales.delivery_notes
                WHERE sales_order_id = :order_id
                  AND tenant_id = :tenant_id
                ORDER BY delivery_date DESC NULLS LAST, created_at DESC
                LIMIT 25
                """
            ),
            {"order_id": order_id, "tenant_id": tenant_id},
        ).mappings().all()
        return [dict(row) for row in rows]
    except Exception:
        db.rollback()
        return []


def _paginate_tab_items(
    items: list[dict[str, Any]],
    *,
    page: int = 1,
    limit: int = 25,
    q: str | None = None,
) -> tuple[list[dict[str, Any]], int]:
    filtered = items
    if q:
        needle = q.casefold()
        filtered = [
            row
            for row in items
            if any(needle in str(value).casefold() for value in row.values())
        ]
    safe_limit = max(1, min(limit, 50))
    safe_page = max(1, page)
    start = (safe_page - 1) * safe_limit
    return filtered[start : start + safe_limit], len(filtered)


def _fetch_order_documents(db: Session, order_id: str, tenant_id: str) -> list[dict[str, Any]]:
    """Belege mit Rechnungsnummer aus Lieferscheinen des Auftrags (read-only)."""
    try:
        rows = db.execute(
            text(
                """
                SELECT id::text AS id,
                       COALESCE(invoice_number, delivery_note_number) AS beleg_nr,
                       delivery_date::text AS beleg_datum,
                       status,
                       invoice_number
                FROM domain_sales.delivery_notes
                WHERE sales_order_id = :order_id
                  AND tenant_id = :tenant_id
                  AND (invoice_number IS NOT NULL AND invoice_number <> '')
                ORDER BY delivery_date DESC NULLS LAST
                LIMIT 25
                """
            ),
            {"order_id": order_id, "tenant_id": tenant_id},
        ).mappings().all()
        return [dict(row) for row in rows]
    except Exception:
        db.rollback()
        return []


@router.get(
    "/{order_id}/screen-summary",
    response_model=dict[str, Any],
    tags=["sales", "orders", "screen-summary"],
    summary="Sales order screen summary abrufen",
)
async def get_sales_order_screen_summary(
    order_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    row = _get_sales_order_row(db, order_id, tenant_id)
    items = _fetch_items(db, order_id, tenant_id)
    customer_name = _fetch_customer_name(db, str(row.get("customer_id")) if row.get("customer_id") else None, tenant_id)
    return build_sales_order_screen_summary(
        order_id=order_id,
        tenant_id=tenant_id,
        order=row,
        item_count=len(items),
        customer_name=customer_name,
    )


@router.get(
    "/{order_id}/tabs/{tab_key}",
    response_model=dict[str, Any],
    tags=["sales", "orders", "screen-summary"],
    summary="Sales order tab list data abrufen",
)
async def get_sales_order_tab_data(
    order_id: str,
    tab_key: str,
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=50),
    q: str | None = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    _get_sales_order_row(db, order_id, tenant_id)

    if tab_key == "positionen":
        items = [item.model_dump(mode="json") for item in _fetch_items(db, order_id, tenant_id)]
        paged_items, total = _paginate_tab_items(items, page=page, limit=limit, q=q)
        return {
            "tab_key": tab_key,
            "table_key": "order_items",
            "items": paged_items,
            "page": page,
            "limit": limit,
            "total": total,
        }

    if tab_key == "lieferung":
        items = _fetch_delivery_notes_for_order(db, order_id, tenant_id)
        paged_items, total = _paginate_tab_items(items, page=page, limit=limit, q=q)
        return {
            "tab_key": tab_key,
            "table_key": "delivery_notes",
            "items": paged_items,
            "page": page,
            "limit": limit,
            "total": total,
        }

    if tab_key == "dokumente":
        items = _fetch_order_documents(db, order_id, tenant_id)
        paged_items, total = _paginate_tab_items(items, page=page, limit=limit, q=q)
        return {
            "tab_key": tab_key,
            "table_key": "order_documents",
            "items": paged_items,
            "page": page,
            "limit": limit,
            "total": total,
        }

    return {"tab_key": tab_key, "table_key": tab_key, "items": [], "page": page, "limit": limit, "total": 0}


@router.post("/", response_model=SalesOrder, status_code=status.HTTP_201_CREATED, summary="Sales order anlegen")
async def create_sales_order(
    payload: SalesOrderCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    effective_tenant = _resolve_tenant_scope(payload.tenant_id, tenant_id)
    order_id = str(uuid4())
    now = datetime.now(timezone.utc)
    order_number = _resolve_order_number(payload.order_number)

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
        {"tenant_id": effective_tenant, "order_number": order_number},
    ).first()
    if duplicate:
        raise HTTPException(status_code=409, detail="order_number already exists")

    from app.services.business_partner_service import BusinessPartnerService

    customer_exists = BusinessPartnerService(db, effective_tenant).customer_exists(payload.customer_id)
    if not customer_exists:
        raise HTTPException(status_code=422, detail="customer_id does not exist")

    assert_customer_allowed_for_sales_order(db, effective_tenant, payload.customer_id)

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
            "order_number": order_number,
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

    row = _get_sales_order_row(db, order_id, effective_tenant)
    return _row_to_order(row, _fetch_items(db, order_id, effective_tenant))


@router.put("/{order_id}", response_model=SalesOrder, summary="Sales order aktualisieren")
async def update_sales_order(
    order_id: str,
    payload: SalesOrderUpdate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    effective_tenant = tenant_id
    current = _get_sales_order_row(db, order_id, effective_tenant)

    data = payload.model_dump(exclude_unset=True)
    if not data:
        return _row_to_order(current, _fetch_items(db, order_id, effective_tenant))

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
        from app.services.business_partner_service import BusinessPartnerService

        customer_exists = BusinessPartnerService(db, effective_tenant).customer_exists(data["customer_id"])
        if not customer_exists:
            raise HTTPException(status_code=400, detail="customer_id does not exist")
        assert_customer_allowed_for_sales_order(db, effective_tenant, data["customer_id"])

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
            text("DELETE FROM domain_crm.sales_order_items WHERE order_id = :order_id AND tenant_id = :tenant_id"),
            {"order_id": order_id, "tenant_id": effective_tenant},
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

    row = _get_sales_order_row(db, order_id, effective_tenant)
    return _row_to_order(row, _fetch_items(db, order_id, effective_tenant))


@router.post("/{order_id}/create-delivery-note", response_model=DeliveryNoteCreatedOut, status_code=201, summary="Delivery from order anlegen")
async def create_delivery_from_order(
    order_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Create a delivery note from a sales order (document flow)."""
    effective_tenant = tenant_id
    order_row = _get_sales_order_row(db, order_id, effective_tenant)
    if order_row["status"] in ("cancelled", "completed"):
        raise HTTPException(status_code=400, detail=f"Auftrag hat Status '{order_row['status']}' und kann nicht geliefert werden")

    cid = order_row.get("customer_id")
    if cid:
        assert_customer_allowed_for_delivery(db, effective_tenant, str(cid))

    from app.core.uuid7 import uuid7
    dn_id = uuid7()
    dn_nr = f"LS-{order_row['order_number']}"

    db.execute(text("CREATE SCHEMA IF NOT EXISTS domain_sales"))
    db.execute(
        text("""
            INSERT INTO domain_sales.delivery_notes
            (id, tenant_id, delivery_note_number, customer_id, delivery_date,
             status, is_printed, is_delivered, totals, sales_order_id, created_at, updated_at)
            VALUES (:id, :tid, :ls, :kid, NOW()::date,
                    'draft', FALSE, FALSE, CAST(:totals AS jsonb), :oid, NOW(), NOW())
        """),
        {
            "id": dn_id, "tid": effective_tenant, "ls": dn_nr,
            "kid": order_row["customer_id"],
            "totals": json.dumps({
                "netto": float(order_row.get("total_amount") or 0),
                "mwst": 0,
                "brutto": float(order_row.get("total_amount") or 0),
            }),
            "oid": order_id,
        },
    )

    items = _fetch_items(db, order_id, effective_tenant)
    for i, item in enumerate(items, 1):
        pos_id = uuid7()
        db.execute(
            text("""
                INSERT INTO domain_sales.delivery_note_positions
                (id, delivery_note_id, pos_nr, artikel_nr, bezeichnung,
                 menge, einheit, listenpreis, rabatt, netto_preis, netto_betrag,
                 mwst_prozent, skontierf, fremdware, created_at, updated_at)
                VALUES (:id, :dnid, :pos, :anr, :desc,
                        :menge, 'Stk', :lp, :rabatt, :np, :nb,
                        0, FALSE, FALSE, NOW(), NOW())
            """),
            {
                "id": pos_id, "dnid": dn_id, "pos": i,
                "anr": item.article_number, "desc": item.description or "",
                "menge": item.quantity, "lp": item.unit_price,
                "rabatt": item.discount_percent,
                "np": float(item.unit_price) * (1 - float(item.discount_percent) / 100),
                "nb": item.line_total,
            },
        )

    db.execute(
        text(
            """
            UPDATE domain_crm.sales_orders
            SET status = 'in_delivery', updated_at = NOW()
            WHERE id = :id AND tenant_id = :tenant_id AND deleted_at IS NULL
            """
        ),
        {"id": order_id, "tenant_id": effective_tenant},
    )
    db.commit()
    return {"ok": True, "delivery_note_id": dn_id, "delivery_note_number": dn_nr, "order_id": order_id}


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response, summary="Sales order löschen")
async def delete_sales_order(
    order_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> Response:
    effective_tenant = tenant_id
    db.execute(
        text("DELETE FROM domain_crm.sales_order_items WHERE order_id = :id AND tenant_id = :tenant_id"),
        {"id": order_id, "tenant_id": effective_tenant},
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


@router.post("/{order_id}/confirm", response_model=SalesOrder, summary="Sales order bestätigen")
async def confirm_sales_order(
    order_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Bestätigt einen offenen Auftrag (open → confirmed)."""
    order = _get_sales_order_row(db, order_id, tenant_id)
    if order["status"] != "open":
        raise HTTPException(status_code=400, detail=f"Auftrag hat Status '{order['status']}' — nur 'open' kann bestätigt werden")
    db.execute(
        text("UPDATE domain_crm.sales_orders SET status = 'confirmed', updated_at = NOW() WHERE id = :id AND tenant_id = :tid"),
        {"id": order_id, "tid": tenant_id},
    )
    db.commit()
    return _row_to_order(_get_sales_order_row(db, order_id, tenant_id))


@router.post("/{order_id}/complete", response_model=SalesOrder, summary="Sales order complete")
async def complete_sales_order(
    order_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Schließt einen Auftrag ab (confirmed/in_delivery → completed)."""
    order = _get_sales_order_row(db, order_id, tenant_id)
    if order["status"] not in ("confirmed", "in_delivery"):
        raise HTTPException(status_code=400, detail=f"Auftrag hat Status '{order['status']}' — nur 'confirmed'/'in_delivery' kann abgeschlossen werden")
    db.execute(
        text("UPDATE domain_crm.sales_orders SET status = 'completed', updated_at = NOW() WHERE id = :id AND tenant_id = :tid"),
        {"id": order_id, "tid": tenant_id},
    )
    db.commit()
    return _row_to_order(_get_sales_order_row(db, order_id, tenant_id))


@router.post("/{order_id}/cancel", response_model=SalesOrder, summary="Sales order stornieren")
async def cancel_sales_order(
    order_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Storniert einen Auftrag (open/confirmed → cancelled)."""
    order = _get_sales_order_row(db, order_id, tenant_id)
    if order["status"] in ("cancelled", "completed"):
        raise HTTPException(status_code=400, detail=f"Auftrag hat Status '{order['status']}' und kann nicht storniert werden")
    db.execute(
        text("UPDATE domain_crm.sales_orders SET status = 'cancelled', updated_at = NOW() WHERE id = :id AND tenant_id = :tid"),
        {"id": order_id, "tid": tenant_id},
    )
    db.commit()
    return _row_to_order(_get_sales_order_row(db, order_id, tenant_id))


# ---------------------------------------------------------------------------
# DOM-SALES-004: AB-Lifecycle / Lieferschein-Close / Preisabweichung
# ---------------------------------------------------------------------------

from pydantic import BaseModel as _BM
from typing import Optional as _Opt


class ABTransitionIn(_BM):
    new_status: str
    operator: _Opt[str] = "system"
    reason: _Opt[str] = None


class LSAdvanceIn(_BM):
    new_status: str
    operator: _Opt[str] = "system"
    quittiert_von: _Opt[str] = None


class PreisabweichungIn(_BM):
    artikel_id: str
    angebots_preis: float
    rechnungs_preis: float
    schwelle_pct: _Opt[float] = 2.0


class PreisabweichungFreigabeIn(_BM):
    entscheidung: str
    operator: str
    grund: _Opt[str] = None


@router.post("/orders/{auftrag_id}/ab-transition", response_model=dict, summary="Auftragsbestätigung Status wechseln")
def ab_transition_endpoint(
    auftrag_id: str,
    body: ABTransitionIn,
    x_tenant_id: _Opt[str] = Header(None),
    db: Session = Depends(get_db),
) -> dict:
    from app.services.sales_ab_lifecycle_service import transition_ab_status, ABLifecycleError
    tenant_id = x_tenant_id or "default"
    try:
        return transition_ab_status(db, auftrag_id, tenant_id, body.new_status,
                                     body.operator or "system", body.reason)
    except ABLifecycleError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/delivery-notes/{ls_id}/advance", response_model=dict, summary="Lieferschein-Status vorwärts")
def ls_advance_endpoint(
    ls_id: str,
    body: LSAdvanceIn,
    x_tenant_id: _Opt[str] = Header(None),
    db: Session = Depends(get_db),
) -> dict:
    from app.services.sales_lieferschein_close_service import advance_lieferschein, LSCloseError
    tenant_id = x_tenant_id or "default"
    try:
        return advance_lieferschein(db, ls_id, tenant_id, body.new_status,
                                     body.operator or "system", body.quittiert_von)
    except LSCloseError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/orders/{auftrag_id}/preisabweichung", response_model=dict, status_code=201, summary="Preisabweichung prüfen")
def pruefe_preisabweichung_endpoint(
    auftrag_id: str,
    body: PreisabweichungIn,
    x_tenant_id: _Opt[str] = Header(None),
    db: Session = Depends(get_db),
) -> dict:
    from app.services.sales_preisabweichung_service import pruefe_preisabweichung, PreisabweichungError
    tenant_id = x_tenant_id or "default"
    try:
        return pruefe_preisabweichung(db, auftrag_id, tenant_id, body.artikel_id,
                                       body.angebots_preis, body.rechnungs_preis,
                                       body.schwelle_pct or 2.0)
    except PreisabweichungError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/preisabweichungen/{abweichung_id}/freigabe", response_model=dict, summary="Preisabweichung freigeben/ablehnen")
def freigabe_preisabweichung_endpoint(
    abweichung_id: str,
    body: PreisabweichungFreigabeIn,
    x_tenant_id: _Opt[str] = Header(None),
    db: Session = Depends(get_db),
) -> dict:
    from app.services.sales_preisabweichung_service import freigabe_preisabweichung, PreisabweichungError
    tenant_id = x_tenant_id or "default"
    try:
        return freigabe_preisabweichung(db, abweichung_id, tenant_id, body.entscheidung,
                                         body.operator, body.grund)
    except PreisabweichungError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
