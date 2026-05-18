"""Tests for report/print gap closure endpoints."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.api import api_router
from app.api.v1.endpoints import report_print


def _client() -> TestClient:
    app = FastAPI()
    db = MagicMock()
    app.dependency_overrides[report_print.get_db] = lambda: db
    app.dependency_overrides[report_print.get_tenant_id] = lambda: "test-tenant"
    app.include_router(report_print.router)
    return TestClient(app)


@pytest.mark.unit
def test_report_print_readiness_lists_repo_contracts():
    resp = _client().get("/report-print/readiness")

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "repo_ready"
    assert "partie_genealogy" in body["capabilities"]
    assert "live_printer_acceptance" in body["external_gates"]


@pytest.mark.unit
def test_partie_genealogy_returns_traceability_graph():
    resp = _client().get("/report-print/parties/PAR-2026-0001/genealogy")

    assert resp.status_code == 200
    body = resp.json()
    assert body["tenant_id"] == "test-tenant"
    assert body["partie_ref"] == "PAR-2026-0001"
    assert body["completeness"]["has_weighing_ticket"] is True
    assert body["completeness"]["has_label_contract"] is True
    assert {node["type"] for node in body["nodes"]} >= {
        "supplier",
        "weighing_ticket",
        "partie",
        "charge",
        "label",
    }
    assert any(edge["relation"] == "identified_by" for edge in body["edges"])


@pytest.mark.unit
def test_weighing_ticket_pdf_preview_returns_artifact_metadata():
    resp = _client().get("/report-print/weighing-tickets/WG-2026-42/pdf-preview")

    assert resp.status_code == 200
    body = resp.json()
    assert body["filename"] == "wiegeschein-WG-2026-42.pdf"
    assert body["content_type"] == "application/pdf"
    assert body["pdf_available"] is True
    assert body["render_mode"] == "preview"
    assert len(body["sha256"]) == 64
    assert body["fields"]["net_weight_kg"] > 0


@pytest.mark.unit
def test_label_payload_contains_gs1_sscc_contract():
    resp = _client().post(
        "/report-print/labels",
        json={
            "partie_ref": "PAR-2026-0001",
            "charge_ref": "CH-2026-0001",
            "article_ref": "ART-WEIZEN-A",
            "gtin": "04012345123456",
            "sscc": "340123451234567890",
            "quantity_kg": 1250.5,
        },
    )

    assert resp.status_code == 201
    body = resp.json()
    assert body["print_ready"] is True
    assert body["template"] == "GS1_LOGISTICS_LABEL"
    assert body["gtin"] == "04012345123456"
    assert body["sscc"] == "340123451234567890"
    assert "(00)340123451234567890" in body["barcode_payload"]
    assert "label_stock_calibration" in body["external_gates"]


@pytest.mark.unit
def test_report_print_router_is_registered_in_api_router():
    paths = {route.path for route in api_router.routes}

    assert "/report-print/readiness" in paths
    assert "/report-print/parties/{partie_ref}/genealogy" in paths
    assert "/report-print/weighing-tickets/{ticket_ref}/pdf-preview" in paths
    assert "/report-print/labels" in paths
