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


def test_create_follow_up_does_not_write_without_tenant_order():
    from unittest.mock import Mock

    db = Mock()
    db.execute.return_value.mappings.return_value.first.return_value = None
    svc = ProcurementMatchService(db=db, tenant_id="tenant-a")

    with pytest.raises(ValueError, match="Bestellung nicht"):
        svc.create_follow_up(bestellnummer="PO-42", action_type="eskalation", grund="Prüfen")

    lookup = db.execute.call_args.args
    assert "tenant_id = :t" in str(lookup[0])
    assert lookup[1] == {"t": "tenant-a", "v": "PO-42"}
    db.execute.assert_called_once()
    db.commit.assert_not_called()
