"""Vertrags-Test des KIM-360°-Bündel-Dashboards (DB-frei)."""

from __future__ import annotations

import pytest

from app.api.v1.endpoints.crm_kim import CustomerDashboard, DashboardMeta

pytestmark = pytest.mark.unit


def test_dashboard_shape_und_meta():
    d = CustomerDashboard(
        customer=None, contacts=[], logs=[], financials=[], documents=[],
        meta=DashboardMeta(
            timings={"customer": 1.2, "contacts": 0.5, "total": 2.0},
            sourceStatus={"customer": "ok", "contacts": "ok"},
        ),
    )
    # Bündel liefert genau die fünf Ströme + meta.timings/sourceStatus.
    assert d.contacts == [] and d.financials == [] and d.documents == []
    assert d.meta.timings["total"] == 2.0
    assert d.meta.sourceStatus["customer"] == "ok"


def test_dashboard_meta_erlaubt_fehlerstatus():
    meta = DashboardMeta(timings={"financials": 12.0}, sourceStatus={"financials": "error:OperationalError"})
    assert meta.sourceStatus["financials"].startswith("error:")
