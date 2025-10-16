"""
Documents Router
API-Endpoints für Belegverwaltung & Folgebeleg-Erstellung
"""

from __future__ import annotations
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Callable, Any
import logging

from .models import SalesOrder, SalesDelivery, SalesInvoice, FollowRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/mcp/documents", tags=["documents"])

# In-Memory Store (TODO: durch echte DB ersetzen)
_DB: Dict[str, dict] = {}


# --- CRUD Endpoints ---


@router.post("/sales_order")
async def upsert_sales_order(doc: SalesOrder) -> dict:
    """Erstellt oder aktualisiert Verkaufsauftrag"""
    try:
        _DB[doc.number] = doc.model_dump()
        logger.info(f"Saved sales order: {doc.number}")
        return {"ok": True, "number": doc.number}
    except Exception as e:
        logger.error(f"Failed to save sales order: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sales_delivery")
async def upsert_sales_delivery(doc: SalesDelivery) -> dict:
    """Erstellt oder aktualisiert Lieferschein"""
    try:
        _DB[doc.number] = doc.model_dump()
        logger.info(f"Saved sales delivery: {doc.number}")
        return {"ok": True, "number": doc.number}
    except Exception as e:
        logger.error(f"Failed to save sales delivery: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sales_invoice")
async def upsert_sales_invoice(doc: SalesInvoice) -> dict:
    """Erstellt oder aktualisiert Rechnung"""
    try:
        # Berechne Gesamtbeträge falls nicht gesetzt
        if doc.subtotalNet == 0 and doc.lines:
            doc.subtotalNet = sum(
                (line.qty * line.price) for line in doc.lines if line.price
            )
            doc.totalTax = sum(
                (line.qty * line.price * line.vatRate / 100) for line in doc.lines if line.price
            )
            doc.totalGross = doc.subtotalNet + doc.totalTax

        # Status-Transition-Logik
        existing = _DB.get(doc.number)
        if existing:
            old_status = existing.get("status", "ENTWURF")
            new_status = doc.status

            # Erlaubte Übergänge
            allowed_transitions = {
                "ENTWURF": ["VERSENDET"],
                "VERSENDET": ["BEZAHLT", "ÜBERFÄLLIG"],
                "BEZAHLT": [],  # Final status
                "ÜBERFÄLLIG": ["BEZAHLT"],  # Kann noch bezahlt werden
            }

            if new_status not in allowed_transitions.get(old_status, []):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status transition: {old_status} → {new_status}"
                )

        _DB[doc.number] = doc.model_dump()
        logger.info(f"Saved sales invoice: {doc.number} (status: {doc.status})")
        return {"ok": True, "number": doc.number}
    except Exception as e:
        logger.error(f"Failed to save sales invoice: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{doc_number}")
async def get_document(doc_number: str) -> dict:
    """Holt einzelnen Beleg"""
    doc = _DB.get(doc_number)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"ok": True, "data": doc}


# --- Belegfluss-Engine ---

# Flow-Matrix: (from_type, to_type) → Transformation-Function
FLOW: Dict[tuple[str, str], Callable[[dict], dict]] = {
    # Order → Delivery
    ("sales_order", "delivery"): lambda payload: {
        "number": payload["number"].replace("SO", "DL"),
        "date": payload["date"],
        "customerId": payload["customerId"],
        "sourceOrder": payload["number"],
        "deliveryAddress": payload.get("deliveryAddress", ""),
        "carrier": "dhl",
        "deliveryDate": payload.get("deliveryDate"),
        "status": "ENTWURF",
        "lines": payload.get("lines", []),
    },
    # Offer → Order
    ("sales_offer", "sales_order"): lambda payload: {
        "number": payload["number"].replace("SO", "SO"),
        "date": payload["date"],
        "customerId": payload["customerId"],
        "salesOfferId": payload["number"],
        "status": "ENTWURF",
        "contactPerson": payload.get("contactPerson"),
        "deliveryDate": payload.get("deliveryDate"),
        "deliveryAddress": payload.get("deliveryAddress"),
        "paymentTerms": payload.get("paymentTerms", "net30"),
        "notes": payload.get("notes", ""),
        "lines": payload.get("lines", []),
    },
    # Order → Invoice (direkt)
    ("sales_order", "invoice"): lambda payload: {
        "number": payload["number"].replace("SO", "INV"),
        "date": payload["date"],
        "customerId": payload["customerId"],
        "sourceOrder": payload["number"],
        "paymentTerms": payload.get("paymentTerms", "net30"),
        "dueDate": payload["date"],  # TODO: +30 Tage berechnen
        "status": "ENTWURF",
        "lines": payload.get("lines", []),
        "subtotalNet": sum(
            (line.get("qty", 0) * line.get("price", 0))
            for line in payload.get("lines", [])
        ),
        "totalTax": sum(
            (line.get("qty", 0) * line.get("price", 0) * line.get("vatRate", 0) / 100)
            for line in payload.get("lines", [])
        ),
        "totalGross": sum(
            (line.get("qty", 0) * line.get("price", 0) * (1 + line.get("vatRate", 0) / 100))
            for line in payload.get("lines", [])
        ),
    },
    # Delivery → Invoice
    ("sales_delivery", "invoice"): lambda payload: {
        "number": payload["number"].replace("DL", "INV"),
        "date": payload["date"],
        "customerId": payload["customerId"],
        "sourceOrder": payload.get("sourceOrder"),
        "sourceDelivery": payload["number"],
        "paymentTerms": "net30",
        "dueDate": payload["date"],  # TODO: +30 Tage berechnen
        "status": "ENTWURF",
        "lines": [
            {**line, "price": 0, "vatRate": 19}
            for line in payload.get("lines", [])
        ],
        "subtotalNet": sum(
            (line.get("qty", 0) * line.get("price", 0))
            for line in payload.get("lines", [])
        ),
        "totalTax": sum(
            (line.get("qty", 0) * line.get("price", 0) * line.get("vatRate", 19) / 100)
            for line in payload.get("lines", [])
        ),
        "totalGross": sum(
            (line.get("qty", 0) * line.get("price", 0) * (1 + line.get("vatRate", 19) / 100))
            for line in payload.get("lines", [])
        ),
    },
}


@router.post("/follow")
async def create_follow_up(req: FollowRequest) -> dict:
    """
    Erstellt Folgebeleg aus Quell-Beleg

    Args:
        req: FollowRequest mit fromType, toType, payload

    Returns:
        Transformierter Folgebeleg
    """
    try:
        flow_key = (req.fromType, req.toType)
        transform_fn = FLOW.get(flow_key)

        if not transform_fn:
            logger.warning(f"Flow not defined: {flow_key}")
            return JSONResponse(
                status_code=400,
                content={"ok": False, "error": "flow not defined"},
            )

        # Transformation durchführen
        out = transform_fn(req.payload)

        logger.info(
            f"Created follow-up: {req.fromType} → {req.toType} (number: {out.get('number')})"
        )

        return {"ok": True, **out}
    except Exception as e:
        logger.error(f"Failed to create follow-up: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Lookup-Endpoints (für Autocomplete) ---


@router.get("/customers/search")
async def search_customers(q: str = "") -> dict:
    """Sucht Kunden (Autocomplete)"""
    # TODO: Echte DB-Suche
    mock_customers = [
        {"id": "CUST-001", "label": "Müller GmbH"},
        {"id": "CUST-002", "label": "Schmidt AG"},
        {"id": "CUST-003", "label": "Weber & Co."},
    ]

    filtered = [c for c in mock_customers if q.lower() in c["label"].lower()]
    return {"ok": True, "data": filtered}


@router.get("/articles/search")
async def search_articles(q: str = "") -> dict:
    """Sucht Artikel (Autocomplete)"""
    # TODO: Echte DB-Suche
    mock_articles = [
        {"id": "ART-001", "label": "Apfel Elstar"},
        {"id": "ART-002", "label": "Birne Conference"},
        {"id": "ART-003", "label": "Kartoffel festkochend"},
    ]

    filtered = [a for a in mock_articles if q.lower() in a["label"].lower()]
    return {"ok": True, "data": filtered}

