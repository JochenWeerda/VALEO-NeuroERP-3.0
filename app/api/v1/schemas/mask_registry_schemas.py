"""Auto-generated domain schemas for mask registry.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class MaskRegistryOut(BaseSchema):
    """Response schema for mask registry endpoints."""
    model_config = ConfigDict(extra="allow")


class OmniboxFilterFieldOut(BaseSchema):
    """Filterbares Feld einer Maske fuer den Omnibox-Intent-Compiler (UIX-060)."""
    key: str
    label: str
    type: str  # 'enum' | 'date' | 'number' | 'text'


class OmniboxCatalogEntryOut(BaseSchema):
    """Katalog-Eintrag fuer die Omnibox: Matching-Basis je ScreenDefinition."""
    screen_id: str
    title: str
    domain: str
    floorplan: str
    synonyms: list[str]
    example_prompts: list[str]
    filterable_fields: list[OmniboxFilterFieldOut]
