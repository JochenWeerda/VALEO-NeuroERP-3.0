"""
Forms Router
API-Endpoints für Form-Specs (Schema-Definitionen)
"""

from __future__ import annotations
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any
from pydantic import BaseModel
import logging
from app.core.dependency_container import container
from app.infrastructure.repositories import CustomerRepository, ArticleRepository

class FollowRequest(BaseModel):
    source_id: str
    fromType: str
    toType: str
    payload: Dict[str, Any]

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/mcp/form-specs", tags=["forms"])

# Flow-Matrix: (fromType, toType) -> transform_fn
def order_to_delivery(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Transformiert Auftrag zu Lieferung"""
    return {
        **payload,
        "type": "sales_delivery",
        "number": payload.get("number", "").replace("SO-", "DL-")
    }

def order_to_invoice(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Transformiert Auftrag zu Rechnung"""
    return {
        **payload,
        "type": "sales_invoice",
        "number": payload.get("number", "").replace("SO-", "INV-")
    }

def delivery_to_invoice(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Transformiert Lieferung zu Rechnung"""
    return {
        **payload,
        "type": "sales_invoice",
        "number": payload.get("number", "").replace("DL-", "INV-")
    }

FLOW: Dict[tuple[str, str], Any] = {
    ("sales_order", "sales_delivery"): order_to_delivery,
    ("sales_order", "sales_invoice"): order_to_invoice,
    ("sales_delivery", "sales_invoice"): delivery_to_invoice,
}

# Form-Specs (In echt: aus DB/Datei laden)
SCHEMAS: Dict[str, Dict[str, Any]] = {
    "sales_order": {
        "id": "sales_order",
        "title": "Verkaufsauftrag",
        "fields": [
            {
                "name": "number",
                "label": "Belegnummer",
                "type": "string",
                "required": True,
                "placeholder": "SO-2025-0001",
            },
            {
                "name": "date",
                "label": "Auftragsdatum",
                "type": "date",
                "required": True,
            },
            {
                "name": "customerId",
                "label": "Kunde",
                "type": "lookup",
                "required": True,
                "lookup": "/api/mcp/documents/customers/search",
                "placeholder": "Kunde suchen...",
            },
            {
                "name": "deliveryAddress",
                "label": "Lieferadresse",
                "type": "text",
                "required": False,
            },
            {
                "name": "paymentTerms",
                "label": "Zahlungsbedingungen",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "net30", "label": "30 Tage netto"},
                    {"value": "net14", "label": "14 Tage netto"},
                    {"value": "cash", "label": "Sofort"},
                ],
            },
            {"name": "notes", "label": "Notizen", "type": "text", "required": False},
        ],
        "lines": {
            "name": "lines",
            "label": "Positionen",
            "columns": [
                {
                    "name": "article",
                    "label": "Artikel",
                    "type": "lookup",
                    "required": True,
                    "lookup": "/api/mcp/documents/articles/search",
                },
                {"name": "qty", "label": "Menge", "type": "number", "required": True},
                {
                    "name": "price",
                    "label": "Preis",
                    "type": "number",
                    "required": True,
                },
            ],
        },
    },
    "sales_delivery": {
        "id": "sales_delivery",
        "title": "Lieferschein",
        "fields": [
            {
                "name": "number",
                "label": "Lieferschein-Nr.",
                "type": "string",
                "required": True,
                "placeholder": "DL-2025-0001",
            },
            {
                "name": "date",
                "label": "Lieferdatum",
                "type": "date",
                "required": True,
            },
            {
                "name": "customerId",
                "label": "Kunde",
                "type": "lookup",
                "required": True,
                "lookup": "/api/mcp/documents/customers/search",
                "placeholder": "Kunde suchen...",
            },
            {
                "name": "sourceOrder",
                "label": "Auftrag (Quelle)",
                "type": "string",
                "required": False,
                "placeholder": "SO-2025-0001",
            },
            {
                "name": "deliveryAddress",
                "label": "Lieferadresse",
                "type": "text",
                "required": True,
            },
            {
                "name": "carrier",
                "label": "Spediteur",
                "type": "select",
                "required": False,
                "options": [
                    {"value": "dhl", "label": "DHL"},
                    {"value": "ups", "label": "UPS"},
                    {"value": "dpd", "label": "DPD"},
                    {"value": "self", "label": "Selbstabholung"},
                ],
            },
            {"name": "notes", "label": "Notizen", "type": "text", "required": False},
        ],
        "lines": {
            "name": "lines",
            "label": "Positionen",
            "columns": [
                {
                    "name": "article",
                    "label": "Artikel",
                    "type": "lookup",
                    "required": True,
                    "lookup": "/api/mcp/documents/articles/search",
                },
                {"name": "qty", "label": "Menge", "type": "number", "required": True},
            ],
        },
    },
    "sales_invoice": {
        "id": "sales_invoice",
        "title": "Rechnung",
        "fields": [
            {
                "name": "number",
                "label": "Rechnungs-Nr.",
                "type": "string",
                "required": True,
                "placeholder": "INV-2025-0001",
            },
            {
                "name": "date",
                "label": "Rechnungsdatum",
                "type": "date",
                "required": True,
            },
            {
                "name": "customerId",
                "label": "Kunde",
                "type": "lookup",
                "required": True,
                "lookup": "/api/mcp/documents/customers/search",
                "placeholder": "Kunde suchen...",
            },
            {
                "name": "sourceOrder",
                "label": "Auftrag (Quelle)",
                "type": "string",
                "required": False,
                "placeholder": "SO-2025-0001",
            },
            {
                "name": "sourceDelivery",
                "label": "Lieferschein (Quelle)",
                "type": "string",
                "required": False,
                "placeholder": "DL-2025-0001",
            },
            {
                "name": "paymentTerms",
                "label": "Zahlungsbedingungen",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "net30", "label": "30 Tage netto"},
                    {"value": "net14", "label": "14 Tage netto"},
                    {"value": "cash", "label": "Sofort"},
                ],
            },
            {
                "name": "dueDate",
                "label": "Fälligkeitsdatum",
                "type": "date",
                "required": True,
            },
            {"name": "notes", "label": "Notizen", "type": "text", "required": False},
        ],
        "lines": {
            "name": "lines",
            "label": "Positionen",
            "columns": [
                {
                    "name": "article",
                    "label": "Artikel",
                    "type": "lookup",
                    "required": True,
                    "lookup": "/api/mcp/documents/articles/search",
                },
                {"name": "qty", "label": "Menge", "type": "number", "required": True},
                {
                    "name": "price",
                    "label": "Preis",
                    "type": "number",
                    "required": True,
                },
                {
                    "name": "vatRate",
                    "label": "MwSt %",
                    "type": "number",
                    "required": True,
                },
            ],
        },
    },
}


@router.get("/{schema_id}")
async def get_schema(schema_id: str) -> dict:
    """Holt Form-Spec für Beleg-Typ"""
    s = SCHEMAS.get(schema_id)
    if not s:
        return JSONResponse(
            status_code=404, content={"ok": False, "error": "schema not found"}
        )
    return {"ok": True, "data": s}


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
                content={"ok": False, "error": f"flow not defined: {flow_key}"},
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


# --- Lookup-Endpoints (Autocomplete) ---


@router.get("/customers/search")
async def search_customers(q: str = "", tenant_id: str = "system") -> dict:
    """Sucht Kunden (Autocomplete)"""
    try:
        customer_repo = container.resolve(CustomerRepository)
        customers = await customer_repo.get_all(tenant_id, search=q, limit=10)

        # Format for autocomplete
        results = [
            {
                "id": c.customer_number or str(c.id),
                "label": c.company_name or f"{c.contact_person} ({c.customer_number})"
            }
            for c in customers
        ]

        logger.debug(f"Customer search: '{q}' → {len(results)} results")
        return {"ok": True, "data": results}
    except Exception as e:
        logger.error(f"Customer search failed: {e}")
        return {"ok": False, "error": str(e)}


@router.get("/articles/search")
async def search_articles(q: str = "", tenant_id: str = "system") -> dict:
    """Sucht Artikel (Autocomplete)"""
    try:
        article_repo = container.resolve(ArticleRepository)
        articles = await article_repo.get_all(tenant_id, search=q, limit=10)

        # Format for autocomplete
        results = [
            {
                "id": a.article_number or str(a.id),
                "label": f"{a.name} ({a.unit})"
            }
            for a in articles
        ]

        logger.debug(f"Article search: '{q}' → {len(results)} results")
        return {"ok": True, "data": results}
    except Exception as e:
        logger.error(f"Article search failed: {e}")
        return {"ok": False, "error": str(e)}

