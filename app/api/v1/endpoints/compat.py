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
from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError
from app.services.einkauf_compat_service import EinkaufCompatService
from app.services.pos_compat_service import PosCompatService
from app.services.inventory_compat_service import InventoryCompatService, FutterCompatService
from app.services.annahme_service import AnnahmeService
from app.services.portal_compat_service import PortalCompatService

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
        customers, customers_total = [], 0  # noqa: F841
    try:
        leads, leads_total = await crm_list_leads(status=None, search=None, skip=0, limit=500)
    except Exception:
        leads, leads_total = [], 0

    won = sum(1 for line_item in leads if getattr(line_item, "status", "") == "won")
    qualified = sum(1 for line_item in leads if getattr(line_item, "status", "") in {"qualified", "proposal", "negotiation", "won"})

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
        except Exception:
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


async def _create_compat_purchase_order(
    db: Session,
    *,
    tenant_id: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
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


@router.post("/purchase-orders", response_model=dict, status_code=201)
async def po_create(payload: dict[str, Any], tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> dict:
    return await _create_compat_purchase_order(db, tenant_id=tenant_id, payload=payload)


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
async def einkauf_goods_receipts(
    tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> list[dict[str, Any]]:
    return EinkaufCompatService(db, tenant_id).list_goods_receipts()


@router.post("/einkauf/goods-receipts", response_model=dict, status_code=201)
async def einkauf_goods_receipts_create(
    payload: dict[str, Any],
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    try:
        result = await EinkaufCompatService(db, tenant_id).create_goods_receipt(payload)
        db.commit()
        return result
    except ValidationFailedError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


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
async def einkauf_anfragen_list(
    tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> list[dict[str, Any]]:
    return EinkaufCompatService(db, tenant_id).list_anfragen()


def _load_einkauf_anfrage(db: Session, anfrage_id: str):
    """Module-level loader so tests can monkeypatch it."""
    from app.services.einkauf_compat_service import EinkaufCompatService as _Svc  # local to avoid circular
    try:
        return _Svc(db, "default").get_anfrage(anfrage_id)
    except EntityNotFoundError:
        return None


@router.get("/einkauf/anfragen/{anfrage_id}", response_model=dict)
async def einkauf_anfrage_get(
    anfrage_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> dict[str, Any]:
    result = _load_einkauf_anfrage(db, anfrage_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Anfrage not found")
    return result


@router.post("/einkauf/anfragen/{anfrage_id}/convert-to-order", response_model=dict)
async def einkauf_anfrage_convert_to_order(
    anfrage_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    try:
        return await EinkaufCompatService(db, tenant_id).convert_anfrage_to_order(anfrage_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/contracts/{contract_id}", response_model=dict)
async def compat_contract_get(
    contract_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return await get_contract_via_router(contract_id=contract_id, db=db, tenant_id=tenant_id)


@router.get("/einkauf/angebote", response_model=list)
async def einkauf_angebote_list(
    tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> list[dict[str, Any]]:
    return EinkaufCompatService(db, tenant_id).list_angebote()


@router.post("/einkauf/angebote/{angebot_id}/review", response_model=dict)
async def einkauf_angebot_review(
    angebot_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> dict[str, Any]:
    try:
        return EinkaufCompatService(db, tenant_id).update_angebot_status(angebot_id, "GEPRUEFT", "geprueft")
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/einkauf/angebote/{angebot_id}/approve", response_model=dict)
async def einkauf_angebot_approve(
    angebot_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> dict[str, Any]:
    try:
        return EinkaufCompatService(db, tenant_id).update_angebot_status(angebot_id, "GENEHMIGT", "genehmigt")
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/einkauf/angebote/{angebot_id}/reject", response_model=dict)
async def einkauf_angebot_reject(
    angebot_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> dict[str, Any]:
    try:
        return EinkaufCompatService(db, tenant_id).update_angebot_status(angebot_id, "ABGELEHNT", "abgelehnt")
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/einkauf/angebote/{angebot_id}/convert-to-order", response_model=dict)
async def einkauf_angebot_convert_to_order(
    angebot_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> dict[str, Any]:
    try:
        return await EinkaufCompatService(db, tenant_id).convert_angebot_to_order(angebot_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/einkauf/anlieferavis", response_model=list)
async def einkauf_anlieferavis_list(
    tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> list[dict[str, Any]]:
    return EinkaufCompatService(db, tenant_id).list_anlieferavis()


@router.post("/einkauf/anlieferavis/{avis_id}/{action}", response_model=dict)
async def einkauf_anlieferavis_transition(
    avis_id: str, action: str,
    tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> dict[str, Any]:
    try:
        return EinkaufCompatService(db, tenant_id).transition_anlieferavis(avis_id, action)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValidationFailedError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/einkauf/auftragsbestaetigungen", response_model=list)
async def einkauf_auftragsbestaetigungen_list(
    tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> list[dict[str, Any]]:
    return EinkaufCompatService(db, tenant_id).list_auftragsbestaetigungen()


@router.post("/einkauf/auftragsbestaetigungen/{bestaetigung_id}/{action}", response_model=dict)
async def einkauf_auftragsbestaetigung_transition(
    bestaetigung_id: str, action: str,
    tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> dict[str, Any]:
    try:
        return EinkaufCompatService(db, tenant_id).transition_auftragsbestaetigung(bestaetigung_id, action)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValidationFailedError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/einkauf/rechnungseingaenge", response_model=list)
async def einkauf_rechnungseingaenge_list(
    tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> list[dict[str, Any]]:
    return EinkaufCompatService(db, tenant_id).list_rechnungseingaenge()


@router.post("/einkauf/rechnungseingaenge/{rechnung_id}/pruefen")
async def einkauf_rechnungseingang_pruefen(
    rechnung_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> dict[str, Any]:
    try:
        return EinkaufCompatService(db, tenant_id).pruefen_rechnung(rechnung_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValidationFailedError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/einkauf/rechnungseingaenge/{rechnung_id}/freigeben")
async def einkauf_rechnungseingang_freigeben(
    rechnung_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> dict[str, Any]:
    try:
        return EinkaufCompatService(db, tenant_id).freigeben_rechnung(rechnung_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValidationFailedError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/einkauf/rechnungseingaenge/{rechnung_id}/verbuchen")
async def einkauf_rechnungseingang_verbuchen(
    rechnung_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> dict[str, Any]:
    try:
        return EinkaufCompatService(db, tenant_id).verbuchen_rechnung(rechnung_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValidationFailedError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


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
async def einkauf_bids(
    anfrage_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> list[dict[str, Any]]:
    return EinkaufCompatService(db, tenant_id).list_bids(anfrage_id)


@router.get("/einkauf/retouren", response_model=list)
async def einkauf_retouren(
    tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> list[dict[str, Any]]:
    return EinkaufCompatService(db, tenant_id).list_retouren()


@router.post("/einkauf/retouren", response_model=dict, status_code=201)
async def einkauf_retouren_create(
    payload: dict[str, Any], tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> dict:
    result = await EinkaufCompatService(db, tenant_id).create_retoure(payload)
    db.commit()
    return result


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
async def futter_einzel(
    tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> list[dict[str, Any]]:
    return FutterCompatService(db, tenant_id).list_einzelfuttermittel()


@router.get("/futter/mischfuttermittel", response_model=list)
async def futter_misch(
    tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> list[dict[str, Any]]:
    return FutterCompatService(db, tenant_id).list_mischfuttermittel()


@router.delete("/futter/einzelfuttermittel/{item_id}", status_code=204, response_class=Response)
async def delete_futter_einzel_item(
    item_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> Response:
    result = FutterCompatService(db, tenant_id).soft_delete_artikel([item_id], tenant_id)
    if result["deleted"] == 0:
        raise HTTPException(status_code=404, detail="Einzelfuttermittel nicht gefunden")
    return Response(status_code=204)


@router.post("/futter/einzelfuttermittel/bulk-delete", response_model=FutterBulkDeleteOut)
async def bulk_delete_futter_einzel(
    payload: FutterBulkDeleteIn, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> FutterBulkDeleteOut:
    result = FutterCompatService(db, tenant_id).soft_delete_artikel(payload.ids, tenant_id)
    return FutterBulkDeleteOut(**result)


@router.delete("/futter/mischfuttermittel/{item_id}", status_code=204, response_class=Response)
async def delete_futter_misch_item(
    item_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> Response:
    result = FutterCompatService(db, tenant_id).soft_delete_artikel([item_id], tenant_id)
    if result["deleted"] == 0:
        raise HTTPException(status_code=404, detail="Mischfuttermittel nicht gefunden")
    return Response(status_code=204)


@router.post("/futter/mischfuttermittel/bulk-delete", response_model=FutterBulkDeleteOut)
async def bulk_delete_futter_misch(
    payload: FutterBulkDeleteIn, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> FutterBulkDeleteOut:
    result = FutterCompatService(db, tenant_id).soft_delete_artikel(payload.ids, tenant_id)
    return FutterBulkDeleteOut(**result)


@router.get("/futter/chargen", response_model=list)
async def futter_chargen(
    tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> list[dict[str, Any]]:
    return FutterCompatService(db, tenant_id).list_chargen()


@router.get("/futter/qualitaetskontrolle", response_model=list)
async def futter_qc(
    tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> list[dict[str, Any]]:
    return FutterCompatService(db, tenant_id).list_qualitaetskontrolle()


@router.get("/futter/statistik", response_model=dict)
async def futter_stats(
    tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> dict:
    return FutterCompatService(db, tenant_id).get_statistik()


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
async def patch_kunde(
    kunden_id: str,
    body: dict = Body(default={}),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    """Partielle Aktualisierung eines Kunden (z.B. Status sperren). Nutzt ``is_active`` (kein Legacy-``status``-Feld)."""
    is_active = _csv_status_to_is_active(body.get("status"))
    q = text("""
        UPDATE domain_crm.customers
        SET is_active = :is_active, updated_at = NOW()
        WHERE id = :id AND tenant_id = :tid
        RETURNING id, is_active
    """)
    try:
        result = db.execute(q, {"id": kunden_id, "is_active": is_active, "tid": tenant_id})
        db.commit()
        row = result.fetchone()
        if row:
            ia = bool(row[1])
            return {"id": str(row[0]), "status": "aktiv" if ia else "gesperrt", "is_active": ia}
    except Exception:
        db.rollback()
    return {
        "id": kunden_id,
        "status": "aktiv" if is_active else "gesperrt",
        "is_active": is_active,
        "updated": True,
    }


# CSV-Import Endpoints -------------------------------------------------------

def _parse_csv_bytes(content: bytes) -> list[dict]:
    """Einfacher CSV-Parser: erkennt ';' oder ',' als Trennzeichen."""
    import csv
    import io
    text_content = content.decode("utf-8-sig", errors="replace")
    _dialect = "excel" if "," in text_content.split("\n")[0] else "excel-tab"  # noqa: F841
    sep = ";" if ";" in text_content.split("\n")[0] else ","
    reader = csv.DictReader(io.StringIO(text_content), delimiter=sep)
    return [dict(row) for row in reader]


def _csv_error_prefix(row_number: int) -> str:
    return f"Zeile {row_number}:"


def _csv_status_to_is_active(status_raw: str | None) -> bool:
    s = (status_raw or "aktiv").strip().lower()
    if s in ("gesperrt", "inaktiv", "blocked", "0", "false", "nein", "sperre"):
        return False
    return True


def _allocate_import_customer_number(db: Session) -> str:
    """Eindeutige Kundennummer für CSV-Neuanlage (global unique customer_number)."""
    import uuid as _uuid

    for _ in range(64):
        cn = f"IMP-{_uuid.uuid4().hex[:10].upper()}"
        row = db.execute(
            text("SELECT 1 FROM domain_crm.customers WHERE customer_number = :cn LIMIT 1"),
            {"cn": cn},
        ).fetchone()
        if not row:
            return cn
    return f"IMP-{_uuid.uuid4().hex}"


def _domain_crm_upsert_customer_norm(
    db: Session,
    tenant_id: str,
    *,
    firma: str,
    kundennummer: str,
    plz: str,
    ort: str,
    land: str,
    email: str,
    telefon: str,
    is_active: bool,
    ust_id: str,
) -> tuple[bool, bool, str | None]:
    """Ein Kunden-Datensatz aus CSV — Dubletten über Nr., E-Mail, USt-Id, Firma+PLZ+Ort. Returns (created, updated, error)."""
    import uuid as uuid_module

    created = updated = False
    try:
        existing_id: str | None = None
        if kundennummer:
            row_ex = db.execute(
                text(
                    "SELECT id FROM domain_crm.customers WHERE tenant_id = :tid AND customer_number = :cn LIMIT 1"
                ),
                {"tid": tenant_id, "cn": kundennummer},
            ).fetchone()
            if row_ex:
                existing_id = str(row_ex[0])
        if not existing_id and email:
            row_ex = db.execute(
                text(
                    """
                    SELECT id FROM domain_crm.customers
                    WHERE tenant_id = :tid
                      AND lower(trim(coalesce(email, ''))) = lower(:em)
                    LIMIT 1
                    """
                ),
                {"tid": tenant_id, "em": email},
            ).fetchone()
            if row_ex:
                existing_id = str(row_ex[0])
        if not existing_id and ust_id:
            row_ex = db.execute(
                text(
                    "SELECT id FROM domain_crm.customers WHERE tenant_id = :tid AND tax_id = :tx LIMIT 1"
                ),
                {"tid": tenant_id, "tx": ust_id},
            ).fetchone()
            if row_ex:
                existing_id = str(row_ex[0])
        if not existing_id:
            row_ex = db.execute(
                text(
                    """
                    SELECT id FROM domain_crm.customers
                    WHERE tenant_id = :tid
                      AND lower(trim(company_name)) = lower(trim(:name))
                      AND coalesce(postal_code, '') = :plz
                      AND coalesce(city, '') = :ort
                    LIMIT 1
                    """
                ),
                {"tid": tenant_id, "name": firma, "plz": plz, "ort": ort},
            ).fetchone()
            if row_ex:
                existing_id = str(row_ex[0])
        if existing_id:
            db.execute(
                text(
                    """
                    UPDATE domain_crm.customers
                    SET company_name = :cname,
                        email = CASE WHEN :email <> '' THEN :email ELSE email END,
                        phone = CASE WHEN :phone <> '' THEN :phone ELSE phone END,
                        postal_code = CASE WHEN :plz <> '' THEN :plz ELSE postal_code END,
                        city = CASE WHEN :ort <> '' THEN :ort ELSE city END,
                        country = CASE WHEN :land <> '' THEN :land ELSE country END,
                        tax_id = CASE WHEN :tx <> '' THEN :tx ELSE tax_id END,
                        is_active = :is_active,
                        updated_at = NOW()
                    WHERE id = :id AND tenant_id = :tid
                    """
                ),
                {
                    "cname": firma[:255],
                    "email": email,
                    "phone": telefon,
                    "plz": plz,
                    "ort": ort,
                    "land": land,
                    "tx": ust_id,
                    "is_active": is_active,
                    "id": existing_id,
                    "tid": tenant_id,
                },
            )
            updated = True
        else:
            cn = kundennummer if kundennummer else _allocate_import_customer_number(db)
            new_id = str(uuid_module.uuid4())
            db.execute(
                text(
                    """
                    INSERT INTO domain_crm.customers (
                        id, tenant_id, customer_number, company_name, email, phone,
                        postal_code, city, country, tax_id, is_active, created_at, updated_at
                    ) VALUES (
                        :id, :tid, :cn, :cname, :email, :phone,
                        :plz, :ort, :land, :tx, :is_active, NOW(), NOW()
                    )
                    """
                ),
                {
                    "id": new_id,
                    "tid": tenant_id,
                    "cn": cn,
                    "cname": firma[:255],
                    "email": email or None,
                    "phone": telefon or None,
                    "plz": plz or None,
                    "ort": ort or None,
                    "land": land,
                    "tx": ust_id or None,
                    "is_active": is_active,
                },
            )
            created = True
    except Exception as e:
        return False, False, str(e)[:120]
    return created, updated, None


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
async def import_kunden_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    """CSV-Import für Kunden (domain_crm.customers). Spalten u.a.: Firma, Ort, PLZ, Land, E-Mail, Telefon, Status, Kundennummer, USt-Id."""

    content = await file.read()
    rows = _parse_csv_bytes(content)
    created = updated = 0
    errors: list[str] = []
    col_map = {
        "firma": "firma",
        "company": "firma",
        "name": "firma",
        "email": "email",
        "e-mail": "email",
        "ort": "ort",
        "city": "ort",
        "plz": "plz",
        "zip": "plz",
        "land": "land",
        "country": "land",
        "telefon": "telefon",
        "phone": "telefon",
        "status": "status",
        "kundennummer": "kundennummer",
        "customer_number": "kundennummer",
        "debitorennummer": "kundennummer",
        "debitor": "kundennummer",
        "ust-id": "ust_id",
        "ust_id": "ust_id",
        "umsatzsteuer_id": "ust_id",
        "umsatzsteuer": "ust_id",
        "tax_id": "ust_id",
    }
    for i, row in enumerate(rows):
        norm = {col_map.get(k.lower().strip(), k.lower().strip()): (v or "").strip() for k, v in row.items()}
        firma = norm.get("firma", "").strip()
        if not firma:
            errors.append(f"{_csv_error_prefix(i+2)} Firma fehlt")
            continue
        dq_payload = {k: v for k, v in norm.items() if v}
        dq_payload["firma"] = firma
        dq_payload.setdefault("land", norm.get("land") or "DE")
        dq_error = _validate_csv_customer_row(dq_payload)
        if dq_error:
            errors.append(f"{_csv_error_prefix(i+2)} {dq_error}")
            continue
        kundennummer = (norm.get("kundennummer") or "").strip()[:50]
        plz = norm.get("plz", "").strip()[:10]
        ort = norm.get("ort", "").strip()[:50]
        land = (norm.get("land", "") or "DE").strip()[:50] or "DE"
        email = norm.get("email", "").strip()[:255]
        telefon = norm.get("telefon", "").strip()[:50]
        ust_id = (norm.get("ust_id") or "").strip()[:50]
        is_active = _csv_status_to_is_active(norm.get("status"))
        cr, up, err = _domain_crm_upsert_customer_norm(
            db,
            tenant_id,
            firma=firma,
            kundennummer=kundennummer,
            plz=plz,
            ort=ort,
            land=land,
            email=email,
            telefon=telefon,
            is_active=is_active,
            ust_id=ust_id,
        )
        if err:
            errors.append(f"Zeile {i+2}: {err}")
        else:
            if cr:
                created += 1
            if up:
                updated += 1
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        return {"created": 0, "updated": 0, "errors": [str(e)]}
    return {"created": created, "updated": updated, "errors": errors}


@router.post("/finance/import/debitoren", response_model=dict)
async def import_debitoren_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    """CSV-Import für Debitoren-Stammdaten → ``domain_crm.customers``. Spalten u.a.: Kunde, Debitorennummer, Land, PLZ, Ort, E-Mail."""
    content = await file.read()
    rows = _parse_csv_bytes(content)
    created = updated = 0
    errors: list[str] = []
    col_map = {
        "kunde": "firma",
        "name": "firma",
        "company": "firma",
        "firma": "firma",
        "debitorennummer": "kundennummer",
        "kundennummer": "kundennummer",
        "ort": "ort",
        "city": "ort",
        "plz": "plz",
        "zip": "plz",
        "land": "land",
        "country": "land",
        "email": "email",
        "e-mail": "email",
        "telefon": "telefon",
        "phone": "telefon",
        "status": "status",
        "ust-id": "ust_id",
        "ust_id": "ust_id",
        "tax_id": "ust_id",
    }
    for i, row in enumerate(rows):
        norm = {col_map.get(k.lower().strip(), k.lower().strip()): (v or "").strip() for k, v in row.items()}
        firma = norm.get("firma", "").strip()
        if not firma:
            errors.append(f"{_csv_error_prefix(i+2)} Kunde/Firma fehlt")
            continue
        dq_payload = {k: v for k, v in norm.items() if v}
        dq_payload["firma"] = firma
        dq_payload.setdefault("land", norm.get("land") or "DE")
        dq_error = _validate_csv_customer_row(dq_payload)
        if dq_error:
            errors.append(f"{_csv_error_prefix(i+2)} {dq_error}")
            continue
        kundennummer = (norm.get("kundennummer") or "").strip()[:50]
        plz = norm.get("plz", "").strip()[:10]
        ort = norm.get("ort", "").strip()[:50]
        land = (norm.get("land", "") or "DE").strip()[:50] or "DE"
        email = norm.get("email", "").strip()[:255]
        telefon = norm.get("telefon", "").strip()[:50]
        ust_id = (norm.get("ust_id") or "").strip()[:50]
        is_active = _csv_status_to_is_active(norm.get("status"))
        cr, up, err = _domain_crm_upsert_customer_norm(
            db,
            tenant_id,
            firma=firma,
            kundennummer=kundennummer,
            plz=plz,
            ort=ort,
            land=land,
            email=email,
            telefon=telefon,
            is_active=is_active,
            ust_id=ust_id,
        )
        if err:
            errors.append(f"Zeile {i+2}: {err}")
        else:
            if cr:
                created += 1
            if up:
                updated += 1
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        return {"created": 0, "updated": 0, "errors": [str(e)]}
    return {"created": created, "updated": updated, "errors": errors}


@router.post("/futter/import/einzelfuttermittel", response_model=dict)
async def import_einzelfuttermittel_csv(
    file: UploadFile = File(...), tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> dict:
    content = await file.read()
    rows = _parse_csv_bytes(content)
    # DQ validation before delegating
    validated, errors = [], []
    for i, row in enumerate(rows):
        norm = {k.lower().strip(): v.strip() for k, v in row.items() if v}
        dq_error = _validate_csv_article_row(norm)
        if dq_error:
            errors.append(f"{_csv_error_prefix(i+2)} {dq_error}")
        else:
            validated.append(norm)
    result = FutterCompatService(db, tenant_id).import_einzelfuttermittel_sql(validated)
    result["errors"] = errors + result.get("errors", [])
    return result


@router.post("/futter/import/mischfuttermittel", response_model=dict)
async def import_mischfuttermittel_csv(
    file: UploadFile = File(...), tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> dict:
    content = await file.read()
    rows = _parse_csv_bytes(content)
    validated, errors = [], []
    for i, row in enumerate(rows):
        norm = {k.lower().strip(): v.strip() for k, v in row.items() if v}
        dq_error = _validate_csv_article_row(norm)
        if dq_error:
            errors.append(f"{_csv_error_prefix(i+2)} {dq_error}")
        else:
            validated.append(norm)
    result = FutterCompatService(db, tenant_id).import_mischfuttermittel_sql(validated)
    result["errors"] = errors + result.get("errors", [])
    return result


@router.post("/futter/import/chargen", response_model=dict)
async def import_chargen_csv(
    file: UploadFile = File(...), tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> dict:
    content = await file.read()
    rows = _parse_csv_bytes(content)
    return FutterCompatService(db, tenant_id).import_chargen_sql(rows)


# Inventory extra endpoints -------------------------------------------------


@router.get("/inventory/inventur", response_model=dict)
async def inventory_inventur(
    tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> dict:
    return InventoryCompatService(db, tenant_id).list_inventur_counts()


@router.post("/inventory/inventur/complete", response_model=dict)
async def inventory_inventur_complete(
    payload: dict[str, list[str]], tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> dict:
    return InventoryCompatService(db, tenant_id).complete_inventur_counts(payload.get("ids", []))


@router.delete("/inventory/inventur/{item_id}", status_code=204)
async def inventory_inventur_stornieren(
    item_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
):
    try:
        InventoryCompatService(db, tenant_id).delete_inventur_count(item_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return None


@router.get("/inventory/mhd-warnings", response_model=dict)
async def inventory_mhd(
    tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> dict:
    return InventoryCompatService(db, tenant_id).get_mhd_warnings()


@router.get("/inventory/top-sellers", response_model=dict)
async def inventory_top_sellers(
    tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> dict:
    return InventoryCompatService(db, tenant_id).get_top_sellers()


@router.get("/inventory/slow-movers", response_model=dict)
async def inventory_slow_movers(
    tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> dict:
    return InventoryCompatService(db, tenant_id).get_slow_movers()


@router.get("/inventory/lots", response_model=dict)
async def inventory_lots(
    search: Optional[str] = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    return InventoryCompatService(db, tenant_id).list_lots(search=search)


@router.get("/inventory/lots/{lot_id}", response_model=dict)
async def inventory_lot_trace(
    lot_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> dict:
    try:
        return InventoryCompatService(db, tenant_id).get_lot(lot_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


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
    tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> dict:
    return AnnahmeService(db, tenant_id).list_lkw_db()


@router.get("/annahme/warteschlange/{reg_id}", response_model=dict)
async def annahme_warteschlange_get(
    reg_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> dict:
    try:
        return AnnahmeService(db, tenant_id).get_lkw_db(reg_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


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
    try:
        return AnnahmeService(db, tenant_id).patch_lkw_db(reg_id, body.status, body.klaerung)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValidationFailedError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/annahme/warteschlange/{reg_id}/repair-article", response_model=dict)
async def annahme_warteschlange_repair_article(
    reg_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> dict:
    try:
        return AnnahmeService(db, tenant_id).repair_article_db(reg_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


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
    base_dir = os.path.realpath(os.path.join(getattr(settings, "UPLOAD_DIR", "uploads"), "annahme"))
    os.makedirs(base_dir, exist_ok=True)
    ext = os.path.splitext(os.path.basename(file.filename or ""))[1] or ".bin"
    # Only allow safe extension characters (alphanumeric + dot)
    if not all(c.isalnum() or c == '.' for c in ext):
        ext = ".bin"
    safe_name = f"{upload_id}{ext}"
    path = os.path.realpath(os.path.join(base_dir, safe_name))
    if not path.startswith(base_dir + os.sep) and path != base_dir:
        raise HTTPException(status_code=400, detail="Ungueltiger Dateipfad")
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
    result = AnnahmeService(db, tenant_id).register_lkw_db(payload)
    return LKWRegistrierungOut(**result)


@router.post("/annahme/warteschlange", response_model=LKWRegistrierungOut, status_code=201, tags=["annahme"])
async def create_lkw_warteschlange_alias(
    payload: LKWRegistrierungIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> LKWRegistrierungOut:
    result = AnnahmeService(db, tenant_id).register_lkw_db(payload)
    return LKWRegistrierungOut(**result)


# Portal compatibility ------------------------------------------------------


@router.get("/portal/dashboard", response_model=dict)
async def portal_dashboard(
    tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> dict:
    return PortalCompatService(db, tenant_id).get_portal_dashboard_full()


@router.get("/portal/anfragen", response_model=list)
async def portal_anfragen(
    tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> list[dict[str, Any]]:
    return PortalCompatService(db, tenant_id).list_portal_anfragen()


@router.get("/portal/bestellungen", response_model=list)
async def portal_bestellungen(
    tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> list[dict[str, Any]]:
    return PortalCompatService(db, tenant_id).list_portal_bestellungen()


@router.get("/portal/dokumente", response_model=list)
async def portal_dokumente(
    tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> list[dict[str, Any]]:
    return PortalCompatService(db, tenant_id).list_portal_dokumente()


@router.get("/portal/feldbuch", response_model=list)
async def portal_feldbuch(
    customer_id: Optional[str] = Query(None),
    tenant_id: Optional[str] = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    return PortalCompatService(db, tenant_id or "").list_portal_feldbuch(customer_id=customer_id)


@router.get("/portal/naehrstoffbilanzen", response_model=list)
async def portal_naehrstoffbilanzen(
    tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> list[dict[str, Any]]:
    return PortalCompatService(db, tenant_id).list_portal_naehrstoffbilanzen()


@router.get("/portal/rechnungen", response_model=list)
async def portal_rechnungen(
    tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> list[dict[str, Any]]:
    return PortalCompatService(db, tenant_id).list_portal_rechnungen()


@router.get("/portal/shop", response_model=list)
async def portal_shop(
    tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> list[dict[str, Any]]:
    return PortalCompatService(db, tenant_id).list_portal_shop()


@router.get("/portal/products", response_model=dict)
async def portal_products(
    kategorie: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
    tenant_id: Optional[str] = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return PortalCompatService(db, tenant_id or "").list_portal_products(
        kategorie=kategorie, search=search, skip=skip, limit=limit
    )


@router.get("/portal/orders", response_model=dict)
async def portal_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status_filter: Optional[str] = Query(None),
    tenant_id: Optional[str] = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return PortalCompatService(db, tenant_id or "").list_sales_orders(
        skip=skip, limit=limit, status_filter=status_filter
    )


@router.get("/portal/orders/{order_id}", response_model=dict)
async def portal_order_detail(
    order_id: str, tenant_id: Optional[str] = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> dict[str, Any]:
    try:
        return PortalCompatService(db, tenant_id or "").get_sales_order(order_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/portal/orders", response_model=dict)
async def portal_create_order(
    body: dict = Body(...),
    tenant_id: Optional[str] = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    result = PortalCompatService(db, tenant_id or "").create_sales_order(body)
    db.commit()
    return result


@router.get("/portal/contracts", response_model=list)
async def portal_contracts(
    tenant_id: Optional[str] = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> list[dict[str, Any]]:
    return PortalCompatService(db, tenant_id or "").list_portal_contracts()


@router.get("/portal/pre-purchases", response_model=list)
async def portal_pre_purchases(
    tenant_id: Optional[str] = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> list[dict[str, Any]]:
    return PortalCompatService(db, tenant_id or "").list_portal_pre_purchases()


@router.get("/portal/vertraege", response_model=list)
async def portal_vertraege(
    tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> list[dict[str, Any]]:
    return PortalCompatService(db, tenant_id).list_portal_vertraege()


@router.get("/portal/zertifikate", response_model=list)
async def portal_zertifikate(
    tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> list[dict[str, Any]]:
    return PortalCompatService(db, tenant_id).list_portal_zertifikate()


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
    return EinkaufCompatService(db, tenant_id).upsert_supplier_rating(supplier_id, payload)


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
async def einkauf_retoure_get(
    retour_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> dict:
    try:
        return EinkaufCompatService(db, tenant_id).get_retoure(retour_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.patch("/einkauf/retouren/{retour_id}", response_model=dict)
async def einkauf_retoure_patch(
    retour_id: str, payload: dict[str, Any],
    tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)
) -> dict:
    result = EinkaufCompatService(db, tenant_id).patch_retoure(retour_id, payload)
    db.commit()
    return result


@router.get("/einkauf/service-entry-sheets", response_model=dict)
async def list_service_entry_sheets(
    status: Optional[str] = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    return EinkaufCompatService(db, tenant_id).list_service_entry_sheets(status=status)


@router.post("/einkauf/service-entry-sheets", response_model=dict, status_code=201)
async def create_service_entry_sheet(
    payload: dict[str, Any],
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    svc = EinkaufCompatService(db, tenant_id)
    result = await svc.create_service_entry_sheet(payload)
    db.commit()
    return result


@router.patch("/einkauf/service-entry-sheets/{ses_id}", response_model=dict)
async def update_service_entry_sheet(
    ses_id: str,
    payload: dict[str, Any],
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    try:
        return EinkaufCompatService(db, tenant_id).update_service_entry_sheet(ses_id, payload)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/einkauf/credit-memos", response_model=list)
async def list_credit_memos(tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    return EinkaufCompatService(db, tenant_id).list_credit_memos()


@router.get("/einkauf/debit-memos", response_model=list)
async def list_debit_memos(tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    return EinkaufCompatService(db, tenant_id).list_debit_memos()


@router.post("/einkauf/credit-memos", response_model=dict, status_code=201)
async def create_credit_memo(
    payload: dict[str, Any],
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    result = await EinkaufCompatService(db, tenant_id).create_credit_memo(payload)
    db.commit()
    return result


@router.post("/einkauf/debit-memos", response_model=dict, status_code=201)
async def create_debit_memo(
    payload: dict[str, Any],
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    result = await EinkaufCompatService(db, tenant_id).create_debit_memo(payload)
    db.commit()
    return result


@router.post("/einkauf/credit-memos/{memo_id}/settle", response_model=dict)
async def settle_credit_memo(
    memo_id: str,
    payload: dict[str, Any],
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    try:
        result = await EinkaufCompatService(db, tenant_id).settle_credit_memo(memo_id, payload)
        db.commit()
        return result
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/einkauf/debit-memos/{memo_id}/settle", response_model=dict)
async def settle_debit_memo(
    memo_id: str,
    payload: dict[str, Any],
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    try:
        result = await EinkaufCompatService(db, tenant_id).settle_debit_memo(memo_id, payload)
        db.commit()
        return result
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


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
    return EinkaufCompatService(db, tenant_id).list_edi_messages()


@router.post("/einkauf/edi/messages", response_model=dict, status_code=201)
async def create_edi_message(
    payload: dict[str, Any],
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    result = await EinkaufCompatService(db, tenant_id).create_edi_message(payload)
    db.commit()
    return result


@router.post("/einkauf/edi/messages/{msg_id}/ack", response_model=dict)
async def ack_edi_message(msg_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> dict:
    try:
        result = await EinkaufCompatService(db, tenant_id).ack_edi_message(msg_id)
        db.commit()
        return result
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


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
        docs = PosCompatService(db, tenant_id).list_suspended_sales()
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
        PosCompatService(db, tenant_id).delete_suspended_sale(sale_id)
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
