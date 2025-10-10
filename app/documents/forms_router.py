"""
Form-Specs Router
Liefert JSON-Schemas für dynamische Formular-Generierung
"""

from __future__ import annotations
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/mcp/form-specs", tags=["forms"])

# Form-Specs (In Production: aus DB/Datei laden)
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
                "lookup": "/api/mcp/customers/search",
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
                    "lookup": "/api/mcp/articles/search",
                },
                {"name": "qty", "label": "Menge", "type": "number", "required": True},
                {"name": "price", "label": "Preis", "type": "number", "required": True},
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
                "lookup": "/api/mcp/customers/search",
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
                    "lookup": "/api/mcp/articles/search",
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
                "lookup": "/api/mcp/customers/search",
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
                    "lookup": "/api/mcp/articles/search",
                },
                {"name": "qty", "label": "Menge", "type": "number", "required": True},
                {"name": "price", "label": "Preis", "type": "number", "required": True},
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
async def get_schema(schema_id: str) -> Dict[str, Any]:
    """
    Holt Form-Schema für Dokumenten-Typ

    Args:
        schema_id: Schema-ID (z.B. "sales_order")

    Returns:
        Form-Schema als JSON
    """
    s = SCHEMAS.get(schema_id)
    if not s:
        logger.warning(f"Schema not found: {schema_id}")
        return JSONResponse(
            status_code=404, content={"ok": False, "error": "schema not found"}
        )

    logger.info(f"Loaded form schema: {schema_id}")
    return {"ok": True, "data": s}

