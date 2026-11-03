"""Antwortschemas der Laborwege (Batch 8, 03.11.2026: typisiert statt extra="allow")."""
from __future__ import annotations

from typing import Any, Optional

from pydantic import ConfigDict, Field

from app.api.v1.schemas.base import BaseSchema


class LaborProbeOut(BaseSchema):
    id: str
    probennummer: str
    typ: str
    artikel: str
    datum: Optional[str] = None
    labor: str
    status: Optional[str] = None


class LaborProbeListOut(BaseSchema):
    items: list[LaborProbeOut]
    total: int


class LaborBefundKurzOut(BaseSchema):
    id: str
    probennummer: str
    entscheidung: Optional[str] = None
    datum: Optional[str] = None
    labor: str


class LaborAuftragOut(BaseSchema):
    id: str
    chargenId: str  # noqa: N815 - Schluessel des Wizards
    chargen_id: str
    labor: str
    analysen: int
    auftragsdatum: str
    status: Optional[str] = None
    befund: Optional[LaborBefundKurzOut] = None
    qs_entscheidung: Optional[str] = None
    folgeaktion: str
    analysewerte: dict[str, Any] = Field(default_factory=dict)
    grenzwerte: dict[str, Any] = Field(default_factory=dict)
    bemerkung: Optional[str] = None


class LaborAuftragListOut(BaseSchema):
    items: list[LaborAuftragOut]
    total: int


class LaborStatsOut(BaseSchema):
    model_config = ConfigDict(populate_by_name=True)

    abgeschlossen: int
    in_bearbeitung: int = Field(alias="in-bearbeitung")
    ausstehend: int


class LaborOut(BaseSchema):
    """Altname, nur noch fuer Aufrufer ausserhalb dieser Wege."""
    model_config = ConfigDict(extra="allow")
