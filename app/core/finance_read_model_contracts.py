"""
Finance Read-Model Contracts — Wave 19 AP6

Gemeinsame Vertragstypen fuer alle Finance-Read-Models.
schema_version=1 ist verbindlich und darf nicht ohne Wave-Beschluss geaendert werden.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


FINANCE_SCHEMA_VERSION = 1


class SettlementCockpitStatus(str, Enum):
    ENTWURF = "ENTWURF"
    ZUR_FREIGABE = "ZUR_FREIGABE"
    TEILWEISE_FREIGEGEBEN = "TEILWEISE_FREIGEGEBEN"
    FREIGEGEBEN = "FREIGEGEBEN"
    ABGELEHNT = "ABGELEHNT"
    VERBUCHT = "VERBUCHT"


class PositionExposureType(str, Enum):
    KONTRAKT = "KONTRAKT"
    LAGER = "LAGER"
    OFFENE_RECHNUNG = "OFFENE_RECHNUNG"
    ABRECHNUNG = "ABRECHNUNG"


@dataclass
class SettlementCockpitRow:
    """Single row in the Settlement-Cockpit Read-Model."""

    settlement_id: str
    tenant_id: str
    customer_id: str
    gross_amount: float
    currency: str
    status: SettlementCockpitStatus
    process_definition_key: str = "agrar_settlement"
    workflow_version: str = "1.0"
    approval_current: int = 0
    approval_required: int = 1
    days_open: int = 0
    has_quality_exception: bool = False
    has_price_override: bool = False
    can_post: bool = False

    @property
    def approval_complete(self) -> bool:
        return self.approval_current >= self.approval_required

    def as_dict(self) -> dict:
        return {
            "settlement_id": self.settlement_id,
            "tenant_id": self.tenant_id,
            "customer_id": self.customer_id,
            "gross_amount": self.gross_amount,
            "currency": self.currency,
            "status": self.status.value,
            "process_definition_key": self.process_definition_key,
            "workflow_version": self.workflow_version,
            "approval_current": self.approval_current,
            "approval_required": self.approval_required,
            "approval_complete": self.approval_complete,
            "days_open": self.days_open,
            "has_quality_exception": self.has_quality_exception,
            "has_price_override": self.has_price_override,
            "can_post": self.can_post,
        }


@dataclass
class PositionExposureRow:
    """Single row in the Position-Exposure Read-Model."""

    position_id: str
    tenant_id: str
    exposure_type: PositionExposureType
    gross_amount: float
    currency: str
    commodity: Optional[str] = None
    counterparty_id: Optional[str] = None
    open_since_days: int = 0
    risk_flag: bool = False

    def as_dict(self) -> dict:
        return {
            "position_id": self.position_id,
            "tenant_id": self.tenant_id,
            "exposure_type": self.exposure_type.value,
            "gross_amount": self.gross_amount,
            "currency": self.currency,
            "commodity": self.commodity,
            "counterparty_id": self.counterparty_id,
            "open_since_days": self.open_since_days,
            "risk_flag": self.risk_flag,
        }


@dataclass
class SettlementCockpitSnapshot:
    """Full Settlement-Cockpit Read-Model snapshot for a tenant."""

    tenant_id: str
    schema_version: int = FINANCE_SCHEMA_VERSION
    rows: list[SettlementCockpitRow] = field(default_factory=list)

    @property
    def total_open(self) -> float:
        return sum(
            r.gross_amount
            for r in self.rows
            if r.status not in (
                SettlementCockpitStatus.VERBUCHT,
                SettlementCockpitStatus.ABGELEHNT,
            )
        )

    @property
    def pending_approval_count(self) -> int:
        return sum(
            1 for r in self.rows
            if r.status in (
                SettlementCockpitStatus.ZUR_FREIGABE,
                SettlementCockpitStatus.TEILWEISE_FREIGEGEBEN,
            )
        )

    def as_dict(self) -> dict:
        return {
            "tenant_id": self.tenant_id,
            "schema_version": self.schema_version,
            "total_open": self.total_open,
            "pending_approval_count": self.pending_approval_count,
            "row_count": len(self.rows),
            "rows": [r.as_dict() for r in self.rows],
        }


@dataclass
class PositionExposureSnapshot:
    """Full Position-Exposure Read-Model snapshot for a tenant."""

    tenant_id: str
    schema_version: int = FINANCE_SCHEMA_VERSION
    rows: list[PositionExposureRow] = field(default_factory=list)

    @property
    def total_exposure(self) -> float:
        return sum(r.gross_amount for r in self.rows)

    @property
    def risk_count(self) -> int:
        return sum(1 for r in self.rows if r.risk_flag)

    def as_dict(self) -> dict:
        return {
            "tenant_id": self.tenant_id,
            "schema_version": self.schema_version,
            "total_exposure": self.total_exposure,
            "risk_count": self.risk_count,
            "row_count": len(self.rows),
            "rows": [r.as_dict() for r in self.rows],
        }
