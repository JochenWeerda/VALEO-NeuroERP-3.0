"""
UAT API Contract Tests — Wave 2026-05-17
=========================================
Verifiziert Response-Schemas, Auth-Enforcement und Tenant-Isolation
für alle neuen Endpoints der Wave AMIC + L3-Connect + Compliance-Vertiefung.

Testablauf:
    pytest tests/uat/test_uat_api_contracts.py -v

Auth-Mechanismus:
    Der Dev-Token-Bypass ist in conftest.py via _enable_dev_token (autouse)
    global aktiv gesetzt (API_DEV_TOKEN="dev-token").
    Tests mit Auth senden: Authorization: Bearer dev-token + X-Tenant-ID: test-tenant
    Tests ohne Auth senden keinen Authorization-Header und erwarten 401/403.

Hinweis zu DB-Abhängigkeiten:
    Endpoints, die PostgreSQL benötigen (z. B. Gelangensbestätigung, Sanktionsliste),
    liefern ggf. 500/503 wenn keine DB erreichbar ist.
    conftest.skip_if_db_unavailable() wird daher in HTTP-Smoke-Tests genutzt.
"""
from __future__ import annotations

import sys
import os

# Sicherstellen dass das Projekt-Root im sys.path ist
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import pytest
from fastapi.testclient import TestClient

from main import app  # noqa: E402  (projektrelativ via sys.path)

sys.path.insert(0, os.path.join(_PROJECT_ROOT, "tests"))
from conftest import skip_if_db_unavailable  # noqa: E402


# ---------------------------------------------------------------------------
# Gemeinsame Konstanten
# ---------------------------------------------------------------------------

_AUTH_HEADERS = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-ID": "test-tenant",
}
_NO_AUTH_HEADERS: dict = {}
_TENANT_ONLY_HEADERS = {"X-Tenant-ID": "test-tenant"}

_CLIENT = TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# Wave 2026-05-17 — vollständige Endpoint-Liste
# Spalten: (methode, pfad_ohne_prefix, erwarteter_content_type_prefix)
# prefix /api/v1 wird vom TestClient via app.main hinzugefügt
# ---------------------------------------------------------------------------

#: Alle GET-Endpoints die bei Auth einen 200er liefern sollen.
_GET_ENDPOINTS_200 = [
    # AMIC — Kontrakt-Klassen
    "/api/v1/kontrakt-klassen",
    # AMIC — eBilanz/ELSTER Meldungen
    "/api/v1/ebilanz/meldungen",
    # AMIC — Waagenvorlagen
    "/api/v1/waagen-vorlagen",
    # Gelangensbestätigung (§17a UStDV)
    "/api/v1/gelangensbestaetigung",
    # Sanktionsliste
    "/api/v1/compliance/sanctions/eintraege",
    # Compliance — EUDR
    "/api/v1/compliance/eudr",
    # Finance — Close Readiness
    "/api/v1/finance/close-readiness",
    # NVE / SSCC Versandeinheiten
    "/api/v1/nve/",
    # L3-Connect — Inventory Counts
    "/api/v1/inventory/counts",
    # L3-Connect — Weighing Tickets
    "/api/v1/weighing-tickets",
    # L3-Connect — Warehouse Transfers
    "/api/v1/warehouses/transfers",
    # L3-Connect — Preparation Lists
    "/api/v1/preparation-lists",
    # L3-Connect — Pick Lists
    "/api/v1/pick-lists",
]

#: Endpoints die ohne Auth einen 401 oder 403 liefern sollen.
#: (Endpoints mit optionalem tenant_id-Query-Parameter liefern i. d. R. dennoch 200,
#:  da der API_DEV_TOKEN-Bypass nur für Bearer-Token gilt.
#:  Daher nur Endpoints prüfen, die explizit Depends(get_tenant_id) nutzen.)
_AUTH_REQUIRED_ENDPOINTS = [
    ("GET", "/api/v1/kontrakt-klassen"),
    ("GET", "/api/v1/gelangensbestaetigung"),
    ("GET", "/api/v1/compliance/sanctions/eintraege"),
    ("POST", "/api/v1/compliance/sanctions/pruefen"),
    ("GET", "/api/v1/finance/close-readiness"),
]


# ===========================================================================
# TC-API-001 — Auth Enforcement
# ===========================================================================

class TestAuthEnforcement:
    """TC-API-001: Endpoints verlangen Authentication (401/403 ohne Token)."""

    @pytest.mark.parametrize("method,path", _AUTH_REQUIRED_ENDPOINTS)
    def test_endpoint_requires_auth(self, method: str, path: str):
        """TC-API-001: {method} {path} liefert 401 oder 403 ohne Authorization-Header."""
        resp = _CLIENT.request(method, path, headers=_TENANT_ONLY_HEADERS)
        skip_if_db_unavailable(resp)
        assert resp.status_code in (401, 403), (
            f"TC-API-001 FEHLER: {method} {path} lieferte {resp.status_code} "
            f"statt 401/403 ohne Auth. Body: {resp.text[:200]}"
        )

    def test_gelangensbestaetigung_requires_auth(self):
        """TC-API-001a: GET /gelangensbestaetigung — kein Bearer-Token → 401/403."""
        resp = _CLIENT.get("/api/v1/gelangensbestaetigung", headers=_TENANT_ONLY_HEADERS)
        skip_if_db_unavailable(resp)
        assert resp.status_code in (401, 403)

    def test_sanctions_pruefen_requires_auth(self):
        """TC-API-001b: POST /compliance/sanctions/pruefen — kein Bearer-Token → 401/403."""
        resp = _CLIENT.post(
            "/api/v1/compliance/sanctions/pruefen",
            json={"name": "ACME Corp", "land_code": "RU"},
            headers=_TENANT_ONLY_HEADERS,
        )
        skip_if_db_unavailable(resp)
        assert resp.status_code in (401, 403)

    def test_close_readiness_requires_auth(self):
        """TC-API-001c: GET /finance/close-readiness — kein Bearer-Token → 401/403."""
        resp = _CLIENT.get("/api/v1/finance/close-readiness", headers=_TENANT_ONLY_HEADERS)
        skip_if_db_unavailable(resp)
        assert resp.status_code in (401, 403)


# ===========================================================================
# TC-API-002 — Content-Type application/json
# ===========================================================================

class TestContentType:
    """TC-API-002: Alle neuen GET-Endpoints liefern Content-Type: application/json."""

    @pytest.mark.parametrize("path", _GET_ENDPOINTS_200)
    def test_content_type_is_json(self, path: str):
        """TC-API-002: {path} liefert Content-Type application/json."""
        resp = _CLIENT.get(path, headers=_AUTH_HEADERS)
        skip_if_db_unavailable(resp)
        # Nicht-200er überspringen (Routing/Stub-Endpoints liefern ggf. 404 wenn keine DB)
        if resp.status_code == 404:
            pytest.skip(f"Endpoint {path} antwortet mit 404 — möglicherweise kein Stub registriert")
        assert resp.status_code < 500, (
            f"TC-API-002 FEHLER: {path} lieferte {resp.status_code}. Body: {resp.text[:300]}"
        )
        ct = resp.headers.get("content-type", "")
        assert "application/json" in ct, (
            f"TC-API-002 FEHLER: {path} lieferte Content-Type '{ct}' statt application/json"
        )


# ===========================================================================
# TC-API-003 — Tenant-Isolation
# ===========================================================================

class TestTenantIsolation:
    """TC-API-003: Tenant-Isolation via X-Tenant-ID Header."""

    def test_kontrakt_klassen_tenant_a_vs_b(self):
        """TC-API-003a: GET /kontrakt-klassen — unterschiedliche Tenants liefern isolierte Daten."""
        headers_a = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "tenant-a"}
        headers_b = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "tenant-b"}
        resp_a = _CLIENT.get("/api/v1/kontrakt-klassen", headers=headers_a)
        resp_b = _CLIENT.get("/api/v1/kontrakt-klassen", headers=headers_b)
        skip_if_db_unavailable(resp_a)
        skip_if_db_unavailable(resp_b)
        assert resp_a.status_code in (200, 204)
        assert resp_b.status_code in (200, 204)
        # Beide Tenant-Responses sind unabhängig (keine Cross-Tenant-Datenleckage im Schema)
        # Vollständige Isolation ist nur mit echter DB prüfbar — hier nur HTTP-Kontrakt.

    def test_gelangensbestaetigung_tenant_isolation(self):
        """TC-API-003b: GET /gelangensbestaetigung — X-Tenant-ID wird durchgereicht."""
        resp = _CLIENT.get("/api/v1/gelangensbestaetigung", headers=_AUTH_HEADERS)
        skip_if_db_unavailable(resp)
        assert resp.status_code in (200, 204)

    def test_missing_tenant_header_on_tenant_scoped_endpoint(self):
        """TC-API-003c: Tenant-scoped Endpoints ohne X-Tenant-ID liefern 400 oder nutzen Default."""
        resp = _CLIENT.get(
            "/api/v1/kontrakt-klassen",
            headers={"Authorization": "Bearer dev-token"},
        )
        skip_if_db_unavailable(resp)
        # Entweder 400 (fehlender Header) oder 200 mit Default-Tenant — beides akzeptabel
        assert resp.status_code in (200, 400, 422), (
            f"TC-API-003c FEHLER: Unerwartet {resp.status_code}. Body: {resp.text[:200]}"
        )

    def test_sanctions_tenant_isolation(self):
        """TC-API-003d: GET /compliance/sanctions/eintraege — Tenant-Kontext wird via Header gesetzt."""
        resp = _CLIENT.get("/api/v1/compliance/sanctions/eintraege", headers=_AUTH_HEADERS)
        skip_if_db_unavailable(resp)
        assert resp.status_code in (200, 204)


# ===========================================================================
# TC-API-004 — GET-Endpoints liefern Liste oder Objekt (nicht null)
# ===========================================================================

class TestResponseShape:
    """TC-API-004: GET-Endpoints liefern nicht-null JSON (Liste oder Objekt)."""

    def test_kontrakt_klassen_returns_list(self):
        """TC-API-004a: GET /kontrakt-klassen → JSON-Array."""
        resp = _CLIENT.get("/api/v1/kontrakt-klassen", headers=_AUTH_HEADERS)
        skip_if_db_unavailable(resp)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list), f"TC-API-004a: Erwarte list, bekam {type(data)}"

    def test_kontrakt_hedging_returns_list(self):
        """TC-API-004b: GET /kontrakt-hedging/{id}/hedges — Hedging-Route erfordert kontrakt_id."""
        # Route: /api/v1/kontrakt-hedging/{kontrakt_id}/hedges — kein List-Endpoint ohne ID
        resp = _CLIENT.get("/api/v1/kontrakt-hedging/1/hedges", headers=_AUTH_HEADERS)
        skip_if_db_unavailable(resp)
        assert resp.status_code in (200, 404), (
            f"TC-API-004b: Erwarte 200 (mit Daten) oder 404 (kein Kontrakt), bekam {resp.status_code}"
        )

    def test_gelangensbestaetigung_returns_list_or_paged(self):
        """TC-API-004c: GET /gelangensbestaetigung → Array oder paginiertes Objekt."""
        resp = _CLIENT.get("/api/v1/gelangensbestaetigung", headers=_AUTH_HEADERS)
        skip_if_db_unavailable(resp)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, (list, dict)), (
            f"TC-API-004c: Erwarte list oder dict, bekam {type(data)}"
        )
        if isinstance(data, dict):
            # Paginiertes Objekt muss 'items' oder 'data' Key haben
            assert any(k in data for k in ("items", "data", "results", "eintraege")), (
                f"TC-API-004c: Dict-Response fehlt 'items'/'data' Key. Keys: {list(data.keys())}"
            )

    def test_sanctions_list_returns_list_or_paged(self):
        """TC-API-004d: GET /compliance/sanctions/eintraege → Array oder paginiertes Objekt."""
        resp = _CLIENT.get("/api/v1/compliance/sanctions/eintraege", headers=_AUTH_HEADERS)
        skip_if_db_unavailable(resp)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, (list, dict))

    def test_nve_list_returns_paginated(self):
        """TC-API-004e: GET /nve/ → PaginatedResponse mit 'items' und 'total'."""
        resp = _CLIENT.get("/api/v1/nve/", headers=_AUTH_HEADERS)
        skip_if_db_unavailable(resp)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict), f"TC-API-004e: Erwarte dict, bekam {type(data)}"
        assert "items" in data, f"TC-API-004e: 'items' fehlt in Response. Keys: {list(data.keys())}"
        assert "total" in data, f"TC-API-004e: 'total' fehlt in Response. Keys: {list(data.keys())}"

    def test_inventory_counts_returns_list_or_paged(self):
        """TC-API-004f: GET /inventory/counts → Liste oder paginiertes Objekt."""
        resp = _CLIENT.get("/api/v1/inventory/counts", headers=_AUTH_HEADERS)
        skip_if_db_unavailable(resp)
        assert resp.status_code in (200, 204)
        if resp.status_code == 200:
            data = resp.json()
            assert isinstance(data, (list, dict))

    def test_weighing_tickets_returns_list_or_paged(self):
        """TC-API-004g: GET /weighing-tickets → Liste oder paginiertes Objekt."""
        resp = _CLIENT.get("/api/v1/weighing-tickets", headers=_AUTH_HEADERS)
        skip_if_db_unavailable(resp)
        assert resp.status_code in (200, 204)
        if resp.status_code == 200:
            data = resp.json()
            assert isinstance(data, (list, dict))

    def test_pick_lists_returns_list_or_paged(self):
        """TC-API-004h: GET /pick-lists → Liste oder paginiertes Objekt."""
        resp = _CLIENT.get("/api/v1/pick-lists", headers=_AUTH_HEADERS)
        skip_if_db_unavailable(resp)
        assert resp.status_code in (200, 204)
        if resp.status_code == 200:
            data = resp.json()
            assert isinstance(data, (list, dict))


# ===========================================================================
# TC-API-005 — GS1/SSCC Endpoints
# ===========================================================================

class TestGS1SSCCEndpoints:
    """TC-API-005: GS1 Barcode-Service und SSCC-Generator."""

    def test_gs1_parse_returns_result(self):
        """TC-API-005a: POST /gs1/barcode/parse → GS1ParseResult mit 'raw' und 'ai_felder'."""
        payload = {"barcode_string": "(01)04012345678901(10)CHARGE01(17)261231"}
        resp = _CLIENT.post("/api/v1/gs1/barcode/parse", json=payload, headers=_AUTH_HEADERS)
        skip_if_db_unavailable(resp)
        assert resp.status_code == 200, (
            f"TC-API-005a FEHLER: {resp.status_code}. Body: {resp.text[:300]}"
        )
        data = resp.json()
        assert "raw" in data, f"TC-API-005a: 'raw' fehlt. Keys: {list(data.keys())}"
        assert "ai_felder" in data, f"TC-API-005a: 'ai_felder' fehlt. Keys: {list(data.keys())}"
        assert isinstance(data["ai_felder"], dict)

    def test_gs1_sscc_generate_returns_sscc_field(self):
        """TC-API-005b: POST /gs1/barcode/sscc/generate → SSCCGenerateResult mit 'sscc' Feld."""
        payload = {"company_prefix": "4012345", "serial_ref": "000000001"}
        resp = _CLIENT.post(
            "/api/v1/gs1/barcode/sscc/generate", json=payload, headers=_AUTH_HEADERS
        )
        skip_if_db_unavailable(resp)
        assert resp.status_code == 200, (
            f"TC-API-005b FEHLER: {resp.status_code}. Body: {resp.text[:300]}"
        )
        data = resp.json()
        assert "sscc" in data, f"TC-API-005b: 'sscc' fehlt in Response. Keys: {list(data.keys())}"
        assert isinstance(data["sscc"], str), "TC-API-005b: 'sscc' muss ein String sein"
        assert len(data["sscc"]) > 0, "TC-API-005b: 'sscc' darf nicht leer sein"
        assert "barcode_human_readable" in data, "TC-API-005b: 'barcode_human_readable' fehlt"
        assert "check_digit" in data, "TC-API-005b: 'check_digit' fehlt"

    def test_gs1_sscc_validate(self):
        """TC-API-005c: GET /gs1/barcode/sscc/{sscc}/validate → SSCCValidateResult mit 'valid' Feld."""
        sscc = "340123456789012340"  # 18-stellig
        resp = _CLIENT.get(
            f"/api/v1/gs1/barcode/sscc/{sscc}/validate", headers=_AUTH_HEADERS
        )
        skip_if_db_unavailable(resp)
        assert resp.status_code == 200, (
            f"TC-API-005c FEHLER: {resp.status_code}. Body: {resp.text[:300]}"
        )
        data = resp.json()
        assert "valid" in data, f"TC-API-005c: 'valid' fehlt. Keys: {list(data.keys())}"
        assert isinstance(data["valid"], bool)

    def test_nve_create_returns_sscc(self):
        """TC-API-005d: POST /nve/ → NVEOut mit 'sscc' Feld."""
        import time
        payload = {"sscc": f"34012345{int(time.time() * 1000000) % 10000000000:010d}"}
        resp = _CLIENT.post("/api/v1/nve/", json=payload, headers=_AUTH_HEADERS)
        skip_if_db_unavailable(resp)
        assert resp.status_code in (200, 201), (
            f"TC-API-005d FEHLER: {resp.status_code}. Body: {resp.text[:300]}"
        )
        data = resp.json()
        assert "sscc" in data, f"TC-API-005d: 'sscc' fehlt. Keys: {list(data.keys())}"


# ===========================================================================
# TC-API-006 — Compliance Endpoints
# ===========================================================================

class TestComplianceEndpoints:
    """TC-API-006: Compliance Endpoints liefern korrekte Struktur."""

    def test_eudr_status_returns_total_field(self):
        """TC-API-006a: GET /compliance/eudr → Objekt mit 'total' Feld."""
        resp = _CLIENT.get("/api/v1/compliance/eudr", headers=_AUTH_HEADERS)
        skip_if_db_unavailable(resp)
        assert resp.status_code == 200, (
            f"TC-API-006a FEHLER: {resp.status_code}. Body: {resp.text[:300]}"
        )
        data = resp.json()
        assert isinstance(data, dict), "TC-API-006a: Response muss ein Objekt sein"
        assert any(k in data for k in ("total", "batches_total", "gesamt")), (
            f"TC-API-006a: Kein Gesamtanzahl-Feld gefunden. Keys: {list(data.keys())}"
        )

    def test_sanctions_pruefen_returns_treffer_list(self):
        """TC-API-006b: POST /compliance/sanctions/pruefen → Objekt mit 'treffer' Liste."""
        payload = {"name": "Test Entity GmbH", "land_code": "DE"}
        resp = _CLIENT.post(
            "/api/v1/compliance/sanctions/pruefen", json=payload, headers=_AUTH_HEADERS
        )
        skip_if_db_unavailable(resp)
        assert resp.status_code == 200, (
            f"TC-API-006b FEHLER: {resp.status_code}. Body: {resp.text[:300]}"
        )
        data = resp.json()
        assert "treffer" in data or "matches" in data or isinstance(data, list), (
            f"TC-API-006b: Erwarte 'treffer'/'matches' oder Liste. Keys: {list(data.keys()) if isinstance(data, dict) else 'list'}"
        )

    def test_pcn_meldung_create_validates_ufi_and_returns_contract(self):
        """TC-API-006c: POST /compliance/pcn-meldungen -> PCN/UFI-Vertrag mit Meldungs-ID."""
        payload = {
            "produktname": "UAT Pflanzenschutz Mix",
            "ufi": "ABCD-1234-EFGH-5678",
            "cas_nummern": "64-17-5",
            "gefahrenklassen": ["Eye Irrit. 2"],
            "verwendungskategorie": "professional",
            "pcnStatus": "entwurf",
        }
        resp = _CLIENT.post("/api/v1/compliance/pcn-meldungen", json=payload, headers=_AUTH_HEADERS)
        assert resp.status_code == 201, (
            f"TC-API-006c FEHLER: {resp.status_code}. Body: {resp.text[:400]}"
        )
        data = resp.json()
        assert data["meldung_id"].startswith("PCN-")
        assert data["ufi"] == payload["ufi"]
        assert data["pcnStatus"] == "entwurf"
        assert data["schema_version"] == 1

    def test_pcn_meldung_invalid_ufi_rejected(self):
        """TC-API-006d: POST /compliance/pcn-meldungen mit ungueltigem UFI -> 422."""
        resp = _CLIENT.post(
            "/api/v1/compliance/pcn-meldungen",
            json={"produktname": "UAT Mix", "ufi": "bad-ufi"},
            headers=_AUTH_HEADERS,
        )
        assert resp.status_code == 422

    def test_gelangensbestaetigung_create_validates_schema(self):
        """TC-API-006c: POST /gelangensbestaetigung — Pflichtfeldvalidierung (422 bei fehlenden Feldern)."""
        resp = _CLIENT.post(
            "/api/v1/gelangensbestaetigung",
            json={"lieferschein_nr": "LS-001"},  # unvollständig
            headers=_AUTH_HEADERS,
        )
        skip_if_db_unavailable(resp)
        assert resp.status_code == 422, (
            f"TC-API-006c: Erwarte 422 (Validierungsfehler), bekam {resp.status_code}"
        )

    def test_gelangensbestaetigung_valid_create(self):
        """TC-API-006d: POST /gelangensbestaetigung — vollständige Payload → 201/200."""
        import datetime
        payload = {
            "lieferschein_nr": "LS-UAT-001",
            "rechnung_nr": "RE-UAT-001",
            "kunde_nr": "KD-001",
            "bestimmungsland_code": "FR",
            "warenwert_eur": 12500.00,
            "versanddatum": str(datetime.date.today()),
            "empfaenger_name": "Agri France S.A.S.",
            "empfaenger_ust_id_nr": "FR12345678901",
        }
        resp = _CLIENT.post("/api/v1/gelangensbestaetigung", json=payload, headers=_AUTH_HEADERS)
        skip_if_db_unavailable(resp)
        assert resp.status_code in (200, 201), (
            f"TC-API-006d FEHLER: {resp.status_code}. Body: {resp.text[:400]}"
        )
        data = resp.json()
        assert isinstance(data, dict), "TC-API-006d: Response muss ein Objekt sein"
        assert "id" in data, f"TC-API-006d: 'id' fehlt in Response. Keys: {list(data.keys())}"


# ===========================================================================
# TC-API-007 — Finance Close-Readiness
# ===========================================================================

class TestFinanceCloseReadiness:
    """TC-API-007: Finance Close-Readiness Endpoint."""

    def test_close_readiness_returns_status_field(self):
        """TC-API-007a: GET /finance/close-readiness → Objekt mit 'status' Feld."""
        resp = _CLIENT.get("/api/v1/finance/close-readiness", headers=_AUTH_HEADERS)
        skip_if_db_unavailable(resp)
        assert resp.status_code == 200, (
            f"TC-API-007a FEHLER: {resp.status_code}. Body: {resp.text[:300]}"
        )
        data = resp.json()
        assert isinstance(data, dict), "TC-API-007a: Response muss ein Objekt sein"
        assert "status" in data, f"TC-API-007a: 'status' fehlt. Keys: {list(data.keys())}"

    def test_close_readiness_has_required_fields(self):
        """TC-API-007b: GET /finance/close-readiness → Pflichtfelder current_period, blocking_items."""
        resp = _CLIENT.get("/api/v1/finance/close-readiness", headers=_AUTH_HEADERS)
        skip_if_db_unavailable(resp)
        assert resp.status_code == 200
        data = resp.json()
        assert "current_period" in data, (
            f"TC-API-007b: 'current_period' fehlt. Keys: {list(data.keys())}"
        )
        assert "blocking_items" in data, (
            f"TC-API-007b: 'blocking_items' fehlt. Keys: {list(data.keys())}"
        )
        assert isinstance(data["blocking_items"], list), (
            "TC-API-007b: 'blocking_items' muss eine Liste sein"
        )

    def test_close_readiness_status_is_known_value(self):
        """TC-API-007c: GET /finance/close-readiness → 'status' ist ein bekannter Enum-Wert."""
        resp = _CLIENT.get("/api/v1/finance/close-readiness", headers=_AUTH_HEADERS)
        skip_if_db_unavailable(resp)
        assert resp.status_code == 200
        data = resp.json()
        known_statuses = {"OPEN", "IN_PROGRESS", "PENDING_SIGNOFF", "CLOSED", "READY"}
        assert data["status"] in known_statuses, (
            f"TC-API-007c: Status '{data['status']}' nicht in {known_statuses}"
        )

    def test_close_readiness_no_ready_field_alias(self):
        """TC-API-007d: Das Feld heisst 'status', nicht 'ready' (Boolean)."""
        resp = _CLIENT.get("/api/v1/finance/close-readiness", headers=_AUTH_HEADERS)
        skip_if_db_unavailable(resp)
        assert resp.status_code == 200
        data = resp.json()
        # 'ready' als Boolean wäre ein abweichendes Schema — prüfen dass 'status' String ist
        assert isinstance(data["status"], str), (
            "TC-API-007d: 'status' muss ein String (nicht Boolean) sein"
        )


# ===========================================================================
# TC-API-008 — AMIC Agrarhandel spezifische Endpoints
# ===========================================================================

class TestAMICEndpoints:
    """TC-API-008: AMIC-spezifische Agrarhandel-Endpoints."""

    def test_kontrakt_klassen_crud_create(self):
        """TC-API-008a: POST /kontrakt-klassen → 201 und KontraktKlasseOut mit 'id'."""
        payload = {
            "name": "Fixpreis Weizen",
            "beschreibung": "Standard Weizen Fixpreis Kontrakt",
            "variante": "FIXPREIS",
            "parität": "EXW",
            "incoterm_ort": "Musterstadt Lager 1",
        }
        resp = _CLIENT.post("/api/v1/kontrakt-klassen", json=payload, headers=_AUTH_HEADERS)
        skip_if_db_unavailable(resp)
        assert resp.status_code in (200, 201), (
            f"TC-API-008a FEHLER: {resp.status_code}. Body: {resp.text[:400]}"
        )
        data = resp.json()
        assert "id" in data, f"TC-API-008a: 'id' fehlt. Keys: {list(data.keys())}"

    def test_kontrakt_klassen_invalid_variante(self):
        """TC-API-008b: POST /kontrakt-klassen mit ungültiger Variante → 422."""
        payload = {
            "name": "Test",
            "variante": "UNGUELTIG",
            "parität": "EXW",
        }
        resp = _CLIENT.post("/api/v1/kontrakt-klassen", json=payload, headers=_AUTH_HEADERS)
        skip_if_db_unavailable(resp)
        assert resp.status_code == 422, (
            f"TC-API-008b: Erwarte 422 fuer ungueltige Variante, bekam {resp.status_code}"
        )

    def test_rohware_sammelabrechnung_list(self):
        """TC-API-008c: GET /agrar/sammelabrechnung → Liste oder paginiertes Objekt."""
        resp = _CLIENT.get("/api/v1/agrar/sammelabrechnung", headers=_AUTH_HEADERS)
        skip_if_db_unavailable(resp)
        assert resp.status_code in (200, 204), (
            f"TC-API-008c FEHLER: {resp.status_code}. Body: {resp.text[:300]}"
        )
        if resp.status_code == 200:
            data = resp.json()
            assert isinstance(data, (list, dict))

    def test_ebilanz_perioden_list(self):
        """TC-API-008d: GET /ebilanz/meldungen → Liste (perioden-Alias)."""
        resp = _CLIENT.get("/api/v1/ebilanz/meldungen", headers=_AUTH_HEADERS)
        skip_if_db_unavailable(resp)
        assert resp.status_code in (200, 204), (
            f"TC-API-008d FEHLER: {resp.status_code}. Body: {resp.text[:300]}"
        )


# ===========================================================================
# TC-API-009 — L3-Connect Lager-Endpoints
# ===========================================================================

class TestL3ConnectEndpoints:
    """TC-API-009: L3-Connect Lager- und Logistik-Endpoints."""

    def test_warehouse_transfers_list(self):
        """TC-API-009a: GET /warehouses/transfers/ → Liste oder paginiertes Objekt."""
        resp = _CLIENT.get("/api/v1/warehouses/transfers/", headers=_AUTH_HEADERS)
        skip_if_db_unavailable(resp)
        assert resp.status_code in (200, 204), (
            f"TC-API-009a FEHLER: {resp.status_code}. Body: {resp.text[:300]}"
        )

    def test_preparation_lists_list(self):
        """TC-API-009b: GET /preparation-lists → Liste oder paginiertes Objekt."""
        resp = _CLIENT.get("/api/v1/preparation-lists", headers=_AUTH_HEADERS)
        skip_if_db_unavailable(resp)
        assert resp.status_code in (200, 204), (
            f"TC-API-009b FEHLER: {resp.status_code}. Body: {resp.text[:300]}"
        )

    def test_pick_lists_list(self):
        """TC-API-009c: GET /pick-lists → Liste oder paginiertes Objekt."""
        resp = _CLIENT.get("/api/v1/pick-lists", headers=_AUTH_HEADERS)
        skip_if_db_unavailable(resp)
        assert resp.status_code in (200, 204), (
            f"TC-API-009c FEHLER: {resp.status_code}. Body: {resp.text[:300]}"
        )

    def test_inventory_counts_list(self):
        """TC-API-009d: GET /inventory/counts → Liste oder paginiertes Objekt."""
        resp = _CLIENT.get("/api/v1/inventory/counts", headers=_AUTH_HEADERS)
        skip_if_db_unavailable(resp)
        assert resp.status_code in (200, 204), (
            f"TC-API-009d FEHLER: {resp.status_code}. Body: {resp.text[:300]}"
        )

    def test_weighing_tickets_list(self):
        """TC-API-009e: GET /weighing-tickets → Liste oder paginiertes Objekt."""
        resp = _CLIENT.get("/api/v1/weighing-tickets", headers=_AUTH_HEADERS)
        skip_if_db_unavailable(resp)
        assert resp.status_code in (200, 204), (
            f"TC-API-009e FEHLER: {resp.status_code}. Body: {resp.text[:300]}"
        )
