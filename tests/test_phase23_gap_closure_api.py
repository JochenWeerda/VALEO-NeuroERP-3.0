from __future__ import annotations

import io
import zipfile

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.mark.unit
def test_pos_dsfinvk_export_zip_contains_required_files():
    from app.api.v1.endpoints import pos_dsfinvk

    app = FastAPI()
    app.include_router(pos_dsfinvk.router)
    client = TestClient(app)

    response = client.get("/dsfinvk/export")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        names = set(archive.namelist())
        assert {
            "cashpointclosing.csv",
            "transactions.csv",
            "lines.csv",
            "datapayment.csv",
            "vat.csv",
            "index.xml",
        }.issubset(names)
        index_xml = archive.read("index.xml").decode("utf-8")
        assert 'version="2.3"' in index_xml
        assert "KASSE-001" in index_xml


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
