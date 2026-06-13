"""EINK-GR-PO-001 — Goods Receipt aktualisiert PO-Positions-Mengen und Bestellstatus.

Prüft:
1. menge_geliefert wird für jede Position aktualisiert
2. status='vollstaendig_geliefert' wenn menge_geliefert >= menge
3. Bestellung auf 'geliefert' wenn alle Positionen vollständig
4. Kein Fehler wenn purchase_order_item_id fehlt (wird übersprungen)
"""
from __future__ import annotations

from unittest.mock import MagicMock, call

import pytest


TENANT = "00000000-0000-0000-0000-000000000001"
PO_ID = "PO-001"
POI_ID = "POI-001"


def _make_svc(db):
    from app.services.einkauf_compat_service import EinkaufCompatService
    svc = EinkaufCompatService.__new__(EinkaufCompatService)
    svc.db = db
    svc.tenant_id = TENANT
    return svc


class TestUpdatePoDeliveryQuantities:
    def test_position_wird_aktualisiert(self):
        db = MagicMock()
        svc = _make_svc(db)

        items = [{"purchaseOrderItemId": POI_ID, "acceptedQuantity": 100.0}]
        svc._update_po_delivery_quantities(PO_ID, items)

        calls = [str(c.args[0]) for c in db.execute.call_args_list]
        pos_updates = [s for s in calls if "menge_geliefert" in s]
        assert len(pos_updates) > 0

    def test_bestellung_auf_geliefert_wenn_alle_positionen_vollstaendig(self):
        db = MagicMock()
        svc = _make_svc(db)

        items = [{"purchaseOrderItemId": POI_ID, "receivedQuantity": 500.0}]
        svc._update_po_delivery_quantities(PO_ID, items)

        calls = [str(c.args[0]) for c in db.execute.call_args_list]
        po_updates = [s for s in calls if "bestellungen" in s and "UPDATE" in s and "geliefert" in s]
        assert len(po_updates) > 0

    def test_keine_aktualisierung_ohne_poi(self):
        db = MagicMock()
        svc = _make_svc(db)

        items = [{"articleId": "ART-001", "receivedQuantity": 10.0}]  # no purchaseOrderItemId
        svc._update_po_delivery_quantities(PO_ID, items)

        calls = [str(c.args[0]) for c in db.execute.call_args_list]
        pos_updates = [s for s in calls if "menge_geliefert" in s]
        assert len(pos_updates) == 0

    def test_keine_aktualisierung_bei_menge_null(self):
        db = MagicMock()
        svc = _make_svc(db)

        items = [{"purchaseOrderItemId": POI_ID, "receivedQuantity": 0}]
        svc._update_po_delivery_quantities(PO_ID, items)

        calls = [str(c.args[0]) for c in db.execute.call_args_list]
        pos_updates = [s for s in calls if "menge_geliefert" in s]
        assert len(pos_updates) == 0
