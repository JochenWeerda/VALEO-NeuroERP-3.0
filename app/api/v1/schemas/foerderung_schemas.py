"""Antwortschemas der Foerderantraege (Batch 8, 03.11.2026: typisiert statt extra="allow")."""
from __future__ import annotations

from typing import Optional

from pydantic import ConfigDict

from app.api.v1.schemas.base import BaseSchema


class FoerderAntragOut(BaseSchema):
    id: str
    nummer: str
    programm: str
    antragsdatum: Optional[str] = None
    flaeche: float = 0
    betrag: float = 0
    status: Optional[str] = None


class FoerderAntragListOut(BaseSchema):
    items: list[FoerderAntragOut]
    total: int
    sum_betrag: float


class FoerderungStatsOut(BaseSchema):
    bewilligt: int
    eingereicht: int
    entwurf: int
    betrag_bewilligt: float


class FoerderungOut(BaseSchema):
    """Altname, nur noch fuer Aufrufer ausserhalb dieser Wege."""
    model_config = ConfigDict(extra="allow")
