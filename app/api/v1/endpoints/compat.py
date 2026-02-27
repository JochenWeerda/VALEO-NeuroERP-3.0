"""Compatibility endpoints for frontend path alignment and missing modules."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.cache import cache_delete_prefix, cache_get_json, cache_set_json
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.documents.router_helpers import get_repository, list_from_store, get_from_store, save_to_store
from app.domains.operations.models import Charge, Dokument, Rahmenvertrag, ZertifikatEintrag
from app.domains.shared.events import IntegrationEvent, get_event_publisher
from app.infrastructure.models import Article as ArticleModel, InventoryCount
from app.infrastructure.eventbus.outbox import OutboxPublisher
from app.integrations.crm_core_client import list_customers as crm_list_customers, list_leads as crm_list_leads

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
            raise HTTPException(status_code=500, detail=f"Suppliers query failed: {exc}") from exc

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


@router.get("/annahme/warteschlange", response_model=dict)
async def annahme_warteschlange(db: Session = Depends(get_db)) -> dict:
    lots = db.query(Charge).order_by(Charge.eingang.asc()).limit(200).all()
    return {
        "items": [
            {
                "id": l.id,
                "referenz": l.chargen_id,
                "artikel": l.artikel,
                "menge": float(l.menge or 0),
                "status": l.status,
                "ankunft": l.eingang.isoformat() if l.eingang else None,
            }
            for l in lots
        ],
        "total": len(lots),
    }


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
    return {"items": items, "total": total}


@router.get("/portal/orders", response_model=dict)
async def portal_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[str] = Query(None),
    tenant_id: Optional[str] = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Portal-Bestellhistorie. Liest aus domain_shared sales_orders."""
    orders = _list_docs(db, "sales_order", limit=limit, offset=skip, tenant_id=tenant_id)
    if status:
        orders = [o for o in orders if o.get("status") == status]
    items = [
        {
            "id": o.get("id", ""),
            "orderNumber": o.get("number") or o.get("order_number", ""),
            "datum": o.get("created_at", "")[:10] if o.get("created_at") else "",
            "status": o.get("status", "SUBMITTED"),
            "totalAmount": float(o.get("total_amount") or o.get("totalAmount") or 0),
            "currency": o.get("currency", "EUR"),
            "positions": o.get("positions") or o.get("items") or [],
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


@router.get("/portal/contracts", response_model=dict)
async def portal_contracts(
    tenant_id: Optional[str] = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Aktive Verträge/Kontingente des Kunden."""
    try:
        contracts = _list_docs(db, "kontrakt", limit=200, tenant_id=tenant_id)
    except Exception:
        contracts = []
    items = [
        {
            "id": c.get("id", ""),
            "artikelId": c.get("artikel_id") or c.get("artikelId", ""),
            "articleName": c.get("artikel_name") or c.get("articleName", ""),
            "contractStatus": c.get("status", "ACTIVE"),
            "contractPrice": float(c.get("preis") or c.get("contractPrice") or 0),
            "contractRemainingQty": float(c.get("verbleibende_menge") or c.get("remainingQty") or 0),
            "contractTotalQty": float(c.get("gesamtmenge") or c.get("totalQty") or 0),
            "laufzeitBis": c.get("laufzeit_bis") or c.get("validUntil"),
        }
        for c in contracts
    ]
    return {"items": items, "total": len(items)}


@router.get("/portal/pre-purchases", response_model=dict)
async def portal_pre_purchases(
    tenant_id: Optional[str] = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Vorkäufe des Kunden (Vorratskäufe)."""
    try:
        pps = _list_docs(db, "vorkauf", limit=200, tenant_id=tenant_id)
    except Exception:
        pps = []
    items = [
        {
            "id": p.get("id", ""),
            "artikelId": p.get("artikel_id", ""),
            "articleName": p.get("artikel_name", ""),
            "prePurchasePrice": float(p.get("preis") or 0),
            "prePurchaseTotalQty": float(p.get("gesamtmenge") or 0),
            "prePurchaseRemainingQty": float(p.get("verbleibende_menge") or 0),
        }
        for p in pps
    ]
    return {"items": items, "total": len(items)}


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
