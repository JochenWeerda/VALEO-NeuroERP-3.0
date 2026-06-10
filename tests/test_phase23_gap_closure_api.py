from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.mark.unit
def test_pos_dsfinvk_export_fails_closed_without_provider_configuration():
    from app.api.v1.endpoints import pos_dsfinvk

    app = FastAPI()
    app.include_router(pos_dsfinvk.router)
    client = TestClient(app)

    response = client.get("/dsfinvk/export")

    assert response.status_code == 409
    assert "nicht konfiguriert" in response.json()["detail"]


@pytest.mark.unit
def test_phase23_routers_include_repo_side_gap_closure_paths():
    from app.api.v1.api import api_router

    paths = {getattr(route, "path", "") for route in api_router.routes}

    expected = {
        "/crm/customers/{customer_id}/360",
        "/finance/asset-accounting/assets",
        "/finance/budgets",
        "/finance/liquidity/forecast",
        "/sales/blanket-orders/",
        "/ebilanz/eric-readiness",
        "/ebilanz/export/erstellen",
        "/gs1/barcode/parse",
        "/pos/dsfinvk/export",
        "/saatzucht/partien",
        "/zoll/ausfuhranmeldungen",
        "/webshop/bestellungen/import",
    }

    assert sorted(expected - paths) == []
