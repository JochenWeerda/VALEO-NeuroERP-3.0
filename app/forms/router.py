"""
Forms Router
API-Endpoints für Form-Specs (Schema-Definitionen)
"""

from __future__ import annotations
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/mcp/form-specs", tags=["forms"])

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
async def search_customers(q: str = "") -> dict:
    """Sucht Kunden (Autocomplete)"""
    # TODO: Echte DB-Suche implementieren
    mock_customers = [
        {"id": "CUST-001", "label": "Müller GmbH"},
        {"id": "CUST-002", "label": "Schmidt AG"},
        {"id": "CUST-003", "label": "Weber & Co. KG"},
        {"id": "CUST-004", "label": "Meyer Handel"},
        {"id": "CUST-005", "label": "Bauer Logistik"},
    ]

    filtered = [c for c in mock_customers if q.lower() in c["label"].lower()]
    logger.debug(f"Customer search: '{q}' → {len(filtered)} results")
    return {"ok": True, "data": filtered}


@router.get("/articles/search")
async def search_articles(q: str = "") -> dict:
    """Sucht Artikel (Autocomplete)"""
    # TODO: Echte DB-Suche implementieren
    mock_articles = [
        {"id": "ART-001", "label": "Apfel Elstar (kg)"},
        {"id": "ART-002", "label": "Birne Conference (kg)"},
        {"id": "ART-003", "label": "Kartoffel festkochend (kg)"},
        {"id": "ART-004", "label": "Tomate rund (kg)"},
        {"id": "ART-005", "label": "Gurke Salat (Stk)"},
    ]

    filtered = [a for a in mock_articles if q.lower() in a["label"].lower()]
    logger.debug(f"Article search: '{q}' → {len(filtered)} results")
    return {"ok": True, "data": filtered}

