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


class WorkspaceStartpageOut(BaseSchema):
    """Rollen-Startseite (UIX-061): screenId/route null wenn keine Zuordnung."""
    role: str | None
    screenId: str | None
    route: str | None


class OmniboxCatalogEntryOut(BaseSchema):
    """Katalog-Eintrag fuer die Omnibox: Matching-Basis je ScreenDefinition."""
    screen_id: str
    title: str
    domain: str
    floorplan: str
    route: str  # kuratierte Frontend-Listen-Route (UIX-060), leer wenn ungebunden
    synonyms: list[str]
    example_prompts: list[str]
    filterable_fields: list[OmniboxFilterFieldOut]
