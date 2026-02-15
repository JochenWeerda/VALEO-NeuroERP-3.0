"""Canonical Docflow command endpoints (DOCFLOW-P0-01..03)."""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
import json
from typing import Any, Optional
from uuid import NAMESPACE_URL, uuid4, uuid5

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from ....core.config import settings
from ....core.database import get_db

router = APIRouter()

DEFAULT_TENANT = settings.DEFAULT_TENANT_ID

_TRANSITIONS: dict[str, dict[str, str]] = {
    "sales_offer": {"sales_order": "offer_to_order"},
    "sales_order": {"sales_delivery": "order_to_delivery", "sales_invoice": "order_to_invoice"},
    "sales_delivery": {"sales_invoice": "delivery_to_invoice"},
    "sales_invoice": {"sales_credit_memo": "invoice_to_credit_memo"},
    "pos_receipt": {"sales_invoice": "receipt_to_invoice", "pos_storno": "receipt_to_storno", "pos_retoure": "receipt_to_retoure"},
    "pos_retoure": {"sales_credit_memo": "retoure_to_credit_memo"},
}

_DOC_PREFIX: dict[str, str] = {
    "sales_offer": "SOF",
    "sales_order": "SOR",
    "sales_delivery": "SDL",
    "sales_invoice": "SIV",
    "sales_credit_memo": "SCM",
    "pos_receipt": "POS",
    "pos_storno": "PST",
    "pos_retoure": "PRT",
}

_POS_TYPES = {"pos_receipt", "pos_storno", "pos_retoure"}


class DocflowItemOut(BaseModel):
    id: str
    line_number: int
    source_line_id: Optional[str] = None
    article_number: str
    description: Optional[str] = None
    quantity: float
    unit: Optional[str] = None
    unit_price: float
    discount_percent: float
    tax_rate: float
    line_total_net: float
    line_total_tax: float
    line_total_gross: float


class DocflowHeaderOut(BaseModel):
    id: str
    tenant_id: str
    doc_type: str
    doc_number: str
    status: str
    source_system: str
    source_ref: Optional[str] = None
    customer_id: Optional[str] = None
    supplier_id: Optional[str] = None
    currency: str
    total_net: float
    total_tax: float
    total_gross: float
    document_date: datetime
    posting_date: Optional[date] = None
    version: int
    created_at: datetime
    updated_at: datetime
    items: list[DocflowItemOut] = Field(default_factory=list)
    pos_compliance: Optional[dict[str, Any]] = None


class DocflowConvertRequest(BaseModel):
    target_doc_type: str = Field(..., min_length=3, max_length=40)
    idempotency_key: str = Field(..., min_length=8, max_length=120)
    quantities_by_source_item_id: dict[str, float] = Field(default_factory=dict)
    expected_version: Optional[int] = Field(default=None, ge=1)
    created_by: Optional[str] = Field(default=None, max_length=100)
    dry_run: bool = False


class DocflowPostRequest(BaseModel):
    idempotency_key: str = Field(..., min_length=8, max_length=120)
    expected_version: Optional[int] = Field(default=None, ge=1)
    posting_date: Optional[date] = None
    posted_by: Optional[str] = Field(default=None, max_length=100)


class DocflowReverseRequest(BaseModel):
    idempotency_key: str = Field(..., min_length=8, max_length=120)
    reason: str = Field(..., min_length=3, max_length=300)
    expected_version: Optional[int] = Field(default=None, ge=1)
    reversed_by: Optional[str] = Field(default=None, max_length=100)


class DocflowCommandResult(BaseModel):
    command: str
    idempotent_hit: bool = False
    source_doc_id: Optional[str] = None
    target_doc_id: Optional[str] = None
    posting_id: Optional[str] = None
    status: str
    payload: dict[str, Any] = Field(default_factory=dict)


class DocflowLineInput(BaseModel):
    article_number: str = Field(..., min_length=1, max_length=80)
    description: Optional[str] = None
    quantity: float = Field(default=0, ge=0)
    unit: Optional[str] = Field(default=None, max_length=20)
    unit_price: float = Field(default=0, ge=0)
    discount_percent: float = Field(default=0, ge=0, le=100)
    tax_rate: float = Field(default=0, ge=0, le=100)
    batch_id: Optional[str] = Field(default=None, max_length=64)
    charge: Optional[str] = Field(default=None, max_length=64)


class PosComplianceInput(BaseModel):
    terminal_id: str = Field(..., min_length=1, max_length=60)
    cash_register_id: Optional[str] = Field(default=None, max_length=60)
    transaction_type: str = Field(default="sale", min_length=4, max_length=20)
    payment_breakdown: Optional[dict[str, Any]] = None
    tse_transaction_id: str = Field(..., min_length=1, max_length=120)
    tse_signature: str = Field(..., min_length=1)
    tse_signature_counter: Optional[int] = None
    transaction_started_at: datetime
    transaction_ended_at: datetime
    receipt_issued_at: datetime
    dsfinvk_export_batch_id: Optional[str] = Field(default=None, max_length=120)
    correction_type: Optional[str] = Field(default=None, max_length=20)
    original_header_id: Optional[str] = Field(default=None, max_length=36)


class DocflowCreateRequest(BaseModel):
    doc_type: str = Field(..., min_length=3, max_length=40)
    doc_number: str = Field(..., min_length=1, max_length=80)
    status: str = Field(default="draft", min_length=3, max_length=20)
    source_system: Optional[str] = Field(default=None, max_length=40)
    source_ref: Optional[str] = Field(default=None, max_length=80)
    customer_id: Optional[str] = None
    supplier_id: Optional[str] = None
    currency: str = Field(default="EUR", min_length=3, max_length=3)
    document_date: Optional[datetime] = None
    posting_date: Optional[date] = None
    created_by: Optional[str] = Field(default=None, max_length=100)
    items: list[DocflowLineInput] = Field(default_factory=list)
    pos_compliance: Optional[PosComplianceInput] = None


class DocflowUpdateRequest(BaseModel):
    expected_version: Optional[int] = Field(default=None, ge=1)
    status: Optional[str] = Field(default=None, min_length=3, max_length=20)
    source_system: Optional[str] = Field(default=None, max_length=40)
    source_ref: Optional[str] = Field(default=None, max_length=80)
    customer_id: Optional[str] = None
    supplier_id: Optional[str] = None
    currency: Optional[str] = Field(default=None, min_length=3, max_length=3)
    document_date: Optional[datetime] = None
    posting_date: Optional[date] = None
    updated_by: Optional[str] = Field(default=None, max_length=100)
    items: Optional[list[DocflowLineInput]] = None
    pos_compliance: Optional[PosComplianceInput] = None


def _money(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _qty(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)


def _line_amounts(
    quantity: Decimal, unit_price: Decimal, discount_percent: Decimal, tax_rate: Decimal
) -> tuple[Decimal, Decimal, Decimal]:
    net = quantity * unit_price * (Decimal("100") - discount_percent) / Decimal("100")
    net = _money(net)
    tax = _money(net * tax_rate / Decimal("100"))
    gross = _money(net + tax)
    return net, tax, gross


def _fetch_doc_header(db: Session, tenant_id: str, doc_id: str) -> Optional[dict[str, Any]]:
    row = db.execute(
        text(
            """
            SELECT *
            FROM domain_docflow.document_headers
            WHERE tenant_id = :tenant_id AND id = :id AND deleted_at IS NULL
            """
        ),
        {"tenant_id": tenant_id, "id": doc_id},
    ).mappings().first()
    return dict(row) if row else None


def _fetch_doc_items(db: Session, tenant_id: str, header_id: str) -> list[dict[str, Any]]:
    rows = db.execute(
        text(
            """
            SELECT *
            FROM domain_docflow.document_items
            WHERE tenant_id = :tenant_id AND header_id = :header_id
            ORDER BY line_number ASC
            """
        ),
        {"tenant_id": tenant_id, "header_id": header_id},
    ).mappings().all()
    return [dict(r) for r in rows]


def _fetch_pos_compliance(db: Session, tenant_id: str, header_id: str) -> Optional[dict[str, Any]]:
    row = db.execute(
        text(
            """
            SELECT *
            FROM domain_docflow.pos_receipt_compliance
            WHERE tenant_id = :tenant_id AND header_id = :header_id
            """
        ),
        {"tenant_id": tenant_id, "header_id": header_id},
    ).mappings().first()
    return dict(row) if row else None


def _validate_pos_compliance_requirements(doc_type: str, pos: Optional[PosComplianceInput]) -> None:
    if doc_type in _POS_TYPES and pos is None:
        raise HTTPException(status_code=400, detail="pos_compliance is required for POS documents")
    if pos is None:
        return
    if pos.transaction_ended_at < pos.transaction_started_at:
        raise HTTPException(status_code=400, detail="transaction_ended_at must be >= transaction_started_at")
    if pos.receipt_issued_at < pos.transaction_started_at:
        raise HTTPException(status_code=400, detail="receipt_issued_at must be >= transaction_started_at")
    if pos.correction_type and not pos.original_header_id:
        raise HTTPException(status_code=400, detail="original_header_id required for correction_type")


def _upsert_pos_compliance(
    db: Session,
    *,
    tenant_id: str,
    header_id: str,
    pos: Optional[PosComplianceInput],
) -> None:
    if pos is None:
        return
    db.execute(
        text(
            """
            INSERT INTO domain_docflow.pos_receipt_compliance
            (id, tenant_id, header_id, terminal_id, cash_register_id, transaction_type, payment_breakdown,
             tse_transaction_id, tse_signature, tse_signature_counter, transaction_started_at, transaction_ended_at,
             receipt_issued_at, dsfinvk_export_batch_id, correction_type, original_header_id, created_at, updated_at)
            VALUES
            (:id, :tenant_id, :header_id, :terminal_id, :cash_register_id, :transaction_type, CAST(:payment_breakdown AS jsonb),
             :tse_transaction_id, :tse_signature, :tse_signature_counter, :transaction_started_at, :transaction_ended_at,
             :receipt_issued_at, :dsfinvk_export_batch_id, :correction_type, :original_header_id, NOW(), NOW())
            ON CONFLICT ON CONSTRAINT uq_pos_tse_header
            DO UPDATE SET
              terminal_id = EXCLUDED.terminal_id,
              cash_register_id = EXCLUDED.cash_register_id,
              transaction_type = EXCLUDED.transaction_type,
              payment_breakdown = EXCLUDED.payment_breakdown,
              tse_transaction_id = EXCLUDED.tse_transaction_id,
              tse_signature = EXCLUDED.tse_signature,
              tse_signature_counter = EXCLUDED.tse_signature_counter,
              transaction_started_at = EXCLUDED.transaction_started_at,
              transaction_ended_at = EXCLUDED.transaction_ended_at,
              receipt_issued_at = EXCLUDED.receipt_issued_at,
              dsfinvk_export_batch_id = EXCLUDED.dsfinvk_export_batch_id,
              correction_type = EXCLUDED.correction_type,
              original_header_id = EXCLUDED.original_header_id,
              updated_at = NOW()
            """
        ),
        {
            "id": str(uuid4()),
            "tenant_id": tenant_id,
            "header_id": header_id,
            "terminal_id": pos.terminal_id,
            "cash_register_id": pos.cash_register_id,
            "transaction_type": pos.transaction_type,
            "payment_breakdown": json.dumps(pos.payment_breakdown or {}),
            "tse_transaction_id": pos.tse_transaction_id,
            "tse_signature": pos.tse_signature,
            "tse_signature_counter": pos.tse_signature_counter,
            "transaction_started_at": pos.transaction_started_at,
            "transaction_ended_at": pos.transaction_ended_at,
            "receipt_issued_at": pos.receipt_issued_at,
            "dsfinvk_export_batch_id": pos.dsfinvk_export_batch_id,
            "correction_type": pos.correction_type,
            "original_header_id": pos.original_header_id,
        },
    )


def _bootstrap_sales_order_if_needed(db: Session, tenant_id: str, doc_id: str) -> Optional[dict[str, Any]]:
    existing = _fetch_doc_header(db, tenant_id, doc_id)
    if existing:
        return existing

    src = db.execute(
        text(
            """
            SELECT id, tenant_id, order_number, customer_id, currency, status, created_at, updated_at
            FROM domain_crm.sales_orders
            WHERE tenant_id = :tenant_id AND id = :id AND deleted_at IS NULL
            """
        ),
        {"tenant_id": tenant_id, "id": doc_id},
    ).mappings().first()
    if not src:
        return None

    src_d = dict(src)
    src_items = db.execute(
        text(
            """
            SELECT id, line_number, article_number, description, quantity, unit_price, discount_percent
            FROM domain_crm.sales_order_items
            WHERE order_id = :order_id
            ORDER BY line_number ASC
            """
        ),
        {"order_id": doc_id},
    ).mappings().all()

    total_net = Decimal("0.00")
    total_tax = Decimal("0.00")
    total_gross = Decimal("0.00")
    now = datetime.now(timezone.utc)

    db.execute(
        text(
            """
            INSERT INTO domain_docflow.document_headers
            (id, tenant_id, doc_type, doc_number, status, source_system, source_ref, customer_id, supplier_id,
             currency, total_net, total_tax, total_gross, document_date, version, created_at, updated_at)
            VALUES
            (:id, :tenant_id, 'sales_order', :doc_number, :status, 'domain_crm.sales_orders', :source_ref, :customer_id, NULL,
             :currency, 0, 0, 0, :document_date, 1, :created_at, :updated_at)
            """
        ),
        {
            "id": str(src_d["id"]),
            "tenant_id": tenant_id,
            "doc_number": src_d["order_number"],
            "status": "open" if (src_d.get("status") or "open") not in {"posted", "reversed"} else src_d["status"],
            "source_ref": str(src_d["id"]),
            "customer_id": str(src_d["customer_id"]) if src_d.get("customer_id") else None,
            "currency": src_d.get("currency") or "EUR",
            "document_date": src_d.get("created_at") or now,
            "created_at": src_d.get("created_at") or now,
            "updated_at": src_d.get("updated_at") or now,
        },
    )

    for item in src_items:
        qty_value = Decimal(str(item.get("quantity") or 0))
        price = Decimal(str(item.get("unit_price") or 0))
        discount = Decimal(str(item.get("discount_percent") or 0))
        tax_rate = Decimal("0")
        line_net, line_tax, line_gross = _line_amounts(qty_value, price, discount, tax_rate)
        total_net += line_net
        total_tax += line_tax
        total_gross += line_gross
        db.execute(
            text(
                """
                INSERT INTO domain_docflow.document_items
                (id, tenant_id, header_id, line_number, source_line_id, article_number, description, quantity, unit,
                 unit_price, discount_percent, tax_rate, line_total_net, line_total_tax, line_total_gross, created_at, updated_at)
                VALUES
                (:id, :tenant_id, :header_id, :line_number, :source_line_id, :article_number, :description, :quantity, NULL,
                 :unit_price, :discount_percent, :tax_rate, :line_total_net, :line_total_tax, :line_total_gross, NOW(), NOW())
                """
            ),
            {
                "id": str(uuid4()),
                "tenant_id": tenant_id,
                "header_id": doc_id,
                "line_number": int(item.get("line_number") or 0),
                "source_line_id": str(item["id"]),
                "article_number": item.get("article_number") or "",
                "description": item.get("description"),
                "quantity": _qty(qty_value),
                "unit_price": price,
                "discount_percent": discount,
                "tax_rate": tax_rate,
                "line_total_net": line_net,
                "line_total_tax": line_tax,
                "line_total_gross": line_gross,
            },
        )

    db.execute(
        text(
            """
            UPDATE domain_docflow.document_headers
            SET total_net = :total_net, total_tax = :total_tax, total_gross = :total_gross, updated_at = NOW()
            WHERE id = :id AND tenant_id = :tenant_id
            """
        ),
        {
            "id": doc_id,
            "tenant_id": tenant_id,
            "total_net": _money(total_net),
            "total_tax": _money(total_tax),
            "total_gross": _money(total_gross),
        },
    )
    return _fetch_doc_header(db, tenant_id, doc_id)


def _allocate_doc_number(db: Session, tenant_id: str, doc_type: str, now: datetime) -> str:
    year = now.year
    prefix = _DOC_PREFIX.get(doc_type, "DOC")
    row = db.execute(
        text(
            """
            SELECT id, counter, prefix, width
            FROM domain_docflow.number_series
            WHERE tenant_id = :tenant_id AND doc_type = :doc_type AND year = :year
            FOR UPDATE
            """
        ),
        {"tenant_id": tenant_id, "doc_type": doc_type, "year": year},
    ).mappings().first()
    if not row:
        current = 1
        width = 6
        db.execute(
            text(
                """
                INSERT INTO domain_docflow.number_series
                (id, tenant_id, doc_type, year, prefix, counter, width, updated_at)
                VALUES (:id, :tenant_id, :doc_type, :year, :prefix, 2, :width, NOW())
                """
            ),
            {
                "id": str(uuid4()),
                "tenant_id": tenant_id,
                "doc_type": doc_type,
                "year": year,
                "prefix": prefix,
                "width": width,
            },
        )
    else:
        current = int(row["counter"])
        width = int(row["width"])
        prefix = row.get("prefix") or prefix
        db.execute(
            text("UPDATE domain_docflow.number_series SET counter = :counter, updated_at = NOW() WHERE id = :id"),
            {"counter": current + 1, "id": row["id"]},
        )
    return f"{prefix}-{year}-{str(current).zfill(width)}"


def _load_idempotent_response(
    db: Session, *, tenant_id: str, command_name: str, resource_id: str, idempotency_key: str
) -> Optional[dict[str, Any]]:
    row = db.execute(
        text(
            """
            SELECT response_payload
            FROM domain_docflow.command_idempotency_keys
            WHERE tenant_id = :tenant_id AND command_name = :command_name
              AND resource_id = :resource_id AND idempotency_key = :idempotency_key
            """
        ),
        {
            "tenant_id": tenant_id,
            "command_name": command_name,
            "resource_id": resource_id,
            "idempotency_key": idempotency_key,
        },
    ).mappings().first()
    return dict(row["response_payload"]) if row and row.get("response_payload") else None


def _store_idempotent_response(
    db: Session,
    *,
    tenant_id: str,
    command_name: str,
    resource_id: str,
    idempotency_key: str,
    response_payload: dict[str, Any],
) -> None:
    db.execute(
        text(
            """
            INSERT INTO domain_docflow.command_idempotency_keys
            (id, tenant_id, command_name, resource_id, idempotency_key, response_payload, created_at)
            VALUES (:id, :tenant_id, :command_name, :resource_id, :idempotency_key, CAST(:response_payload AS jsonb), NOW())
            ON CONFLICT ON CONSTRAINT uq_docflow_command_idempotency
            DO UPDATE SET response_payload = EXCLUDED.response_payload
            """
        ),
        {
            "id": str(uuid4()),
            "tenant_id": tenant_id,
            "command_name": command_name,
            "resource_id": resource_id,
            "idempotency_key": idempotency_key,
            "response_payload": json.dumps(response_payload),
        },
    )


def _best_effort_audit(
    db: Session, *, tenant_id: str, action: str, resource_type: str, resource_id: str, payload: dict[str, Any]
) -> None:
    try:
        db.execute(
            text(
                """
                INSERT INTO infrastructure.audit_log
                (id, user_id, action, resource_type, resource_id, old_values, new_values, ip_address, user_agent, timestamp)
                VALUES
                (CAST(:id AS uuid), NULL, :action, :resource_type, CAST(:resource_id AS uuid), '{}'::jsonb, CAST(:new_values AS jsonb), NULL, NULL, NOW())
                """
            ),
            {
                "id": str(uuid4()),
                "action": action,
                "resource_type": resource_type,
                "resource_id": str(uuid5(NAMESPACE_URL, f"{resource_type}:{resource_id}")),
                "new_values": json.dumps({"tenant_id": tenant_id, **payload}),
            },
        )
    except Exception:
        pass


def _upsert_outbox_event(
    db: Session, *, tenant_id: str, event_type: str, aggregate_id: str, payload: dict[str, Any]
) -> str:
    event_id = str(uuid4())
    db.execute(
        text(
            """
            INSERT INTO outbox_events
            (id, event_type, aggregate_id, payload, timestamp, published, retry_count, tenant_id)
            VALUES (:id, :event_type, :aggregate_id, :payload, NOW(), FALSE, 0, :tenant_id)
            """
        ),
        {
            "id": event_id,
            "event_type": event_type,
            "aggregate_id": aggregate_id,
            "payload": json.dumps(payload),
            "tenant_id": tenant_id,
        },
    )
    return event_id


def _row_to_header_out(db: Session, tenant_id: str, header_id: str) -> DocflowHeaderOut:
    header = _fetch_doc_header(db, tenant_id, header_id)
    if not header:
        raise HTTPException(status_code=404, detail="Document not found")
    items = _fetch_doc_items(db, tenant_id, header_id)
    pos_compliance = _fetch_pos_compliance(db, tenant_id, header_id)
    return DocflowHeaderOut(
        id=str(header["id"]),
        tenant_id=str(header["tenant_id"]),
        doc_type=str(header["doc_type"]),
        doc_number=str(header["doc_number"]),
        status=str(header["status"]),
        source_system=str(header["source_system"]),
        source_ref=header.get("source_ref"),
        customer_id=header.get("customer_id"),
        supplier_id=header.get("supplier_id"),
        currency=str(header.get("currency") or "EUR"),
        total_net=float(header.get("total_net") or 0),
        total_tax=float(header.get("total_tax") or 0),
        total_gross=float(header.get("total_gross") or 0),
        document_date=header["document_date"],
        posting_date=header.get("posting_date"),
        version=int(header.get("version") or 1),
        created_at=header["created_at"],
        updated_at=header["updated_at"],
        pos_compliance=pos_compliance,
        items=[
            DocflowItemOut(
                id=str(i["id"]),
                line_number=int(i.get("line_number") or 0),
                source_line_id=i.get("source_line_id"),
                article_number=str(i.get("article_number") or ""),
                description=i.get("description"),
                quantity=float(i.get("quantity") or 0),
                unit=i.get("unit"),
                unit_price=float(i.get("unit_price") or 0),
                discount_percent=float(i.get("discount_percent") or 0),
                tax_rate=float(i.get("tax_rate") or 0),
                line_total_net=float(i.get("line_total_net") or 0),
                line_total_tax=float(i.get("line_total_tax") or 0),
                line_total_gross=float(i.get("line_total_gross") or 0),
            )
            for i in items
        ],
    )


@router.get("/", response_model=list[DocflowHeaderOut])
async def list_documents(
    tenant_id: Optional[str] = Query(None),
    doc_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    effective_tenant = tenant_id or DEFAULT_TENANT
    where = ["tenant_id = :tenant_id", "deleted_at IS NULL"]
    params: dict[str, Any] = {"tenant_id": effective_tenant, "limit": limit}
    if doc_type:
        where.append("doc_type = :doc_type")
        params["doc_type"] = doc_type
    rows = db.execute(
        text(
            f"""
            SELECT id
            FROM domain_docflow.document_headers
            WHERE {" AND ".join(where)}
            ORDER BY created_at DESC
            LIMIT :limit
            """
        ),
        params,
    ).mappings().all()
    return [_row_to_header_out(db, effective_tenant, str(r["id"])) for r in rows]


@router.get("/{doc_id}", response_model=DocflowHeaderOut)
async def get_document(
    doc_id: str,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    effective_tenant = tenant_id or DEFAULT_TENANT
    bootstrapped = _bootstrap_sales_order_if_needed(db, effective_tenant, doc_id)
    if not bootstrapped:
        raise HTTPException(status_code=404, detail="Document not found")
    db.commit()
    return _row_to_header_out(db, effective_tenant, doc_id)


@router.get("/{doc_id}/pos-compliance", response_model=dict[str, Any])
async def get_pos_compliance(
    doc_id: str,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    effective_tenant = tenant_id or DEFAULT_TENANT
    header = _fetch_doc_header(db, effective_tenant, doc_id)
    if not header:
        raise HTTPException(status_code=404, detail="Document not found")
    payload = _fetch_pos_compliance(db, effective_tenant, doc_id)
    if not payload:
        raise HTTPException(status_code=404, detail="POS compliance not found")
    return payload


@router.post("/", response_model=DocflowHeaderOut)
async def create_document(
    payload: DocflowCreateRequest,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    effective_tenant = tenant_id or DEFAULT_TENANT
    _validate_pos_compliance_requirements(payload.doc_type, payload.pos_compliance)
    now = datetime.now(timezone.utc)
    doc_id = str(uuid4())

    total_net = Decimal("0")
    total_tax = Decimal("0")
    total_gross = Decimal("0")
    for line in payload.items:
        line_net, line_tax, line_gross = _line_amounts(
            _qty(Decimal(str(line.quantity))),
            Decimal(str(line.unit_price)),
            Decimal(str(line.discount_percent)),
            Decimal(str(line.tax_rate)),
        )
        total_net += line_net
        total_tax += line_tax
        total_gross += line_gross

    try:
        db.execute(
            text(
                """
                INSERT INTO domain_docflow.document_headers
                (id, tenant_id, doc_type, doc_number, status, source_system, source_ref, customer_id, supplier_id,
                 currency, total_net, total_tax, total_gross, document_date, posting_date, version, created_by, updated_by, created_at, updated_at)
                VALUES
                (:id, :tenant_id, :doc_type, :doc_number, :status, :source_system, :source_ref, :customer_id, :supplier_id,
                 :currency, :total_net, :total_tax, :total_gross, :document_date, :posting_date, 1, :created_by, :updated_by, NOW(), NOW())
                """
            ),
            {
                "id": doc_id,
                "tenant_id": effective_tenant,
                "doc_type": payload.doc_type,
                "doc_number": payload.doc_number,
                "status": payload.status,
                "source_system": payload.source_system or "docflow.ui",
                "source_ref": payload.source_ref,
                "customer_id": payload.customer_id,
                "supplier_id": payload.supplier_id,
                "currency": payload.currency,
                "total_net": _money(total_net),
                "total_tax": _money(total_tax),
                "total_gross": _money(total_gross),
                "document_date": payload.document_date or now,
                "posting_date": payload.posting_date,
                "created_by": payload.created_by,
                "updated_by": payload.created_by,
            },
        )

        for idx, line in enumerate(payload.items, start=1):
            qty_value = _qty(Decimal(str(line.quantity)))
            price = Decimal(str(line.unit_price))
            discount = Decimal(str(line.discount_percent))
            tax_rate = Decimal(str(line.tax_rate))
            line_net, line_tax, line_gross = _line_amounts(qty_value, price, discount, tax_rate)
            db.execute(
                text(
                    """
                    INSERT INTO domain_docflow.document_items
                    (id, tenant_id, header_id, line_number, source_line_id, article_number, description, quantity, unit,
                     unit_price, discount_percent, tax_rate, line_total_net, line_total_tax, line_total_gross, batch_id, charge, created_at, updated_at)
                    VALUES
                    (:id, :tenant_id, :header_id, :line_number, NULL, :article_number, :description, :quantity, :unit,
                     :unit_price, :discount_percent, :tax_rate, :line_total_net, :line_total_tax, :line_total_gross, :batch_id, :charge, NOW(), NOW())
                    """
                ),
                {
                    "id": str(uuid4()),
                    "tenant_id": effective_tenant,
                    "header_id": doc_id,
                    "line_number": idx,
                    "article_number": line.article_number,
                    "description": line.description,
                    "quantity": qty_value,
                    "unit": line.unit,
                    "unit_price": price,
                    "discount_percent": discount,
                    "tax_rate": tax_rate,
                    "line_total_net": line_net,
                    "line_total_tax": line_tax,
                    "line_total_gross": line_gross,
                    "batch_id": line.batch_id,
                    "charge": line.charge,
                },
            )

        _upsert_pos_compliance(
            db,
            tenant_id=effective_tenant,
            header_id=doc_id,
            pos=payload.pos_compliance,
        )

        _best_effort_audit(
            db,
            tenant_id=effective_tenant,
            action="docflow_create",
            resource_type="docflow_document",
            resource_id=doc_id,
            payload={"doc_type": payload.doc_type, "doc_number": payload.doc_number, "status": payload.status},
        )
        db.commit()
        return _row_to_header_out(db, effective_tenant, doc_id)
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"create failed: {exc}") from exc


@router.put("/{doc_id}", response_model=DocflowHeaderOut)
async def update_document(
    doc_id: str,
    payload: DocflowUpdateRequest,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    effective_tenant = tenant_id or DEFAULT_TENANT
    header = _fetch_doc_header(db, effective_tenant, doc_id)
    if not header:
        raise HTTPException(status_code=404, detail="Document not found")
    if payload.expected_version and int(header.get("version") or 1) != payload.expected_version:
        raise HTTPException(status_code=409, detail="Version conflict")
    if str(header.get("status")) in {"posted", "reversed", "cancelled"}:
        raise HTTPException(status_code=409, detail="Posted/Reversed/Cancelled document cannot be edited")
    effective_doc_type = str(header.get("doc_type") or "")
    _validate_pos_compliance_requirements(effective_doc_type, payload.pos_compliance)

    try:
        updates: dict[str, Any] = {
            "id": doc_id,
            "tenant_id": effective_tenant,
            "updated_by": payload.updated_by,
        }
        set_parts: list[str] = ["updated_at = NOW()", "version = version + 1", "updated_by = :updated_by"]
        if payload.status is not None:
            set_parts.append("status = :status")
            updates["status"] = payload.status
        if payload.customer_id is not None:
            set_parts.append("customer_id = :customer_id")
            updates["customer_id"] = payload.customer_id
        if payload.source_system is not None:
            set_parts.append("source_system = :source_system")
            updates["source_system"] = payload.source_system
        if payload.source_ref is not None:
            set_parts.append("source_ref = :source_ref")
            updates["source_ref"] = payload.source_ref
        if payload.supplier_id is not None:
            set_parts.append("supplier_id = :supplier_id")
            updates["supplier_id"] = payload.supplier_id
        if payload.currency is not None:
            set_parts.append("currency = :currency")
            updates["currency"] = payload.currency
        if payload.document_date is not None:
            set_parts.append("document_date = :document_date")
            updates["document_date"] = payload.document_date
        if payload.posting_date is not None:
            set_parts.append("posting_date = :posting_date")
            updates["posting_date"] = payload.posting_date

        db.execute(
            text(f"UPDATE domain_docflow.document_headers SET {', '.join(set_parts)} WHERE id = :id AND tenant_id = :tenant_id"),
            updates,
        )

        if payload.items is not None:
            db.execute(
                text("DELETE FROM domain_docflow.document_items WHERE tenant_id = :tenant_id AND header_id = :header_id"),
                {"tenant_id": effective_tenant, "header_id": doc_id},
            )
            total_net = Decimal("0")
            total_tax = Decimal("0")
            total_gross = Decimal("0")
            for idx, line in enumerate(payload.items, start=1):
                qty_value = _qty(Decimal(str(line.quantity)))
                price = Decimal(str(line.unit_price))
                discount = Decimal(str(line.discount_percent))
                tax_rate = Decimal(str(line.tax_rate))
                line_net, line_tax, line_gross = _line_amounts(qty_value, price, discount, tax_rate)
                total_net += line_net
                total_tax += line_tax
                total_gross += line_gross
                db.execute(
                    text(
                        """
                        INSERT INTO domain_docflow.document_items
                        (id, tenant_id, header_id, line_number, source_line_id, article_number, description, quantity, unit,
                         unit_price, discount_percent, tax_rate, line_total_net, line_total_tax, line_total_gross, batch_id, charge, created_at, updated_at)
                        VALUES
                        (:id, :tenant_id, :header_id, :line_number, NULL, :article_number, :description, :quantity, :unit,
                         :unit_price, :discount_percent, :tax_rate, :line_total_net, :line_total_tax, :line_total_gross, :batch_id, :charge, NOW(), NOW())
                        """
                    ),
                    {
                        "id": str(uuid4()),
                        "tenant_id": effective_tenant,
                        "header_id": doc_id,
                        "line_number": idx,
                        "article_number": line.article_number,
                        "description": line.description,
                        "quantity": qty_value,
                        "unit": line.unit,
                        "unit_price": price,
                        "discount_percent": discount,
                        "tax_rate": tax_rate,
                        "line_total_net": line_net,
                        "line_total_tax": line_tax,
                        "line_total_gross": line_gross,
                        "batch_id": line.batch_id,
                        "charge": line.charge,
                    },
                )

            db.execute(
                text(
                    """
                    UPDATE domain_docflow.document_headers
                    SET total_net = :total_net, total_tax = :total_tax, total_gross = :total_gross
                    WHERE id = :id AND tenant_id = :tenant_id
                    """
                ),
                {
                    "id": doc_id,
                    "tenant_id": effective_tenant,
                    "total_net": _money(total_net),
                    "total_tax": _money(total_tax),
                    "total_gross": _money(total_gross),
                },
            )

        _upsert_pos_compliance(
            db,
            tenant_id=effective_tenant,
            header_id=doc_id,
            pos=payload.pos_compliance,
        )

        _best_effort_audit(
            db,
            tenant_id=effective_tenant,
            action="docflow_update",
            resource_type="docflow_document",
            resource_id=doc_id,
            payload={"updated_by": payload.updated_by},
        )
        db.commit()
        return _row_to_header_out(db, effective_tenant, doc_id)
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"update failed: {exc}") from exc


@router.post("/{doc_id}/convert", response_model=DocflowCommandResult)
async def convert_document(
    doc_id: str,
    payload: DocflowConvertRequest,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    effective_tenant = tenant_id or DEFAULT_TENANT
    idempotent = _load_idempotent_response(
        db,
        tenant_id=effective_tenant,
        command_name="convert",
        resource_id=doc_id,
        idempotency_key=payload.idempotency_key,
    )
    if idempotent:
        return DocflowCommandResult(**idempotent, idempotent_hit=True)

    try:
        source = _bootstrap_sales_order_if_needed(db, effective_tenant, doc_id)
        if not source:
            raise HTTPException(status_code=404, detail="Source document not found")
        if payload.expected_version and int(source.get("version") or 1) != payload.expected_version:
            raise HTTPException(status_code=409, detail="Version conflict")

        source_type = str(source["doc_type"])
        relation_type = _TRANSITIONS.get(source_type, {}).get(payload.target_doc_type)
        if not relation_type:
            raise HTTPException(status_code=400, detail=f"Transition not allowed: {source_type} -> {payload.target_doc_type}")
        source_pos = _fetch_pos_compliance(db, effective_tenant, doc_id)
        if payload.target_doc_type in _POS_TYPES and not source_pos:
            raise HTTPException(status_code=400, detail="POS conversion requires source POS compliance")

        source_items = _fetch_doc_items(db, effective_tenant, doc_id)
        selected_items: list[dict[str, Any]] = []
        for item in source_items:
            src_qty = Decimal(str(item.get("quantity") or 0))
            target_qty = src_qty
            if payload.quantities_by_source_item_id:
                raw = payload.quantities_by_source_item_id.get(str(item["id"]))
                if raw is None:
                    continue
                target_qty = Decimal(str(raw))
                if target_qty < 0:
                    raise HTTPException(status_code=400, detail="Negative quantity in partial conversion")
                if target_qty > src_qty:
                    raise HTTPException(status_code=400, detail="Partial conversion exceeds source quantity")
            if target_qty > 0:
                selected_items.append({"item": item, "target_qty": _qty(target_qty)})
        if not selected_items:
            raise HTTPException(status_code=400, detail="No convertible item quantities provided")

        total_net = Decimal("0")
        total_tax = Decimal("0")
        total_gross = Decimal("0")
        for entry in selected_items:
            src = entry["item"]
            qty_value = entry["target_qty"]
            price = Decimal(str(src.get("unit_price") or 0))
            discount = Decimal(str(src.get("discount_percent") or 0))
            tax_rate = Decimal(str(src.get("tax_rate") or 0))
            line_net, line_tax, line_gross = _line_amounts(qty_value, price, discount, tax_rate)
            total_net += line_net
            total_tax += line_tax
            total_gross += line_gross

        if payload.dry_run:
            return DocflowCommandResult(
                command="convert",
                source_doc_id=doc_id,
                status="dry_run",
                payload={
                    "source_doc_type": source_type,
                    "target_doc_type": payload.target_doc_type,
                    "relation_type": relation_type,
                    "item_count": len(selected_items),
                    "total_net": float(_money(total_net)),
                    "total_tax": float(_money(total_tax)),
                    "total_gross": float(_money(total_gross)),
                },
            )

        now = datetime.now(timezone.utc)
        target_id = str(uuid4())
        target_number = _allocate_doc_number(db, effective_tenant, payload.target_doc_type, now)
        db.execute(
            text(
                """
                INSERT INTO domain_docflow.document_headers
                (id, tenant_id, doc_type, doc_number, status, source_system, source_ref, customer_id, supplier_id,
                 currency, total_net, total_tax, total_gross, document_date, version, created_by, updated_by, created_at, updated_at)
                VALUES
                (:id, :tenant_id, :doc_type, :doc_number, 'open', 'docflow.convert', :source_ref, :customer_id, :supplier_id,
                 :currency, :total_net, :total_tax, :total_gross, :document_date, 1, :created_by, :updated_by, NOW(), NOW())
                """
            ),
            {
                "id": target_id,
                "tenant_id": effective_tenant,
                "doc_type": payload.target_doc_type,
                "doc_number": target_number,
                "source_ref": doc_id,
                "customer_id": source.get("customer_id"),
                "supplier_id": source.get("supplier_id"),
                "currency": source.get("currency") or "EUR",
                "total_net": _money(total_net),
                "total_tax": _money(total_tax),
                "total_gross": _money(total_gross),
                "document_date": now,
                "created_by": payload.created_by,
                "updated_by": payload.created_by,
            },
        )

        line_no = 1
        for entry in selected_items:
            src = entry["item"]
            qty_value = entry["target_qty"]
            price = Decimal(str(src.get("unit_price") or 0))
            discount = Decimal(str(src.get("discount_percent") or 0))
            tax_rate = Decimal(str(src.get("tax_rate") or 0))
            line_net, line_tax, line_gross = _line_amounts(qty_value, price, discount, tax_rate)
            target_item_id = str(uuid4())
            db.execute(
                text(
                    """
                    INSERT INTO domain_docflow.document_items
                    (id, tenant_id, header_id, line_number, source_line_id, article_number, description, quantity,
                     unit, unit_price, discount_percent, tax_rate, line_total_net, line_total_tax, line_total_gross, metadata, created_at, updated_at)
                    VALUES
                    (:id, :tenant_id, :header_id, :line_number, :source_line_id, :article_number, :description, :quantity,
                     :unit, :unit_price, :discount_percent, :tax_rate, :line_total_net, :line_total_tax, :line_total_gross, CAST(:metadata AS jsonb), NOW(), NOW())
                    """
                ),
                {
                    "id": target_item_id,
                    "tenant_id": effective_tenant,
                    "header_id": target_id,
                    "line_number": line_no,
                    "source_line_id": str(src["id"]),
                    "article_number": src.get("article_number") or "",
                    "description": src.get("description"),
                    "quantity": qty_value,
                    "unit": src.get("unit"),
                    "unit_price": price,
                    "discount_percent": discount,
                    "tax_rate": tax_rate,
                    "line_total_net": line_net,
                    "line_total_tax": line_tax,
                    "line_total_gross": line_gross,
                    "metadata": json.dumps({"converted_from": str(src["id"])}),
                },
            )
            db.execute(
                text(
                    """
                    INSERT INTO domain_docflow.document_links
                    (id, tenant_id, from_header_id, to_header_id, relation_type, from_item_id, to_item_id, quantity_linked, created_at)
                    VALUES
                    (:id, :tenant_id, :from_header_id, :to_header_id, :relation_type, :from_item_id, :to_item_id, :quantity_linked, NOW())
                    """
                ),
                {
                    "id": str(uuid4()),
                    "tenant_id": effective_tenant,
                    "from_header_id": doc_id,
                    "to_header_id": target_id,
                    "relation_type": relation_type,
                    "from_item_id": str(src["id"]),
                    "to_item_id": target_item_id,
                    "quantity_linked": qty_value,
                },
            )
            line_no += 1

        if payload.target_doc_type in _POS_TYPES and source_pos:
            correction_type = "storno" if payload.target_doc_type == "pos_storno" else "retoure"
            _upsert_pos_compliance(
                db,
                tenant_id=effective_tenant,
                header_id=target_id,
                pos=PosComplianceInput(
                    terminal_id=str(source_pos.get("terminal_id") or ""),
                    cash_register_id=source_pos.get("cash_register_id"),
                    transaction_type="storno" if correction_type == "storno" else "retoure",
                    payment_breakdown=source_pos.get("payment_breakdown") or {},
                    tse_transaction_id=f"{source_pos.get('tse_transaction_id')}-R",
                    tse_signature=str(source_pos.get("tse_signature") or ""),
                    tse_signature_counter=source_pos.get("tse_signature_counter"),
                    transaction_started_at=now,
                    transaction_ended_at=now,
                    receipt_issued_at=now,
                    dsfinvk_export_batch_id=source_pos.get("dsfinvk_export_batch_id"),
                    correction_type=correction_type,
                    original_header_id=doc_id,
                ),
            )

        event_id = _upsert_outbox_event(
            db,
            tenant_id=effective_tenant,
            event_type="docflow.document.converted",
            aggregate_id=target_id,
            payload={
                "source_doc_id": doc_id,
                "target_doc_id": target_id,
                "source_doc_type": source_type,
                "target_doc_type": payload.target_doc_type,
                "relation_type": relation_type,
                "idempotency_key": payload.idempotency_key,
            },
        )
        db.execute(
            text(
                """
                UPDATE domain_docflow.document_headers
                SET updated_at = NOW(), version = version + 1, updated_by = :updated_by
                WHERE id = :id AND tenant_id = :tenant_id
                """
            ),
            {"id": doc_id, "tenant_id": effective_tenant, "updated_by": payload.created_by},
        )

        response_payload = {
            "command": "convert",
            "source_doc_id": doc_id,
            "target_doc_id": target_id,
            "status": "ok",
            "payload": {
                "target_doc_number": target_number,
                "target_doc_type": payload.target_doc_type,
                "outbox_event_id": event_id,
                "total_gross": float(_money(total_gross)),
                "item_count": len(selected_items),
            },
        }
        _store_idempotent_response(
            db,
            tenant_id=effective_tenant,
            command_name="convert",
            resource_id=doc_id,
            idempotency_key=payload.idempotency_key,
            response_payload=response_payload,
        )
        _best_effort_audit(
            db,
            tenant_id=effective_tenant,
            action="docflow_convert",
            resource_type="docflow_document",
            resource_id=target_id,
            payload=response_payload,
        )
        db.commit()
        return DocflowCommandResult(**response_payload)
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"convert failed: {exc}") from exc


@router.post("/{doc_id}/post", response_model=DocflowCommandResult)
async def post_document(
    doc_id: str,
    payload: DocflowPostRequest,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    effective_tenant = tenant_id or DEFAULT_TENANT
    idempotent = _load_idempotent_response(
        db,
        tenant_id=effective_tenant,
        command_name="post",
        resource_id=doc_id,
        idempotency_key=payload.idempotency_key,
    )
    if idempotent:
        return DocflowCommandResult(**idempotent, idempotent_hit=True)

    try:
        header = _bootstrap_sales_order_if_needed(db, effective_tenant, doc_id)
        if not header:
            raise HTTPException(status_code=404, detail="Document not found")
        if payload.expected_version and int(header.get("version") or 1) != payload.expected_version:
            raise HTTPException(status_code=409, detail="Version conflict")
        if str(header.get("status")) in {"reversed", "cancelled"}:
            raise HTTPException(status_code=409, detail="Document cannot be posted in current status")
        if str(header.get("doc_type") or "") in _POS_TYPES:
            pos = _fetch_pos_compliance(db, effective_tenant, doc_id)
            if not pos:
                raise HTTPException(status_code=400, detail="POS posting requires POS/TSE compliance payload")

        posting_id = str(uuid4())
        outbox_event_id = _upsert_outbox_event(
            db,
            tenant_id=effective_tenant,
            event_type="docflow.document.posted",
            aggregate_id=doc_id,
            payload={"doc_id": doc_id, "doc_type": header.get("doc_type"), "idempotency_key": payload.idempotency_key},
        )

        db.execute(
            text(
                """
                INSERT INTO domain_docflow.document_postings
                (id, tenant_id, header_id, posting_type, journal_entry_id, amount, currency, idempotency_key, outbox_event_id, posted_by, posted_at)
                VALUES
                (:id, :tenant_id, :header_id, 'post', NULL, :amount, :currency, :idempotency_key, :outbox_event_id, :posted_by, NOW())
                """
            ),
            {
                "id": posting_id,
                "tenant_id": effective_tenant,
                "header_id": doc_id,
                "amount": Decimal(str(header.get("total_gross") or 0)),
                "currency": header.get("currency") or "EUR",
                "idempotency_key": payload.idempotency_key,
                "outbox_event_id": outbox_event_id,
                "posted_by": payload.posted_by,
            },
        )
        db.execute(
            text(
                """
                UPDATE domain_docflow.document_headers
                SET status = 'posted', posting_date = :posting_date, updated_at = NOW(), updated_by = :updated_by, version = version + 1
                WHERE id = :id AND tenant_id = :tenant_id
                """
            ),
            {
                "id": doc_id,
                "tenant_id": effective_tenant,
                "posting_date": payload.posting_date or date.today(),
                "updated_by": payload.posted_by,
            },
        )

        response_payload = {
            "command": "post",
            "source_doc_id": doc_id,
            "posting_id": posting_id,
            "status": "ok",
            "payload": {"outbox_event_id": outbox_event_id, "posting_date": str(payload.posting_date or date.today())},
        }
        _store_idempotent_response(
            db,
            tenant_id=effective_tenant,
            command_name="post",
            resource_id=doc_id,
            idempotency_key=payload.idempotency_key,
            response_payload=response_payload,
        )
        _best_effort_audit(
            db,
            tenant_id=effective_tenant,
            action="docflow_post",
            resource_type="docflow_document",
            resource_id=doc_id,
            payload=response_payload,
        )
        db.commit()
        return DocflowCommandResult(**response_payload)
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"post failed: {exc}") from exc


@router.post("/{doc_id}/reverse", response_model=DocflowCommandResult)
async def reverse_document(
    doc_id: str,
    payload: DocflowReverseRequest,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    effective_tenant = tenant_id or DEFAULT_TENANT
    idempotent = _load_idempotent_response(
        db,
        tenant_id=effective_tenant,
        command_name="reverse",
        resource_id=doc_id,
        idempotency_key=payload.idempotency_key,
    )
    if idempotent:
        return DocflowCommandResult(**idempotent, idempotent_hit=True)

    try:
        header = _fetch_doc_header(db, effective_tenant, doc_id)
        if not header:
            raise HTTPException(status_code=404, detail="Document not found")
        if payload.expected_version and int(header.get("version") or 1) != payload.expected_version:
            raise HTTPException(status_code=409, detail="Version conflict")
        if str(header.get("status")) == "reversed":
            raise HTTPException(status_code=409, detail="Document already reversed")

        posting_id = str(uuid4())
        outbox_event_id = _upsert_outbox_event(
            db,
            tenant_id=effective_tenant,
            event_type="docflow.document.reversed",
            aggregate_id=doc_id,
            payload={
                "doc_id": doc_id,
                "doc_type": header.get("doc_type"),
                "reason": payload.reason,
                "idempotency_key": payload.idempotency_key,
            },
        )
        db.execute(
            text(
                """
                INSERT INTO domain_docflow.document_postings
                (id, tenant_id, header_id, posting_type, journal_entry_id, amount, currency, idempotency_key, outbox_event_id, posted_by, posted_at)
                VALUES
                (:id, :tenant_id, :header_id, 'reverse', NULL, :amount, :currency, :idempotency_key, :outbox_event_id, :posted_by, NOW())
                """
            ),
            {
                "id": posting_id,
                "tenant_id": effective_tenant,
                "header_id": doc_id,
                "amount": Decimal(str(header.get("total_gross") or 0)),
                "currency": header.get("currency") or "EUR",
                "idempotency_key": payload.idempotency_key,
                "outbox_event_id": outbox_event_id,
                "posted_by": payload.reversed_by,
            },
        )
        db.execute(
            text(
                """
                UPDATE domain_docflow.document_headers
                SET status = 'reversed', updated_at = NOW(), updated_by = :updated_by, version = version + 1
                WHERE id = :id AND tenant_id = :tenant_id
                """
            ),
            {"id": doc_id, "tenant_id": effective_tenant, "updated_by": payload.reversed_by},
        )

        response_payload = {
            "command": "reverse",
            "source_doc_id": doc_id,
            "posting_id": posting_id,
            "status": "ok",
            "payload": {"reason": payload.reason, "outbox_event_id": outbox_event_id},
        }
        _store_idempotent_response(
            db,
            tenant_id=effective_tenant,
            command_name="reverse",
            resource_id=doc_id,
            idempotency_key=payload.idempotency_key,
            response_payload=response_payload,
        )
        _best_effort_audit(
            db,
            tenant_id=effective_tenant,
            action="docflow_reverse",
            resource_type="docflow_document",
            resource_id=doc_id,
            payload=response_payload,
        )
        db.commit()
        return DocflowCommandResult(**response_payload)
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"reverse failed: {exc}") from exc
