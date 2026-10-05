"""Response-Schemas fuer die POS-Fiskalisierung (TSE / DSFinV-K).

SPEC-P1-06 Welle 2: ersetzt ``response_model=dict[str, Any]`` in
``app/api/v1/endpoints/pos_fiscalization.py``.

Sechs der neun Endpunkte liefern bereits die Pydantic-Vertraege
``FiscalTransactionResult`` bzw. ``ProviderResult`` aus
``app.services.fiscalization.contracts`` — dort genuegt es, das vorhandene
Modell als ``response_model`` zu deklarieren. Nur Konfiguration, Readiness und
Tageswerte brauchen eigene Schemas; ihre Feldlisten stammen aus
``FiscalizationService.get_config``, ``.readiness`` und ``.daily_summary``.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import Field

from app.api.v1.schemas.base import BaseSchema
from app.services.fiscalization.contracts import (
    FiscalProductReadiness,
    ProviderReadiness,
)


class FiscalConfigOut(BaseSchema):
    """``GET`` und ``PUT /pos/fiscalization/config``.

    ``settings`` ist bereits um Secret-Pfade bereinigt (``_public_settings``);
    ``updated_at`` fehlt, solange der Mandant keine Konfiguration hat.
    """

    provider: Optional[str] = Field(
        default=None, description="fiskaly | swissbit_cloud | swissbit_gateway | simulation"
    )
    dsfinvk_provider: Optional[str] = Field(default=None, description="fiskaly | simulation")
    cash_register_id: Optional[str] = Field(default=None, description="Kassen-/TSS-ID")
    client_id: Optional[str] = None
    simulation_allowed: Optional[bool] = None
    settings: dict[str, Any] = Field(
        default_factory=dict, description="Oeffentliche Einstellungen ohne Provider-Secrets"
    )
    updated_at: Optional[datetime] = None
    configured: bool = Field(
        default=False, description="False, solange der Mandant keine Konfiguration hinterlegt hat"
    )


class FiscalReadinessOut(BaseSchema):
    """``GET /pos/fiscalization/readiness``"""

    configured: Optional[bool] = None
    config_blockers: list[str] = Field(
        default_factory=list, description="Fehlende Mandantenkonfiguration"
    )
    sign: Optional[ProviderReadiness] = Field(default=None, description="TSE-Signaturprovider")
    dsfinvk: Optional[ProviderReadiness] = Field(default=None, description="DSFinV-K-Provider")
    products: list[FiscalProductReadiness] = Field(default_factory=list)
    ready: Optional[bool] = Field(
        default=None, description="True nur ohne Config-Blocker und mit beiden Providern bereit"
    )


class FiscalDailySummaryOut(BaseSchema):
    """``GET /pos/fiscalization/daily-summary`` — signierte Tageswerte."""

    transaction_count: Optional[int] = None
    gross_total: Optional[float] = None
    cash_total: Optional[float] = None
    card_total: Optional[float] = None
    incomplete_count: Optional[int] = Field(
        default=None, description="Transaktionen, die nicht im Zustand FINISHED sind"
    )
