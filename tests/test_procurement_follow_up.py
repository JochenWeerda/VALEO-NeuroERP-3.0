"""Validierung Folgeaktionen — reine Service-Regeln ohne DB-Mocks (DOM-PROC-004.4).

DB-Pfade werden in tests/test_procurement_match_integration.py abgedeckt.
"""

from __future__ import annotations

import pytest

from app.services.procurement_match_service import ProcurementMatchService

pytestmark = pytest.mark.unit


def test_create_follow_up_rejects_unknown_action():
    svc = ProcurementMatchService(db=None, tenant_id="tenant-demo")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="Unbekannte Folgeaktion"):
        svc.create_follow_up(bestellnummer="DEMO-PO-001", action_type="storno", grund="Testgrund")


def test_create_follow_up_requires_grund():
    svc = ProcurementMatchService(db=None, tenant_id="tenant-demo")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="Grund ist Pflicht"):
        svc.create_follow_up(bestellnummer="DEMO-PO-001", action_type="nachforderung", grund="   ")
