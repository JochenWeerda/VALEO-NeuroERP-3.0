"""Partnerbruecke (ADR Geschaeftspartnerstamm, Stufe 1): jede Kunden- und Lieferantenanlage haengt an einem
Geschaeftspartner des Mandanten. Alles rollt zurueck."""
from uuid import uuid4

import httpx
import pytest
from sqlalchemy import text

from app.api.v1.endpoints import finance_stammdaten
from app.services import customer_service
from test_gdpr_subject_boundary import subject_data, keys, probe  # noqa: F401

pytestmark = [pytest.mark.integration, pytest.mark.needs_live_db]


@pytest.fixture(scope="session", autouse=True)
def _seed_contract_test_tenants():
    """Dedicated probe test owns only rollback-scoped rows."""
    yield


@pytest.fixture
def anlage(require_db, subject_data, monkeypatch):
    client, db, provider, tenant, foreign, *_ = subject_data
    client.app.include_router(finance_stammdaten.router, prefix="/api/v1")

    async def offline(_payload):
        raise httpx.ConnectError("crm-core im Test nicht erreichbar")

    monkeypatch.setattr(customer_service, "_crm_create", offline)

    def send(path, body, *, selected=tenant):
        token = provider.token(selected, changes={"roles": ["FINANCE_BEARBEITEN"],
                                                 "identity_type": "human", "sub": "human-a"})
        return client.post(path, headers={"Authorization": "Bearer " + token}, json=body)

    def partner_von(tabelle, spalte, satz_id):
        return db.execute(text(f"SELECT {spalte} FROM {tabelle} WHERE id = :id"), {"id": satz_id}).scalar()

    def partner(pid):
        return db.execute(text("SELECT tenant_id, is_customer, is_supplier, name_1, country FROM "
                               "domain_crm.business_partners WHERE partner_id = :p"), {"p": pid}).one()

    return send, partner_von, partner, tenant, foreign


def debitor(name, ust=None):
    return {"debtor_number": "DEB-" + uuid4().hex[:12], "company_name": name, "street": "Weg 1",
            "postal_code": "12345", "city": "Ort", "country": "DE", **({"vat_id": ust} if ust else {})}


def kreditor(name, ust=None):
    return {"creditor_number": "KRE-" + uuid4().hex[:12], "company_name": name, "country": "Deutschland",
            **({"vat_id": ust} if ust else {})}


def test_landwirt_als_kunde_und_lieferant_ist_ein_partner(anlage):
    send, partner_von, partner, tenant, _ = anlage
    name, ust = "Hof Synthetik " + uuid4().hex[:6], "DE" + str(uuid4().int)[:9]
    kunde = send("/api/v1/finance/debitoren", debitor(name, ust))
    assert kunde.status_code == 201, kunde.text
    pid = partner_von("domain_crm.customers", "business_partner_id", kunde.json()["id"])
    assert pid
    lieferant = send("/api/v1/finance/creditors", kreditor(name, ust.lower()))
    assert lieferant.status_code == 201, lieferant.text
    assert partner_von("domain_einkauf.lieferanten", "partner_id", lieferant.json()["id"]) == pid
    stand = partner(pid)
    assert (stand.tenant_id, stand.is_customer, stand.is_supplier, stand.name_1) == (tenant, True, True, name)


def test_name_allein_ordnet_nie_zu(anlage):
    send, partner_von, partner, _, _ = anlage
    name = "Hof Gleichname " + uuid4().hex[:6]
    erster = send("/api/v1/finance/debitoren", debitor(name)).json()["id"]
    zweiter = send("/api/v1/finance/creditors", kreditor(name)).json()["id"]
    a = partner_von("domain_crm.customers", "business_partner_id", erster)
    b = partner_von("domain_einkauf.lieferanten", "partner_id", zweiter)
    assert a and b and a != b
    assert partner(b).country == "DE"  # 'Deutschland' -> ISO-2


def test_fremder_mandant_teilt_keinen_partner(anlage):
    send, partner_von, partner, tenant, foreign = anlage
    name, ust = "Hof Mandant " + uuid4().hex[:6], "DE" + str(uuid4().int)[:9]
    eigen = send("/api/v1/finance/debitoren", debitor(name, ust)).json()["id"]
    fremd = send("/api/v1/finance/debitoren", debitor(name, ust), selected=foreign).json()["id"]
    a = partner_von("domain_crm.customers", "business_partner_id", eigen)
    b = partner_von("domain_crm.customers", "business_partner_id", fremd)
    assert a != b
    assert (partner(a).tenant_id, partner(b).tenant_id) == (tenant, foreign)



def test_csv_import_haengt_neuen_kunden_an_partner(require_db, subject_data):
    from app.api.v1.endpoints.compat import _domain_crm_upsert_customer_norm

    _, db, _, tenant, *_ = subject_data
    nummer = "IMP-" + uuid4().hex[:10]
    created, updated, fehler = _domain_crm_upsert_customer_norm(
        db, tenant, firma="Importhof " + nummer, kundennummer=nummer, plz="12345", ort="Ort", land="DE",
        email="", telefon="", is_active=True, ust_id="")
    assert (created, updated, fehler) == (True, False, None)
    pid = db.execute(text("SELECT business_partner_id FROM domain_crm.customers WHERE tenant_id = :t "
                          "AND customer_number = :n"), {"t": tenant, "n": nummer}).scalar()
    assert db.execute(text("SELECT tenant_id, is_customer FROM domain_crm.business_partners WHERE partner_id = :p"),
                      {"p": pid}).one() == (tenant, True)
