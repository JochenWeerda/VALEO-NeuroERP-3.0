"""Guard-Tests der Lot-Folgeaktionen (DOM-SUPPLY-004.3) — Pflicht-Grund/Menge.

Diese Prüfungen greifen vor jedem DB-Zugriff, daher ohne Session testbar.
"""

from __future__ import annotations

import pytest

from app.services.supply_chain_lot_service import LotActionError, SupplyChainLotService

pytestmark = pytest.mark.unit


def _svc() -> SupplyChainLotService:
    return SupplyChainLotService(db=None, tenant_id="t")  # type: ignore[arg-type]


def test_block_requires_grund():
    with pytest.raises(LotActionError):
        _svc().block("LOT-1", "   ")


def test_release_requires_grund():
    with pytest.raises(LotActionError):
        _svc().release("LOT-1", "")


def test_shrinkage_requires_grund():
    with pytest.raises(LotActionError):
        _svc().shrinkage("LOT-1", 100.0, "")


def test_shrinkage_requires_positive_menge():
    with pytest.raises(LotActionError):
        _svc().shrinkage("LOT-1", 0, "Grund")
    with pytest.raises(LotActionError):
        _svc().shrinkage("LOT-1", -5, "Grund")
