"""Zahlungslaeufe gehoeren einem Mandanten, und freigeben darf nicht, wer angelegt hat.

Bis zum 07.10.2026 nahmen alle acht Wege den Mandanten aus ``Query("system")``
(``/plan`` sogar aus dem Rumpf); das Frontend schickte nie einen mit — die ganze
Oberflaeche lief auf dem Mandanten "system". Keiner pruefte eine Rolle, die Freigabe
nahm den Freigeber als freien Text.

Was diese Vertraege festhalten:

* Der Mandant kommt aus dem geprueften Kontext; ein fremder Mandant sieht, aendert
  und gibt nichts frei.
* Rollen werden **vor** dem ersten Datenbankzugriff geprueft; Freigeben und
  Ausfuehren nur ``FINANCE_ADMIN``/``admin``.
* **Vier Augen:** Wer den Lauf angelegt hat, gibt ihn nicht frei. Freigeber ist der
  angemeldete Nutzer, nicht ein Wort im Rumpf.
"""

from __future__ import annotations

import os
import uuid
from datetime import date, timedelta

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    os.environ.get("DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe"),
)
os.environ.setdefault("DATABASE_URL", DB_URL)
os.environ.setdefault("API_DEV_TOKEN", "dev-token")

from app.api.v1.endpoints import payment_runs as endpoint  # noqa: E402
from app.auth.deps import get_current_user  # noqa: E402
from app.core.database import get_db  # noqa: E402

PREFIX = "/api/v1/finance/payment-runs"

# ── 1. Rollen vor der Datenbank ─────────────────────────────────────────────

CASES = [
    ("POST", "/plan", "write"),
    ("POST", "", "write"),
    ("GET", "", "read"),
    ("GET", "/lauf", "read"),
    ("POST", "/lauf/approve", "admin"),
    ("POST", "/lauf/execute", "admin"),
    ("GET", "/lauf/sepa-xml", "read"),
    ("POST", "/lauf/return-payment", "write"),
]
ROLES = [None, "user", "PERSONAL_ADMIN", "FINANCE_LESEN", "FINANCE_BEARBEITEN", "FINANCE_ADMIN", "admin", "manager"]
ALLOWED = {
    "read": {"FINANCE_LESEN", "FINANCE_BEARBEITEN", "FINANCE_ADMIN", "admin", "manager"},
    "write": {"FINANCE_BEARBEITEN", "FINANCE_ADMIN", "admin", "manager"},
    "admin": {"FINANCE_ADMIN", "admin"},
}


@pytest.fixture
def grenze():
    app = FastAPI()
    app.include_router(endpoint.router, prefix="/api/v1/finance")
    aufrufe = []

    def datenbank():
        aufrufe.append("db")
        raise HTTPException(418, "autorisierte Datenbankgrenze")

    app.dependency_overrides[get_db] = datenbank
    with TestClient(app) as client:
        yield app, client, aufrufe


@pytest.mark.parametrize("method,suffix,zugang", CASES)
@pytest.mark.parametrize("rolle", ROLES)
def test_rollen_vor_der_datenbank(grenze, method, suffix, zugang, rolle):
    app, client, aufrufe = grenze
    app.dependency_overrides[get_current_user] = lambda: {"sub": "kasse", "roles": [] if rolle is None else [rolle]}
    antwort = client.request(method, PREFIX + suffix, json={})
    erlaubt = rolle in ALLOWED[zugang]
    assert antwort.status_code == (418 if erlaubt else 403), antwort.text
    assert aufrufe == (["db"] if erlaubt else [])


def test_jeder_weg_hat_eine_zugangsklasse():
    wege = {
        (m, r.path.replace("{run_id}", "lauf"))
        for r in endpoint.router.routes for m in r.methods
    }
    assert wege == {(m, "/payment-runs" + s) for m, s, _ in CASES}


def test_kein_weg_nimmt_den_mandanten_aus_query_oder_rumpf():
    from pathlib import Path

    quelle = Path("app/api/v1/endpoints/payment_runs.py").read_text(encoding="utf-8")
    assert 'Query("system"' not in quelle
    assert "request.tenant_id" not in quelle


# ── 2. Gegen die Datenbank ──────────────────────────────────────────────────

HAUS_A = f"zl-a-{uuid.uuid4().hex[:6]}"
HAUS_B = f"zl-b-{uuid.uuid4().hex[:6]}"


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as v:
            spalte = v.execute(text(
                "SELECT 1 FROM information_schema.columns WHERE table_schema='domain_erp' "
                "AND table_name='payment_runs' AND column_name='created_by'"
            )).scalar()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    if not spalte:
        pytest.skip("Migration mandant_finanz_crm_20261007 nicht angewandt")
    return motor


@pytest.fixture
def app_mit_db(engine):
    from sqlalchemy import text

    with engine.begin() as v:
        for haus in (HAUS_A, HAUS_B):
            v.execute(text("INSERT INTO domain_shared.tenants (id, name) VALUES (:i, :n) ON CONFLICT (id) DO NOTHING"),
                      {"i": haus, "n": f"Pruefbetrieb {haus}"})
    from app.main import app

    nutzer = {"sub": "anleger", "roles": ["FINANCE_ADMIN"]}
    app.dependency_overrides[get_current_user] = lambda: nutzer
    yield app, nutzer
    app.dependency_overrides.pop(get_current_user, None)
    with engine.begin() as v:
        v.execute(text(
            "DELETE FROM domain_erp.payment_run_items WHERE payment_run_id IN "
            "(SELECT id FROM domain_erp.payment_runs WHERE tenant_id = ANY(:h))"
        ), {"h": [HAUS_A, HAUS_B]})
        v.execute(text("DELETE FROM domain_erp.payment_runs WHERE tenant_id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]})


def kopf(haus: str) -> dict[str, str]:
    return {"X-Tenant-ID": haus, "Authorization": "Bearer dev-token"}


def anlegen(client, haus: str) -> str:
    antwort = client.post(PREFIX, headers=kopf(haus), json={
        "run_number": f"ZL-{uuid.uuid4().hex[:8]}",
        "execution_date": (date.today() + timedelta(days=2)).isoformat(),
        "initiator_name": "Pruefbetrieb", "initiator_iban": "DE02120300000000202051", "initiator_bic": "BYLADEM1001",
        "payments": [{"creditor_id": "K-1", "creditor_name": "Lieferant", "iban": "DE89370400440532013000",
                      "amount": "12.50", "purpose": "RE-1"}],
    })
    assert antwort.status_code == 201, antwort.text
    return antwort.json()["id"]


@pytest.mark.integration
class TestMandantUndVierAugen:
    def test_der_lauf_gehoert_dem_anlegenden_mandanten(self, engine, app_mit_db):
        from sqlalchemy import text

        app, _ = app_mit_db
        client = TestClient(app)
        lauf = anlegen(client, HAUS_A)
        with engine.connect() as v:
            zeile = v.execute(text("SELECT tenant_id, created_by FROM domain_erp.payment_runs WHERE id = :i"),
                              {"i": lauf}).first()
        assert zeile == (HAUS_A, "anleger")
        assert client.get(f"{PREFIX}/{lauf}", headers=kopf(HAUS_A)).status_code == 200
        assert client.get(f"{PREFIX}/{lauf}", headers=kopf(HAUS_B)).status_code == 404
        ids_b = [r["id"] for r in client.get(PREFIX, headers=kopf(HAUS_B)).json()]
        assert lauf not in ids_b

    def test_wer_anlegt_gibt_nicht_frei(self, engine, app_mit_db):
        app, nutzer = app_mit_db
        client = TestClient(app)
        lauf = anlegen(client, HAUS_A)
        antwort = client.post(f"{PREFIX}/{lauf}/approve", headers=kopf(HAUS_A), json={"approved_by": "jemand anderes"})
        assert antwort.status_code == 409, antwort.text
        assert "Vier-Augen" in antwort.text

    def test_ein_zweiter_gibt_frei_und_steht_als_freigeber_da(self, engine, app_mit_db):
        app, nutzer = app_mit_db
        client = TestClient(app)
        lauf = anlegen(client, HAUS_A)
        nutzer["sub"] = "pruefer"
        try:
            antwort = client.post(f"{PREFIX}/{lauf}/approve", headers=kopf(HAUS_A), json={"approved_by": "erfunden"})
        finally:
            nutzer["sub"] = "anleger"
        assert antwort.status_code == 200, antwort.text
        # Der angemeldete Nutzer, nicht das Wort im Rumpf.
        assert antwort.json()["approved_by"] == "pruefer"
        assert antwort.json()["status"] == "approved"

    def test_ein_fremder_mandant_gibt_nicht_frei(self, engine, app_mit_db):
        app, nutzer = app_mit_db
        client = TestClient(app)
        lauf = anlegen(client, HAUS_A)
        nutzer["sub"] = "pruefer"
        try:
            antwort = client.post(f"{PREFIX}/{lauf}/approve", headers=kopf(HAUS_B), json={})
        finally:
            nutzer["sub"] = "anleger"
        assert antwort.status_code == 404
        assert client.get(f"{PREFIX}/{lauf}", headers=kopf(HAUS_A)).json()["status"] == "draft"

    def test_planung_nimmt_den_mandanten_nicht_aus_dem_rumpf(self, engine, app_mit_db):
        app, _ = app_mit_db
        client = TestClient(app)
        antwort = client.post(f"{PREFIX}/plan", headers=kopf(HAUS_A), json={
            "execution_date": date.today().isoformat(), "tenant_id": "system",
        })
        assert antwort.status_code == 200, antwort.text
