"""
Lookup Router
Autocomplete-API für Kunden, Artikel, etc.
"""

from __future__ import annotations
from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from app.core.database import get_db
from app.infrastructure.models import Customer, Article

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/mcp/lookup", tags=["lookup"])


@router.get("/customers")
async def lookup_customers(
    q: str = Query(""),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Sucht Kunden (Autocomplete). Liefert bis zu 20 Treffer."""
    query = db.query(Customer).filter(Customer.is_active == True)  # noqa: E712
    if q:
        pattern = f"%{q}%"
        query = query.filter(
            (Customer.company_name.ilike(pattern))
            | (Customer.customer_number.ilike(pattern))
            | (Customer.last_name.ilike(pattern))
        )
    rows = query.limit(20).all()
    data = [
        {
            "id": c.customer_number or c.id,
            "label": c.company_name or f"{c.last_name}",
            "hint": getattr(c, "city", "") or "",
        }
        for c in rows
    ]
    logger.debug("Customer lookup: '%s' → %d results", q, len(data))
    return {"ok": True, "data": data}


@router.get("/articles")
async def lookup_articles(
    q: str = Query(""),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Sucht Artikel (Autocomplete). Liefert bis zu 20 Treffer."""
    query = db.query(Article).filter(Article.is_active == True)  # noqa: E712
    if q:
        pattern = f"%{q}%"
        query = query.filter(
            (Article.name.ilike(pattern))
            | (Article.article_number.ilike(pattern))
        )
    rows = query.limit(20).all()
    data = [
        {
            "id": a.article_number or a.id,
            "label": a.name,
            "hint": getattr(a, "unit", "") or "",
        }
        for a in rows
    ]
    logger.debug("Article lookup: '%s' → %d results", q, len(data))
    return {"ok": True, "data": data}
