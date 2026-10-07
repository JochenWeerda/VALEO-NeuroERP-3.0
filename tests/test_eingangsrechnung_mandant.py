"""Eingangsrechnungen gehoeren einem Mandanten; Freigeber ist, wer angemeldet ist.

Bis zum 07.10.2026 arbeitete das ganze AP-Modul ohne Mandant: Anlegen, Lesen,
Aendern, Loeschen, Liste, Freigabe und **Buchen** (Journal + offener Posten mit dem
Mandanten aus dem Dokument). Keine gespeicherte Rechnung trug einen Mandanten, und
der Pruef-Helfer des Workflows liess mandantenlose Rechnungen durch — also alle.
Der Workflow zaehlte Freigeber ueber ``approved_by`` aus dem Rumpf: eine Person
konnte eine Zwei-Stufen-Freigabe mit zwei Namen erfuellen.
"""

from __future__ import annotations

import json
import os
import uuid

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    os.environ.get("DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe"),
)
os.environ.setdefault("DATABASE_URL", DB_URL)
os.environ.setdefault("API_DEV_TOKEN", "dev-token")

from app.api.v1.endpoints import ap_approval_workflow as workflow  # noqa: E402
from app.api.v1.endpoints import ap_invoices as endpoint  # noqa: E402
from app.auth.deps import get_current_user  # noqa: E402
from app.core.database import get_db  # noqa: E402

PREFIX = "/api/v1/finance/ap/invoices"
WORKFLOW = "/api/v1/finance/ap/approval-workflow"

ROLES = [None, "user", "PERSONAL_ADMIN", "FINANCE_LESEN", "FINANCE_BEARBEITEN", "FINANCE_ADMIN", "admin", "manager"]
ALLOWED = {
    "read": {"FINANCE_LESEN", "FINANCE_BEARBEITEN", "FINANCE_ADMIN", "admin", "manager"},
    "write": {"FINANCE_BEARBEITEN", "FINANCE_ADMIN", "admin", "manager"},
    "admin": {"FINANCE_ADMIN", "admin"},
}
CASES = [
    ("POST", PREFIX + "/", "write"),
    ("GET", PREFIX + "/", "read"),
    ("GET", PREFIX + "/RE-1", "read"),
    ("PUT", PREFIX + "/RE-1", "write"),
    ("DELETE", PREFIX + "/RE-1", "admin"),
    ("POST", PREFIX + "/RE-1/approve", "admin"),
    ("POST", PREFIX + "/RE-1/post?posted_by=x", "admin"),
    ("POST", PREFIX + "/RE-1/actions/freigeben", "admin"),
    ("GET", WORKFLOW + "/rules", "read"),
    ("POST", WORKFLOW + "/rules", "admin"),
    ("POST", WORKFLOW + "/request", "write"),
    ("POST", WORKFLOW + "/approve", "admin"),
    ("GET", WORKFLOW + "/status/RE-1", "read"),
]


@pytest.fixture
def grenze():
    app = FastAPI()
    app.include_router(endpoint.router, prefix="/api/v1/finance")
    app.include_router(workflow.router, prefix="/api/v1/finance")
    aufrufe = []

    def datenbank():
        aufrufe.append("db")
        raise HTTPException(418, "autorisierte Datenbankgrenze")

    app.dependency_overrides[get_db] = datenbank
    with TestClient(app) as client:
        yield app, client, aufrufe


def test_die_pfade_stimmen():
    from app.main import app

    pfade = {getattr(r, "path", "") for r in app.routes}
    for _, pfad, _ in CASES:
        roh = pfad.split("?")[0].replace("RE-1", "{invoice_id}")
        roh = roh.replace("/{invoice_id}/actions/", "/{entity_id}/actions/")
        assert roh in pfade, roh


@pytest.mark.parametrize("method,pfad,zugang", CASES)
@pytest.mark.parametrize("rolle", ROLES)
def test_rollen_vor_der_datenbank(grenze, method, pfad, zugang, rolle):
    app, client, aufrufe = grenze
    app.dependency_overrides[get_current_user] = lambda: {"sub": "kasse", "roles": [] if rolle is None else [rolle]}
    antwort = client.request(method, pfad, json={})
    erlaubt = rolle in ALLOWED[zugang]
    assert antwort.status_code == (418 if erlaubt else 403), antwort.text
    assert aufrufe == (["db"] if erlaubt else [])


def test_der_helfer_laesst_nichts_mandantenloses_durch():
    with pytest.raises(HTTPException) as fehler:
        workflow._ensure_invoice_tenant_access({"number": "RE-1"}, "haus-a")
    assert fehler.value.status_code == 404
    with pytest.raises(HTTPException) as fehler:
        workflow._ensure_invoice_tenant_access({"number": "RE-1", "tenantId": "haus-b"}, "haus-a")
    assert fehler.value.status_code == 404
    assert workflow._ensure_invoice_tenant_access({"tenantId": "haus-a"}, "haus-a") == {"tenantId": "haus-a"}


# ── Gegen die Datenbank ─────────────────────────────────────────────────────

HAUS_A = f"ap-a-{uuid.uuid4().hex[:6]}"
HAUS_B = f"ap-b-{uuid.uuid4().hex[:6]}"
NUMMERN: list[str] = []


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as v:
            v.execute(text("SELECT 1 FROM documents LIMIT 0"))
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    return motor


@pytest.fixture
def client(engine):
    from sqlalchemy import text

    from app.main import app

    with engine.begin() as v:
        for haus in (HAUS_A, HAUS_B):
            v.execute(text("INSERT INTO domain_shared.tenants (id, name) VALUES (:i, :n) ON CONFLICT (id) DO NOTHING"),
                      {"i": haus, "n": f"Pruefbetrieb {haus}"})
    nutzer = {"sub": "kasse", "roles": ["FINANCE_ADMIN"]}
    app.dependency_overrides[get_current_user] = lambda: nutzer
    yield TestClient(app)
    app.dependency_overrides.pop(get_current_user, None)
    with engine.begin() as v:
        v.execute(text("DELETE FROM documents WHERE doc_type = 'ap_invoice' AND doc_number = ANY(:n)"), {"n": NUMMERN})


def kopf(haus: str) -> dict[str, str]:
    return {"X-Tenant-ID": haus, "Authorization": "Bearer dev-token"}


def anlegen(client, haus: str, nummer: str | None = None):
    nummer = nummer or f"RE-{uuid.uuid4().hex[:8]}"
    NUMMERN.append(nummer)
    return nummer, client.post(f"{PREFIX}/", headers=kopf(haus), json={
        "number": nummer, "date": "2026-10-07", "customerId": "supplier-1", "dueDate": "2026-11-06",
        "lines": [{"article": "Weizen", "qty": 1, "price": 100.0, "vatRate": 19.0}],
    })


def gespeichert(engine, nummer: str) -> dict:
    from sqlalchemy import text

    with engine.connect() as v:
        roh = v.execute(text("SELECT data FROM documents WHERE doc_type = 'ap_invoice' AND doc_number = :n"),
                        {"n": nummer}).scalar()
    return roh if isinstance(roh, dict) else json.loads(roh)


@pytest.mark.integration
class TestMandant:
    def test_anlegen_traegt_den_mandanten(self, engine, client):
        nummer, antwort = anlegen(client, HAUS_A)
        assert antwort.status_code == 201, antwort.text
        assert gespeichert(engine, nummer)["tenantId"] == HAUS_A

    def test_ein_fremder_mandant_sieht_und_aendert_nichts(self, engine, client):
        nummer, _ = anlegen(client, HAUS_A)
        assert client.get(f"{PREFIX}/{nummer}", headers=kopf(HAUS_A)).status_code == 200
        assert client.get(f"{PREFIX}/{nummer}", headers=kopf(HAUS_B)).status_code == 404
        assert client.delete(f"{PREFIX}/{nummer}", headers=kopf(HAUS_B)).status_code == 404
        assert client.post(f"{PREFIX}/{nummer}/approve", headers=kopf(HAUS_B)).status_code == 404
        assert client.post(f"{PREFIX}/{nummer}/post?posted_by=x", headers=kopf(HAUS_B)).status_code == 404
        nummern_b = [r.get("number") for r in client.get(f"{PREFIX}/", headers=kopf(HAUS_B)).json()]
        assert nummer not in nummern_b
        assert gespeichert(engine, nummer)["tenantId"] == HAUS_A

    def test_anlegen_ueberschreibt_keine_fremde_rechnung(self, engine, client):
        nummer, _ = anlegen(client, HAUS_A)
        _, antwort = anlegen(client, HAUS_B, nummer)
        assert antwort.status_code == 409
        assert gespeichert(engine, nummer)["tenantId"] == HAUS_A

    def test_eine_mandantenlose_altrechnung_sieht_niemand(self, engine, client):
        from sqlalchemy import text

        nummer = f"RE-ALT-{uuid.uuid4().hex[:6]}"
        NUMMERN.append(nummer)
        with engine.begin() as v:
            v.execute(text(
                "INSERT INTO documents (id, doc_type, doc_number, data, created_at, updated_at) "
                "VALUES (:i, 'ap_invoice', :n, :d, NOW(), NOW())"
            ), {"i": str(uuid.uuid4()), "n": nummer, "d": json.dumps({"number": nummer, "status": "ENTWURF"})})
        assert client.get(f"{PREFIX}/{nummer}", headers=kopf(HAUS_A)).status_code == 404

    def test_eine_person_erfuellt_keine_zwei_stufen_freigabe(self, engine, client):
        from sqlalchemy import text

        regel = client.post(f"{WORKFLOW}/rules", headers=kopf(HAUS_A), json={
            "name": "Vier Augen", "conditions": [{"field": "amount", "operator": "gt", "value": 0}],
            "required_approvals": 2, "approval_roles": ["FINANCE_ADMIN"], "priority": 100,
        })
        assert regel.status_code == 201, regel.text
        try:
            nummer, _ = anlegen(client, HAUS_A)
            antrag = client.post(f"{WORKFLOW}/request", headers=kopf(HAUS_A),
                                 json={"invoice_id": nummer, "requested_by": "einkauf"})
            assert antrag.status_code == 200, antrag.text
            erste = client.post(f"{WORKFLOW}/approve", headers=kopf(HAUS_A), json={
                "invoice_id": nummer, "approved_by": "Frau A", "action": "approve"})
            assert erste.status_code == 200, erste.text
            # Derselbe angemeldete Nutzer, ein anderer Name im Rumpf: keine zweite Stufe.
            zweite = client.post(f"{WORKFLOW}/approve", headers=kopf(HAUS_A), json={
                "invoice_id": nummer, "approved_by": "Herr B", "action": "approve"})
            assert zweite.status_code == 400, zweite.text
            with engine.connect() as v:
                freigeber = [z[0] for z in v.execute(text(
                    "SELECT a.approved_by FROM domain_erp.ap_approvals a "
                    "JOIN domain_erp.ap_approval_requests r ON r.id = a.request_id "
                    "WHERE r.invoice_id = :n AND r.tenant_id = :h"), {"n": nummer, "h": HAUS_A})]
            assert freigeber == ["kasse"]
        finally:
            with engine.begin() as v:
                v.execute(text(
                    "DELETE FROM domain_erp.ap_approvals WHERE request_id IN "
                    "(SELECT id FROM domain_erp.ap_approval_requests WHERE tenant_id = :h)"), {"h": HAUS_A})
                v.execute(text("DELETE FROM domain_erp.ap_approval_requests WHERE tenant_id = :h"), {"h": HAUS_A})
                v.execute(text("DELETE FROM domain_erp.ap_approval_rules WHERE tenant_id = :h"), {"h": HAUS_A})
