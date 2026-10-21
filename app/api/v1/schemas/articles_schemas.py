"""Auto-generated domain schemas for articles.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from typing import Optional, Union
from uuid import UUID

from pydantic import ConfigDict


class ArticlesOut(BaseSchema):
    """Response schema for articles endpoints."""
    model_config = ConfigDict(extra="allow")


# Zeilenformen der Artikelregister (Studio-Maske ``artikel/stamm``, 20.10.2026): typisiert, damit das Feldvertrags-
# Gate die Spalten der Maske gegen die Antwort pruefen kann.

class ArtikelLieferantZeile(BaseSchema):
    id: Union[str, UUID]
    article_id: Union[str, UUID]
    partner_id: Optional[Union[str, UUID]] = None
    supplier_number: Optional[str] = None
    supplier_name: Optional[str] = None
    supplier_article_number: Optional[str] = None
    purchase_price: Optional[float] = None
    price_valid_from: Optional[str] = None
    price_valid_to: Optional[str] = None
    lead_time_days: Optional[int] = None
    min_order_quantity: Optional[float] = None
    is_preferred: Optional[bool] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ArtikelLieferantenOut(BaseSchema):
    items: list[ArtikelLieferantZeile]


class ArtikelPreisZeile(BaseSchema):
    id: Union[str, UUID]
    article_id: Union[str, UUID]
    price_net: float
    price_incl_freight: Optional[float] = None
    price_unit: Optional[str] = None
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None
    customer_name: Optional[str] = None
    partner_id: Optional[Union[str, UUID]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ArtikelPreiseOut(BaseSchema):
    items: list[ArtikelPreisZeile]


class ArtikelDokumentZeile(BaseSchema):
    id: Union[str, UUID]
    article_id: Union[str, UUID]
    document_id: Optional[Union[str, UUID]] = None
    document_name: Optional[str] = None
    document_type: Optional[str] = None
    document_category: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ArtikelDokumenteOut(BaseSchema):
    items: list[ArtikelDokumentZeile]
