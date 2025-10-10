"""
Lookup Router
Autocomplete-API für Kunden, Artikel, etc.
"""

from __future__ import annotations
from fastapi import APIRouter, Query
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/mcp/lookup", tags=["lookup"])

# Mock-Daten (TODO: durch echte DB-Suche ersetzen)
_FAKE_CUSTOMERS = [
    {"id": "CUST-001", "label": "Landhandel Meyer GmbH", "hint": "Emden"},
    {"id": "CUST-002", "label": "AGRAR Nord GmbH", "hint": "Oldenburg"},
    {"id": "CUST-003", "label": "Müller Agrar KG", "hint": "Bremen"},
    {"id": "CUST-004", "label": "Schmidt Landtechnik", "hint": "Leer"},
    {"id": "CUST-005", "label": "Weber Großhandel", "hint": "Wilhelmshaven"},
]

_FAKE_ARTICLES = [
    {"id": "WHEAT-11", "label": "Weizen A", "hint": "25kg Sack", "cost": 2.1, "price": 2.8},
    {"id": "CORN-07", "label": "Mais B", "hint": "25kg Sack", "cost": 1.8, "price": 2.4},
    {"id": "APPL-01", "label": "Apfel Gala", "hint": "Kiste 10kg", "cost": 1.2, "price": 1.8},
    {"id": "PEAR-03", "label": "Birne Conference", "hint": "Kiste 10kg", "cost": 1.5, "price": 2.2},
    {"id": "POTATO-05", "label": "Kartoffel festkochend", "hint": "25kg Sack", "cost": 0.8, "price": 1.2},
]


@router.get("/customers")
async def lookup_customers(q: str = Query("")) -> Dict[str, Any]:
    """
    Sucht Kunden (Autocomplete)

    Args:
        q: Suchbegriff

    Returns:
        Liste von Kunden mit id, label, hint
    """
    ql = q.lower()
    data = [
        c
        for c in _FAKE_CUSTOMERS
        if ql in c["id"].lower() or ql in c["label"].lower()
    ]
    logger.debug(f"Customer lookup: '{q}' → {len(data)} results")
    return {"ok": True, "data": data}


@router.get("/articles")
async def lookup_articles(q: str = Query("")) -> Dict[str, Any]:
    """
    Sucht Artikel (Autocomplete)

    Args:
        q: Suchbegriff

    Returns:
        Liste von Artikeln mit id, label, hint, cost
    """
    ql = q.lower()
    data = [
        a
        for a in _FAKE_ARTICLES
        if ql in a["id"].lower() or ql in a["label"].lower()
    ]
    logger.debug(f"Article lookup: '{q}' → {len(data)} results")
    return {"ok": True, "data": data}

