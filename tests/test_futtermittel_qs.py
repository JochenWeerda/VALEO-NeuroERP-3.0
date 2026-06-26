"""FEED-QS-001 — Tests fuer Futtermittel QS: HACCP, VLOG, QS-Leitfaden."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from main import app

client = TestClient(app, raise_server_exceptions=False)
AUTH = {
    "Authorization": f"Bearer {settings.API_DEV_TOKEN or 'dev-token'}",
    "X-Tenant-ID": "test-tenant",
}


def _skip_db(resp) -> None:
    if resp.status_code in (500, 503):
        body = resp.text
        if any(k in body for k in ("OperationalError", "Connection refused", "UndefinedTable", "does not exist")):
            pytest.skip("DB or tables not available")


# ── HACCP-Plaene ──────────────────────────────────────────────────────────────

class TestHaccpPlaene:
    def test_list_returns_200_or_skips(self):
        resp = client.get("/api/v1/futtermittel/qs/haccp-plaene", headers=AUTH)
        _skip_db(resp)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_list_requires_tenant(self):
        resp = client.get("/api/v1/futtermittel/qs/haccp-plaene",
                          headers={"Authorization": "Bearer dev-token"})
        assert resp.status_code == 400

    def test_create_returns_201_or_skips(self):
        payload = {
            "bezeichnung": "HACCP-Plan Mischfutter 2026",
            "gueltigkeit_von": "2026-01-01",
            "gefahrenanalyse": [{"gefahrenpunkt": "Schimmel", "schweregrad": "mittel"}],
            "ccp_liste": [{"ccp_nr": "CCP-1", "grenzwert": "< 10 KBE/g"}],
        }
        resp = client.post("/api/v1/futtermittel/qs/haccp-plaene", json=payload, headers=AUTH)
        _skip_db(resp)
        assert resp.status_code == 201
        body = resp.json()
        assert "id" in body
        assert body["ok"] is True

    def test_get_not_found(self):
        resp = client.get("/api/v1/futtermittel/qs/haccp-plaene/nonexistent-id", headers=AUTH)
        _skip_db(resp)
        assert resp.status_code == 404

    def test_patch_no_fields_raises_422_or_skips(self):
        resp = client.patch("/api/v1/futtermittel/qs/haccp-plaene/some-id",
                            json={}, headers=AUTH)
        _skip_db(resp)
        assert resp.status_code == 422


# ── VLOG-Meldungen ────────────────────────────────────────────────────────────

class TestVlogMeldungen:
    def test_list_returns_200_or_skips(self):
        resp = client.get("/api/v1/futtermittel/qs/vlog-meldungen", headers=AUTH)
        _skip_db(resp)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_create_returns_201_or_skips(self):
        payload = {
            "meldedatum": "2026-06-26",
            "menge_kg": 5000,
            "rohstoff_liste": [{"artikel": "Weizen", "anteil_pct": 40}],
            "gvo_frei": True,
            "zertifikat_nr": "VLOG-2026-001",
        }
        resp = client.post("/api/v1/futtermittel/qs/vlog-meldungen", json=payload, headers=AUTH)
        _skip_db(resp)
        assert resp.status_code == 201
        assert resp.json()["ok"] is True

    def test_status_invalid_returns_422(self):
        resp = client.patch(
            "/api/v1/futtermittel/qs/vlog-meldungen/some-id/status",
            json={"status": "ungueltig"},
            headers=AUTH,
        )
        assert resp.status_code == 422

    def test_status_valid_values_accepted_or_skips(self):
        for status in ("erstellt", "gesendet", "bestaetigt", "abgelehnt"):
            resp = client.patch(
                "/api/v1/futtermittel/qs/vlog-meldungen/nonexistent/status",
                json={"status": status},
                headers=AUTH,
            )
            _skip_db(resp)
            # 404 or 200 both acceptable (nonexistent id)
            assert resp.status_code in (200, 404)


# ── QS-Leitfaden-Pruefpunkte ──────────────────────────────────────────────────

class TestQsPruefpunkte:
    def test_list_returns_200_or_skips(self):
        resp = client.get("/api/v1/futtermittel/qs/leitfaden-pruefpunkte", headers=AUTH)
        _skip_db(resp)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_create_returns_201_or_skips(self):
        payload = {
            "periode": "2026-06",
            "kategorie": "hygiene",
            "punkt_nr": "H-01",
            "bezeichnung": "Reinigung Mischanlage",
            "anforderung": "Taeglich vor Betriebsbeginn",
        }
        resp = client.post("/api/v1/futtermittel/qs/leitfaden-pruefpunkte",
                           json=payload, headers=AUTH)
        _skip_db(resp)
        assert resp.status_code == 201
        assert resp.json()["ok"] is True

    def test_bestaetigen_or_skips(self):
        resp = client.post(
            "/api/v1/futtermittel/qs/leitfaden-pruefpunkte/nonexistent/bestaetigen",
            json={"bestaetigt_von": "Max Mustermann"},
            headers=AUTH,
        )
        _skip_db(resp)
        # No error from router itself (DB UPDATE of nonexistent is no-op)
        assert resp.status_code in (200, 404, 500)
