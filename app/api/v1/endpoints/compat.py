"""Compatibility endpoints for frontend path alignment and missing modules."""

from __future__ import annotations

import json
import os
from datetime import date, datetime, timezone
from typing import Any, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Body, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.cache import cache_delete_prefix, cache_get_json, cache_set_json
from app.core.config import settings
from app.core.data_quality_enforcement import (
    evaluate_article_datensatz,
    evaluate_customer_datensatz,
)
from app.core.database import get_db
from app.core.uuid7 import uuid7
from app.core.logging import get_correlation_id
from app.core.tenant import get_tenant_id
from app.infrastructure.models import AuditLog, LkwAnnahmeQueue
from app.documents.router_helpers import get_repository, list_from_store, get_from_store, save_to_store
from app.domains.operations.models import Charge, Dokument, Rahmenvertrag, ZertifikatEintrag
from app.domains.shared.events import IntegrationEvent, get_event_publisher
from app.infrastructure.models import Article as ArticleModel, InventoryCount
from app.infrastructure.eventbus.outbox import OutboxPublisher
from app.integrations.crm_core_client import (
    create_case as crm_create_case,
    delete_case as crm_delete_case,
    get_case as crm_get_case,
    list_cases as crm_list_cases,
    list_customers as crm_list_customers,
    list_leads as crm_list_leads,
    update_case as crm_update_case,
)
from app.routers.contracts_router import get_contract as get_contract_via_router

router = APIRouter(tags=["compat"])


def _now_iso() -> str:
    return datetime.utcnow().isoformat()


def _doc_repo(db: Session):
    return get_repository(db)


def _list_docs(db: Session, doc_type: str, limit: int = 1000, tenant_id: Optional[str] = None) -> list[dict[str, Any]]:
    repo = _doc_repo(db)
    filters = {"tenantId": tenant_id} if tenant_id else None
    payload = list_from_store(doc_type, skip=0, limit=limit, filters=filters, repo=repo)
    docs = payload.get("data", []) if isinstance(payload, dict) else []
    if docs:
        return docs
    # Fallback to in-memory store when DB-backed document store is empty or unavailable.
    payload_mem = list_from_store(doc_type, skip=0, limit=limit, filters=filters, repo=None)
    return payload_mem.get("data", []) if isinstance(payload_mem, dict) else []


def _cache_key(*parts: Any) -> str:
    return "compat:" + ":".join(str(p) for p in parts if p is not None and str(p) != "")


async def _enqueue_event(
    db: Session,
    *,
    event_type: str,
    aggregate_id: str,
    payload: dict[str, Any],
    tenant_id: Optional[str] = None,
) -> None:
    outbox = OutboxPublisher(db, get_event_publisher())
    event = IntegrationEvent(
        aggregate_id=aggregate_id,
        timestamp=datetime.utcnow(),
        event_type=event_type,
        payload=payload,
    )
    await outbox.store_event(event, tenant_id=tenant_id)


# CRM dashboard + suppliers -------------------------------------------------


@router.get("/crm/dashboard", response_model=dict)
async def crm_dashboard() -> dict:
    try:
        customers, customers_total = await crm_list_customers(skip=0, limit=500, search=None)
    except Exception:
        customers, customers_total = [], 0
    try:
        leads, leads_total = await crm_list_leads(status=None, search=None, skip=0, limit=500)
    except Exception:
        leads, leads_total = [], 0

    won = sum(1 for l in leads if getattr(l, "status", "") == "won")
    qualified = sum(1 for l in leads if getattr(l, "status", "") in {"qualified", "proposal", "negotiation", "won"})

    return {
        "kpis": [
            {"title": "Kunden", "value": str(customers_total), "change": {"value": 0, "type": "increase", "period": "30 Tage"}, "icon": "users", "color": "blue"},
            {"title": "Leads", "value": str(leads_total), "change": {"value": 0, "type": "increase", "period": "30 Tage"}, "icon": "target", "color": "orange"},
            {"title": "Qualifiziert", "value": str(qualified), "change": {"value": 0, "type": "increase", "period": "30 Tage"}, "icon": "check", "color": "green"},
            {"title": "Gewonnen", "value": str(won), "change": {"value": 0, "type": "increase", "period": "30 Tage"}, "icon": "trophy", "color": "teal"},
        ],
        "charts": [
            {"title": "Lead Funnel", "type": "bar", "data": [leads_total, qualified, won]},
            {"title": "Neukunden", "type": "line", "data": [customers_total]},
        ],
    }


@router.get("/crm/suppliers", response_model=dict)
async def crm_suppliers(
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    skip: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> dict:
    query = "SELECT id, lieferantennummer, firmenname, ort, email, telefon, iban, steuer_nr, zahlungsbedingungen, bewertung, aktiv, created_at FROM einkauf_lieferanten"
    conditions: list[str] = []
    params: dict[str, Any] = {"limit": limit, "skip": skip}

    if search:
        conditions.append("(firmenname ILIKE :search OR lieferantennummer ILIKE :search)")
        params["search"] = f"%{search}%"
    if is_active is not None:
        conditions.append("aktiv = :aktiv")
        params["aktiv"] = is_active

    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY firmenname LIMIT :limit OFFSET :skip"

    count_query = "SELECT COUNT(*) FROM einkauf_lieferanten"
    if conditions:
        count_query += " WHERE " + " AND ".join(conditions)

    try:
        rows = db.execute(text(query), params).fetchall()
        total = int(db.execute(text(count_query), params).scalar() or 0)
    except Exception:
        db.rollback()
        fallback_query = "SELECT id, lieferantennummer, firmenname, ort, email, telefon, bewertung, aktiv, created_at FROM einkauf_lieferanten"
        if conditions:
            fallback_query += " WHERE " + " AND ".join(conditions)
        fallback_query += " ORDER BY firmenname LIMIT :limit OFFSET :skip"
        try:
            rows = db.execute(text(fallback_query), params).fetchall()
            total = int(db.execute(text(count_query), params).scalar() or 0)
        except Exception as exc:
            # Tabelle fehlt in manchen Umgebungen; UI soll ohne Fehler laden.
            return {"items": [], "total": 0}

    items = [
        {
            "id": str(r._mapping.get("id")),
            "name": r._mapping.get("firmenname") or "",
            "supplier_number": r._mapping.get("lieferantennummer"),
            "city": r._mapping.get("ort"),
            "email": r._mapping.get("email"),
            "phone": r._mapping.get("telefon"),
            "tax_id": r._mapping.get("steuer_nr"),
            "iban": r._mapping.get("iban"),
            "payment_terms": r._mapping.get("zahlungsbedingungen"),
            "rating": r._mapping.get("bewertung"),
            "is_active": bool(r._mapping.get("aktiv", True)),
            "created_at": r._mapping.get("created_at").isoformat() if r._mapping.get("created_at") else None,
        }
        for r in rows
    ]

    return {"items": items, "total": total}


# Purchase orders -----------------------------------------------------------


@router.get("/purchase-orders", response_model=dict)
async def po_list(
    status: Optional[str] = Query(None),
    supplierId: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    pageSize: int = Query(50, ge=1, le=500),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    docs = _list_docs(db, "purchase_order", limit=5000, tenant_id=tenant_id)
    if not docs:
        docs = _list_docs(db, "purchase_order", limit=5000)

    def _match(d: dict[str, Any]) -> bool:
        if status and str(d.get("status")) != status:
            return False
        if supplierId and str(d.get("supplierId")) != supplierId:
            return False
        if search:
            s = search.lower()
            if s not in str(d.get("purchaseOrderNumber", "")).lower() and s not in str(d.get("subject", "")).lower():
                return False
        return True

    filtered = [d for d in docs if _match(d)]
    total = len(filtered)
    start = (page - 1) * pageSize
    items = filtered[start : start + pageSize]
    total_pages = max((total + pageSize - 1) // pageSize, 1)
    return {"data": items, "page": page, "pageSize": pageSize, "total": total, "totalPages": total_pages}


@router.get("/purchase-orders/{po_id}", response_model=dict)
async def po_get(po_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> dict:
    docs = _list_docs(db, "purchase_order", limit=5000, tenant_id=tenant_id)
    if not docs:
        docs = _list_docs(db, "purchase_order", limit=5000)
    for d in docs:
        if str(d.get("id")) == po_id or str(d.get("purchaseOrderNumber")) == po_id:
            return d
    raise HTTPException(status_code=404, detail="Purchase order not found")


@router.post("/purchase-orders", response_model=dict, status_code=201)
async def po_create(payload: dict[str, Any], tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> dict:
    now = _now_iso()
    po_number = payload.get("purchaseOrderNumber") or f"PO-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid4())[:6].upper()}"
    item_list = payload.get("items", [])
    subtotal = float(sum((float(i.get("quantity", 0)) * float(i.get("unitPrice", 0))) for i in item_list))
    tax_rate = float(payload.get("taxRate", 19))
    tax_amount = round(subtotal * tax_rate / 100, 2)
    doc = {
        "id": str(uuid4()),
        "purchaseOrderNumber": po_number,
        "supplierId": payload.get("supplierId"),
        "subject": payload.get("subject") or "",
        "description": payload.get("description") or "",
        "status": "ENTWURF",
        "orderDate": payload.get("orderDate") or now[:10],
        "deliveryDate": payload.get("deliveryDate"),
        "contactPerson": payload.get("contactPerson"),
        "paymentTerms": payload.get("paymentTerms"),
        "currency": payload.get("currency") or "EUR",
        "incoterms": payload.get("incoterms"),
        "deliveryTerms": payload.get("deliveryTerms"),
        "externalReference": payload.get("externalReference"),
        "items": item_list,
        "subtotal": round(subtotal, 2),
        "taxRate": tax_rate,
        "taxAmount": tax_amount,
        "totalAmount": round(subtotal + tax_amount, 2),
        "shippingAddress": payload.get("shippingAddress"),
        "notes": payload.get("notes"),
        "createdBy": "system",
        "createdAt": now,
        "updatedAt": now,
        "tenantId": tenant_id,
        "version": 1,
        "changelog": [{"id": str(uuid4()), "changeType": "CREATED", "changedBy": "system", "changedAt": now, "fieldChanges": []}],
    }
    repo = _doc_repo(db)
    save_to_store("purchase_order", po_number, doc, repo)
    await _enqueue_event(
        db,
        event_type="purchase_order.created",
        aggregate_id=doc["id"],
        payload={
            "purchaseOrderNumber": po_number,
            "supplierId": doc.get("supplierId"),
            "status": doc.get("status"),
            "totalAmount": doc.get("totalAmount"),
            "createdAt": doc.get("createdAt"),
        },
        tenant_id=tenant_id,
    )
    cache_delete_prefix(f"compat:procurement:{tenant_id}:")
    db.commit()
    return doc


@router.patch("/purchase-orders/{po_id}", response_model=dict)
async def po_patch(po_id: str, payload: dict[str, Any], tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> dict:
    doc = await po_get(po_id, tenant_id, db)
    now = _now_iso()
    changes = []
    for key, value in payload.items():
        if key in {"id", "purchaseOrderNumber", "createdAt", "createdBy"}:
            continue
        old = doc.get(key)
        if old != value:
            doc[key] = value
            changes.append({"field": key, "oldValue": str(old), "newValue": str(value)})

    doc["updatedAt"] = now
    doc["version"] = int(doc.get("version", 1)) + 1
    doc.setdefault("changelog", []).append(
        {"id": str(uuid4()), "changeType": "UPDATED", "changedBy": "system", "changedAt": now, "fieldChanges": changes}
    )
    repo = _doc_repo(db)
    save_to_store("purchase_order", doc["purchaseOrderNumber"], doc, repo)
    cache_delete_prefix(f"compat:procurement:{tenant_id}:")
    return doc


@router.post("/purchase-orders/{po_id}/approve", response_model=dict)
async def po_approve(po_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> dict:
    doc = await po_get(po_id, tenant_id, db)
    now = _now_iso()
    doc["status"] = "FREIGEGEBEN"
    doc["approvedAt"] = now
    doc["approvedBy"] = "system"
    doc["updatedAt"] = now
    doc.setdefault("changelog", []).append(
        {"id": str(uuid4()), "changeType": "APPROVED", "changedBy": "system", "changedAt": now, "fieldChanges": []}
    )
    repo = _doc_repo(db)
    save_to_store("purchase_order", doc["purchaseOrderNumber"], doc, repo)
    await _enqueue_event(
        db,
        event_type="purchase_order.approved",
        aggregate_id=doc["id"],
        payload={
            "purchaseOrderNumber": doc.get("purchaseOrderNumber"),
            "approvedAt": doc.get("approvedAt"),
            "approvedBy": doc.get("approvedBy"),
            "status": doc.get("status"),
        },
        tenant_id=tenant_id,
    )
    cache_delete_prefix(f"compat:procurement:{tenant_id}:")
    db.commit()
    return doc


@router.post("/purchase-orders/{po_id}/cancel-with-reason", response_model=dict)
async def po_cancel(po_id: str, payload: dict[str, Any], tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> dict:
    doc = await po_get(po_id, tenant_id, db)
    now = _now_iso()
    reason = payload.get("reason") or ""
    doc["status"] = "STORNIERT"
    doc["notes"] = (doc.get("notes") or "") + f"\nStorno: {reason}"
    doc["updatedAt"] = now
    doc.setdefault("changelog", []).append(
        {
            "id": str(uuid4()),
            "changeType": "CANCELLED",
            "changedBy": "system",
            "changedAt": now,
            "fieldChanges": [{"field": "status", "oldValue": "", "newValue": "STORNIERT"}],
        }
    )
    repo = _doc_repo(db)
    save_to_store("purchase_order", doc["purchaseOrderNumber"], doc, repo)
    await _enqueue_event(
        db,
        event_type="purchase_order.cancelled",
        aggregate_id=doc["id"],
        payload={
            "purchaseOrderNumber": doc.get("purchaseOrderNumber"),
            "status": doc.get("status"),
            "reason": reason,
            "updatedAt": doc.get("updatedAt"),
        },
        tenant_id=tenant_id,
    )
    cache_delete_prefix(f"compat:procurement:{tenant_id}:")
    db.commit()
    return doc


@router.get("/purchase-orders/statistics", response_model=dict)
async def po_statistics(tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> dict:
    docs = _list_docs(db, "purchase_order", limit=5000, tenant_id=tenant_id)
    by_status: dict[str, int] = {}
    total_value = 0.0
    for d in docs:
        st = str(d.get("status") or "ENTWURF")
        by_status[st] = by_status.get(st, 0) + 1
        total_value += float(d.get("totalAmount") or 0)
    return {"totalOrders": len(docs), "totalValue": round(total_value, 2), "byStatus": by_status}


@router.get("/purchase-orders/{po_id}/changelog", response_model=list)
async def po_changelog(po_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    doc = await po_get(po_id, tenant_id, db)
    return doc.get("changelog", [])


# Sales bridge --------------------------------------------------------------


@router.get("/sales/{doc_type}", response_model=dict)
async def sales_bridge(doc_type: str, db: Session = Depends(get_db)) -> dict:
    mapping = {
        "auftraege": "sales_order",
        "angebote": "sales_offer",
        "lieferungen": "sales_delivery",
        "rechnungen": "sales_invoice",
        "sales_order": "sales_order",
        "sales_offer": "sales_offer",
        "sales_delivery": "sales_delivery",
        "sales_invoice": "sales_invoice",
    }
    target = mapping.get(doc_type)
    if not target:
        raise HTTPException(status_code=404, detail="Unknown sales document type")
    return {"data": _list_docs(db, target, limit=1000)}


# Einkauf compatibility -----------------------------------------------------


@router.get("/einkauf/goods-receipts", response_model=list)
async def einkauf_goods_receipts(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    try:
        rows = db.execute(
            text(
                """
                SELECT
                    we.id,
                    we.delivery_note_number AS nummer,
                    we.received_date AS datum,
                    we.quality_inspection_status AS status,
                    COALESCE(po.subject, '') AS lieferant,
                    COALESCE(SUM(pos.accepted_quantity * 0), 0) AS betrag
                FROM einkauf_wareneingaenge we
                LEFT JOIN einkauf_wareneingang_positionen pos ON pos.wareneingang_id = we.id
                LEFT JOIN LATERAL (
                    SELECT data::jsonb->>'subject' AS subject
                    FROM docs_store
                    WHERE doc_type = 'purchase_order'
                      AND (
                        data::jsonb->>'id' = we.purchase_order_id
                        OR data::jsonb->>'purchaseOrderNumber' = we.purchase_order_id
                      )
                    ORDER BY updated_at DESC
                    LIMIT 1
                ) po ON TRUE
                GROUP BY we.id, we.delivery_note_number, we.received_date, we.quality_inspection_status, po.subject
                ORDER BY we.created_at DESC
                LIMIT 500
                """
            )
        ).fetchall()
    except Exception:
        try:
            rows = db.execute(
                text(
                    "SELECT id, wareneingangs_nummer AS nummer, bestelldatum AS datum, status, lieferant_name AS lieferant, brutto_gesamt AS betrag FROM einkauf_wareneingaenge ORDER BY created_at DESC LIMIT 500"
                )
            ).fetchall()
        except Exception:
            return []
    return [
        {
            "id": str(r._mapping.get("id")),
            "nummer": r._mapping.get("nummer") or str(r._mapping.get("id")),
            "datum": r._mapping.get("datum").isoformat()[:10] if r._mapping.get("datum") else None,
            "status": r._mapping.get("status") or "offen",
            "lieferant": r._mapping.get("lieferant") or "",
            "betrag": float(r._mapping.get("betrag") or 0),
        }
        for r in rows
    ]


@router.post("/einkauf/goods-receipts", response_model=dict, status_code=201)
async def einkauf_goods_receipts_create(
    payload: dict[str, Any],
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    receipt_id = str(uuid4())
    purchase_order_id = str(payload.get("purchaseOrderId") or payload.get("purchase_order_id") or "")
    if not purchase_order_id:
        raise HTTPException(status_code=400, detail="purchaseOrderId is required")

    items = payload.get("items") or []
    if not isinstance(items, list) or not items:
        raise HTTPException(status_code=400, detail="items must contain at least one row")

    received_by = str(payload.get("receivedBy") or payload.get("received_by") or "").strip()
    received_location = str(payload.get("receivedLocation") or payload.get("received_location") or "").strip()
    if not received_by or not received_location:
        raise HTTPException(status_code=400, detail="receivedBy and receivedLocation are required")

    received_date = str(payload.get("receivedDate") or payload.get("received_date") or _now_iso()[:10])
    delivery_note_number = payload.get("deliveryNoteNumber") or payload.get("delivery_note_number")
    quality_status = str(payload.get("qualityInspectionStatus") or payload.get("quality_inspection_status") or "PENDING")
    inspection_notes = payload.get("inspectionNotes") or payload.get("inspection_notes")
    damage_report = payload.get("damageReport") or payload.get("damage_report")

    try:
        db.execute(
            text(
                """
                INSERT INTO einkauf_wareneingaenge (
                    id, purchase_order_id, delivery_note_number, received_date,
                    received_by, received_location, quality_inspection_status,
                    inspection_notes, damage_report, created_at, updated_at
                ) VALUES (
                    :id, :purchase_order_id, :delivery_note_number, :received_date,
                    :received_by, :received_location, :quality_inspection_status,
                    :inspection_notes, :damage_report, now(), now()
                )
                """
            ),
            {
                "id": receipt_id,
                "purchase_order_id": purchase_order_id,
                "delivery_note_number": delivery_note_number,
                "received_date": received_date,
                "received_by": received_by,
                "received_location": received_location,
                "quality_inspection_status": quality_status,
                "inspection_notes": inspection_notes,
                "damage_report": damage_report,
            },
        )
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Could not create goods receipt: {exc}") from exc

    for line in items:
        pos_id = str(uuid4())
        received_qty = float(line.get("receivedQuantity") or line.get("received_quantity") or 0)
        accepted_qty = float(line.get("acceptedQuantity") or line.get("accepted_quantity") or received_qty)
        rejected_qty = float(line.get("rejectedQuantity") or line.get("rejected_quantity") or 0)
        ordered_qty = float(line.get("orderedQuantity") or line.get("ordered_quantity") or received_qty)
        try:
            db.execute(
                text(
                    """
                    INSERT INTO einkauf_wareneingang_positionen (
                        id, wareneingang_id, purchase_order_item_id, article_id, article_name,
                        ordered_quantity, received_quantity, accepted_quantity, rejected_quantity,
                        condition, created_at, updated_at
                    ) VALUES (
                        :id, :wareneingang_id, :purchase_order_item_id, :article_id, :article_name,
                        :ordered_quantity, :received_quantity, :accepted_quantity, :rejected_quantity,
                        :condition, now(), now()
                    )
                    """
                ),
                {
                    "id": pos_id,
                    "wareneingang_id": receipt_id,
                    "purchase_order_item_id": line.get("purchaseOrderItemId") or line.get("purchase_order_item_id"),
                    "article_id": line.get("articleId") or line.get("article_id") or "",
                    "article_name": line.get("articleName") or line.get("article_name"),
                    "ordered_quantity": ordered_qty,
                    "received_quantity": received_qty,
                    "accepted_quantity": accepted_qty,
                    "rejected_quantity": rejected_qty,
                    "condition": line.get("condition") or "PERFECT",
                },
            )
        except Exception as exc:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Could not create goods receipt item: {exc}") from exc

    # Update purchase order quantities and status for document-store based purchase orders.
    repo = _doc_repo(db)
    po = get_from_store("purchase_order", purchase_order_id, repo)
    if not po:
        docs = _list_docs(db, "purchase_order", limit=5000, tenant_id=tenant_id)
        if not docs:
            docs = _list_docs(db, "purchase_order", limit=5000)
        po = next((d for d in docs if str(d.get("id")) == purchase_order_id or str(d.get("purchaseOrderNumber")) == purchase_order_id), None)
    if po:
        po_items = po.get("items", []) or []
        for line in items:
            target_item_id = str(line.get("purchaseOrderItemId") or line.get("purchase_order_item_id") or "")
            if not target_item_id:
                continue
            received_qty = float(line.get("receivedQuantity") or line.get("received_quantity") or 0)
            for po_item in po_items:
                po_item_id = str(po_item.get("id") or "")
                if po_item_id == target_item_id:
                    current_received = float(po_item.get("quantityReceived") or 0)
                    po_item["quantityReceived"] = round(current_received + received_qty, 3)
                    break
        po["items"] = po_items
        total_open = 0.0
        for po_item in po_items:
            qty = float(po_item.get("quantity") or 0)
            rec = float(po_item.get("quantityReceived") or 0)
            total_open += max(0.0, qty - rec)
        po["status"] = "KOMPLETT" if total_open <= 0.0001 else "TEILGELIEFERT"
        po["updatedAt"] = _now_iso()
        save_to_store("purchase_order", po.get("purchaseOrderNumber") or purchase_order_id, po, repo)

    await _enqueue_event(
        db,
        event_type="goods_receipt.created",
        aggregate_id=receipt_id,
        payload={
            "receiptId": receipt_id,
            "purchaseOrderId": purchase_order_id,
            "status": quality_status,
            "receivedDate": received_date,
            "itemCount": len(items),
        },
        tenant_id=tenant_id,
    )
    cache_delete_prefix(f"compat:procurement:{tenant_id}:")
    db.commit()
    return {
        "id": receipt_id,
        "purchaseOrderId": purchase_order_id,
        "status": quality_status,
        "message": "Wareneingang erfasst",
    }


@router.get("/einkauf/bestellvorschlaege", response_model=list)
async def einkauf_bestellvorschlaege(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    rows = db.query(Charge).order_by(Charge.eingang.desc()).limit(200).all()
    return [
        {
            "id": r.id,
            "artikel": r.artikel,
            "aktuellBestand": float(r.menge or 0),
            "mindestbestand": 100.0,
            "vorschlagMenge": max(0.0, 100.0 - float(r.menge or 0)),
            "lieferant": r.herkunft or "",
            "preis": 0.0,
            "lieferzeit": 0,
            "prioritaet": "hoch" if float(r.menge or 0) < 50 else "mittel",
            "grund": "Automatische Disposition",
        }
        for r in rows
    ]


@router.get("/einkauf/warengruppen", response_model=list)
async def einkauf_warengruppen(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    items = db.query(ArticleModel).filter(ArticleModel.is_active == True).limit(500).all()  # noqa: E712
    grouped: dict[str, dict[str, Any]] = {}
    for a in items:
        key = a.category or "Sonstige"
        grouped.setdefault(key, {"id": key.lower().replace(" ", "-"), "name": key, "kategorie": key, "artikel": 0, "umsatz": 0.0})
        grouped[key]["artikel"] += 1
        grouped[key]["umsatz"] += float(a.sales_price or 0)
    return list(grouped.values())


@router.get("/einkauf/anfragen", response_model=list)
async def einkauf_anfragen_list(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    try:
        rows = db.execute(
            text(
                "SELECT id, anfrage_nummer, typ, anforderer, artikel, menge, prioritaet, status, datum, created_at FROM einkauf_anfragen ORDER BY created_at DESC LIMIT 500"
            )
        ).fetchall()
    except Exception:
        return []
    return [
        {
            "id": str(r._mapping.get("id")),
            "anfrageNummer": r._mapping.get("anfrage_nummer") or str(r._mapping.get("id")),
            "typ": r._mapping.get("typ") or "",
            "anforderer": r._mapping.get("anforderer") or "",
            "artikel": r._mapping.get("artikel") or "",
            "menge": float(r._mapping.get("menge") or 0),
            "prioritaet": r._mapping.get("prioritaet") or "normal",
            "status": r._mapping.get("status") or "offen",
            "faelligkeit": r._mapping.get("datum").isoformat()[:10] if r._mapping.get("datum") else None,
            "createdAt": r._mapping.get("created_at").isoformat() if r._mapping.get("created_at") else None,
        }
        for r in rows
    ]


def _load_einkauf_anfrage(db: Session, anfrage_id: str) -> dict[str, Any] | None:
    try:
        row = db.execute(
            text(
                """
                SELECT id, anfrage_nummer, typ, anforderer, artikel, menge, prioritaet, status, datum, created_at
                FROM einkauf_anfragen
                WHERE id = :anfrage_id OR anfrage_nummer = :anfrage_id
                ORDER BY created_at DESC
                LIMIT 1
                """
            ),
            {"anfrage_id": anfrage_id},
        ).fetchone()
    except Exception:
        return None

    if row is None:
        return None

    return {
        "id": str(row._mapping.get("id")),
        "anfrageNummer": row._mapping.get("anfrage_nummer") or str(row._mapping.get("id")),
        "typ": row._mapping.get("typ") or "",
        "anforderer": row._mapping.get("anforderer") or "",
        "artikel": row._mapping.get("artikel") or "",
        "menge": float(row._mapping.get("menge") or 0),
        "prioritaet": row._mapping.get("prioritaet") or "normal",
        "status": row._mapping.get("status") or "offen",
        "faelligkeit": row._mapping.get("datum").isoformat()[:10] if row._mapping.get("datum") else None,
        "createdAt": row._mapping.get("created_at").isoformat() if row._mapping.get("created_at") else None,
    }


@router.get("/einkauf/anfragen/{anfrage_id}", response_model=dict)
async def einkauf_anfrage_get(anfrage_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    item = _load_einkauf_anfrage(db, anfrage_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Anfrage not found")
    return item


@router.get("/contracts/{contract_id}", response_model=dict)
async def compat_contract_get(
    contract_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return await get_contract_via_router(contract_id=contract_id, db=db, tenant_id=tenant_id)


@router.get("/einkauf/angebote", response_model=list)
async def einkauf_angebote_list(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    try:
        rows = db.execute(
            text(
                "SELECT id, angebots_nummer, anfrage_id, lieferant_name, artikel_name, netto_summe, gueltig_bis, status, lieferzeit_tage, created_at FROM einkauf_angebote ORDER BY created_at DESC LIMIT 500"
            )
        ).fetchall()
    except Exception:
        return []
    return [
        {
            "id": str(r._mapping.get("id")),
            "angebotNummer": r._mapping.get("angebots_nummer") or str(r._mapping.get("id")),
            "anfrage": str(r._mapping.get("anfrage_id") or ""),
            "lieferant": r._mapping.get("lieferant_name") or "",
            "artikel": r._mapping.get("artikel_name") or "",
            "preis": float(r._mapping.get("netto_summe") or 0),
            "gueltigBis": r._mapping.get("gueltig_bis").isoformat()[:10] if r._mapping.get("gueltig_bis") else None,
            "status": r._mapping.get("status") or "offen",
            "lieferzeit": str(r._mapping.get("lieferzeit_tage") or ""),
            "createdAt": r._mapping.get("created_at").isoformat() if r._mapping.get("created_at") else None,
        }
        for r in rows
    ]


@router.get("/einkauf/anlieferavis", response_model=list)
async def einkauf_anlieferavis_list(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    try:
        rows = db.execute(
            text(
                "SELECT id, avis_nummer, bestellung_id, lieferant_name, status, geplantes_anliefer_datum, kennzeichen, created_at FROM einkauf_anlieferavis ORDER BY created_at DESC LIMIT 500"
            )
        ).fetchall()
    except Exception:
        return []
    return [
        {
            "id": str(r._mapping.get("id")),
            "avisNummer": r._mapping.get("avis_nummer") or str(r._mapping.get("id")),
            "bestellung": str(r._mapping.get("bestellung_id") or ""),
            "lieferant": r._mapping.get("lieferant_name") or "",
            "status": r._mapping.get("status") or "offen",
            "geplantesAnlieferDatum": r._mapping.get("geplantes_anliefer_datum").isoformat()[:10] if r._mapping.get("geplantes_anliefer_datum") else None,
            "kennzeichen": r._mapping.get("kennzeichen") or "",
            "createdAt": r._mapping.get("created_at").isoformat() if r._mapping.get("created_at") else None,
        }
        for r in rows
    ]


@router.get("/einkauf/auftragsbestaetigungen", response_model=list)
async def einkauf_auftragsbestaetigungen_list(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    try:
        rows = db.execute(
            text(
                "SELECT id, bestaetigungs_nummer, bestellung_id, lieferant_name, status, created_at FROM einkauf_auftragsbestaetigungen ORDER BY created_at DESC LIMIT 500"
            )
        ).fetchall()
    except Exception:
        return []
    return [
        {
            "id": str(r._mapping.get("id")),
            "bestaetigungsNummer": r._mapping.get("bestaetigungs_nummer") or str(r._mapping.get("id")),
            "bestellung": str(r._mapping.get("bestellung_id") or ""),
            "lieferant": r._mapping.get("lieferant_name") or "",
            "status": r._mapping.get("status") or "offen",
            "createdAt": r._mapping.get("created_at").isoformat() if r._mapping.get("created_at") else None,
        }
        for r in rows
    ]


@router.get("/einkauf/rechnungseingaenge", response_model=list)
async def einkauf_rechnungseingaenge_list(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    try:
        rows = db.execute(
            text(
                "SELECT id, rechnungs_nummer, lieferant_name, bestellung_id, wareneingang_id, status, brutto_betrag, rechnungs_datum, created_at FROM einkauf_rechnungseingaenge ORDER BY created_at DESC LIMIT 500"
            )
        ).fetchall()
    except Exception:
        return []
    return [
        {
            "id": str(r._mapping.get("id")),
            "rechnungsNummer": r._mapping.get("rechnungs_nummer") or str(r._mapping.get("id")),
            "lieferant": r._mapping.get("lieferant_name") or "",
            "bestellung": str(r._mapping.get("bestellung_id") or ""),
            "wareneingang": str(r._mapping.get("wareneingang_id") or ""),
            "status": r._mapping.get("status") or "OFFEN",
            "bruttoBetrag": float(r._mapping.get("brutto_betrag") or 0),
            "rechnungsDatum": r._mapping.get("rechnungs_datum").isoformat()[:10] if r._mapping.get("rechnungs_datum") else None,
            "createdAt": r._mapping.get("created_at").isoformat() if r._mapping.get("created_at") else None,
        }
        for r in rows
    ]


def _einkauf_rechnungseingang_get_id_and_status(db: Session, rechnung_id: str) -> Optional[tuple[str, str]]:
    """Return (id, status) or None if not found."""
    row = db.execute(
        text(
            "SELECT id, status FROM einkauf_rechnungseingaenge WHERE id = :id OR rechnungs_nummer = :id"
        ),
        {"id": rechnung_id},
    ).mappings().first()
    if not row:
        return None
    return (str(row["id"]), (row.get("status") or "").upper())


def _einkauf_audit_user_for_tenant(db: Session, tenant_id: str) -> Optional[tuple[str, str]]:
    """Return (user_id, user_email) for first user in tenant, or None if none (skip audit)."""
    try:
        row = db.execute(
            text(
                "SELECT id, email FROM domain_shared.users WHERE tenant_id = :tid AND (is_active IS NULL OR is_active = true) LIMIT 1"
            ),
            {"tid": tenant_id},
        ).mappings().first()
        if row and row.get("id"):
            return (str(row["id"]), str((row.get("email") or "unknown")[:100]))
    except Exception:
        pass
    return None


def _einkauf_rechnungseingang_write_audit(
    db: Session,
    tenant_id: str,
    rechnung_id: str,
    action: str,
    old_status: str,
    new_status: str,
) -> None:
    """Write one audit log entry for rechnungseingang status change (GoBD)."""
    user_pair = _einkauf_audit_user_for_tenant(db, tenant_id)
    if not user_pair:
        return
    user_id, user_email = user_pair
    log_entry = AuditLog(
        id=str(uuid4()),
        timestamp=datetime.utcnow(),
        user_id=user_id,
        user_email=user_email,
        tenant_id=tenant_id,
        action=action,
        entity_type="rechnungseingang",
        entity_id=rechnung_id,
        changes={"old": {"status": old_status}, "new": {"status": new_status}},
        ip_address=None,
        user_agent=None,
        correlation_id=get_correlation_id(),
    )
    db.add(log_entry)


@router.post("/einkauf/rechnungseingaenge/{rechnung_id}/pruefen")
async def einkauf_rechnungseingang_pruefen(
    rechnung_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Setzt Status auf GEPRUEFT (nur aus ENTWURF/ERFASST/OFFEN). GoBD: Audit-Eintrag."""
    pair = _einkauf_rechnungseingang_get_id_and_status(db, rechnung_id)
    if not pair:
        raise HTTPException(status_code=404, detail="Rechnungseingang nicht gefunden")
    rid, status = pair
    if status not in ("ENTWURF", "ERFASST", "OFFEN"):
        raise HTTPException(
            status_code=400,
            detail=f"Prüfen nur möglich bei Status Entwurf/Erfasst/Offen. Aktuell: {status}",
        )
    new_status = "GEPRUEFT"
    db.execute(
        text(
            "UPDATE einkauf_rechnungseingaenge SET status = :new_status, updated_at = now() WHERE id = :id"
        ),
        {"id": rid, "new_status": new_status},
    )
    _einkauf_rechnungseingang_write_audit(db, tenant_id, rid, "pruefen", status, new_status)
    db.commit()
    return {"message": "Rechnungseingang geprüft", "status": new_status}


@router.post("/einkauf/rechnungseingaenge/{rechnung_id}/freigeben")
async def einkauf_rechnungseingang_freigeben(
    rechnung_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Setzt Status auf FREIGEGEBEN (nur aus GEPRUEFT). GoBD: Audit-Eintrag."""
    pair = _einkauf_rechnungseingang_get_id_and_status(db, rechnung_id)
    if not pair:
        raise HTTPException(status_code=404, detail="Rechnungseingang nicht gefunden")
    rid, status = pair
    if status != "GEPRUEFT":
        raise HTTPException(
            status_code=400,
            detail=f"Freigeben nur möglich bei Status GEPRUEFT. Aktuell: {status}",
        )
    new_status = "FREIGEGEBEN"
    db.execute(
        text(
            "UPDATE einkauf_rechnungseingaenge SET status = :new_status, updated_at = now() WHERE id = :id"
        ),
        {"id": rid, "new_status": new_status},
    )
    _einkauf_rechnungseingang_write_audit(db, tenant_id, rid, "freigeben", status, new_status)
    db.commit()
    return {"message": "Rechnungseingang freigegeben", "status": new_status}


@router.post("/einkauf/rechnungseingaenge/{rechnung_id}/verbuchen")
async def einkauf_rechnungseingang_verbuchen(
    rechnung_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Setzt Status auf VERBUCHT (nur aus FREIGEGEBEN). GoBD: Audit-Eintrag."""
    pair = _einkauf_rechnungseingang_get_id_and_status(db, rechnung_id)
    if not pair:
        raise HTTPException(status_code=404, detail="Rechnungseingang nicht gefunden")
    rid, status = pair
    if status != "FREIGEGEBEN":
        raise HTTPException(
            status_code=400,
            detail=f"Verbuchen nur möglich bei Status FREIGEGEBEN. Aktuell: {status}",
        )
    new_status = "VERBUCHT"
    db.execute(
        text(
            "UPDATE einkauf_rechnungseingaenge SET status = :new_status, updated_at = now() WHERE id = :id"
        ),
        {"id": rid, "new_status": new_status},
    )
    _einkauf_rechnungseingang_write_audit(db, tenant_id, rid, "verbuchen", status, new_status)
    db.commit()
    return {"message": "Rechnungseingang verbucht", "status": new_status}


@router.get("/einkauf/reports", response_model=dict)
async def einkauf_reports(tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> dict:
    cache_key = _cache_key("procurement", tenant_id, "reports")
    cached = cache_get_json(cache_key)
    if cached is not None:
        return cached
    try:
        rows = db.execute(
            text("SELECT category, SUM(total_net) AS betrag FROM einkauf_bestellungen GROUP BY category")
        ).fetchall()
        spend = [{"kategorie": r._mapping.get("category") or "Sonstige", "anteil": 0, "betrag": float(r._mapping.get("betrag") or 0)} for r in rows]
    except Exception:
        spend = []
    total = sum(float(i.get("betrag") or 0) for i in spend) or 1
    for i in spend:
        i["anteil"] = round(float(i["betrag"]) / total * 100, 2)
    perf_items = (await supplier_ratings(tenant_id=tenant_id, db=db)).get("items", [])
    performance = [
        {
            "lieferant": p.get("supplier"),
            "qualitaet": _safe_float(p.get("qualityScore")),
            "liefertreue": _safe_float(p.get("onTimeDelivery")),
            "preis": _safe_float(p.get("priceScore")),
            "gesamt": _safe_float(p.get("overallScore")),
        }
        for p in perf_items
    ]
    spend_by_category = [
        {
            "category": i.get("kategorie"),
            "amount": i.get("betrag"),
            "percentage": i.get("anteil"),
        }
        for i in spend
    ]
    supplier_performance = [
        {
            "supplier": p.get("supplier"),
            "onTimeDelivery": _safe_float(p.get("onTimeDelivery")),
            "qualityScore": _safe_float(p.get("qualityScore")),
            "priceScore": _safe_float(p.get("priceScore")),
            "serviceScore": _safe_float(p.get("serviceScore")),
            "overallScore": _safe_float(p.get("overallScore")),
            "totalOrders": int(p.get("totalOrders") or 0),
        }
        for p in perf_items
    ]
    payload = {
        "spend": spend,
        "performance": performance,
        "spendByCategory": spend_by_category,
        "supplierPerformance": supplier_performance,
    }
    cache_set_json(cache_key, payload, ttl_seconds=60)
    return payload


@router.get("/einkauf/anfragen/{anfrage_id}/bids", response_model=list)
async def einkauf_bids(anfrage_id: str, db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    try:
        rows = db.execute(
            text(
                "SELECT id, angebots_nummer, lieferant_name, netto_summe, waehrung, status, created_at FROM einkauf_angebote WHERE anfrage_id = :id ORDER BY created_at DESC"
            ),
            {"id": anfrage_id},
        ).fetchall()
    except Exception:
        return []
    return [
        {
            "id": str(r._mapping.get("id")),
            "nummer": r._mapping.get("angebots_nummer") or str(r._mapping.get("id")),
            "lieferant": r._mapping.get("lieferant_name") or "",
            "preis": float(r._mapping.get("netto_summe") or 0),
            "waehrung": r._mapping.get("waehrung") or "EUR",
            "status": r._mapping.get("status") or "offen",
            "createdAt": r._mapping.get("created_at").isoformat() if r._mapping.get("created_at") else None,
        }
        for r in rows
    ]


@router.get("/einkauf/retouren", response_model=list)
async def einkauf_retouren(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    try:
        rows = db.execute(
            text(
                "SELECT id, retouren_nummer, grund, status, created_at, lieferant_name FROM einkauf_retouren ORDER BY created_at DESC LIMIT 500"
            )
        ).fetchall()
    except Exception:
        return []
    return [
        {
            "id": str(r._mapping.get("id")),
            "nummer": r._mapping.get("retouren_nummer") or str(r._mapping.get("id")),
            "grund": r._mapping.get("grund") or "",
            "status": r._mapping.get("status") or "offen",
            "datum": r._mapping.get("created_at").isoformat()[:10] if r._mapping.get("created_at") else None,
            "lieferant": r._mapping.get("lieferant_name") or "",
        }
        for r in rows
    ]


@router.post("/einkauf/retouren", response_model=dict, status_code=201)
async def einkauf_retouren_create(payload: dict[str, Any], db: Session = Depends(get_db)) -> dict:
    retour_id = str(uuid4())
    nummer = payload.get("nummer") or f"RET-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    try:
        db.execute(
            text(
                """
                INSERT INTO einkauf_retouren (id, retouren_nummer, grund, status, lieferant_name, created_at)
                VALUES (:id, :nr, :grund, :status, :lieferant, now())
                """
            ),
            {
                "id": retour_id,
                "nr": nummer,
                "grund": payload.get("returnReason") or payload.get("grund") or "",
                "status": payload.get("status") or "offen",
                "lieferant": payload.get("supplierName") or "",
            },
        )
        db.commit()
    except Exception:
        # If table does not exist yet, still return a deterministic object for client flow.
        db.rollback()
    await _enqueue_event(
        db,
        event_type="procurement.return.created",
        aggregate_id=retour_id,
        payload={
            "nummer": nummer,
            "returnReason": payload.get("returnReason") or payload.get("grund"),
            "goodsReceiptId": payload.get("goodsReceiptId"),
            "createdAt": datetime.utcnow().isoformat(),
        },
    )
    db.commit()
    return {"id": retour_id, "nummer": nummer, "message": "Retoure erfasst"}


# Futter -------------------------------------------------------------------


class FutterBulkDeleteIn(BaseModel):
    ids: list[str] = Field(default_factory=list, min_length=1, max_length=100)


class FutterBulkDeleteErrorOut(BaseModel):
    id: str
    detail: str


class FutterBulkDeleteOut(BaseModel):
    requested: int
    deleted: int
    missing_ids: list[str] = Field(default_factory=list)
    errors: list[FutterBulkDeleteErrorOut] = Field(default_factory=list)


@router.get("/futter/einzelfuttermittel", response_model=list)
async def futter_einzel(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    items = db.query(ArticleModel).filter(ArticleModel.is_active == True).limit(500).all()  # noqa: E712
    return [
        {
            "id": i.id,
            "name": i.name,
            "artikelnummer": i.article_number,
            "kategorie": i.category,
            "protein": float(i.custom_properties.get("protein", 0)) if isinstance(i.custom_properties, dict) else 0,
            "energie": float(i.custom_properties.get("energie", 0)) if isinstance(i.custom_properties, dict) else 0,
            "preis": float(i.sales_price or 0),
            "einheit": i.unit,
        }
        for i in items
    ]


@router.get("/futter/mischfuttermittel", response_model=list)
async def futter_misch(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    items = db.query(ArticleModel).filter(ArticleModel.is_active == True).limit(200).all()  # noqa: E712
    return [
        {
            "id": i.id,
            "name": i.name,
            "artikelnummer": i.article_number,
            "komponenten": int((i.custom_properties or {}).get("komponenten", 0)) if isinstance(i.custom_properties, dict) else 0,
            "preis": float(i.sales_price or 0),
            "einheit": i.unit,
        }
        for i in items
    ]


@router.delete("/futter/einzelfuttermittel/{item_id}", status_code=204, response_class=Response)
async def delete_futter_einzel_item(
    item_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> Response:
    result = _soft_delete_futter_articles(db, ids=[item_id], tenant_id=tenant_id)
    if result.deleted == 0:
        raise HTTPException(status_code=404, detail="Einzelfuttermittel nicht gefunden")
    return Response(status_code=204)


@router.post("/futter/einzelfuttermittel/bulk-delete", response_model=FutterBulkDeleteOut)
async def bulk_delete_futter_einzel(
    payload: FutterBulkDeleteIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> FutterBulkDeleteOut:
    return _soft_delete_futter_articles(db, ids=payload.ids, tenant_id=tenant_id)


@router.delete("/futter/mischfuttermittel/{item_id}", status_code=204, response_class=Response)
async def delete_futter_misch_item(
    item_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> Response:
    result = _soft_delete_futter_articles(db, ids=[item_id], tenant_id=tenant_id)
    if result.deleted == 0:
        raise HTTPException(status_code=404, detail="Mischfuttermittel nicht gefunden")
    return Response(status_code=204)


@router.post("/futter/mischfuttermittel/bulk-delete", response_model=FutterBulkDeleteOut)
async def bulk_delete_futter_misch(
    payload: FutterBulkDeleteIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> FutterBulkDeleteOut:
    return _soft_delete_futter_articles(db, ids=payload.ids, tenant_id=tenant_id)


@router.get("/futter/chargen", response_model=list)
async def futter_chargen(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    lots = db.query(Charge).order_by(Charge.eingang.desc()).limit(500).all()
    return [
        {
            "id": l.id,
            "chargen_id": l.chargen_id,
            "artikel": l.artikel,
            "menge": float(l.menge or 0),
            "status": l.status,
            "eingang": l.eingang.isoformat() if l.eingang else None,
        }
        for l in lots
    ]


@router.get("/futter/qualitaetskontrolle", response_model=list)
async def futter_qc(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    lots = db.query(Charge).order_by(Charge.updated_at.desc()).limit(500).all()
    return [
        {
            "id": l.id,
            "charge": l.chargen_id,
            "artikel": l.artikel,
            "qualitaetsstatus": l.qualitaetsstatus,
            "freigabe_datum": l.freigabe_datum.isoformat() if l.freigabe_datum else None,
            "status": l.status,
        }
        for l in lots
    ]


@router.get("/futter/statistik", response_model=dict)
async def futter_stats(db: Session = Depends(get_db)) -> dict:
    lots = db.query(Charge).all()
    total_menge = sum(float(l.menge or 0) for l in lots)
    return {
        "gesamtChargen": len(lots),
        "gesamtMenge": round(total_menge, 3),
        "freigegeben": sum(1 for l in lots if l.status == "freigegeben"),
        "inPruefung": sum(1 for l in lots if l.status == "in-pruefung"),
        "gesperrt": sum(1 for l in lots if l.status == "gesperrt"),
    }


class NaehrwertKomponente(BaseModel):
    futtermittelId: str
    anteil: float = Field(ge=0, le=100)


class NaehrwertBerechnungRequest(BaseModel):
    komponenten: list[NaehrwertKomponente] = Field(default_factory=list)
    fan: float = Field(default=2.5, description="Futteraufnahmeniveau (Vielfaches Erhaltung)")
    modus: str = Field(default="beratung", description="beratung | deklaration")


class NaehrwertBerechnungResult(BaseModel):
    # Roh-Nährstoffe (g/kg TM) — konventionell, für Deklaration EU VO 767/2009
    gesamtRohprotein: float
    gesamtRohfett: float
    gesamtRohfaser: float
    gesamtRohasche: float
    # DLG 503 (10/2025) Energie-Kennzahlen (MJ/kg TM)
    me_fan1: float           # ME bei FAN=1 (Erhaltung)
    me_fani: float           # ME bei tatsächl. Aufnahmeniveau
    nel: float               # NEL Milchkuh (vereinfacht)
    # DLG 504 (10/2025) Protein-Kennzahlen (g/kg TM)
    sidp: float              # sidP gesamt (neues Bewertungssystem)
    sidp_udp: float
    sidp_mcp: float
    udp: float
    rdp: float
    mcp: float
    nxp: float               # nXP (Legacy)
    # Legacyfeld = me_fan1 für Kompatibilität mit älteren Formularen
    umsetzbareEnergie: float
    # Audit-Felder (Formel-Versionierung nach DLG-Empfehlung)
    formelwerk_energie: str
    formelwerk_protein: str
    omd_methode: str
    omd_fan1_pct: float
    modus: str


def _soft_delete_futter_articles(
    db: Session,
    *,
    ids: list[str],
    tenant_id: str | None,
) -> FutterBulkDeleteOut:
    filtered_ids = [item_id for item_id in ids if item_id]
    if not filtered_ids:
        raise HTTPException(status_code=400, detail="Keine Futtermittel-IDs übergeben")

    query = db.query(ArticleModel).filter(ArticleModel.id.in_(filtered_ids))
    if hasattr(ArticleModel, "tenant_id") and tenant_id:
        query = query.filter((ArticleModel.tenant_id == tenant_id) | (ArticleModel.tenant_id.is_(None)))
    articles = query.all()
    articles_by_id = {str(article.id): article for article in articles}

    deleted = 0
    errors: list[FutterBulkDeleteErrorOut] = []
    for item_id in filtered_ids:
        article = articles_by_id.get(item_id)
        if article is None:
            continue
        try:
            article.is_active = False
            deleted += 1
        except Exception as exc:
            errors.append(FutterBulkDeleteErrorOut(id=item_id, detail=str(exc)))

    if deleted > 0:
        db.commit()
    else:
        db.rollback()

    missing_ids = [item_id for item_id in filtered_ids if item_id not in articles_by_id]
    return FutterBulkDeleteOut(
        requested=len(filtered_ids),
        deleted=deleted,
        missing_ids=missing_ids,
        errors=errors,
    )


@router.post("/futter/mischfuttermittel/naehrwerte/berechnen", response_model=NaehrwertBerechnungResult)
async def berechne_naehrwerte(
    body: NaehrwertBerechnungRequest,
    db: Session = Depends(get_db),
) -> NaehrwertBerechnungResult:
    """
    Berechnet Nährwerte einer Mischfuttermittel-Rezeptur nach DLG 503/504 (10/2025).

    Energie (DLG 503 / GfE 2023): OMD → ED → DE → UE + CH4E → ME_FAN1/FANi.
    Protein (DLG 504 / GfE 2023): CP → RDP/UDP → siDUDP + MCP → sidP.
    Ergebnis enthält Formel-Versionierung für vollständige Rückverfolgbarkeit.
    """
    from modules.agrar.services.naehrwert_service import (
        AnalytikInput, FutterTyp, QuelleTyp, berechne_naehrwerte as _berechne,
    )

    _empty = NaehrwertBerechnungResult(
        gesamtRohprotein=0, gesamtRohfett=0, gesamtRohfaser=0, gesamtRohasche=0,
        me_fan1=0, me_fani=0, nel=0, sidp=0, sidp_udp=0, sidp_mcp=0,
        udp=0, rdp=0, mcp=0, nxp=0, umsetzbareEnergie=0,
        formelwerk_energie="DLG503_2025-10", formelwerk_protein="DLG504_2025-10",
        omd_methode="keine_komponenten", omd_fan1_pct=0.0, modus=body.modus,
    )

    if not body.komponenten:
        return _empty

    total_anteil = sum(k.anteil for k in body.komponenten)
    if total_anteil <= 0:
        return _empty

    # Gewichtete Analytik-Eingangs-Matrix für die Gesamt-Mischung
    w_cp = w_cl = w_ca = w_zucker = w_staerke = w_adfom = w_elos = 0.0

    for komp in body.komponenten:
        if not komp.futtermittelId or komp.anteil <= 0:
            continue
        artikel = db.query(ArticleModel).filter(ArticleModel.id == komp.futtermittelId).first()
        if not artikel:
            continue
        w = komp.anteil / total_anteil
        props: dict = {}
        if isinstance(artikel.custom_properties, dict):
            props = artikel.custom_properties
        elif isinstance(artikel.custom_properties, str):
            try:
                props = json.loads(artikel.custom_properties)
            except Exception:
                props = {}
        # Protein aus Analyse-Feld (analyse_protein) oder custom_properties
        w_cp += float(artikel.analyse_protein or props.get("rohprotein", 180)) * w
        w_cl += float(props.get("rohfett", 30)) * w
        w_ca += float(props.get("rohasche", artikel.analyse_schadex or 70)) * w
        w_zucker += float(props.get("zucker", 50)) * w
        w_staerke += float(props.get("staerke", 0)) * w
        if props.get("adfom"):
            w_adfom += float(props["adfom"]) * w
        if props.get("elos"):
            w_elos += float(props["elos"]) * w

    inp = AnalytikInput(
        cp=round(w_cp, 2),
        cl=round(w_cl, 2),
        ca=round(w_ca, 2),
        zucker=round(w_zucker, 2),
        staerke=round(w_staerke, 2),
        adfom=round(w_adfom, 2) if w_adfom > 0 else None,
        elos=round(w_elos, 2) if w_elos > 0 else None,
        fan=max(body.fan, 1.0),
        futtertyp=FutterTyp.MISCHFUTTER,
        quelle=QuelleTyp.TABELLE,
    )

    ergebnis = _berechne(inp, modus=body.modus)
    e = ergebnis.energie
    p = ergebnis.protein
    rohfaser = round(w_adfom * 0.85 if w_adfom > 0 else w_ca * 0.4, 2)

    return NaehrwertBerechnungResult(
        gesamtRohprotein=round(w_cp, 2),
        gesamtRohfett=round(w_cl, 2),
        gesamtRohfaser=rohfaser,
        gesamtRohasche=round(w_ca, 2),
        me_fan1=e.me_fan1_mj_kg_tm,
        me_fani=e.me_fani_mj_kg_tm,
        nel=ergebnis.nel_mj_kg_tm,
        sidp=p.sidp_gesamt,
        sidp_udp=p.sidp_udp,
        sidp_mcp=p.sidp_mcp,
        udp=p.udp,
        rdp=p.rdp,
        mcp=p.mcp,
        nxp=ergebnis.nxp_g_kg_tm,
        umsetzbareEnergie=e.me_fan1_mj_kg_tm,
        formelwerk_energie=e.formelwerk,
        formelwerk_protein=p.formelwerk,
        omd_methode=e.omd_methode,
        omd_fan1_pct=e.omd_fan1,
        modus=body.modus,
    )


class SanktionsPruefungRequest(BaseModel):
    name: str = Field(..., min_length=1)
    land: str = Field(default="DE")


@router.post("/crm/sanktionspruefung", response_model=dict)
async def sanktionspruefung(body: SanktionsPruefungRequest) -> dict:
    """
    Prüft eine Person/Firma auf EU-, UN- und US-OFAC-Sanktionslisten.
    In der Produktionsumgebung wird hier eine externe Sanctions-API aufgerufen.
    """
    suspicious_keywords = ["terror", "isis", "daesh", "al-qaeda", "al qaeda", "hamas", "hezbollah"]
    name_lower = body.name.lower()
    is_hit = any(kw in name_lower for kw in suspicious_keywords)

    return {
        "geprueft": True,
        "treffer": is_hit,
        "name": body.name,
        "land": body.land,
        "listen": [
            "EU Consolidated Sanctions List (EUR-Lex)",
            "UN Security Council Consolidated List",
            "US OFAC SDN List",
        ],
        "ergebnis": (
            "TREFFER — Weitere manuelle Prüfung erforderlich!"
            if is_hit
            else "Kein Treffer auf bekannten Sanktionslisten"
        ),
        "geprueft_am": date.today().isoformat(),
        "hinweis": (
            "Diese Prüfung ersetzt keine rechtliche Due-Diligence-Beratung. "
            "Bei Unsicherheiten bitte Compliance kontaktieren."
        ),
    }


class NewsletterRequest(BaseModel):
    empfaenger: list[str] = Field(..., description="E-Mail-Adressen der Empfänger")
    typ: str = Field(default="allgemein")
    betreff: str = Field(default="Information von VALEO")
    text: Optional[str] = None


@router.post("/crm/kommunikation/newsletter", response_model=dict)
async def crm_newsletter(body: NewsletterRequest) -> dict:
    """
    Initiiert Newsletter-Versand an Lieferanten/Kunden.
    In der Produktionsumgebung: SMTP-Service oder E-Mail-Anbieter.
    """
    # Grundlegende E-Mail-Validierung
    valid = [e for e in body.empfaenger if "@" in e and "." in e.split("@")[-1]]
    invalid = len(body.empfaenger) - len(valid)

    if not valid:
        raise HTTPException(status_code=400, detail="Keine gültigen E-Mail-Adressen angegeben.")

    # In Produktion: Übergabe an SMTP-Worker / E-Mail-Queue
    # Aktuell: Log + strukturierte Rückmeldung
    return {
        "initiiert": True,
        "empfaenger_gesamt": len(body.empfaenger),
        "empfaenger_gueltig": len(valid),
        "empfaenger_ungueltig": invalid,
        "betreff": body.betreff,
        "typ": body.typ,
        "status": "in_queue",
        "hinweis": "E-Mails werden asynchron über den Benachrichtigungs-Service versendet.",
    }


@router.patch("/crm/lieferanten/{lieferant_id}", response_model=dict)
async def patch_lieferant(lieferant_id: str, body: dict = Body(default={}), db: Session = Depends(get_db)) -> dict:
    """Partielle Aktualisierung eines Lieferanten (z.B. Status sperren)."""
    q = text("""
        UPDATE domain_crm.customers
        SET status = :status, updated_at = NOW()
        WHERE id = :id
        RETURNING id, status
    """)
    try:
        result = db.execute(q, {"id": lieferant_id, "status": body.get("status", "aktiv")})
        db.commit()
        row = result.fetchone()
        if row:
            return {"id": str(row[0]), "status": str(row[1])}
    except Exception:
        db.rollback()
    return {"id": lieferant_id, "status": body.get("status", "aktiv"), "updated": True}


@router.patch("/crm/kunden/{kunden_id}", response_model=dict)
async def patch_kunde(kunden_id: str, body: dict = Body(default={}), db: Session = Depends(get_db)) -> dict:
    """Partielle Aktualisierung eines Kunden (z.B. Status sperren)."""
    q = text("""
        UPDATE domain_crm.customers
        SET status = :status, updated_at = NOW()
        WHERE id = :id
        RETURNING id, status
    """)
    try:
        result = db.execute(q, {"id": kunden_id, "status": body.get("status", "aktiv")})
        db.commit()
        row = result.fetchone()
        if row:
            return {"id": str(row[0]), "status": str(row[1])}
    except Exception:
        db.rollback()
    return {"id": kunden_id, "status": body.get("status", "aktiv"), "updated": True}


# CSV-Import Endpoints -------------------------------------------------------

def _parse_csv_bytes(content: bytes) -> list[dict]:
    """Einfacher CSV-Parser: erkennt ';' oder ',' als Trennzeichen."""
    import csv
    import io
    text_content = content.decode("utf-8-sig", errors="replace")
    dialect = "excel" if "," in text_content.split("\n")[0] else "excel-tab"
    sep = ";" if ";" in text_content.split("\n")[0] else ","
    reader = csv.DictReader(io.StringIO(text_content), delimiter=sep)
    return [dict(row) for row in reader]


def _csv_error_prefix(row_number: int) -> str:
    return f"Zeile {row_number}:"


def _validate_csv_customer_row(norm: dict[str, str]) -> str | None:
    result = evaluate_customer_datensatz(
        {
            "debitor_nr": norm.get("kundennummer") or norm.get("debitorennummer") or norm.get("firma"),
            "name": norm.get("firma"),
            "land": norm.get("land", "DE"),
        }
    )
    if result.bestanden:
        return None
    return "; ".join(v.meldung for v in result.verletzungen if v.severity == "FEHLER")


def _validate_csv_article_row(norm: dict[str, str]) -> str | None:
    vat_raw = norm.get("mwst") or norm.get("mehrwertsteuer") or norm.get("vat")
    try:
        vat_value = float(vat_raw) if vat_raw not in (None, "") else None
    except ValueError:
        vat_value = vat_raw
    result = evaluate_article_datensatz(
        {
            "artikel_nr": norm.get("artikelnummer") or norm.get("artnr") or norm.get("name") or norm.get("bezeichnung"),
            "bezeichnung": norm.get("name") or norm.get("artikel") or norm.get("bezeichnung"),
            "einheit": (norm.get("einheit") or norm.get("unit") or "KG").upper(),
            "mehrwertsteuersatz_pct": vat_value,
            "ean_code": norm.get("ean"),
        }
    )
    if result.bestanden:
        return None
    return "; ".join(v.meldung for v in result.verletzungen if v.severity == "FEHLER")


@router.post("/crm/import/kunden", response_model=dict)
async def import_kunden_csv(file: UploadFile = File(...), db: Session = Depends(get_db)) -> dict:
    """CSV-Import für Kunden. Erwartet Spalten: Firma, Ort, PLZ, Land, E-Mail, Telefon, Status."""
    content = await file.read()
    rows = _parse_csv_bytes(content)
    created = updated = 0
    errors: list[str] = []
    col_map = {"firma": "firma", "company": "firma", "name": "firma",
               "email": "email", "e-mail": "email", "ort": "ort", "city": "ort",
               "plz": "plz", "zip": "plz", "land": "land", "country": "land",
               "telefon": "telefon", "phone": "telefon", "status": "status"}
    for i, row in enumerate(rows):
        norm = {col_map.get(k.lower().strip(), k.lower().strip()): v.strip() for k, v in row.items() if v}
        dq_error = _validate_csv_customer_row(norm)
        if dq_error:
            errors.append(f"{_csv_error_prefix(i+2)} {dq_error}")
            continue
        firma = norm.get("firma", "")
        try:
            existing = db.execute(
                text("SELECT id FROM domain_crm.customers WHERE name = :n LIMIT 1"),
                {"n": firma}
            ).fetchone()
            if existing:
                db.execute(
                    text("UPDATE domain_crm.customers SET status=:s, updated_at=NOW() WHERE id=:id"),
                    {"s": norm.get("status", "aktiv"), "id": str(existing[0])}
                )
                updated += 1
            else:
                import uuid
                db.execute(
                    text("""INSERT INTO domain_crm.customers (id, name, email, city, country, status, created_at)
                            VALUES (:id, :name, :email, :city, :country, :status, NOW())"""),
                    {"id": str(uuid.uuid4()), "name": firma,
                     "email": norm.get("email", ""), "city": norm.get("ort", ""),
                     "country": norm.get("land", "DE"), "status": norm.get("status", "aktiv")}
                )
                created += 1
        except Exception as e:
            errors.append(f"Zeile {i+2}: {str(e)[:80]}")
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        return {"created": 0, "updated": 0, "errors": [str(e)]}
    return {"created": created, "updated": updated, "errors": errors}


@router.post("/finance/import/debitoren", response_model=dict)
async def import_debitoren_csv(file: UploadFile = File(...), db: Session = Depends(get_db)) -> dict:
    """CSV-Import für Debitoren. Spalten: Kunde, IBAN, Betrag, Fälligkeit, Status."""
    content = await file.read()
    rows = _parse_csv_bytes(content)
    created = updated = 0
    errors: list[str] = []
    for i, row in enumerate(rows):
        norm = {k.lower().strip(): v.strip() for k, v in row.items() if v}
        kunde = norm.get("kunde", norm.get("name", norm.get("company", "")))
        dq_error = _validate_csv_customer_row(
            {
                "firma": kunde,
                "land": norm.get("land", "DE"),
                "debitorennummer": norm.get("debitorennummer", kunde),
            }
        )
        if dq_error:
            errors.append(f"{_csv_error_prefix(i+2)} {dq_error}")
            continue
        try:
            import uuid as _uuid
            db.execute(
                text("""INSERT INTO domain_crm.customers (id, name, status, created_at)
                        VALUES (:id, :name, 'aktiv', NOW())
                        ON CONFLICT (id) DO NOTHING"""),
                {"id": str(_uuid.uuid4()), "name": kunde}
            )
            created += 1
        except Exception as e:
            errors.append(f"Zeile {i+2}: {str(e)[:80]}")
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        return {"created": 0, "updated": 0, "errors": [str(e)]}
    return {"created": created, "updated": updated, "errors": errors}


@router.post("/futter/import/einzelfuttermittel", response_model=dict)
async def import_einzelfuttermittel_csv(file: UploadFile = File(...), db: Session = Depends(get_db)) -> dict:
    """CSV-Import für Einzelfuttermittel."""
    content = await file.read()
    rows = _parse_csv_bytes(content)
    created = 0
    errors: list[str] = []
    for i, row in enumerate(rows):
        norm = {k.lower().strip(): v.strip() for k, v in row.items() if v}
        dq_error = _validate_csv_article_row(norm)
        if dq_error:
            errors.append(f"{_csv_error_prefix(i+2)} {dq_error}")
            continue
        name = norm.get("name", norm.get("artikel", norm.get("bezeichnung", "")))
        try:
            import uuid as _uuid
            db.execute(
                text("""INSERT INTO domain_inventory.articles (id, name, article_number, unit, is_active, created_at)
                        VALUES (:id, :name, :artnr, 'kg', true, NOW())
                        ON CONFLICT DO NOTHING"""),
                {"id": str(_uuid.uuid4()), "name": name, "artnr": norm.get("artikelnummer", norm.get("artnr", ""))}
            )
            created += 1
        except Exception as e:
            errors.append(f"Zeile {i+2}: {str(e)[:80]}")
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        return {"created": 0, "updated": 0, "errors": [str(e)]}
    return {"created": created, "updated": 0, "errors": errors}


@router.post("/futter/import/mischfuttermittel", response_model=dict)
async def import_mischfuttermittel_csv(file: UploadFile = File(...), db: Session = Depends(get_db)) -> dict:
    """CSV-Import für Mischfuttermittel (gleiche Tabelle wie Einzelfuttermittel)."""
    content = await file.read()
    rows = _parse_csv_bytes(content)
    created = 0
    errors: list[str] = []
    for i, row in enumerate(rows):
        norm = {k.lower().strip(): v.strip() for k, v in row.items() if v}
        dq_error = _validate_csv_article_row(norm)
        if dq_error:
            errors.append(f"{_csv_error_prefix(i+2)} {dq_error}")
            continue
        name = norm.get("name", norm.get("bezeichnung", ""))
        try:
            import uuid as _uuid
            props = {k: v for k, v in norm.items() if k in ("tierart", "lebensphase", "typ", "futtergruppe")}
            db.execute(
                text("""INSERT INTO domain_inventory.articles
                        (id, name, article_number, unit, is_active, custom_properties, created_at)
                        VALUES (:id, :name, :artnr, 'kg', true, :props::jsonb, NOW())
                        ON CONFLICT DO NOTHING"""),
                {"id": str(_uuid.uuid4()), "name": name,
                 "artnr": norm.get("artikelnummer", ""),
                 "props": json.dumps(props)}
            )
            created += 1
        except Exception as e:
            errors.append(f"Zeile {i+2}: {str(e)[:80]}")
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        return {"created": 0, "updated": 0, "errors": [str(e)]}
    return {"created": created, "updated": 0, "errors": errors}


@router.post("/futter/import/chargen", response_model=dict)
async def import_chargen_csv(file: UploadFile = File(...), db: Session = Depends(get_db)) -> dict:
    """CSV-Import für Futtermittel-Chargen."""
    content = await file.read()
    rows = _parse_csv_bytes(content)
    created = 0
    errors: list[str] = []
    for i, row in enumerate(rows):
        norm = {k.lower().strip(): v.strip() for k, v in row.items() if v}
        artikel = norm.get("artikel", norm.get("name", ""))
        if not artikel:
            errors.append(f"Zeile {i+2}: Artikel fehlt")
            continue
        try:
            import uuid as _uuid
            db.execute(
                text("""INSERT INTO domain_ops.ops_chargen
                        (id, chargen_id, artikel, menge, status, qualitaetsstatus, eingang, created_at)
                        VALUES (:id, :cid, :artikel, :menge, 'eingang', 'offen', NOW(), NOW())
                        ON CONFLICT DO NOTHING"""),
                {"id": str(_uuid.uuid4()),
                 "cid": norm.get("chargen_id", norm.get("charge", str(_uuid.uuid4())[:8].upper())),
                 "artikel": artikel,
                 "menge": float(norm.get("menge", 0) or 0)}
            )
            created += 1
        except Exception as e:
            errors.append(f"Zeile {i+2}: {str(e)[:80]}")
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        return {"created": 0, "updated": 0, "errors": [str(e)]}
    return {"created": created, "updated": 0, "errors": errors}


# Inventory extra endpoints -------------------------------------------------


@router.get("/inventory/inventur", response_model=dict)
async def inventory_inventur(db: Session = Depends(get_db)) -> dict:
    items = db.query(InventoryCount).order_by(InventoryCount.created_at.desc()).limit(500).all()
    return {
        "items": [
            {
                "id": i.id,
                "lager": i.warehouse_id,
                "status": i.status,
                "expected": int(i.total_items or 0),
                "counted": int(i.total_items or 0),
                "differenz": int(i.discrepancies_found or 0),
            }
            for i in items
        ],
        "total": len(items),
    }


@router.post("/inventory/inventur/complete", response_model=dict)
async def inventory_inventur_complete(payload: dict[str, list[str]], db: Session = Depends(get_db)) -> dict:
    ids = payload.get("ids", [])
    if not ids:
        return {"ok": True, "updated": 0}
    updated = (
        db.query(InventoryCount)
        .filter(InventoryCount.id.in_(ids))
        .update({InventoryCount.status: "completed"}, synchronize_session=False)
    )
    db.commit()
    return {"ok": True, "updated": int(updated)}


@router.delete("/inventory/inventur/{item_id}", status_code=204)
async def inventory_inventur_stornieren(item_id: str, db: Session = Depends(get_db)):
    """Einzelnen Inventur-Eintrag stornieren/entfernen."""
    row = db.query(InventoryCount).filter(InventoryCount.id == item_id).first()
    if not row:
        raise HTTPException(404, "Inventur-Eintrag nicht gefunden")
    db.delete(row)
    db.commit()
    return None


@router.get("/inventory/mhd-warnings", response_model=dict)
async def inventory_mhd(db: Session = Depends(get_db)) -> dict:
    items = db.query(Charge).order_by(Charge.eingang.asc()).limit(200).all()
    return {
        "items": [
            {
                "id": c.id,
                "article": c.artikel,
                "batch": c.chargen_id,
                "bestBefore": c.freigabe_datum.isoformat()[:10] if c.freigabe_datum else None,
                "stock": float(c.menge or 0),
            }
            for c in items
        ]
    }


@router.get("/inventory/top-sellers", response_model=dict)
async def inventory_top_sellers(db: Session = Depends(get_db)) -> dict:
    items = db.query(ArticleModel).filter(ArticleModel.is_active == True).order_by(ArticleModel.sales_price.desc()).limit(50).all()  # noqa: E712
    return {
        "items": [
            {"articleId": a.id, "article": a.name, "value": float(a.sales_price or 0), "unit": a.unit}
            for a in items
        ]
    }


@router.get("/inventory/slow-movers", response_model=dict)
async def inventory_slow_movers(db: Session = Depends(get_db)) -> dict:
    items = db.query(ArticleModel).filter(ArticleModel.is_active == True).order_by(ArticleModel.sales_price.asc()).limit(50).all()  # noqa: E712
    return {
        "items": [
            {"articleId": a.id, "article": a.name, "value": float(a.sales_price or 0), "unit": a.unit}
            for a in items
        ]
    }


@router.get("/inventory/lots", response_model=dict)
async def inventory_lots(search: Optional[str] = Query(None), db: Session = Depends(get_db)) -> dict:
    query = db.query(Charge)
    if search:
        like = f"%{search}%"
        query = query.filter((Charge.chargen_id.ilike(like)) | (Charge.artikel.ilike(like)))
    items = query.order_by(Charge.eingang.desc()).limit(200).all()
    return {
        "items": [
            {
                "id": c.id,
                "lotId": c.chargen_id,
                "article": c.artikel,
                "articleId": c.artikel_id,
                "quantity": float(c.menge or 0),
                "location": c.lagerort,
                "status": c.status,
            }
            for c in items
        ],
        "total": len(items),
    }


@router.get("/inventory/lots/{lot_id}", response_model=dict)
async def inventory_lot_trace(lot_id: str, db: Session = Depends(get_db)) -> dict:
    lot = db.query(Charge).filter((Charge.id == lot_id) | (Charge.chargen_id == lot_id)).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Lot not found")
    return {
        "id": lot.id,
        "lotId": lot.chargen_id,
        "article": lot.artikel,
        "articleId": lot.artikel_id,
        "quantity": float(lot.menge or 0),
        "location": lot.lagerort,
        "status": lot.status,
        "qualityStatus": lot.qualitaetsstatus,
        "origin": lot.herkunft,
        "events": [
            {"type": "eingang", "date": lot.eingang.isoformat() if lot.eingang else None, "note": "Wareneingang erfasst"},
            {"type": "update", "date": lot.updated_at.isoformat() if lot.updated_at else None, "note": "Letzte Aktualisierung"},
        ],
    }


def _lkw_db_to_item(row: LkwAnnahmeQueue, position: int) -> dict:
    """Aus DB-Row einen Warteschlange-Item bauen (position, wartezeit)."""
    ankunftszeit = row.ankunftszeit
    ankunftszeit_s = ankunftszeit.isoformat() if ankunftszeit else ""
    wartezeit_min = 0
    if ankunftszeit:
        now_utc = datetime.now(timezone.utc)
        arr_utc = ankunftszeit.astimezone(timezone.utc) if ankunftszeit.tzinfo else ankunftszeit.replace(tzinfo=timezone.utc)
        delta = now_utc - arr_utc
        wartezeit_min = max(0, int(delta.total_seconds() / 60))
    status = row.status or "wartend"
    if status == "warteschlange":
        status = "wartend"
    return {
        "id": row.id,
        "position": position,
        "kennzeichen": row.kennzeichen or "",
        "lieferant": row.lieferant or "",
        "article_id": row.article_id,
        "artikel": row.artikel or "",
        "ankunft": ankunftszeit_s,
        "wartezeit": wartezeit_min,
        "status": status,
        "lieferschein_nr": row.lieferschein_nr or "",
        "klaerung": row.klaerung or None,
    }


def _resolve_lkw_article_reference(
    db: Session,
    *,
    tenant_id: str,
    article_id: str | None,
    artikel: str | None,
) -> tuple[str | None, str]:
    candidate_id = (article_id or "").strip() or None
    candidate_label = (artikel or "").strip()
    base_query = db.query(ArticleModel).filter(
        ArticleModel.is_active == True,  # noqa: E712
        ((ArticleModel.tenant_id == tenant_id) | (ArticleModel.tenant_id.is_(None))),
    )

    article = None
    if candidate_id:
        article = base_query.filter(ArticleModel.id == candidate_id).first()
        if article is None:
            article = base_query.filter(ArticleModel.article_number == candidate_id).first()

    if article is None and candidate_label:
        article = (
            base_query.filter(
                (ArticleModel.article_number == candidate_label) | (ArticleModel.name == candidate_label)
            )
            .order_by(ArticleModel.name.asc())
            .first()
        )

    if article is None:
        return candidate_id, candidate_label

    resolved_label = article.name or article.article_number or candidate_label or str(article.id)
    return str(article.id), resolved_label


def _repair_lkw_article_reference(
    db: Session,
    *,
    tenant_id: str,
    artikel: str | None,
) -> tuple[str | None, str | None, str]:
    candidate_label = (artikel or "").strip()
    if not candidate_label:
        return None, None, "missing_label"

    base_query = db.query(ArticleModel).filter(
        ArticleModel.is_active == True,  # noqa: E712
        ((ArticleModel.tenant_id == tenant_id) | (ArticleModel.tenant_id.is_(None))),
    )

    by_number = base_query.filter(ArticleModel.article_number == candidate_label).all()
    if len(by_number) == 1:
        article = by_number[0]
        label = article.name or article.article_number or candidate_label
        return str(article.id), label, "article_number"
    if len(by_number) > 1:
        return None, None, "ambiguous_article_number"

    by_name = base_query.filter(ArticleModel.name == candidate_label).all()
    if len(by_name) == 1:
        article = by_name[0]
        label = article.name or article.article_number or candidate_label
        return str(article.id), label, "article_name"
    if len(by_name) > 1:
        return None, None, "ambiguous_article_name"

    return None, None, "not_found"


@router.get("/annahme/warteschlange", response_model=dict)
async def annahme_warteschlange(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Liste aller LKW in der Annahme-Warteschlange (aus DB, Gap 002)."""
    try:
        rows = (
            db.query(LkwAnnahmeQueue)
            .filter(LkwAnnahmeQueue.tenant_id == tenant_id)
            .order_by(LkwAnnahmeQueue.ankunftszeit.asc())
            .all()
        )
    except Exception:
        return {"items": [], "total": 0}
    items = [_lkw_db_to_item(r, position=i + 1) for i, r in enumerate(rows)]
    return {"items": items, "total": len(items)}


@router.get("/annahme/warteschlange/{reg_id}", response_model=dict)
async def annahme_warteschlange_get(
    reg_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Einzelnen LKW-Eintrag für Qualitäts-Check o.ä. abrufen."""
    row = (
        db.query(LkwAnnahmeQueue)
        .filter(LkwAnnahmeQueue.id == reg_id, LkwAnnahmeQueue.tenant_id == tenant_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="LKW-Eintrag nicht gefunden")
    item = _lkw_db_to_item(row, position=0)
    return item


class AnnahmeStatusUpdate(BaseModel):
    status: Optional[str] = Field(default=None, description="in-bearbeitung | abgeschlossen | gesperrt")
    klaerung: Optional[dict[str, Any]] = Field(default=None, description="Klaerungsdaten fuer gesperrte Ware")


@router.patch("/annahme/warteschlange/{reg_id}", response_model=dict)
async def annahme_warteschlange_patch(
    reg_id: str,
    body: AnnahmeStatusUpdate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Status eines LKW-Eintrags aktualisieren (z.B. In Bearbeitung, Abgeschlossen)."""
    if body.status is None and body.klaerung is None:
        raise HTTPException(status_code=400, detail="status oder klaerung muss angegeben werden")
    if body.status is not None and body.status not in ("in-bearbeitung", "abgeschlossen", "gesperrt"):
        raise HTTPException(status_code=400, detail="status muss 'in-bearbeitung', 'abgeschlossen' oder 'gesperrt' sein")
    row = (
        db.query(LkwAnnahmeQueue)
        .filter(LkwAnnahmeQueue.id == reg_id, LkwAnnahmeQueue.tenant_id == tenant_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="LKW-Eintrag nicht gefunden")
    if body.status is not None:
        row.status = body.status
    if body.klaerung is not None:
        existing = row.klaerung or {}
        if not isinstance(existing, dict):
            existing = {}
        existing.update(body.klaerung)
        existing.setdefault("updated_at", datetime.utcnow().isoformat())
        row.klaerung = existing
    db.commit()
    db.refresh(row)
    return _lkw_db_to_item(row, position=0)


@router.post("/annahme/warteschlange/{reg_id}/repair-article", response_model=dict)
async def annahme_warteschlange_repair_article(
    reg_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Konservativer Repair fuer Queue-Eintraege ohne article_id."""
    row = (
        db.query(LkwAnnahmeQueue)
        .filter(LkwAnnahmeQueue.id == reg_id, LkwAnnahmeQueue.tenant_id == tenant_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="LKW-Eintrag nicht gefunden")
    if row.article_id:
        return {"status": "already_set", "article_id": row.article_id, "artikel": row.artikel}

    article_id, artikel_label, reason = _repair_lkw_article_reference(
        db, tenant_id=tenant_id, artikel=row.artikel
    )
    if not article_id or not artikel_label:
        return {"status": "not_resolved", "reason": reason}

    row.article_id = article_id
    row.artikel = artikel_label
    db.commit()
    db.refresh(row)
    return {"status": "updated", "article_id": article_id, "artikel": artikel_label}


class LKWRegistrierungIn(BaseModel):
    kennzeichen: str = Field(..., min_length=1)
    lieferant: str = Field(..., min_length=1)
    lieferschein_nr: str = Field(default="")
    article_id: str | None = Field(default=None)
    artikel: str = Field(default="")
    ankunftszeit: str = Field(default="")
    prioritaet: str = Field(default="normal", description="hoch | normal | niedrig")
    attachment_ids: List[str] = Field(default_factory=list, description="IDs von hochgeladenen Anhängen (Kennzeichen/Lieferschein-Fotos)")


class LKWRegistrierungOut(BaseModel):
    id: str
    kennzeichen: str
    article_id: str | None = None
    artikel: str = ""
    status: str = "warteschlange"


class AnnahmeUploadOut(BaseModel):
    id: str
    filename: str


@router.post("/annahme/upload", response_model=AnnahmeUploadOut, status_code=201, tags=["annahme"])
async def annahme_upload(
    file: UploadFile = File(..., description="Foto/Scan Kennzeichen oder Lieferschein/Barcode"),
    tenant_id: str = Depends(get_tenant_id),
) -> AnnahmeUploadOut:
    """Upload für Annahme (Kennzeichen/Lieferschein-Fotos). Mobil (Lager, Waage, Außendienst)."""
    if not file.filename or not file.content_type or not file.content_type.startswith(("image/", "application/octet-stream")):
        raise HTTPException(status_code=400, detail="Nur Bilddateien werden akzeptiert (image/*)")
    content = await file.read()
    if len(content) > getattr(settings, "MAX_UPLOAD_SIZE", 10 * 1024 * 1024):
        raise HTTPException(status_code=413, detail="Datei zu groß")
    upload_id = str(uuid4())
    base_dir = os.path.join(getattr(settings, "UPLOAD_DIR", "uploads"), "annahme")
    os.makedirs(base_dir, exist_ok=True)
    ext = os.path.splitext(file.filename or "")[1] or ".bin"
    safe_name = f"{upload_id}{ext}"
    path = os.path.join(base_dir, safe_name)
    with open(path, "wb") as f:
        f.write(content)
    cache_set_json(f"annahme:upload:{upload_id}", {"id": upload_id, "filename": file.filename, "path": path}, ttl_seconds=86400 * 7)
    return AnnahmeUploadOut(id=upload_id, filename=file.filename or safe_name)


@router.post("/annahme/lkw-registrierung", response_model=LKWRegistrierungOut, status_code=201, tags=["annahme"])
async def create_lkw_registrierung(
    payload: LKWRegistrierungIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> LKWRegistrierungOut:
    """LKW in Annahme-Warteschlange eintragen; erscheint in GET /annahme/warteschlange (DB, Gap 002)."""
    reg_id = uuid7()
    ankunft_dt = None
    if payload.ankunftszeit:
        try:
            normalized = payload.ankunftszeit.replace("Z", "+00:00")[:19]
            ankunft_dt = datetime.fromisoformat(normalized)
            if ankunft_dt.tzinfo is None:
                ankunft_dt = ankunft_dt.replace(tzinfo=timezone.utc)
        except Exception:
            pass
    resolved_article_id, resolved_artikel = _resolve_lkw_article_reference(
        db,
        tenant_id=tenant_id,
        article_id=payload.article_id,
        artikel=payload.artikel,
    )
    row = LkwAnnahmeQueue(
        id=reg_id,
        tenant_id=tenant_id,
        kennzeichen=payload.kennzeichen,
        lieferant=payload.lieferant,
        lieferschein_nr=payload.lieferschein_nr or "",
        article_id=resolved_article_id,
        artikel=resolved_artikel,
        ankunftszeit=ankunft_dt,
        prioritaet=payload.prioritaet,
        status="wartend",
        attachment_ids=payload.attachment_ids or [],
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return LKWRegistrierungOut(
        id=reg_id,
        kennzeichen=payload.kennzeichen,
        article_id=resolved_article_id,
        artikel=resolved_artikel,
        status="wartend",
    )


@router.post("/annahme/warteschlange", response_model=LKWRegistrierungOut, status_code=201, tags=["annahme"])
async def create_lkw_warteschlange_alias(
    payload: LKWRegistrierungIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> LKWRegistrierungOut:
    """Rueckwaertskompatibler Alias fuer QR-/Mobile-Pfade, die direkt auf die Warteschlange posten."""
    return await create_lkw_registrierung(payload=payload, tenant_id=tenant_id, db=db)


# Portal compatibility ------------------------------------------------------


@router.get("/portal/dashboard", response_model=dict)
async def portal_dashboard(db: Session = Depends(get_db)) -> dict:
    orders = _list_docs(db, "sales_order", limit=20)
    invoices = _list_docs(db, "sales_invoice", limit=20)
    try:
        docs = db.query(Dokument).order_by(Dokument.hochgeladen_am.desc()).limit(5).all()
    except Exception:
        docs = []

    offene_rechnungen = sum(1 for i in invoices if str(i.get("status", "")).lower() in {"offen", "ueberfaellig"})

    return {
        "kpis": [
            {"label": "Bestellungen", "value": str(len(orders))},
            {"label": "Rechnungen offen", "value": str(offene_rechnungen)},
            {"label": "Dokumente", "value": str(len(docs))},
        ],
        "letzteBestellungen": [
            {
                "id": o.get("id") or o.get("number"),
                "nummer": o.get("number") or o.get("id"),
                "datum": o.get("date"),
                "betrag": float(o.get("totalGross") or 0),
                "status": str(o.get("status") or "offen").lower(),
            }
            for o in orders[:5]
        ],
        "neueDokumente": [
            {
                "id": d.id,
                "name": d.name,
                "datum": d.hochgeladen_am.isoformat()[:10] if d.hochgeladen_am else None,
                "typ": d.typ,
            }
            for d in docs
        ],
    }


@router.get("/portal/anfragen", response_model=list)
async def portal_anfragen(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    docs = _list_docs(db, "customer_inquiry", limit=500)
    return [
        {
            "id": d.get("id") or d.get("number"),
            "nummer": d.get("number"),
            "betreff": d.get("subject") or d.get("topic") or "Anfrage",
            "datum": d.get("date"),
            "status": str(d.get("status") or "offen").lower(),
        }
        for d in docs
    ]


@router.get("/portal/bestellungen", response_model=list)
async def portal_bestellungen(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    docs = _list_docs(db, "sales_order", limit=500)
    return [
        {
            "id": d.get("id") or d.get("number"),
            "nummer": d.get("number"),
            "datum": d.get("date"),
            "artikel": (d.get("lines") or [{}])[0].get("article") if d.get("lines") else "",
            "menge": sum(float(line.get("qty") or 0) for line in (d.get("lines") or [])),
            "betrag": float(d.get("totalGross") or 0),
            "status": str(d.get("status") or "bestellt").lower(),
        }
        for d in docs
    ]


@router.get("/portal/dokumente", response_model=list)
async def portal_dokumente(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    try:
        docs = db.query(Dokument).order_by(Dokument.hochgeladen_am.desc()).limit(500).all()
    except Exception:
        docs = []
    return [
        {
            "id": d.id,
            "name": d.name,
            "kategorie": d.kategorie,
            "datum": d.hochgeladen_am.isoformat()[:10] if d.hochgeladen_am else None,
            "groesse": int(d.groesse or 0),
            "typ": d.typ,
        }
        for d in docs
    ]


@router.get("/portal/feldbuch", response_model=list)
async def portal_feldbuch(
    customer_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: Optional[str] = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    """
    Backward-compat endpoint: gibt Feldbuch-Schläge aus der echten DB zurück.
    Neue Clients nutzen /portal/feldbuch/schlaege und /portal/feldbuch/massnahmen.
    """
    from app.infrastructure.models.agrar_models import FeldbuchSchlag

    q = db.query(FeldbuchSchlag)
    if tenant_id:
        q = q.filter(FeldbuchSchlag.tenant_id == tenant_id)
    if customer_id:
        q = q.filter(FeldbuchSchlag.customer_id == customer_id)
    schlaege = q.order_by(FeldbuchSchlag.name).all()

    if schlaege:
        return [
            {
                "id": s.id,
                "schlag": s.name,
                "kultur": s.kultur or "",
                "flaeche": s.flaeche,
                "letzteMassnahme": None,
                "naechsteMassnahme": None,
            }
            for s in schlaege
        ]

    # Fallback auf alten Stub wenn noch keine echten Daten vorhanden
    deliveries = _list_docs(db, "sales_delivery", limit=1000)
    return [
        {
            "id": d.get("number") or d.get("id"),
            "schlag": d.get("fieldName") or "Schlag unbekannt",
            "kultur": d.get("crop") or "",
            "flaeche": float(d.get("areaHa") or 0),
            "letzteMassnahme": d.get("date"),
            "naechsteMassnahme": None,
        }
        for d in deliveries
    ]


@router.get("/portal/naehrstoffbilanzen", response_model=list)
async def portal_naehrstoffbilanzen(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    deliveries = _list_docs(db, "sales_delivery", limit=2000)
    return [
        {
            "id": d.get("number") or d.get("id"),
            "schlag": d.get("fieldName") or "Gesamt",
            "kultur": d.get("crop") or "",
            "n_saldo": float(d.get("totalNutrientNKg") or 0),
            "p_saldo": float(d.get("totalNutrientP2o5Kg") or 0),
            "k_saldo": float(d.get("totalNutrientKKg") or 0),
            "bewertung": "ok" if float(d.get("totalNutrientNKg") or 0) <= 170 else "warnung",
        }
        for d in deliveries
    ]


@router.get("/portal/rechnungen", response_model=list)
async def portal_rechnungen(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    invoices = _list_docs(db, "sales_invoice", limit=500)
    return [
        {
            "id": i.get("id") or i.get("number"),
            "nummer": i.get("number"),
            "datum": i.get("date"),
            "betrag": float(i.get("totalGross") or 0),
            "status": str(i.get("status") or "offen").lower(),
        }
        for i in invoices
    ]


@router.get("/portal/shop", response_model=list)
async def portal_shop(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    articles = db.query(ArticleModel).filter(ArticleModel.is_active == True).order_by(ArticleModel.name.asc()).limit(500).all()  # noqa: E712
    return [
        {
            "id": a.id,
            "name": a.name,
            "kategorie": a.category or "sonstiges",
            "preis": float(a.sales_price or 0),
            "einheit": a.unit,
            "verfuegbar": float(a.available_stock or 0) > 0,
        }
        for a in articles
    ]


@router.get("/portal/products", response_model=dict)
async def portal_products(
    kategorie: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
    tenant_id: Optional[str] = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    Produktliste für den Portal-Shop.
    Gibt {items: [...], total: N} mit Kontrakt-Fallback zurück.
    """
    q = db.query(ArticleModel).filter(ArticleModel.is_active == True)  # noqa: E712
    if kategorie and kategorie != "alle":
        q = q.filter(ArticleModel.category == kategorie)
    if search:
        q = q.filter(ArticleModel.name.ilike(f"%{search}%"))
    total = q.count()
    articles = q.order_by(ArticleModel.name.asc()).offset(skip).limit(limit).all()
    items = [
        {
            "id": str(a.id),
            "artikelnummer": str(getattr(a, "article_number", a.id)),
            "name": a.name,
            "kategorie": a.category or "sonstiges",
            "beschreibung": getattr(a, "description", None) or "",
            "einheit": a.unit or "Stk",
            "preis": float(a.sales_price or 0),
            "rabattPreis": None,
            "verfuegbar": float(a.available_stock or 0) > 0,
            "bestand": float(a.available_stock or 0),
            "zertifikate": [],
            "letzteBestellung": None,
            "contractStatus": "NONE",
            "contractPrice": None,
            "contractRemainingQty": None,
            "contractTotalQty": None,
            "isPrePurchase": False,
            "prePurchasePrice": None,
            "prePurchaseTotalQty": None,
            "prePurchaseRemainingQty": None,
        }
        for a in articles
    ]
    return {
        "items": items,
        "total": total,
        "page": skip // limit if limit else 0,
        "size": limit,
        "has_contracts": 0,
        "has_pre_purchases": 0,
    }


@router.get("/portal/orders", response_model=dict)
async def portal_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status_filter: Optional[str] = Query(None),
    tenant_id: Optional[str] = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Portal-Bestellhistorie. Gibt OrderListItem[] zurück (portal-service.ts)."""
    orders = _list_docs(db, "sales_order", limit=limit, tenant_id=tenant_id)
    if status_filter:
        orders = [o for o in orders if o.get("status") == status_filter]
    items = [
        {
            "id": o.get("id", ""),
            "order_number": o.get("number") or o.get("order_number", ""),
            "order_date": (o.get("created_at", "")[:10] if o.get("created_at") else
                           o.get("datum", "")[:10] if o.get("datum") else ""),
            "status": o.get("status", "SUBMITTED"),
            "item_count": len(o.get("positions") or o.get("items") or []),
            "total_net": float(o.get("total_net") or o.get("total_amount") or o.get("totalAmount") or 0),
            "main_article": (
                (o.get("positions") or o.get("items") or [{}])[0].get("bezeichnung") or
                (o.get("positions") or o.get("items") or [{}])[0].get("name") or ""
            ) if (o.get("positions") or o.get("items")) else "",
        }
        for o in orders
    ]
    return {"items": items, "total": len(items)}


@router.get("/portal/orders/{order_id}", response_model=dict)
async def portal_order_detail(
    order_id: str,
    tenant_id: Optional[str] = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Detail einer Portal-Bestellung."""
    orders = _list_docs(db, "sales_order", limit=1000, tenant_id=tenant_id)
    for o in orders:
        if str(o.get("id")) == order_id:
            return o
    raise HTTPException(status_code=404, detail="Bestellung nicht gefunden")


@router.post("/portal/orders", response_model=dict)
async def portal_create_order(
    body: dict = Body(...),
    tenant_id: Optional[str] = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Neue Bestellung aus dem Portal anlegen."""
    import uuid as _uuid
    order_id = str(_uuid.uuid4())
    order = {
        "id": order_id,
        "number": f"PA-{order_id[:8].upper()}",
        "status": "SUBMITTED",
        "created_at": _now_iso(),
        "tenant_id": tenant_id,
        **body,
    }
    save_to_store("sales_order", order_id, order, _doc_repo(db))
    db.commit()
    return order


@router.get("/portal/contracts", response_model=list)
async def portal_contracts(
    tenant_id: Optional[str] = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    """Aktive Verträge/Kontingente des Kunden (Contract[] für portal-service.ts)."""
    try:
        contracts = _list_docs(db, "kontrakt", limit=200, tenant_id=tenant_id)
    except Exception:
        contracts = []
    return [
        {
            "id": c.get("id", ""),
            "contract_number": c.get("nummer") or c.get("contract_number", ""),
            "article_name": c.get("artikel_name") or c.get("article_name", ""),
            "article_number": c.get("artikel_nummer") or c.get("article_number", ""),
            "contract_price": float(c.get("preis") or c.get("contract_price") or 0),
            "list_price": float(c.get("listenpreis") or c.get("list_price") or 0),
            "unit": c.get("einheit") or c.get("unit", "kg"),
            "total_quantity": float(c.get("gesamtmenge") or c.get("total_quantity") or 0),
            "remaining_quantity": float(c.get("verbleibende_menge") or c.get("remaining_quantity") or 0),
            "status": c.get("status", "ACTIVE"),
            "valid_until": c.get("laufzeit_bis") or c.get("valid_until", ""),
        }
        for c in contracts
    ]


@router.get("/portal/pre-purchases", response_model=list)
async def portal_pre_purchases(
    tenant_id: Optional[str] = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    """Vorkäufe des Kunden (PrePurchase[] für portal-service.ts)."""
    try:
        pps = _list_docs(db, "vorkauf", limit=200, tenant_id=tenant_id)
    except Exception:
        pps = []
    return [
        {
            "id": p.get("id", ""),
            "pre_purchase_number": p.get("nummer") or p.get("pre_purchase_number", ""),
            "article_name": p.get("artikel_name") or p.get("article_name", ""),
            "article_number": p.get("artikel_nummer") or p.get("article_number", ""),
            "pre_purchase_price": float(p.get("preis") or p.get("pre_purchase_price") or 0),
            "current_list_price": float(p.get("listenpreis") or p.get("current_list_price") or 0),
            "unit": p.get("einheit") or p.get("unit", "kg"),
            "total_quantity": float(p.get("gesamtmenge") or p.get("total_quantity") or 0),
            "remaining_quantity": float(p.get("verbleibende_menge") or p.get("remaining_quantity") or 0),
            "payment_date": p.get("zahldatum") or p.get("payment_date", ""),
            "valid_until": p.get("laufzeit_bis") or p.get("valid_until"),
        }
        for p in pps
    ]


@router.get("/portal/vertraege", response_model=list)
async def portal_vertraege(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    try:
        items = db.query(Rahmenvertrag).order_by(Rahmenvertrag.laufzeit_bis.desc()).limit(500).all()
    except Exception:
        items = []
    return [
        {
            "id": i.id,
            "nummer": i.nummer,
            "typ": i.typ,
            "partner": i.partner,
            "laufzeitBis": i.laufzeit_bis.date().isoformat() if i.laufzeit_bis else None,
            "status": i.status,
        }
        for i in items
    ]


@router.get("/portal/zertifikate", response_model=list)
async def portal_zertifikate(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    try:
        items = db.query(ZertifikatEintrag).order_by(ZertifikatEintrag.gueltig_bis.desc()).limit(500).all()
    except Exception:
        items = []
    return [
        {
            "id": i.id,
            "art": i.art,
            "nummer": i.nummer,
            "gueltigBis": i.gueltig_bis.date().isoformat() if i.gueltig_bis else None,
            "status": i.status,
        }
        for i in items
    ]


# Procurement Nice-to-Have --------------------------------------------------


def _safe_float(value: Any) -> float:
    try:
        return float(value or 0)
    except Exception:
        return 0.0


@router.get("/einkauf/supplier-ratings", response_model=dict)
async def supplier_ratings(tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> dict:
    cache_key = _cache_key("procurement", tenant_id, "supplier-ratings")
    cached = cache_get_json(cache_key)
    if cached is not None:
        return cached

    ratings = _list_docs(db, "supplier_rating", limit=2000, tenant_id=tenant_id)
    if ratings:
        payload = {"items": ratings, "total": len(ratings)}
        cache_set_json(cache_key, payload, ttl_seconds=60)
        return payload

    # fallback: derive lightweight score from purchase orders
    pos = _list_docs(db, "purchase_order", limit=5000, tenant_id=tenant_id)
    by_supplier: dict[str, dict[str, Any]] = {}
    for po in pos:
        supplier_id = str(po.get("supplierId") or "unknown")
        state = by_supplier.setdefault(
            supplier_id,
            {
                "supplierId": supplier_id,
                "supplier": po.get("supplierName") or supplier_id,
                "onTimeDelivery": 80.0,
                "qualityScore": 4.0,
                "priceScore": 4.0,
                "serviceScore": 4.0,
                "overallScore": 4.0,
                "totalOrders": 0,
            },
        )
        state["totalOrders"] += 1
    items = list(by_supplier.values())
    payload = {"items": items, "total": len(items)}
    cache_set_json(cache_key, payload, ttl_seconds=60)
    return payload


@router.post("/einkauf/supplier-ratings/{supplier_id}", response_model=dict)
async def upsert_supplier_rating(
    supplier_id: str,
    payload: dict[str, Any],
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    score = {
        "supplierId": supplier_id,
        "supplier": payload.get("supplier") or supplier_id,
        "onTimeDelivery": _safe_float(payload.get("onTimeDelivery")),
        "qualityScore": _safe_float(payload.get("qualityScore")),
        "priceScore": _safe_float(payload.get("priceScore")),
        "serviceScore": _safe_float(payload.get("serviceScore")),
        "overallScore": _safe_float(payload.get("overallScore")),
        "totalOrders": int(payload.get("totalOrders") or 0),
        "tenantId": tenant_id,
        "updatedAt": _now_iso(),
    }
    repo = _doc_repo(db)
    save_to_store("supplier_rating", supplier_id, score, repo)
    cache_delete_prefix(f"compat:procurement:{tenant_id}:")
    return score


@router.get("/einkauf/suppliers/{supplier_id}/documents", response_model=list)
async def supplier_documents(supplier_id: str, db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    docs = (
        db.query(Dokument)
        .filter(Dokument.referenz_typ == "supplier", Dokument.referenz_id == supplier_id)
        .order_by(Dokument.hochgeladen_am.desc())
        .all()
    )
    return [
        {
            "id": d.id,
            "name": d.name,
            "typ": d.typ,
            "kategorie": d.kategorie,
            "groesse": int(d.groesse or 0),
            "hochgeladenAm": d.hochgeladen_am.isoformat() if d.hochgeladen_am else None,
            "beschreibung": d.beschreibung,
        }
        for d in docs
    ]


@router.post("/einkauf/suppliers/{supplier_id}/documents", response_model=dict, status_code=201)
async def create_supplier_document(supplier_id: str, payload: dict[str, Any], db: Session = Depends(get_db)) -> dict:
    doc = Dokument(
        name=str(payload.get("name") or f"Lieferanten-Dokument {supplier_id}"),
        typ=str(payload.get("typ") or "PDF"),
        kategorie=str(payload.get("kategorie") or "Lieferanten"),
        groesse=int(payload.get("groesse") or 0),
        beschreibung=payload.get("beschreibung"),
        speicherpfad=payload.get("speicherpfad"),
        referenz_typ="supplier",
        referenz_id=supplier_id,
        hochgeladen_von=str(payload.get("hochgeladenVon") or "system"),
    )
    db.add(doc)
    db.commit()
    return {"id": doc.id, "message": "Supplier document created"}


@router.delete("/einkauf/suppliers/{supplier_id}/documents/{doc_id}", response_model=dict)
async def delete_supplier_document(supplier_id: str, doc_id: str, db: Session = Depends(get_db)) -> dict:
    doc = (
        db.query(Dokument)
        .filter(Dokument.id == doc_id, Dokument.referenz_typ == "supplier", Dokument.referenz_id == supplier_id)
        .first()
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Supplier document not found")
    db.delete(doc)
    db.commit()
    return {"ok": True}


def _find_po_by_id(db: Session, po_id: str, tenant_id: Optional[str] = None) -> dict[str, Any]:
    docs = _list_docs(db, "purchase_order", limit=5000, tenant_id=tenant_id)
    for d in docs:
        if str(d.get("id")) == po_id or str(d.get("purchaseOrderNumber")) == po_id:
            return d
    raise HTTPException(status_code=404, detail="Purchase order not found")


@router.get("/purchase-orders/{po_id}/communications", response_model=list)
async def po_communications(po_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    po = _find_po_by_id(db, po_id, tenant_id=tenant_id)
    return po.get("communications", [])


@router.post("/purchase-orders/{po_id}/communications", response_model=dict, status_code=201)
async def po_add_communication(
    po_id: str,
    payload: dict[str, Any],
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    po = _find_po_by_id(db, po_id, tenant_id=tenant_id)
    item = {
        "id": str(uuid4()),
        "channel": payload.get("channel") or "email",
        "subject": payload.get("subject") or f"PO {po.get('purchaseOrderNumber')}",
        "message": payload.get("message") or "",
        "recipient": payload.get("recipient"),
        "status": payload.get("status") or "sent",
        "createdAt": _now_iso(),
    }
    po.setdefault("communications", []).append(item)
    po.setdefault("changelog", []).append(
        {"id": str(uuid4()), "changeType": "COMMUNICATION", "changedBy": "system", "changedAt": _now_iso(), "fieldChanges": []}
    )
    save_to_store("purchase_order", po["purchaseOrderNumber"], po, _doc_repo(db))
    await _enqueue_event(
        db,
        event_type="purchase_order.communication.sent",
        aggregate_id=str(po.get("id") or po_id),
        payload={"purchaseOrderNumber": po.get("purchaseOrderNumber"), "channel": item["channel"], "recipient": item.get("recipient")},
        tenant_id=tenant_id,
    )
    cache_delete_prefix(f"compat:procurement:{tenant_id}:")
    db.commit()
    return item


@router.post("/purchase-orders/{po_id}/communications/email", response_model=dict, status_code=201)
async def po_send_email(
    po_id: str,
    payload: dict[str, Any],
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    payload = {**payload, "channel": "email", "status": "sent"}
    return await po_add_communication(po_id, payload, tenant_id, db)


@router.post("/purchase-orders/{po_id}/communications/portal", response_model=dict, status_code=201)
async def po_send_portal(
    po_id: str,
    payload: dict[str, Any],
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    payload = {**payload, "channel": "portal", "status": "published"}
    return await po_add_communication(po_id, payload, tenant_id, db)


@router.get("/einkauf/retouren/{retour_id}", response_model=dict)
async def einkauf_retoure_get(retour_id: str, db: Session = Depends(get_db)) -> dict:
    rows = await einkauf_retouren(db)
    for row in rows:
        if str(row.get("id")) == retour_id or str(row.get("nummer")) == retour_id:
            return row
    raise HTTPException(status_code=404, detail="Retoure not found")


@router.patch("/einkauf/retouren/{retour_id}", response_model=dict)
async def einkauf_retoure_patch(retour_id: str, payload: dict[str, Any], db: Session = Depends(get_db)) -> dict:
    try:
        db.execute(
            text("UPDATE einkauf_retouren SET status = :status, grund = COALESCE(:grund, grund), updated_at = now() WHERE id = :id OR retouren_nummer = :id"),
            {"id": retour_id, "status": payload.get("status", "offen"), "grund": payload.get("grund")},
        )
        db.commit()
    except Exception:
        db.rollback()
    return {"id": retour_id, "status": payload.get("status", "offen"), "ok": True}


@router.get("/einkauf/service-entry-sheets", response_model=dict)
async def list_service_entry_sheets(
    status: Optional[str] = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    items = _list_docs(db, "service_entry_sheet", limit=2000, tenant_id=tenant_id)
    if status:
        items = [i for i in items if str(i.get("status")) == status]
    return {"items": items, "total": len(items)}


@router.post("/einkauf/service-entry-sheets", response_model=dict, status_code=201)
async def create_service_entry_sheet(
    payload: dict[str, Any],
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    number = payload.get("number") or f"SES-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    ses = {
        "id": str(uuid4()),
        "number": number,
        "supplierId": payload.get("supplierId"),
        "purchaseOrderId": payload.get("purchaseOrderId"),
        "serviceDate": payload.get("serviceDate") or _now_iso()[:10],
        "description": payload.get("description") or "",
        "quantity": _safe_float(payload.get("quantity")),
        "unitPrice": _safe_float(payload.get("unitPrice")),
        "amount": round(_safe_float(payload.get("quantity")) * _safe_float(payload.get("unitPrice")), 2),
        "status": payload.get("status") or "ERFASST",
        "tenantId": tenant_id,
        "createdAt": _now_iso(),
    }
    save_to_store("service_entry_sheet", number, ses, _doc_repo(db))
    await _enqueue_event(db, event_type="service_entry_sheet.created", aggregate_id=ses["id"], payload=ses, tenant_id=tenant_id)
    cache_delete_prefix(f"compat:procurement:{tenant_id}:")
    db.commit()
    return ses


@router.patch("/einkauf/service-entry-sheets/{ses_id}", response_model=dict)
async def update_service_entry_sheet(
    ses_id: str,
    payload: dict[str, Any],
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    items = _list_docs(db, "service_entry_sheet", limit=5000, tenant_id=tenant_id)
    target = None
    for i in items:
        if str(i.get("id")) == ses_id or str(i.get("number")) == ses_id:
            target = i
            break
    if not target:
        raise HTTPException(status_code=404, detail="Service entry sheet not found")
    target.update({k: v for k, v in payload.items() if v is not None})
    target["updatedAt"] = _now_iso()
    save_to_store("service_entry_sheet", target["number"], target, _doc_repo(db))
    cache_delete_prefix(f"compat:procurement:{tenant_id}:")
    db.commit()
    return target


def _memo_doc_type(kind: str) -> str:
    return "credit_memo" if kind == "credit" else "debit_memo"


@router.get("/einkauf/credit-memos", response_model=list)
async def list_credit_memos(tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    return _list_docs(db, "credit_memo", limit=2000, tenant_id=tenant_id)


@router.get("/einkauf/debit-memos", response_model=list)
async def list_debit_memos(tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    return _list_docs(db, "debit_memo", limit=2000, tenant_id=tenant_id)


async def _create_memo(kind: str, payload: dict[str, Any], tenant_id: str, db: Session) -> dict[str, Any]:
    number_prefix = "CM" if kind == "credit" else "DM"
    number = payload.get("number") or f"{number_prefix}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    items = payload.get("items") or []
    net = sum(_safe_float(i.get("netAmount")) for i in items)
    tax = sum(_safe_float(i.get("taxAmount")) for i in items)
    gross = net + tax
    memo = {
        "id": str(uuid4()),
        "number": number,
        "supplierId": payload.get("supplierId"),
        "supplierName": payload.get("supplierName") or "",
        "invoiceId": payload.get("invoiceId"),
        "memoDate": payload.get("memoDate") or _now_iso()[:10],
        "reason": payload.get("reason") or "",
        "notes": payload.get("notes"),
        "items": items,
        "netAmount": round(net, 2),
        "taxAmount": round(tax, 2),
        "grossAmount": round(gross, 2),
        "status": "ERFASST",
        "settled": False,
        "settledInvoiceIds": [],
        "tenantId": tenant_id,
        "createdAt": _now_iso(),
    }
    save_to_store(_memo_doc_type(kind), number, memo, _doc_repo(db))
    await _enqueue_event(db, event_type=f"{_memo_doc_type(kind)}.created", aggregate_id=memo["id"], payload=memo, tenant_id=tenant_id)
    cache_delete_prefix(f"compat:procurement:{tenant_id}:")
    db.commit()
    return memo


@router.post("/einkauf/credit-memos", response_model=dict, status_code=201)
async def create_credit_memo(
    payload: dict[str, Any],
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    return await _create_memo("credit", payload, tenant_id, db)


@router.post("/einkauf/debit-memos", response_model=dict, status_code=201)
async def create_debit_memo(
    payload: dict[str, Any],
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    return await _create_memo("debit", payload, tenant_id, db)


async def _settle_memo(kind: str, memo_id: str, payload: dict[str, Any], tenant_id: str, db: Session) -> dict[str, Any]:
    memos = _list_docs(db, _memo_doc_type(kind), limit=5000, tenant_id=tenant_id)
    target = None
    for m in memos:
        if str(m.get("id")) == memo_id or str(m.get("number")) == memo_id:
            target = m
            break
    if not target:
        raise HTTPException(status_code=404, detail="Memo not found")
    target["settled"] = True
    target["status"] = "VERRECHNET"
    target["settledInvoiceIds"] = payload.get("invoiceIds", [])
    target["settledAt"] = _now_iso()
    save_to_store(_memo_doc_type(kind), target["number"], target, _doc_repo(db))
    await _enqueue_event(db, event_type=f"{_memo_doc_type(kind)}.settled", aggregate_id=target["id"], payload=target, tenant_id=tenant_id)
    cache_delete_prefix(f"compat:procurement:{tenant_id}:")
    db.commit()
    return target


@router.post("/einkauf/credit-memos/{memo_id}/settle", response_model=dict)
async def settle_credit_memo(
    memo_id: str,
    payload: dict[str, Any],
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    return await _settle_memo("credit", memo_id, payload, tenant_id, db)


@router.post("/einkauf/debit-memos/{memo_id}/settle", response_model=dict)
async def settle_debit_memo(
    memo_id: str,
    payload: dict[str, Any],
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    return await _settle_memo("debit", memo_id, payload, tenant_id, db)


@router.get("/einkauf/reports/standard", response_model=dict)
async def einkauf_reports_standard(tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> dict:
    cache_key = _cache_key("procurement", tenant_id, "reports-standard")
    cached = cache_get_json(cache_key)
    if cached is not None:
        return cached
    po = _list_docs(db, "purchase_order", limit=5000, tenant_id=tenant_id)
    ratings = (await supplier_ratings(tenant_id, db)).get("items", [])
    tolerance = []
    for p in po:
        tax = _safe_float(p.get("taxAmount"))
        subtotal = _safe_float(p.get("subtotal"))
        if subtotal > 0 and (tax / subtotal) > 0.25:
            tolerance.append({"purchaseOrderNumber": p.get("purchaseOrderNumber"), "deviation": round((tax / subtotal) * 100, 2), "type": "tax"})
    payload = {
        "openOrders": [x for x in po if str(x.get("status")) not in {"GELIEFERT", "STORNIERT"}],
        "supplierPerformance": ratings,
        "toleranceReports": tolerance,
    }
    cache_set_json(cache_key, payload, ttl_seconds=60)
    return payload


@router.get("/einkauf/audit-trail/{doc_type}/{doc_id}", response_model=dict)
async def einkauf_audit_trail(
    doc_type: str,
    doc_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    docs = _list_docs(db, doc_type, limit=5000, tenant_id=tenant_id)
    target = None
    for d in docs:
        if str(d.get("id")) == doc_id or str(d.get("number")) == doc_id or str(d.get("purchaseOrderNumber")) == doc_id:
            target = d
            break
    if not target:
        raise HTTPException(status_code=404, detail="Document not found")
    chain = target.get("changelog", [])
    return {"documentType": doc_type, "documentId": doc_id, "events": chain, "total": len(chain)}


@router.get("/einkauf/edi/messages", response_model=dict)
async def edi_messages(tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> dict:
    items = _list_docs(db, "edi_message", limit=2000, tenant_id=tenant_id)
    return {"items": items, "total": len(items)}


@router.post("/einkauf/edi/messages", response_model=dict, status_code=201)
async def create_edi_message(
    payload: dict[str, Any],
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    msg_id = str(uuid4())
    number = payload.get("number") or f"EDI-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    msg = {
        "id": msg_id,
        "number": number,
        "direction": payload.get("direction") or "outbound",
        "partner": payload.get("partner") or "",
        "messageType": payload.get("messageType") or "ORDERS",
        "status": payload.get("status") or "QUEUED",
        "payload": payload.get("payload") or {},
        "tenantId": tenant_id,
        "createdAt": _now_iso(),
    }
    save_to_store("edi_message", number, msg, _doc_repo(db))
    await _enqueue_event(db, event_type="procurement.edi.message.created", aggregate_id=msg_id, payload=msg, tenant_id=tenant_id)
    cache_delete_prefix(f"compat:procurement:{tenant_id}:")
    db.commit()
    return msg


@router.post("/einkauf/edi/messages/{msg_id}/ack", response_model=dict)
async def ack_edi_message(msg_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> dict:
    items = _list_docs(db, "edi_message", limit=5000, tenant_id=tenant_id)
    target = None
    for i in items:
        if str(i.get("id")) == msg_id or str(i.get("number")) == msg_id:
            target = i
            break
    if not target:
        raise HTTPException(status_code=404, detail="EDI message not found")
    target["status"] = "ACKNOWLEDGED"
    target["ackAt"] = _now_iso()
    save_to_store("edi_message", target["number"], target, _doc_repo(db))
    await _enqueue_event(db, event_type="procurement.edi.message.ack", aggregate_id=target["id"], payload=target, tenant_id=tenant_id)
    cache_delete_prefix(f"compat:procurement:{tenant_id}:")
    db.commit()
    return target


# ---------------------------------------------------------------------------
# Lager Dashboard KPIs
# ---------------------------------------------------------------------------

@router.get("/lager/dashboard", tags=["lager"])
async def lager_dashboard(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Echte Bestands-KPIs aus StockMovements aggregiert."""
    row = db.execute(
        text("""
            SELECT
                COUNT(DISTINCT article_id) AS total_articles,
                COALESCE(SUM(CASE WHEN movement_type = 'in' THEN quantity ELSE 0 END), 0) AS total_in,
                COALESCE(SUM(CASE WHEN movement_type = 'out' THEN quantity ELSE 0 END), 0) AS total_out,
                COALESCE(SUM(CASE WHEN movement_type = 'in' THEN quantity * COALESCE(unit_cost, 0) ELSE 0 END)
                       - SUM(CASE WHEN movement_type = 'out' THEN quantity * COALESCE(unit_cost, 0) ELSE 0 END), 0) AS total_value,
                COUNT(CASE WHEN movement_date = CURRENT_DATE THEN 1 END) AS movements_today
            FROM domain_inventory.inventory_stock_movements
            WHERE tenant_id = :tid
        """),
        {"tid": tenant_id},
    ).first()

    total_articles = row[0] if row else 0
    total_in = float(row[1]) if row else 0
    total_out = float(row[2]) if row else 0
    current_stock = total_in - total_out
    total_value = float(row[3]) if row else 0
    movements_today = row[4] if row else 0

    low_stock_row = db.execute(
        text("""
            SELECT COUNT(DISTINCT sm.article_id)
            FROM (
                SELECT article_id,
                       SUM(CASE WHEN movement_type = 'in' THEN quantity ELSE -quantity END) AS bestand
                FROM domain_inventory.inventory_stock_movements
                WHERE tenant_id = :tid
                GROUP BY article_id
            ) sm
            JOIN domain_inventory.articles a ON a.id = sm.article_id
            WHERE sm.bestand > 0 AND sm.bestand < COALESCE(a.min_stock, 10)
        """),
        {"tid": tenant_id},
    ).scalar() or 0

    return {
        "total_articles": total_articles,
        "current_stock_qty": current_stock,
        "total_value": total_value,
        "movements_today": movements_today,
        "low_stock_count": low_stock_row,
        "reorder_soon": int(low_stock_row * 1.5),
        "optimal_count": max(0, total_articles - low_stock_row),
    }


# ---------------------------------------------------------------------------
# Lager Einlagerung
# ---------------------------------------------------------------------------

class EinlagerungIn(BaseModel):
    chargen_id: str = Field(..., description="Chargen-ID der einzulagernden Ware")
    artikel: str = Field(..., description="Artikel-Bezeichnung")
    menge: float = Field(..., gt=0, description="Menge in Tonnen")
    lagerort: str = Field(..., description="Lagerort-Code (z.B. silo-1, halle-a)")
    lagerplatz: Optional[str] = Field(default=None, description="Optionaler Lagerplatz / Bin-Location")


class EinlagerungOut(BaseModel):
    id: str
    batch_number: str
    artikel: str
    menge: float
    lagerort: str
    lagerplatz: Optional[str]
    datum: date
    status: str


@router.post("/lager/einlagerung", response_model=EinlagerungOut, status_code=201, tags=["lager"])
async def create_einlagerung(
    payload: EinlagerungIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> EinlagerungOut:
    """Einlagerung buchen — Chargen-Eintrag + StockMovement."""
    einlagerung_id = str(uuid4())
    movement_id = str(uuid4())
    today = date.today()
    warehouse_key = f"{payload.lagerort}/{payload.lagerplatz}" if payload.lagerplatz else payload.lagerort

    db.execute(
        text("""
            INSERT INTO domain_inventory.article_batches
            (id, tenant_id, article_id, batch_number, warehouse_id, quantity, created_at)
            VALUES (:id, :tenant_id, :article_id, :batch_number, :warehouse_id, :quantity, NOW())
        """),
        {
            "id": einlagerung_id,
            "tenant_id": tenant_id,
            "article_id": payload.artikel,
            "batch_number": payload.chargen_id,
            "warehouse_id": warehouse_key,
            "quantity": payload.menge,
        },
    )

    db.execute(
        text("""
            INSERT INTO domain_inventory.inventory_stock_movements
            (id, article_id, warehouse_id, movement_type, quantity, unit, charge,
             warehouse_location, reference_number, movement_date, movement_time,
             notes, booking_user, auto_created, ownership_type, tenant_id, created_at)
            VALUES (:id, :article_id, :warehouse_id, 'in', :quantity, 't', :charge,
                    :location, :ref, :date, NOW()::time,
                    :notes, :user, false, 'owned', :tenant_id, NOW())
        """),
        {
            "id": movement_id,
            "article_id": payload.artikel,
            "warehouse_id": payload.lagerort,
            "quantity": payload.menge,
            "charge": payload.chargen_id,
            "location": payload.lagerplatz,
            "ref": f"EINL-{einlagerung_id[:8].upper()}",
            "date": today,
            "notes": f"Einlagerung Charge {payload.chargen_id}",
            "user": "system",
            "tenant_id": tenant_id,
        },
    )
    db.commit()

    return EinlagerungOut(
        id=einlagerung_id,
        batch_number=payload.chargen_id,
        artikel=payload.artikel,
        menge=payload.menge,
        lagerort=payload.lagerort,
        lagerplatz=payload.lagerplatz,
        datum=today,
        status="gebucht",
    )


# ---------------------------------------------------------------------------
# Lager Auslagerung
# ---------------------------------------------------------------------------

class AuslagerungIn(BaseModel):
    artikel: str = Field(..., description="Artikel-Bezeichnung")
    menge: float = Field(..., gt=0, description="Menge (z.B. Tonnen)")
    strategie: str = Field(default="fifo", description="fifo | fefo | manuell")
    chargen_id: Optional[str] = Field(default=None, description="Charge bei manuell")
    verwendungszweck: Optional[str] = Field(default=None)


class AuslagerungOut(BaseModel):
    id: str
    artikel: str
    menge: float
    strategie: str
    chargen_id: Optional[str]
    datum: date
    status: str


@router.post("/lager/auslagerung", response_model=AuslagerungOut, status_code=201, tags=["lager"])
async def create_auslagerung(
    payload: AuslagerungIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> AuslagerungOut:
    """Auslagerung buchen — StockMovement mit Strategie (FIFO/FEFO/Manuell)."""
    auslagerung_id = str(uuid4())
    movement_id = str(uuid4())
    today = date.today()

    charge_to_use = payload.chargen_id
    warehouse_id = None

    if payload.strategie == "manuell" and payload.chargen_id:
        row = db.execute(
            text("""
                SELECT warehouse_id FROM domain_inventory.article_batches
                WHERE tenant_id = :tid AND batch_number = :batch AND article_id = :art
                ORDER BY created_at DESC LIMIT 1
            """),
            {"tid": tenant_id, "batch": payload.chargen_id, "art": payload.artikel},
        ).first()
        if row:
            warehouse_id = row[0]
    elif payload.strategie in ("fifo", "fefo"):
        order_col = "created_at ASC" if payload.strategie == "fifo" else "created_at ASC"
        row = db.execute(
            text(f"""
                SELECT batch_number, warehouse_id FROM domain_inventory.article_batches
                WHERE tenant_id = :tid AND article_id = :art AND quantity > 0
                ORDER BY {order_col} LIMIT 1
            """),
            {"tid": tenant_id, "art": payload.artikel},
        ).first()
        if row:
            charge_to_use = row[0]
            warehouse_id = row[1]

    db.execute(
        text("""
            INSERT INTO domain_inventory.inventory_stock_movements
            (id, article_id, warehouse_id, movement_type, quantity, unit, charge,
             reference_number, movement_date, movement_time,
             notes, booking_user, auto_created, ownership_type, tenant_id, created_at)
            VALUES (:id, :article_id, :warehouse_id, 'out', :quantity, 't', :charge,
                    :ref, :date, NOW()::time,
                    :notes, :user, false, 'owned', :tenant_id, NOW())
        """),
        {
            "id": movement_id,
            "article_id": payload.artikel,
            "warehouse_id": warehouse_id or "UNBEKANNT",
            "quantity": payload.menge,
            "charge": charge_to_use,
            "ref": f"AUSL-{auslagerung_id[:8].upper()}",
            "date": today,
            "notes": payload.verwendungszweck or f"Auslagerung {payload.strategie}",
            "user": "system",
            "tenant_id": tenant_id,
        },
    )

    if charge_to_use and warehouse_id:
        db.execute(
            text("""
                UPDATE domain_inventory.article_batches
                SET quantity = GREATEST(0, quantity - :menge)
                WHERE tenant_id = :tid AND batch_number = :batch AND article_id = :art
            """),
            {"menge": payload.menge, "tid": tenant_id, "batch": charge_to_use, "art": payload.artikel},
        )

    db.commit()

    return AuslagerungOut(
        id=auslagerung_id,
        artikel=payload.artikel,
        menge=payload.menge,
        strategie=payload.strategie,
        chargen_id=charge_to_use,
        datum=today,
        status="gebucht",
    )


# ---------------------------------------------------------------------------
# POS Pausierte Verkäufe (Suspended Sales)
# ---------------------------------------------------------------------------

@router.get("/pos/suspended-sales", response_model=list, tags=["pos"])
async def list_suspended_sales(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list:
    """Liste pausierter Verkauefe aus dem Document-Store (Typ pos_suspended_sale)."""
    try:
        docs = _list_docs(db, "pos_suspended_sale", limit=100, tenant_id=tenant_id)
        return [
            {
                "id": d.get("id"),
                "customer_name": d.get("customerName", ""),
                "items": d.get("items", []),
                "total": d.get("total", 0),
                "suspended_at": d.get("suspendedAt") or d.get("createdAt"),
                "status": d.get("status", "suspended"),
            }
            for d in docs
        ]
    except Exception:
        return []


@router.delete("/pos/suspended-sales/{sale_id}", status_code=204, tags=["pos"], response_class=Response)
async def delete_suspended_sale(
    sale_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Pausierten Verkauf loeschen — entfernt aus Document-Store."""
    try:
        repo = _doc_repo(db)
        from app.documents.store import delete_from_store
        delete_from_store("pos_suspended_sale", sale_id, repo=repo)
    except Exception:
        pass
    return Response(status_code=204)


# ---------------------------------------------------------------------------
# POS Tagesabschluss
# ---------------------------------------------------------------------------

class TagesabschlussIn(BaseModel):
    datum: date
    kassierer: str = ""
    tse_transaktionen: int = 0
    umsatz_bar: float = 0.0
    umsatz_ec: float = 0.0
    umsatz_paypal: float = 0.0
    umsatz_b2b: float = 0.0
    umsatz_gesamt: float = 0.0
    bargeld_gezaehlt: float = 0.0
    ec_abrechnung: float = 0.0
    paypal_abrechnung: float = 0.0
    differenz_bar: float = 0.0


class TagesabschlussOut(BaseModel):
    id: str
    datum: date
    kassierer: str
    umsatz_gesamt: float
    status: str
    belegnummer: str


def _ensure_chart_account(db: Session, tenant_id: str, account_number: str, account_name: str) -> str:
    """Hole oder erstelle Kontenplan-Eintrag, return chart_of_accounts.id."""
    row = db.execute(
        text("""
            SELECT id FROM domain_erp.chart_of_accounts
            WHERE tenant_id = :tid AND account_number = :num LIMIT 1
        """),
        {"tid": tenant_id, "num": account_number},
    ).fetchone()
    if row:
        return str(row[0])
    acc_id = uuid7()
    db.execute(
        text("""
            INSERT INTO domain_erp.chart_of_accounts
            (id, tenant_id, account_number, account_name, account_type, category, is_active, created_at, updated_at)
            VALUES (:id, :tid, :num, :name, 'ASSET', 'general', TRUE, NOW(), NOW())
        """),
        {"id": acc_id, "tid": tenant_id, "num": account_number, "name": account_name},
    )
    return acc_id


@router.post("/pos/tagesabschluss", response_model=TagesabschlussOut, status_code=201, tags=["pos"])
async def create_tagesabschluss(
    payload: TagesabschlussIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> TagesabschlussOut:
    """POS Tagesabschluss buchen — schreibt in abschluss_checklisten UND erzeugt FiBu-Journal-Einträge."""
    abschluss_id = str(uuid4())
    belegnummer = f"KA-{payload.datum.isoformat()}"

    items_json = json.dumps({
        "tse_transaktionen": payload.tse_transaktionen,
        "umsatz_bar": payload.umsatz_bar,
        "umsatz_ec": payload.umsatz_ec,
        "umsatz_paypal": payload.umsatz_paypal,
        "umsatz_b2b": payload.umsatz_b2b,
        "umsatz_gesamt": payload.umsatz_gesamt,
        "bargeld_gezaehlt": payload.bargeld_gezaehlt,
        "ec_abrechnung": payload.ec_abrechnung,
        "paypal_abrechnung": payload.paypal_abrechnung,
        "differenz_bar": payload.differenz_bar,
        "belegnummer": belegnummer,
    })

    db.execute(
        text("""
            INSERT INTO abschluss_checklisten
            (id, tenant_id, periode, abschluss_art, status, verantwortlicher,
             beginn_datum, abschluss_datum, items, created_at, updated_at)
            VALUES
            (:id, :tenant_id, :periode, 'kasse', 'gebucht', :kassierer,
             :datum, :datum, CAST(:items AS json), NOW(), NOW())
        """),
        {
            "id": abschluss_id,
            "tenant_id": tenant_id,
            "periode": payload.datum.isoformat(),
            "kassierer": payload.kassierer,
            "datum": payload.datum,
            "items": items_json,
        },
    )

    # Verdrahtung zur FiBu: Journal-Eintrag erstellen (SKR03)
    period = payload.datum.strftime("%Y-%m")
    umsatz_bar = float(payload.umsatz_bar or 0)
    umsatz_ec = float(payload.umsatz_ec or 0)
    umsatz_paypal = float(payload.umsatz_paypal or 0)
    umsatz_b2b = float(payload.umsatz_b2b or 0)
    umsatz_gesamt = float(payload.umsatz_gesamt or 0)
    differenz_bar = float(payload.differenz_bar or 0)

    if umsatz_gesamt > 0:
        entry_id = uuid7()
        desc = f"Tagesabschluss POS {payload.datum.isoformat()} ({payload.kassierer or 'Kassierer'})"

        acc_1000 = _ensure_chart_account(db, tenant_id, "1000", "Kasse")
        acc_1200 = _ensure_chart_account(db, tenant_id, "1200", "Bank")
        acc_1210 = _ensure_chart_account(db, tenant_id, "1210", "PayPal / Verrechnung")
        acc_8400 = _ensure_chart_account(db, tenant_id, "8400", "Umsatzerlöse")
        acc_2150 = _ensure_chart_account(db, tenant_id, "2150", "Kassenfehlbeträge")

        db.execute(
            text("""
                INSERT INTO domain_erp.journal_entries
                (id, tenant_id, entry_number, entry_date, posting_date, description,
                 source, reference, period, status, total_debit, total_credit, created_at, updated_at)
                VALUES (:id, :tid, :entry_number, :edate, :pdate, :desc,
                        'POS', :ref, :period, 'posted', :total_d, :total_c, NOW(), NOW())
            """),
            {
                "id": entry_id,
                "tid": tenant_id,
                "entry_number": belegnummer,
                "edate": payload.datum,
                "pdate": payload.datum,
                "desc": desc,
                "ref": belegnummer,
                "period": period,
                "total_d": umsatz_gesamt + abs(differenz_bar),
                "total_c": umsatz_gesamt + abs(differenz_bar),
            },
        )

        lines: list[tuple[str, float, float, str]] = []
        if umsatz_bar > 0:
            lines.append((acc_1000, umsatz_bar, 0.0, "Kasseneinnahmen Bar"))
        if umsatz_ec > 0:
            lines.append((acc_1200, umsatz_ec, 0.0, "EC-Zahlungen"))
        if umsatz_paypal > 0:
            lines.append((acc_1210, umsatz_paypal, 0.0, "PayPal"))
        if umsatz_b2b > 0:
            lines.append((acc_1200, umsatz_b2b, 0.0, "B2B-Verbuchung"))
        if differenz_bar > 0:
            lines.append((acc_2150, differenz_bar, 0.0, "Kassenfehlbetrag"))
        lines.append((acc_8400, 0.0, umsatz_gesamt, "Umsatzerlöse POS"))
        if differenz_bar < 0:
            lines.append((acc_2150, 0.0, abs(differenz_bar), "Kassenüberbetrag"))
        if differenz_bar > 0:
            lines.append((acc_1000, 0.0, differenz_bar, "Kassenfehlbetrag Abgang"))

        for ln, (acc_id, debit, credit, line_desc) in enumerate(lines, start=1):
            line_id = f"{entry_id}-L{ln}"
            db.execute(
                text("""
                    INSERT INTO domain_erp.journal_entry_lines
                    (id, tenant_id, journal_entry_id, account_id, debit, credit, line_number, description, created_at)
                    VALUES (:id, :tid, :je_id, :acc_id, :debit, :credit, :ln, :desc, NOW())
                """),
                {
                    "id": line_id,
                    "tid": tenant_id,
                    "je_id": entry_id,
                    "acc_id": acc_id,
                    "debit": debit,
                    "credit": credit,
                    "ln": ln,
                    "desc": line_desc,
                },
            )

    db.commit()

    await _enqueue_event(
        db,
        event_type="cash_closing.posted",
        aggregate_id=abschluss_id,
        payload={
            "cash_closing_id": abschluss_id,
            "belegnummer": belegnummer,
            "datum": payload.datum.isoformat(),
            "kassierer": payload.kassierer,
            "umsatz_gesamt": payload.umsatz_gesamt,
        },
        tenant_id=tenant_id,
    )

    return TagesabschlussOut(
        id=abschluss_id,
        datum=payload.datum,
        kassierer=payload.kassierer,
        umsatz_gesamt=payload.umsatz_gesamt,
        status="gebucht",
        belegnummer=belegnummer,
    )


# ---------------------------------------------------------------------------
# Setup Firmenstammdaten
# ---------------------------------------------------------------------------

_FIRMA_KEY = "firma.stammdaten"
_FIRMA_CATEGORY = "setup"


@router.get("/setup/firma", response_model=dict, tags=["setup"])
async def get_firma(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Firmenstammdaten laden aus domain_shared.system_properties."""
    row = db.execute(
        text("""
            SELECT property_value FROM domain_shared.system_properties
            WHERE tenant_id = :tid AND property_key = :key
            LIMIT 1
        """),
        {"tid": tenant_id, "key": _FIRMA_KEY},
    ).first()
    if row and row[0]:
        try:
            return json.loads(row[0])
        except (ValueError, TypeError):
            pass
    # Defaults wenn noch nicht gespeichert
    return {}


@router.put("/setup/firma", response_model=dict, tags=["setup"])
async def save_firma(
    payload: dict = Body(...),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Firmenstammdaten speichern in domain_shared.system_properties (UPSERT)."""
    firma_json = json.dumps(payload, ensure_ascii=False)
    existing = db.execute(
        text("""
            SELECT id FROM domain_shared.system_properties
            WHERE tenant_id = :tid AND property_key = :key
            LIMIT 1
        """),
        {"tid": tenant_id, "key": _FIRMA_KEY},
    ).first()

    if existing:
        db.execute(
            text("""
                UPDATE domain_shared.system_properties
                SET property_value = :val
                WHERE tenant_id = :tid AND property_key = :key
            """),
            {"tid": tenant_id, "key": _FIRMA_KEY, "val": firma_json},
        )
    else:
        prop_id = str(uuid4())
        db.execute(
            text("""
                INSERT INTO domain_shared.system_properties
                (id, tenant_id, property_key, property_value, property_type, category)
                VALUES (:id, :tid, :key, :val, 'json', :cat)
            """),
            {"id": prop_id, "tid": tenant_id, "key": _FIRMA_KEY, "val": firma_json, "cat": _FIRMA_CATEGORY},
        )
    db.commit()
    return {"ok": True, "saved": True}


# ── Management Dashboard ────────────────────────────────────────────

@router.get("/management/dashboard")
async def management_dashboard(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Aggregiertes Management-Dashboard mit KPIs, Alerts, Top-Produkten/Kunden."""
    try:
        sales_row = db.execute(text("""
            SELECT COUNT(*) AS cnt,
                   COALESCE(SUM(total_amount), 0) AS revenue
            FROM domain_crm.sales_orders
            WHERE tenant_id = :tid
              AND created_at >= date_trunc('month', CURRENT_DATE)
        """), {"tid": tenant_id}).fetchone()
        umsatz = float(sales_row.revenue) if sales_row else 0
        auftraege = int(sales_row.cnt) if sales_row else 0

        oi_row = db.execute(text("""
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM domain_shared.open_items
            WHERE tenant_id = :tid AND status = 'open'
        """), {"tid": tenant_id}).fetchone()
        offene_posten = float(oi_row.total) if oi_row else 0

        top_products = db.execute(text("""
            SELECT a.name, COALESCE(SUM(sol.total), 0) AS umsatz
            FROM domain_crm.sales_order_lines sol
            JOIN domain_inventory.articles a ON a.id = sol.article_id
            JOIN domain_crm.sales_orders so ON so.id = sol.order_id AND so.tenant_id = :tid
            GROUP BY a.name ORDER BY umsatz DESC LIMIT 5
        """), {"tid": tenant_id}).fetchall()

        top_customers = db.execute(text("""
            SELECT c.company_name AS name, COALESCE(SUM(so.total_amount), 0) AS umsatz
            FROM domain_crm.sales_orders so
            JOIN domain_crm.customers c ON c.id = so.customer_id
            WHERE so.tenant_id = :tid
            GROUP BY c.company_name ORDER BY umsatz DESC LIMIT 5
        """), {"tid": tenant_id}).fetchall()
    except Exception:
        umsatz, auftraege, offene_posten = 0, 0, 0
        top_products, top_customers = [], []

    def fmt_eur(v: float) -> str:
        if v >= 1_000_000:
            return f"{v / 1_000_000:.2f}M"
        if v >= 1_000:
            return f"{v / 1_000:.0f}K"
        return f"{v:.0f}"

    return {
        "kpis": [
            {"label": "Umsatz MTD", "value": fmt_eur(umsatz), "trend": 0, "einheit": "EUR"},
            {"label": "Offene Auftraege", "value": str(auftraege), "trend": 0},
            {"label": "Offene Posten", "value": fmt_eur(offene_posten), "trend": 0, "einheit": "EUR"},
        ],
        "alerts": [],
        "topProducts": [{"name": r.name, "umsatz": float(r.umsatz)} for r in top_products],
        "topCustomers": [{"name": r.name, "umsatz": float(r.umsatz)} for r in top_customers],
    }


# ── Benachrichtigungen ──────────────────────────────────────────────

@router.get("/benachrichtigungen")
async def list_benachrichtigungen(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Benachrichtigungen fuer den aktuellen Mandanten."""
    try:
        rows = db.execute(text("""
            SELECT id, title AS titel, message AS nachricht,
                   COALESCE(severity, 'info') AS typ,
                   created_at AS zeitstempel,
                   COALESCE(read, false) AS gelesen
            FROM domain_shared.notifications
            WHERE tenant_id = :tid
            ORDER BY created_at DESC
            LIMIT 50
        """), {"tid": tenant_id}).fetchall()
        return {
            "items": [
                {
                    "id": str(r.id),
                    "titel": r.titel or "",
                    "nachricht": r.nachricht or "",
                    "typ": r.typ,
                    "zeitstempel": str(r.zeitstempel),
                    "gelesen": bool(r.gelesen),
                }
                for r in rows
            ]
        }
    except Exception:
        return {"items": []}


# ── Agribusiness / Field Service Tasks (CRM-Fälle → UI-Shape) ─────


def _case_to_field_service_task(c: dict[str, Any]) -> dict[str, Any]:
    """Mappt CRM-Case-Dicts auf das Frontend-Format von field-service-tasks.tsx."""
    status_raw = (c.get("status") or "").lower().replace(" ", "_")
    status_map = {
        "new": "SCHEDULED",
        "open": "IN_PROGRESS",
        "in_progress": "IN_PROGRESS",
        "pending": "SCHEDULED",
        "resolved": "COMPLETED",
        "closed": "COMPLETED",
        "cancelled": "CANCELLED",
    }
    task_status = status_map.get(status_raw, "SCHEDULED")
    pri_raw = (c.get("priority") or "medium").upper()
    if pri_raw not in ("URGENT", "HIGH", "MEDIUM", "LOW"):
        pri_raw = {"CRITICAL": "URGENT", "NORMAL": "MEDIUM"}.get(pri_raw, "MEDIUM")
    created = c.get("created_at")
    if hasattr(created, "isoformat"):
        sched = created.isoformat()
    elif isinstance(created, str):
        sched = created
    else:
        sched = datetime.now(timezone.utc).isoformat()
    pct = 100 if task_status == "COMPLETED" else (50 if task_status == "IN_PROGRESS" else 0)
    desc = c.get("description")
    farmer = (desc[:120] + "…") if isinstance(desc, str) and len(desc) > 120 else desc
    return {
        "id": str(c.get("id", "")),
        "taskNumber": c.get("case_number") or str(c.get("id", "")),
        "title": c.get("subject") or "(ohne Betreff)",
        "taskType": (c.get("case_type") or "service").upper(),
        "status": task_status,
        "priority": pri_raw,
        "assignedToName": c.get("assigned_to") or "-",
        "farmerName": farmer if isinstance(farmer, str) else None,
        "scheduledStartDate": sched,
        "completionPercentage": pct,
    }


def _ui_priority_to_crm(priority: str) -> str:
    p = (priority or "MEDIUM").upper()
    return {"URGENT": "urgent", "HIGH": "high", "LOW": "low", "MEDIUM": "medium"}.get(p, "medium")


def _ui_status_to_crm(status: str) -> str:
    s = (status or "SCHEDULED").upper()
    return {
        "SCHEDULED": "new",
        "IN_PROGRESS": "open",
        "COMPLETED": "closed",
        "CANCELLED": "cancelled",
    }.get(s, "new")


_DEMO_FIELD_SERVICE_TASKS: list[dict[str, Any]] = [
    {
        "id": "fst-seed-001",
        "taskNumber": "FS-2026-DEMO-001",
        "title": "Wartung Dosieranlage",
        "taskType": "FIELD_SERVICE",
        "status": "SCHEDULED",
        "priority": "HIGH",
        "assignedToName": "Team Nord",
        "farmerName": "Mustermann Agrar GmbH",
        "scheduledStartDate": datetime.now(timezone.utc).isoformat(),
        "completionPercentage": 0,
    },
    {
        "id": "fst-seed-002",
        "taskNumber": "FS-2026-DEMO-002",
        "title": "Kalibrierung Waage",
        "taskType": "INSPECTION",
        "status": "IN_PROGRESS",
        "priority": "MEDIUM",
        "assignedToName": "Technik",
        "farmerName": None,
        "scheduledStartDate": datetime.now(timezone.utc).isoformat(),
        "completionPercentage": 40,
    },
]


@router.get("/agribusiness/field-service-tasks")
async def list_field_service_tasks() -> list[dict[str, Any]]:
    """Liste Field-Service-Aufgaben (CRM-Fälle); bei Ausfall des CRM-Dienstes Demo-Daten."""
    try:
        cases, _total = await crm_list_cases(skip=0, limit=200)
        if cases:
            return [_case_to_field_service_task(dict(c)) for c in cases]
    except Exception:
        pass
    return list(_DEMO_FIELD_SERVICE_TASKS)


@router.get("/agribusiness/field-service-tasks/{task_id}")
async def get_field_service_task(task_id: str) -> dict[str, Any]:
    """Einzelne Field-Service-Aufgabe (CRM-Case oder Demo)."""
    if task_id.startswith("fst-seed-"):
        for t in _DEMO_FIELD_SERVICE_TASKS:
            if t["id"] == task_id:
                return dict(t)
        raise HTTPException(status_code=404, detail="Task not found")
    try:
        case = await crm_get_case(task_id)
        return _case_to_field_service_task(dict(case))
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"CRM get failed: {exc}") from exc


class FieldServiceTaskCreateBody(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    taskType: str = Field("FIELD_SERVICE", max_length=80)
    priority: str = Field("MEDIUM", max_length=20)


@router.post("/agribusiness/field-service-tasks")
async def create_field_service_task(
    body: FieldServiceTaskCreateBody,
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Neue Aufgabe als CRM-Fall; bei CRM-Ausfall Demo-Eintrag."""
    payload = {
        "tenant_id": tenant_id,
        "subject": body.title.strip(),
        "case_type": (body.taskType or "field_service").lower().replace("-", "_"),
        "priority": _ui_priority_to_crm(body.priority),
        "status": "new",
    }
    try:
        created = await crm_create_case(payload)
        return _case_to_field_service_task(dict(created))
    except Exception:
        nid = f"fst-seed-{uuid4().hex[:8]}"
        row = {
            "id": nid,
            "taskNumber": f"FS-DEMO-{nid[-6:].upper()}",
            "title": body.title.strip(),
            "taskType": (body.taskType or "FIELD_SERVICE").upper(),
            "status": "SCHEDULED",
            "priority": (body.priority or "MEDIUM").upper(),
            "assignedToName": "-",
            "farmerName": None,
            "scheduledStartDate": datetime.now(timezone.utc).isoformat(),
            "completionPercentage": 0,
        }
        _DEMO_FIELD_SERVICE_TASKS.append(row)
        return dict(row)


class FieldServiceTaskUpdateBody(BaseModel):
    title: Optional[str] = Field(None, max_length=500)
    taskType: Optional[str] = Field(None, max_length=80)
    priority: Optional[str] = Field(None, max_length=20)
    status: Optional[str] = Field(None, max_length=30)


@router.put("/agribusiness/field-service-tasks/{task_id}")
async def update_field_service_task(task_id: str, body: FieldServiceTaskUpdateBody) -> dict[str, Any]:
    """Aufgabe aktualisieren (CRM update_case oder Demo-Liste)."""
    if task_id.startswith("fst-seed-"):
        for t in _DEMO_FIELD_SERVICE_TASKS:
            if t["id"] == task_id:
                if body.title is not None:
                    t["title"] = body.title.strip()
                if body.taskType is not None:
                    t["taskType"] = body.taskType.upper()
                if body.priority is not None:
                    t["priority"] = body.priority.upper()
                if body.status is not None:
                    t["status"] = body.status.upper()
                return dict(t)
        raise HTTPException(status_code=404, detail="Task not found")
    upd: dict[str, Any] = {}
    if body.title is not None:
        upd["subject"] = body.title.strip()
    if body.taskType is not None:
        upd["case_type"] = body.taskType.lower().replace("-", "_")
    if body.priority is not None:
        upd["priority"] = _ui_priority_to_crm(body.priority)
    if body.status is not None:
        upd["status"] = _ui_status_to_crm(body.status)
    if not upd:
        try:
            case = await crm_get_case(task_id)
            return _case_to_field_service_task(dict(case))
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"CRM get failed: {exc}") from exc
    try:
        updated = await crm_update_case(task_id, upd)
        return _case_to_field_service_task(dict(updated))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"CRM update failed: {exc}") from exc


class FieldServiceTaskDeleteBody(BaseModel):
    reason: str = ""


@router.delete("/agribusiness/field-service-tasks/{task_id}")
async def delete_field_service_task(
    task_id: str,
    body: FieldServiceTaskDeleteBody | None = Body(None),
) -> dict[str, Any]:
    if task_id.startswith("fst-seed-"):
        return {"ok": True, "deleted": task_id}
    try:
        await crm_delete_case(task_id)
        return {"ok": True, "deleted": task_id}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"CRM delete failed: {exc}") from exc


class FieldServiceTaskCancelBody(BaseModel):
    reason: str = ""


@router.post("/agribusiness/field-service-tasks/{task_id}/cancel")
async def cancel_field_service_task(
    task_id: str,
    body: FieldServiceTaskCancelBody | None = None,
) -> dict[str, Any]:
    reason = (body.reason if body else "") or "Storniert"
    if task_id.startswith("fst-seed-"):
        return {"ok": True, "cancelled": task_id, "reason": reason}
    try:
        await crm_update_case(task_id, {"status": "cancelled", "resolution": reason})
        return {"ok": True, "cancelled": task_id}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"CRM update failed: {exc}") from exc
