"""
Tests for gs1_barcode, webhook_system, customers.umkreissuche, ruestliste endpoints.
"""

from __future__ import annotations

import math
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# GS1 Tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_gs1_parse_ean13_extracts_gtin():
    from app.api.v1.endpoints.gs1_barcode import _parse_gs1
    result = _parse_gs1("4006381333931", "AUTO")
    assert result.format_erkannt == "EAN13"
    assert result.gtin == "4006381333931"
    assert result.fehler is None


@pytest.mark.unit
def test_gs1_parse_ai_128_charge_und_verfall():
    from app.api.v1.endpoints.gs1_barcode import _parse_gs1
    barcode = "(01)12345678901234(10)LOT001(17)260531"
    result = _parse_gs1(barcode, "AUTO")
    assert result.charge_nr == "LOT001"
    assert result.verfallsdatum == "2026-05-31"
    assert result.gtin == "12345678901234"


@pytest.mark.unit
def test_gs1_parse_sscc_shipping_unit():
    from app.api.v1.endpoints.gs1_barcode import _parse_gs1
    barcode = "(00)340123451234567895(01)12345678901234(10)LOT-SSCC"
    result = _parse_gs1(barcode, "AUTO")
    assert result.sscc == "340123451234567895"
    assert result.ai_felder["00"] == "340123451234567895"
    assert result.charge_nr == "LOT-SSCC"


@pytest.mark.unit
def test_gs1_verfallsdatum_konvertierung():
    from app.api.v1.endpoints.gs1_barcode import _convert_yymmdd
    assert _convert_yymmdd("260531") == "2026-05-31"
    assert _convert_yymmdd("991231") == "2099-12-31"


@pytest.mark.unit
def test_gs1_batch_parse_liste():
    from app.api.v1.endpoints.gs1_barcode import _parse_gs1, GS1ParseInput
    from fastapi.testclient import TestClient
    from fastapi import FastAPI
    from app.api.v1.endpoints.gs1_barcode import router

    app = FastAPI()
    app.include_router(router, prefix="/gs1")
    client = TestClient(app)

    payload = [
        {"barcode_string": "4006381333931", "format": "AUTO"},
        {"barcode_string": "(01)12345678901234(10)LOT001", "format": "AUTO"},
        {"barcode_string": "(01)98765432109876(17)251231", "format": "AUTO"},
    ]
    response = client.post("/gs1/batch-parse", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


# ---------------------------------------------------------------------------
# Webhook Tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_webhook_bereiche_liste():
    from fastapi import FastAPI
    from app.api.v1.endpoints.webhook_system import router, VALID_BEREICHE

    app = FastAPI()
    app.include_router(router, prefix="/webhooks")
    client = TestClient(app)

    response = client.get("/webhooks/bereiche")
    assert response.status_code == 200
    bereiche = response.json()
    assert "WIEGUNG_NEU" in bereiche


@pytest.mark.unit
def test_webhook_register_https_only():
    from fastapi import FastAPI
    from app.api.v1.endpoints.webhook_system import router

    app = FastAPI()
    app.include_router(router, prefix="/webhooks")
    client = TestClient(app, raise_server_exceptions=False)

    # HTTP URL should be rejected at validation level
    payload = {"url": "http://example.com/hook", "bereich": "WIEGUNG_NEU"}
    response = client.post("/webhooks/bereiche/WIEGUNG_NEU", json=payload)
    assert response.status_code in (422, 400, 503)


@pytest.mark.unit
def test_webhook_register_ungueltig_bereich():
    from fastapi import FastAPI
    from app.api.v1.endpoints.webhook_system import router

    app = FastAPI()
    app.include_router(router, prefix="/webhooks")
    client = TestClient(app, raise_server_exceptions=False)

    payload = {"url": "https://example.com/hook", "bereich": "UNBEKANNTER_BEREICH"}
    response = client.post("/webhooks/bereiche/UNBEKANNTER_BEREICH", json=payload)
    assert response.status_code in (422, 400)


@pytest.mark.unit
def test_webhook_register_success():
    from fastapi import FastAPI
    from app.api.v1.endpoints.webhook_system import router

    app = FastAPI()
    app.include_router(router, prefix="/webhooks")

    mock_db = MagicMock()
    # Simulate MAX(nr) query returning 0
    nr_result = MagicMock()
    nr_result.__getitem__ = lambda self, k: 1
    mock_mapping = MagicMock()
    mock_mapping.one.return_value = nr_result
    mock_execute = MagicMock()
    mock_execute.mappings.return_value = mock_mapping
    mock_db.execute.return_value = mock_execute

    from app.api.v1.endpoints.webhook_system import register_webhook, WebhookCreate
    payload = WebhookCreate(url="https://example.com/hook", bereich="WIEGUNG_NEU")
    result = register_webhook("WIEGUNG_NEU", payload, mock_db)
    assert result.id is not None
    assert result.bereich == "WIEGUNG_NEU"


@pytest.mark.unit
def test_webhook_delete():
    from fastapi import FastAPI
    from app.api.v1.endpoints.webhook_system import router

    app = FastAPI()
    app.include_router(router, prefix="/webhooks")

    mock_db = MagicMock()
    delete_result = MagicMock()
    delete_result.rowcount = 1
    mock_db.execute.return_value = delete_result

    from app.api.v1.endpoints.webhook_system import unregister_webhook
    # Should not raise
    unregister_webhook(42, mock_db)
    mock_db.commit.assert_called_once()


# ---------------------------------------------------------------------------
# Haversine / Umkreissuche Tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_umkreissuche_haversine_filter():
    """Two customers: one ~10km away, one ~300km away — only close one returned for radius=50km."""
    from app.api.v1.endpoints.customers import _haversine

    # Berlin as origin
    origin_lat, origin_lon = 52.5200, 13.4050

    # ~10km north
    close_lat, close_lon = 52.6100, 13.4050
    dist_close = _haversine(origin_lat, origin_lon, close_lat, close_lon)
    assert dist_close < 50.0

    # ~300km southwest (Frankfurt)
    far_lat, far_lon = 50.1109, 8.6821
    dist_far = _haversine(origin_lat, origin_lon, far_lat, far_lon)
    assert dist_far > 50.0


@pytest.mark.unit
def test_umkreissuche_missing_geo_graceful():
    from fastapi import FastAPI
    from app.api.v1.endpoints import customers as cmod

    app = FastAPI()
    app.include_router(cmod.router, prefix="/customers")

    mock_db = MagicMock()
    mock_db.execute.side_effect = Exception("relation does not exist")

    from app.core.database import get_db
    app.dependency_overrides[get_db] = lambda: mock_db

    client = TestClient(app)
    payload = {"breitengrad": 52.52, "laengengrad": 13.405, "radius_km": 50.0}
    response = client.post("/customers/umkreissuche", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ergebnisse"] == []
    assert "migration_hint" in data


# ---------------------------------------------------------------------------
# Rüstliste Tests
# ---------------------------------------------------------------------------

def _make_ruestliste_app():
    from fastapi import FastAPI
    from app.api.v1.endpoints import ruestliste as rmod
    app = FastAPI()
    app.include_router(rmod.router, prefix="/lager/ruestliste")
    return app


@pytest.mark.unit
def test_ruestliste_create_and_bearbeiten():
    from app.api.v1.endpoints.ruestliste import create_ruestliste, bearbeiten, RuestlisteCreate, RuestlistePosition

    mock_db = MagicMock()
    mock_db.execute.return_value = MagicMock()

    payload = RuestlisteCreate(
        auftrag_nr="AUF-2026-001",
        positionen=[RuestlistePosition(artikel_nr="ART-001", menge=5.0, lagerplatz="A-01")],
        erstellt_fuer="operator1",
        prioritaet="NORMAL",
    )
    result = create_ruestliste(payload, mock_db)
    assert result.status == "OFFEN"
    assert result.auftrag_nr == "AUF-2026-001"
    assert result.ruestlisten_nr.startswith("RL-")

    # Now simulate bearbeiten transition
    mock_row = MagicMock()
    mock_row.__getitem__ = lambda self, i: ["some-id", "OFFEN"][i]  # [0]=id, [1]=status
    mock_db.execute.return_value = mock_row
    mock_db.execute.return_value.first.return_value = mock_row

    # Patch _set_status to test it in isolation
    with patch("app.api.v1.endpoints.ruestliste._set_status", return_value={"ruestlisten_nr": result.ruestlisten_nr, "status": "IN_BEARBEITUNG"}) as mock_set:
        res = bearbeiten(result.ruestlisten_nr, mock_db)
        mock_set.assert_called_once_with(result.ruestlisten_nr, "IN_BEARBEITUNG", ["OFFEN"], mock_db)
        assert res["status"] == "IN_BEARBEITUNG"


@pytest.mark.unit
def test_ruestliste_verarbeitet():
    from app.api.v1.endpoints.ruestliste import verarbeitet

    mock_db = MagicMock()
    with patch("app.api.v1.endpoints.ruestliste._set_status", return_value={"ruestlisten_nr": "RL-20260517-0001", "status": "VERARBEITET"}) as mock_set:
        res = verarbeitet("RL-20260517-0001", mock_db)
        mock_set.assert_called_once_with("RL-20260517-0001", "VERARBEITET", ["IN_BEARBEITUNG"], mock_db, verarbeitet=True)
        assert res["status"] == "VERARBEITET"


@pytest.mark.unit
def test_ruestliste_abbrechen_von_offen():
    from app.api.v1.endpoints.ruestliste import abbrechen

    mock_db = MagicMock()
    with patch("app.api.v1.endpoints.ruestliste._set_status", return_value={"ruestlisten_nr": "RL-20260517-0002", "status": "ABGEBROCHEN"}) as mock_set:
        res = abbrechen("RL-20260517-0002", mock_db)
        mock_set.assert_called_once_with("RL-20260517-0002", "ABGEBROCHEN", ["OFFEN", "IN_BEARBEITUNG"], mock_db)
        assert res["status"] == "ABGEBROCHEN"
