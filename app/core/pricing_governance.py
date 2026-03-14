"""
Pricing Governance Models — Wave 3 AP4
Klassifizierung von Pricing- und Marktdatenquellen
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class PricingSourceType(str, Enum):
    exchange = "exchange"          # Warenbörse
    broker = "broker"
    spot_market = "spot_market"
    internal_cost = "internal_cost"
    fixed_contract = "fixed_contract"
    manual_override = "manual_override"


class PricingSourceReliability(str, Enum):
    authoritative = "authoritative"
    indicative = "indicative"
    estimated = "estimated"
    override = "override"


class PricingSourceManifest(BaseModel):
    source_id: str
    label: str
    source_type: PricingSourceType
    reliability: PricingSourceReliability
    tenant_id: str | None = None  # None = global
    update_frequency_minutes: int | None = None
    requires_approval_for_use: bool = False
    audit_on_use: bool = True
    schema_version: int = 1


class PricingGovernancePolicy(BaseModel):
    tenant_id: str
    sources: list[PricingSourceManifest]
    default_source_id: str | None = None
    require_approval_for_manual_override: bool = True
    schema_version: int = 1

    def get_source(self, source_id: str) -> PricingSourceManifest | None:
        for source in self.sources:
            if source.source_id == source_id:
                return source
        return None


def build_default_pricing_sources() -> list[PricingSourceManifest]:
    """Returns standard pricing source manifests."""
    return [
        PricingSourceManifest(
            source_id="MATIF",
            label="MATIF Warenbörse",
            source_type=PricingSourceType.exchange,
            reliability=PricingSourceReliability.authoritative,
        ),
        PricingSourceManifest(
            source_id="XONTRO",
            label="XONTRO Börse",
            source_type=PricingSourceType.exchange,
            reliability=PricingSourceReliability.authoritative,
        ),
        PricingSourceManifest(
            source_id="spot_daily",
            label="Tages-Spotmarkt",
            source_type=PricingSourceType.spot_market,
            reliability=PricingSourceReliability.indicative,
        ),
        PricingSourceManifest(
            source_id="fixed_contract",
            label="Festpreiskontrakt",
            source_type=PricingSourceType.fixed_contract,
            reliability=PricingSourceReliability.authoritative,
        ),
        PricingSourceManifest(
            source_id="manual_override",
            label="Manuelle Preiskorrektur",
            source_type=PricingSourceType.manual_override,
            reliability=PricingSourceReliability.override,
            requires_approval_for_use=True,
        ),
    ]
