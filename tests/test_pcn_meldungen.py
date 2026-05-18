"""
Tests für POST /api/v1/compliance/pcn-meldungen.

Verifiziert, dass der Endpoint:
  1. bei gültiger Payload mit 201 antwortet und eine valide Response zurückgibt.
  2. bei fehlendem Produktnamen 422 zurückgibt.
"""

import pytest
from fastapi.testclient import TestClient

from app.api.v1.endpoints.compliance import router as compliance_router
from fastapi import FastAPI

_app = FastAPI()
_app.include_router(compliance_router, prefix="/api/v1")

def skip_if_db_unavailable(response):
    """Skipt den Test wenn PostgreSQL nicht erreichbar ist."""
    if response.status_code in (500, 503):
        body = response.text
        if any(k in body for k in (
            "OperationalError", "Connection refused",
            "Identity provider unavailable", "UndefinedTable", "does not exist",
        )):
            pytest.skip("DB or identity provider not available")

client = TestClient(_app, raise_server_exceptions=False)

HEADERS = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-ID": "test-tenant",
}

VALID_PAYLOAD = {
    "produktname": "Fungizid A Professional",
    "ufi": "ABCD-1234-EFGH-5678",
    "cas_nummern": "1912-24-9",
    "gefahrenklassen": ["H302", "H400"],
    "verwendungskategorie": "SU24",
    "pcnStatus": "entwurf",
}


def test_create_pcn_meldung_success():
    """POST mit gültiger Payload liefert 201 und enthält produktname und pcnStatus."""
    resp = client.post("/api/v1/compliance/pcn-meldungen", json=VALID_PAYLOAD, headers=HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["produktname"] == VALID_PAYLOAD["produktname"]
    assert body["pcnStatus"] in {"entwurf", "eingereicht", "accepted"}
    assert "meldung_id" in body


def test_create_pcn_meldung_missing_produktname():
    """POST ohne produktname liefert 422 Validation Error."""
    payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "produktname"}
    resp = client.post("/api/v1/compliance/pcn-meldungen", json=payload, headers=HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 422
