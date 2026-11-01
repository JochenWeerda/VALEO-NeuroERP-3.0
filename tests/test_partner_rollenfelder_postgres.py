"""Stufe 3 Geschaeftspartnerstamm: Bank, Skonto und Steuernummer liegen am Partner, Klaerfaelle werden als
Maskenaktion entschieden. Alles rollt zurueck."""
from uuid import uuid4

import httpx
import pytest
from sqlalchemy import text

from app.api.v1.endpoints import crm_partner_klaerfaelle, finance_stammdaten
from app.services import customer_service
from test_gdpr_subject_boundary import subject_data, keys, probe  # noqa: F401

pytestmark = [pytest.mark.integration, pytest.mark.needs_live_db]
IBAN = "DE89370400440532013000"


@pytest.fixture(scope="session", autouse=True)
def _seed_contract_test_tenants():
    """Dedicated probe test owns only rollback-scoped rows."""
    yield


@pytest.fixture
def welt(require_db, subject_data, monkeypatch):
    client, db, provider, tenant, foreign, *_ = subject_data
    client.app.include_router(finance_stammdaten.router, prefix="/api/v1")
    client.app.include_router(crm_partner_klaerfaelle.router, prefix="/api/v1")

    async def offline(_payload):
        raise httpx.ConnectError("crm-core im Test nicht erreichbar")

    monkeypatch.setattr(customer_service, "_crm_create", offline)

    def send(method, path, *, selected=tenant, roles=("FINANCE_BEARBEITEN", "SALES_BEARBEITEN"), **kw):
        token = provider.token(selected, changes={"roles": list(roles), "identity_type": "human", "sub": "human-a"})
        return client.request(method, path, headers={"Authorization": "Bearer " + token}, **kw)

    return db, send, tenant, foreign


def _debitor(name, ust, **extra):
    return {"debtor_number": "DEB-" + uuid4().hex[:12], "company_name": name, "street": "Weg 1",
            "postal_code": "12345", "city": "Ort", "country": "DE", "vat_id": ust, **extra}


def test_bank_und_skonto_landen_am_partner_und_in_der_detailmaske(welt):
    db, send, *_ = welt
    name, ust = "Bankhof " + uuid4().hex[:6], "DE" + str(uuid4().int)[:9]
    r = send("POST", "/api/v1/finance/debitoren", json=_debitor(
        name, ust, iban="DE89 3704 0044 0532 0130 00", bic="COBADEFFXXX", bank_name="Commerzbank",
        account_holder=name, discount_days=10, discount_percent=2, tax_number="12/345/67890"))
    assert r.status_code == 201, r.text
    detail = send("GET", f"/api/v1/finance/debitoren/{r.json()['id']}").json()
    assert (detail["iban"], detail["bic"], detail["skonto_tage"], detail["skonto_prozent"]) == (IBAN, "COBADEFFXXX", 10, 2.0)
    assert detail["geschaeftspartner_nr"]

    # Derselbe Landwirt als Lieferant: gleiche Bank (anders geschrieben) passt, eine andere wird abgelehnt.
    gleich = send("POST", "/api/v1/finance/creditors", json={
        "creditor_number": "KRE-" + uuid4().hex[:10], "company_name": name, "vat_id": ust, "iban": IBAN})
    assert gleich.status_code == 201, gleich.text
    assert send("GET", f"/api/v1/finance/kreditoren/{gleich.json()['id']}").json()["iban"] == IBAN
    anders = send("POST", "/api/v1/finance/creditors", json={
        "creditor_number": "KRE-" + uuid4().hex[:10], "company_name": name, "vat_id": ust,
        "iban": "DE02120300000000202051"})
    assert anders.status_code == 409, anders.text


def test_ungueltige_iban_und_bank_beim_kreditor_aendern(welt):
    _, send, *_ = welt
    assert send("POST", "/api/v1/finance/debitoren",
                json=_debitor("Hof X", "DE" + str(uuid4().int)[:9], iban="DE00123")).status_code == 400
    k = send("POST", "/api/v1/finance/creditors", json={"creditor_number": "KRE-" + uuid4().hex[:10],
                                                          "company_name": "Hof Y " + uuid4().hex[:6]})
    assert k.status_code == 201, k.text
    r = send("PATCH", f"/api/v1/finance/creditors/{k.json()['id']}", json={"iban": IBAN})
    assert r.status_code == 422 and "Geschaeftspartner" in r.text


def _klaerfall(db, tenant, name):
    kunde, fall = str(uuid4()), str(uuid4())
    db.execute(text("INSERT INTO domain_crm.customers (id, tenant_id, customer_number, company_name) "
                    "VALUES (:i, :t, :n, :name)"), {"i": kunde, "t": tenant, "n": "K-" + kunde[:12], "name": name})
    db.execute(text("INSERT INTO domain_crm.partner_klaerfaelle (id, tenant_id, quelle, satz_id, grund) "
                    "VALUES (:f, :t, 'kunde', :k, 'Test')"), {"f": fall, "t": tenant, "k": kunde})
    db.commit()  # Die Aktions-Runtime rollt nach der Pruefung zurueck; die aeussere Testtransaktion bleibt.
    return kunde, fall


def _partner(db, tenant, name="Partner " + uuid4().hex[:6]):
    pid = str(uuid4())
    db.execute(text("INSERT INTO domain_crm.business_partners (partner_id, tenant_id, partner_number, name_1) "
                    "VALUES (:p, :t, :n, :name)"), {"p": pid, "t": tenant, "n": "P-" + pid[:10], "name": name})
    db.commit()
    return pid


def test_klaerfall_zuordnen_nur_mit_grund_und_eigenem_partner(welt):
    db, send, tenant, foreign = welt
    kunde, fall = _klaerfall(db, tenant, "Klaerhof " + uuid4().hex[:6])
    eigen, fremd = _partner(db, tenant), _partner(db, foreign)
    pfad = f"/api/v1/crm/partner-klaerfaelle/{fall}/actions/zuordnen"
    assert send("POST", pfad, json={"partner_id": eigen}).json()["success"] is False  # ohne Begruendung
    r = send("POST", pfad, json={"partner_id": fremd, "_auditReason": "Test"}).json()
    assert r["success"] is False and "nicht im Mandanten" in str(r["validationErrors"])
    r = send("POST", pfad, json={"partner_id": eigen, "_auditReason": "Gleicher Betrieb"}).json()
    assert r["success"] is True, r
    assert db.execute(text("SELECT business_partner_id FROM domain_crm.customers WHERE id = :k"),
                      {"k": kunde}).scalar() == eigen
    assert db.execute(text("SELECT is_customer FROM domain_crm.business_partners WHERE partner_id = :p"),
                      {"p": eigen}).scalar() is True
    assert send("GET", "/api/v1/crm/partner-klaerfaelle").json() == [] or \
        all(f["id"] != fall for f in send("GET", "/api/v1/crm/partner-klaerfaelle").json())
    # Fremder Mandant sieht und entscheidet den Fall nicht.
    assert send("POST", pfad, selected=foreign, json={"partner_id": fremd, "_auditReason": "x"}).json()["success"] is False


def test_klaerfall_neuer_partner_und_rolle(welt):
    db, send, tenant, _ = welt
    name = "Neuhof " + uuid4().hex[:6]
    kunde, fall = _klaerfall(db, tenant, name)
    _partner(db, tenant, name)  # gleichnamiger Partner: genau der Grund des Klaerfalls
    pfad = f"/api/v1/crm/partner-klaerfaelle/{fall}/actions/neuer-partner"
    assert send("POST", pfad, roles=("FINANCE_BEARBEITEN",), json={"_auditReason": "x"}).status_code == 403
    r = send("POST", pfad, json={"_auditReason": "Anderer Betrieb gleichen Namens"}).json()
    assert r["success"] is True, r
    pid = db.execute(text("SELECT business_partner_id FROM domain_crm.customers WHERE id = :k"), {"k": kunde}).scalar()
    assert db.execute(text("SELECT count(*) FROM domain_crm.business_partners WHERE tenant_id = :t AND name_1 = :n"),
                      {"t": tenant, "n": name}).scalar() == 2
    assert db.execute(text("SELECT tenant_id FROM domain_crm.business_partners WHERE partner_id = :p"),
                      {"p": pid}).scalar() == tenant
