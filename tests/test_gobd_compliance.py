"""
GoBD Compliance Tests
Tests für revisionssichere Buchhaltung, Hash-Chain, Audit-Trail
"""

from fastapi.testclient import TestClient
from main import app
import pytest

_client = TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def client():
    return _client


class TestGoBDStatus:
    """Tests für GoBD Status-Endpunkt"""

    def test_gobd_status(self, client):
        """Test: GoBD Status abrufen"""
        response = client.get("/api/gobd/status", headers={"Authorization": "Bearer dev-token"})
        assert response.status_code == 200
        data = response.json()
        assert "gesamt_score" in data
        assert "ergebnisse" in data
        assert isinstance(data["ergebnisse"], list)

    def test_gobd_status_alle_bereiche(self, client):
        """Test: Alle GoBD-Bereiche vorhanden"""
        response = client.get("/api/gobd/status", headers={"Authorization": "Bearer dev-token"})
        assert response.status_code == 200
        ergebnisse = response.json()["ergebnisse"]
        bereiche = {e["bereich"] for e in ergebnisse}
        
        expected_bereiche = {
            "ordnungsgemaessigkeit",
            "vollstaendigkeit",
            "richtigkeit",
            "zeitnahme",
            "unveraenderlichkeit",
            "nachvollziehbarkeit",
            "aufbewahrung"
        }
        assert expected_bereiche.issubset(bereiche)


class TestHashChain:
    """Tests für Hash-Chain Validierung"""

    def test_verify_hash_chain(self, client):
        """Test: Hash-Chain verifizieren"""
        response = client.post(
            "/api/gobd/hash-chain/verify",
            headers={"Authorization": "Bearer dev-token"},
            json={
                "von_datum": "2026-01-01",
                "bis_datum": "2026-01-31"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "gueltig" in data
        assert "fehlerhafte_buchungen" in data
        assert data["gueltig"] is True or data["gueltig"] is False

    def test_letzter_hash(self, client):
        """Test: Letzten Hash abrufen"""
        response = client.get("/api/gobd/hash-chain/letzter", headers={"Authorization": "Bearer dev-token"})
        assert response.status_code == 200
        data = response.json()
        assert "letzter_hash" in data
        assert "letzte_sequenznummer" in data


class TestBelegnummern:
    """Tests für Belegnummern-Kontrolle"""

    def test_belegnummern_kontrolle(self, client):
        """Test: Belegnummern prüfen"""
        response = client.get(
            "/api/gobd/belegnummern?belegart=RE&jahr=2026",
            headers={"Authorization": "Bearer dev-token"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "gesamt_belege" in data
        assert "luecken" in data
        assert "status" in data


class TestVerfahrensdokumentation:
    """Tests für Verfahrensdokumentation"""

    def test_verfahrensdokumentation_json(self, client):
        """Test: Verfahrensdokumentation als JSON"""
        response = client.get(
            "/api/gobd/verfahrensdokumentation?format=json",
            headers={"Authorization": "Bearer dev-token"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "software_name" in data
        assert "aufbewahrungsfristen" in data

    def test_verfahrensdokumentation_pdf(self, client):
        """Test: Verfahrensdokumentation als PDF"""
        response = client.get(
            "/api/gobd/verfahrensdokumentation?format=pdf",
            headers={"Authorization": "Bearer dev-token"}
        )
        assert response.status_code == 200


class TestAufbewahrung:
    """Tests für Aufbewahrungsfristen"""

    def test_aufbewahrungs_fristen(self, client):
        """Test: Aufbewahrungsfristen abrufen"""
        response = client.get("/api/gobd/aufbewahrung", headers={"Authorization": "Bearer dev-token"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for item in data:
            assert "dokument_typ" in item
            assert "ablauf_datum" in item
            assert "status" in item


class TestBuchungslog:
    """Tests für revisionssicheres Journal"""

    def test_buchungslog(self, client):
        """Test: Buchungslog abrufen"""
        response = client.get(
            "/api/gobd/journal?von_datum=2026-01-01&bis_datum=2026-01-31",
            headers={"Authorization": "Bearer dev-token"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestNachvollziehbarkeit:
    """Tests für Nachvollziehbarkeit"""

    def test_nachvollziehbarkeit(self, client):
        """Test: Nachvollziehbarkeit prüfen"""
        response = client.get(
            "/api/gobd/nachvollziehbarkeit?von_datum=2026-01-01&bis_datum=2026-01-31",
            headers={"Authorization": "Bearer dev-token"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "anzahl_belege" in data
        assert "anzahl_benutzer" in data
        assert "anzahl_aktionen" in data
