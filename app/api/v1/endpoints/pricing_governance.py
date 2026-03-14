"""
Pricing Governance Endpoints — Wave 3 AP4
Klassifizierung von Pricing- und Marktdatenquellen.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from ....core.tenant import get_tenant_id
from ....core.pricing_governance import (
    PricingSourceManifest,
    PricingGovernancePolicy,
    build_default_pricing_sources,
)

router = APIRouter(prefix="/pricing", tags=["pricing", "governance"])

# ---------------------------------------------------------------------------
# In-memory store (per tenant)
# ---------------------------------------------------------------------------

_SOURCES: dict[str, list[dict]] = {}  # tenant_id → list of source dicts


def _get_sources(tenant_id: str) -> list[PricingSourceManifest]:
    if tenant_id not in _SOURCES:
        # Seed with defaults
        defaults = build_default_pricing_sources()
        _SOURCES[tenant_id] = [s.model_dump() for s in defaults]
    return [PricingSourceManifest(**s) for s in _SOURCES[tenant_id]]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/sources", response_model=list[PricingSourceManifest])
async def list_pricing_sources(tenant_id: str = Depends(get_tenant_id)):
    """List all pricing sources for the tenant."""
    return _get_sources(tenant_id)


@router.get("/governance", response_model=PricingGovernancePolicy)
async def get_governance_policy(tenant_id: str = Depends(get_tenant_id)):
    """Get the pricing governance policy for the tenant."""
    sources = _get_sources(tenant_id)
    # Default source: first authoritative exchange source
    default_source_id = None
    for s in sources:
        if s.source_type == "exchange" and s.reliability == "authoritative":
            default_source_id = s.source_id
            break

    return PricingGovernancePolicy(
        tenant_id=tenant_id,
        sources=sources,
        default_source_id=default_source_id,
        require_approval_for_manual_override=True,
    )
