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
from testgrenze import ALLE_FACHROLLEN, ersetze_bearer, ersetze_mandant, ersetze_nutzer
ersetze_bearer(_app, *ALLE_FACHROLLEN)
ersetze_mandant(_app)
ersetze_nutzer(_app, *ALLE_FACHROLLEN)

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



def test_gescheitertes_speichern_meldet_keinen_erfolg():
    """Bis 20.10.2026 antwortete die Anlage bei einem Datenbankfehler mit 201 und hielt die Meldung nur im
    Arbeitsspeicher; die Liste las sie bei einem Lesefehler von dort. Jetzt: 503, nichts angelegt."""
    import asyncio

    from fastapi import HTTPException

    from app.api.v1.endpoints.compliance import create_pcn_meldung

    class Kaputt:
        zurueckgerollt = False

        def add(self, obj):  # noqa: ANN001
            pass

        def commit(self):
            raise RuntimeError("Datenbank weg")

        def rollback(self):
            self.zurueckgerollt = True

    db = Kaputt()
    with pytest.raises(HTTPException) as fehler:
        asyncio.run(create_pcn_meldung(body={"produktname": "Reiniger X", "ufi": "AB12-CD34-EF56-GH78"},
                                       db=db, tenant_id="t-1"))
    assert fehler.value.status_code == 503
    assert db.zurueckgerollt
