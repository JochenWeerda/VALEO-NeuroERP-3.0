"""Intrastat-Pruefung auf der gespeicherten Meldung des Mandanten (20.10.2026).

Vorher pruefte ``/compliance/intrastat/meldungen/{id}/validate`` eine erfundene Beispielmeldung und meldete fuer
jede Kennung "gueltig" — auch dem Agenten-Werkzeug ``valeo_compliance_intrastat_validate``. Jetzt:

* eine vollstaendige Meldung ist gueltig;
* fehlerhafte Pflichtfelder werden als Verstoesse genannt;
* unbekannte und fremde Meldungen ergeben 404;
* das Agenten-Werkzeug zeigt auf diesen Weg.
"""
from __future__ import annotations

import os
import uuid

import pytest
from fastapi import Request  # Modulebene: FastAPI loest die Annotation hier auf

pytestmark = pytest.mark.integration

DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    os.environ.get("DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe"),
)
os.environ.setdefault("DATABASE_URL", DB_URL)

HAUS_A = f"intra-a-{uuid.uuid4().hex[:6]}"
HAUS_B = f"intra-b-{uuid.uuid4().hex[:6]}"


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as conn:
            conn.execute(text("SELECT 1 FROM domain_compliance.intrastat_meldungen LIMIT 0"))
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    return motor


@pytest.fixture(scope="module", autouse=True)
def aufraeumen(engine):
    from sqlalchemy import text

    yield
    with engine.begin() as v:
        v.execute(text("DELETE FROM domain_compliance.intrastat_meldungen WHERE tenant_id = ANY(:h)"),
                  {"h": [HAUS_A, HAUS_B]})


@pytest.fixture(autouse=True)
def gepruefte_person():
    from app.auth.deps import get_current_user
    from app.core.security import require_bearer_token
    from app.main import app
    from testgrenze import ALLE_FACHROLLEN, mandant_aus_kopf

    def geprueft(request: Request) -> str:
        tenant = mandant_aus_kopf(request)
        request.state.tenant_id = tenant
        request.state.tenant_verified = True
        request.state.token_claims = {"sub": "pruefer", "tenant_id": tenant, "roles": list(ALLE_FACHROLLEN)}
        return "pruefstand"

    app.dependency_overrides[require_bearer_token] = geprueft
    app.dependency_overrides[get_current_user] = lambda: {"sub": "pruefer", "roles": list(ALLE_FACHROLLEN)}
    yield
    app.dependency_overrides.pop(require_bearer_token, None)
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture(scope="module")
def client(engine):
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


def meldung(client, haus: str = HAUS_A) -> str:
    antwort = client.post("/api/v1/intrastat/meldungen", headers={"X-Tenant-ID": haus}, json={
        "meldezeitraum": "2026-09", "meldungsart": "EINGANG", "cn8_warennummer": "10019900",
        "ursprungsland": "FR", "bestimmungsland": "DE", "statistischer_wert_eur": 12500.0,
        "nettomasse_kg": 50000.0, "menge": 50.0, "mengeneinheit": "t", "geschaeftsvorgang_code": 11})
    assert antwort.status_code == 201, antwort.text
    return antwort.json()["id"]


def test_vollstaendige_meldung_ist_gueltig(client):
    kennung = meldung(client)
    antwort = client.get(f"/api/v1/intrastat/meldungen/{kennung}/validate", headers={"X-Tenant-ID": HAUS_A})
    assert antwort.status_code == 200, antwort.text
    assert antwort.json()["valid"] is True and antwort.json()["violations"] == []


def test_fehlerhafte_pflichtfelder_sind_verstoesse(engine, client):
    from sqlalchemy import text

    kennung = meldung(client)
    with engine.begin() as v:
        v.execute(text("UPDATE domain_compliance.intrastat_meldungen SET cn8_warennummer = '1001', "
                       "geschaeftsvorgang_code = 0 WHERE id = :i"), {"i": kennung})
    daten = client.get(f"/api/v1/intrastat/meldungen/{kennung}/validate", headers={"X-Tenant-ID": HAUS_A}).json()
    assert daten["valid"] is False
    assert {v["code"] for v in daten["violations"]} == {"INVALID_CN8", "INVALID_GESCHAEFTSART"}


def test_unbekannte_und_fremde_meldungen_ergeben_404(client):
    kennung = meldung(client, HAUS_B)
    assert client.get(f"/api/v1/intrastat/meldungen/{kennung}/validate",
                      headers={"X-Tenant-ID": HAUS_A}).status_code == 404
    assert client.get("/api/v1/intrastat/meldungen/INTRA-STUB/validate",
                      headers={"X-Tenant-ID": HAUS_A}).status_code == 404


def test_agentenwerkzeug_zeigt_auf_die_echte_pruefung():
    from app.core.mcp_tool_contracts import get_process_kernel_mcp_tools

    vertrag = get_process_kernel_mcp_tools().by_tool_name("valeo_compliance_intrastat_validate")
    assert vertrag.api_endpoint == "GET /api/v1/intrastat/meldungen/{meldung_id}/validate"
