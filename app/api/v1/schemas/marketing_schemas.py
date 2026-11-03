"""Antwortschemas der Marketingkampagnen (Batch 8, 03.11.2026: typisiert statt extra="allow")."""
from __future__ import annotations

from typing import Optional

from pydantic import ConfigDict

from app.api.v1.schemas.base import BaseSchema


class MarketingKampagneOut(BaseSchema):
    id: str
    name: str
    typ: str
    zielgruppe: Optional[str] = None
    startdatum: Optional[str] = None
    enddatum: Optional[str] = None
    budget: float = 0
    status: Optional[str] = None


class MarketingKampagneListOut(BaseSchema):
    items: list[MarketingKampagneOut]
    total: int


class MarketingStatsOut(BaseSchema):
    aktiv: int
    geplant: int
    beendet: int
    budget_aktiv: float


class MarketingKpiOut(BaseSchema):
    """Plan aus der Kampagne; Ist-Werte gibt es erst mit einer Kostenquelle (bis dahin None, nicht 0)."""
    id: str
    name: str
    status: Optional[str] = None
    budget_plan: float
    budget_ist: Optional[float] = None
    open_rate: Optional[float] = None
    click_rate: Optional[float] = None
    conversion_rate: Optional[float] = None
    roi: Optional[float] = None


class MarketingOut(BaseSchema):
    """Altname, nur noch fuer Aufrufer ausserhalb dieser Wege."""
    model_config = ConfigDict(extra="allow")
