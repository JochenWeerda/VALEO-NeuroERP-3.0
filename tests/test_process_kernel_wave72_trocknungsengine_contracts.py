"""
Wave 72 — Gap 003: Trocknungsengine Core-Contract API
Versionierte, GoBD-konforme Trocknungsabrechnung mit SHA-256 Audit-Hash.
Tests: stateless Preview-Endpoint + Branchenrichtwerte-Defaults.
"""
from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import agrar_settlements


@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    app.include_router(agrar_settlements.router)
    return TestClient(app)


# ---------------------------------------------------------------------------
# GET /trocknungs-regelsets/defaults
# ---------------------------------------------------------------------------

def test_defaults_returns_five_fruchtarten(client: TestClient):
    resp = client.get("/trocknungs-regelsets/defaults")
    assert resp.status_code == 200
    body = resp.json()
    assert set(body["regelsets"].keys()) >= {"WW", "SG", "RA", "KM", "ZR"}


def test_defaults_schema_version_1(client: TestClient):
    resp = client.get("/trocknungs-regelsets/defaults")
    assert resp.json()["schema_version"] == 1


def test_defaults_ww_has_expected_threshold(client: TestClient):
    resp = client.get("/trocknungs-regelsets/defaults")
    ww = resp.json()["regelsets"]["WW"]
    # WW Basisfeuchte nach Branchenrichtwert: 14.5 %
    assert ww["start_threshold_pct"] == pytest.approx(14.5, abs=0.5)


def test_defaults_each_fruchtart_has_schwund_faktor(client: TestClient):
    resp = client.get("/trocknungs-regelsets/defaults")
    for code, params in resp.json()["regelsets"].items():
        assert "schwund_faktor" in params, f"{code} fehlt schwund_faktor"
        assert params["schwund_faktor"] > 0


def test_defaults_quelle_contains_dlg(client: TestClient):
    body = client.get("/trocknungs-regelsets/defaults").json()
    assert "DLG" in body["quelle"]


# ---------------------------------------------------------------------------
# POST /trocknungs-abrechnung/preview  — Normalfälle
# ---------------------------------------------------------------------------

# WW: Eingangsfeuchte 18 % > start_threshold (14.5) → Abzug erwartet
VALID_WW_REQUEST = {
    "crop_code": "WW",
    "brutto_gewicht_kg": 20000.0,
    "eingangs_feuchte_pct": 18.0,
    "ziel_feuchte_pct": 14.0,
    "methode": "FAKTOR_STUFUNG",
}


def test_preview_ww_returns_200(client: TestClient):
    resp = client.post("/trocknungs-abrechnung/preview", json=VALID_WW_REQUEST)
    assert resp.status_code == 200


def test_preview_ww_contains_audit_hash(client: TestClient):
    body = client.post("/trocknungs-abrechnung/preview", json=VALID_WW_REQUEST).json()
    assert "audit_hash" in body
    assert len(body["audit_hash"]) == 64  # SHA-256 hex


def test_preview_ww_nettogewicht_less_than_brutto(client: TestClient):
    body = client.post("/trocknungs-abrechnung/preview", json=VALID_WW_REQUEST).json()
    # netto_gewicht_kg serialized as string (Decimal)
    assert float(body["netto_gewicht_kg"]) < VALID_WW_REQUEST["brutto_gewicht_kg"]


def test_preview_ww_positionen_not_empty(client: TestClient):
    body = client.post("/trocknungs-abrechnung/preview", json=VALID_WW_REQUEST).json()
    assert len(body["positionen"]) >= 1


def test_preview_ww_schema_version_1(client: TestClient):
    body = client.post("/trocknungs-abrechnung/preview", json=VALID_WW_REQUEST).json()
    assert body["schema_version"] == 1


def test_preview_ww_validierung_ok(client: TestClient):
    body = client.post("/trocknungs-abrechnung/preview", json=VALID_WW_REQUEST).json()
    assert "validierung" in body
    assert body["validierung"]["valid"] is True


def test_preview_deterministic_same_input_same_hash(client: TestClient):
    h1 = client.post("/trocknungs-abrechnung/preview", json=VALID_WW_REQUEST).json()["audit_hash"]
    h2 = client.post("/trocknungs-abrechnung/preview", json=VALID_WW_REQUEST).json()["audit_hash"]
    assert h1 == h2


def test_preview_different_feuchte_different_hash(client: TestClient):
    req_a = {**VALID_WW_REQUEST, "eingangs_feuchte_pct": 18.0}
    req_b = {**VALID_WW_REQUEST, "eingangs_feuchte_pct": 20.0}
    h_a = client.post("/trocknungs-abrechnung/preview", json=req_a).json()["audit_hash"]
    h_b = client.post("/trocknungs-abrechnung/preview", json=req_b).json()["audit_hash"]
    assert h_a != h_b


def test_preview_higher_feuchte_yields_higher_abzug(client: TestClient):
    req_lo = {**VALID_WW_REQUEST, "eingangs_feuchte_pct": 16.0}
    req_hi = {**VALID_WW_REQUEST, "eingangs_feuchte_pct": 22.0}
    body_lo = client.post("/trocknungs-abrechnung/preview", json=req_lo).json()
    body_hi = client.post("/trocknungs-abrechnung/preview", json=req_hi).json()
    assert float(body_hi["netto_gewicht_kg"]) < float(body_lo["netto_gewicht_kg"])


def test_preview_feuchte_gleich_ziel_kein_abzug(client: TestClient):
    """Eingangsfeuchte = Zielfeuchte → feuchte_delta = 0 → kein Schwund."""
    req = {**VALID_WW_REQUEST, "eingangs_feuchte_pct": 14.0}  # = Zielfeuchte
    body = client.post("/trocknungs-abrechnung/preview", json=req).json()
    assert float(body["gesamt_abzug_kg"]) == pytest.approx(0.0, abs=0.01)


def test_preview_raps_uses_own_defaults(client: TestClient):
    req = {
        "crop_code": "RA",
        "brutto_gewicht_kg": 10000.0,
        "eingangs_feuchte_pct": 11.0,
        "ziel_feuchte_pct": 9.0,
        "methode": "FAKTOR_STUFUNG",
    }
    resp = client.post("/trocknungs-abrechnung/preview", json=req)
    assert resp.status_code == 200
    body = resp.json()
    assert body["crop_code"] == "RA"


def test_preview_custom_kosten_produce_kosten_position(client: TestClient):
    req = {
        **VALID_WW_REQUEST,
        "trocknungskosten_eur_per_pct_per_t": 2.50,
    }
    body = client.post("/trocknungs-abrechnung/preview", json=req).json()
    arten = [p["art"] for p in body["positionen"]]
    assert "TROCKNUNGSKOSTEN" in arten


# ---------------------------------------------------------------------------
# POST /trocknungs-abrechnung/preview  — Validierungsfehler
# ---------------------------------------------------------------------------

def test_preview_rejects_unknown_methode(client: TestClient):
    req = {**VALID_WW_REQUEST, "methode": "UNBEKANNTE_METHODE"}
    resp = client.post("/trocknungs-abrechnung/preview", json=req)
    assert resp.status_code == 422


def test_preview_rejects_zero_gewicht(client: TestClient):
    req = {**VALID_WW_REQUEST, "brutto_gewicht_kg": 0}
    resp = client.post("/trocknungs-abrechnung/preview", json=req)
    assert resp.status_code == 422


def test_preview_rejects_feuchte_over_100(client: TestClient):
    req = {**VALID_WW_REQUEST, "eingangs_feuchte_pct": 101.0}
    resp = client.post("/trocknungs-abrechnung/preview", json=req)
    assert resp.status_code == 422


def test_preview_ww_audit_entry_contains_crop_code(client: TestClient):
    body = client.post("/trocknungs-abrechnung/preview", json=VALID_WW_REQUEST).json()
    assert body["crop_code"] == "WW"
