"""Stufe 3b Geschaeftspartnerstamm: eigene Debitoren- und Kreditorennummer je Partner, je Mandant eindeutig.
Alles rollt zurueck."""
import importlib.util
from pathlib import Path
from uuid import uuid4

import httpx
import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.api.v1.endpoints import finance_stammdaten
from app.core.exceptions import ConflictError
from app.services import customer_service
from app.services.business_partner_service import BusinessPartnerService
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

    def send(method, path, body=None, *, selected=tenant):
        token = provider.token(selected, changes={"roles": ["FINANCE_BEARBEITEN"],
                                                 "identity_type": "human", "sub": "human-a"})
        return client.request(method, path, headers={"Authorization": "Bearer " + token}, json=body)

    def konten(pid):
        return db.execute(text("SELECT debtor_account, creditor_account FROM domain_crm.business_partners "
                               "WHERE partner_id = :p"), {"p": pid}).one()

    return db, send, konten, tenant, foreign


def debitor(name, ust):
    return {"debtor_number": "DEB-" + uuid4().hex[:12], "company_name": name, "street": "Weg 1",
            "postal_code": "12345", "city": "Ort", "country": "DE", "vat_id": ust}


def kreditor(name, ust):
    return {"creditor_number": "KRE-" + uuid4().hex[:12], "company_name": name, "country": "Deutschland",
            "vat_id": ust}


def _hof():
    return "Hof Konto " + uuid4().hex[:6], "DE" + str(uuid4().int)[:9]


def test_landwirt_mit_beiden_rollen_hat_je_rolle_genau_ein_konto(anlage):
    db, send, konten, *_ = anlage
    name, ust = _hof()
    kunde = send("POST", "/api/v1/finance/debitoren", debitor(name, ust))
    assert kunde.status_code == 201, kunde.text
    pid = db.execute(text("SELECT business_partner_id FROM domain_crm.customers WHERE id = :i"),
                     {"i": kunde.json()["id"]}).scalar()
    debitorenkonto, kreditorenkonto = konten(pid)
    assert 10000 <= int(debitorenkonto) <= 69999 and kreditorenkonto is None
    assert kunde.json()["debitoren_nr"] == debitorenkonto

    lieferant = send("POST", "/api/v1/finance/creditors", kreditor(name, ust))
    assert lieferant.status_code == 201, lieferant.text
    zweiter_kunde = send("POST", "/api/v1/finance/debitoren", debitor(name, ust))
    assert zweiter_kunde.status_code == 201, zweiter_kunde.text
    # Gleicher Partner: die Debitorennummer bleibt, die Kreditorennummer kommt aus dem eigenen Kreis.
    assert konten(pid).debtor_account == debitorenkonto
    assert 70000 <= int(konten(pid).creditor_account) <= 99999

    detail = send("GET", f"/api/v1/finance/kreditoren/{lieferant.json()['id']}").json()
    assert detail["kreditoren_nr"] == konten(pid).creditor_account
    assert detail["lieferantennummer"].startswith("KRE-")  # Lieferantennummer ist nicht das Konto
    gelistet = next(r for r in send("GET", "/api/v1/finance/debitoren").json() if r["id"] == kunde.json()["id"])
    assert gelistet["debitoren_nr"] == debitorenkonto


def test_nummern_je_mandant_eigener_kreis_und_eindeutig(anlage):
    db, send, konten, tenant, foreign = anlage
    eigen = send("POST", "/api/v1/finance/debitoren", debitor(*_hof())).json()
    fremd = send("POST", "/api/v1/finance/debitoren", debitor(*_hof()), selected=foreign).json()
    assert eigen["debitoren_nr"] and fremd["debitoren_nr"]
    kreise = db.execute(text("SELECT tenant_id FROM domain_shared.number_ranges WHERE range_type = 'debtor_account' "
                             "AND tenant_id IN (:a, :b)"), {"a": tenant, "b": foreign}).scalars().all()
    assert sorted(kreise) == sorted([tenant, foreign])

    pid = db.execute(text("SELECT business_partner_id FROM domain_crm.customers WHERE id = :i"),
                     {"i": fremd["id"]}).scalar()
    db.execute(text("SAVEPOINT doppelt"))
    with pytest.raises(IntegrityError):
        db.execute(text("INSERT INTO domain_crm.business_partners (partner_id, tenant_id, partner_number, name_1, "
                        "debtor_account) VALUES (:i, :t, :nr, 'Doppelt', :n)"),
                   {"i": str(uuid4()), "t": foreign, "nr": "GP-" + uuid4().hex[:12], "n": konten(pid).debtor_account})
    db.execute(text("ROLLBACK TO SAVEPOINT doppelt"))


def test_vergebene_nummer_wird_uebersprungen_und_voller_kreis_abgelehnt(anlage):
    db, send, konten, tenant, _ = anlage
    svc = BusinessPartnerService(db, tenant)
    naechste = svc.naechste_kontonummer("is_customer")
    # Von Hand vergebene Nummer direkt dahinter: der Kreis springt darueber.
    db.execute(text("INSERT INTO domain_crm.business_partners (partner_id, tenant_id, partner_number, name_1, "
                    "debtor_account) VALUES (:i, :t, :nr, 'Hand', :n)"),
               {"i": str(uuid4()), "t": tenant, "nr": "GP-" + uuid4().hex[:12], "n": str(int(naechste) + 1)})
    assert svc.naechste_kontonummer("is_customer") == str(int(naechste) + 2)

    db.execute(text("UPDATE domain_shared.number_ranges SET current_value = 70000 WHERE tenant_id = :t "
                    "AND range_type = 'debtor_account'"), {"t": tenant})
    with pytest.raises(ConflictError, match="ausgeschoepft"):
        svc.naechste_kontonummer("is_customer")
    antwort = send("POST", "/api/v1/finance/debitoren", debitor(*_hof()))
    assert antwort.status_code == 409, antwort.text


def test_vergebene_kontonummer_bleibt_unveraendert(anlage):
    db, send, konten, tenant, _ = anlage
    kunde = send("POST", "/api/v1/finance/debitoren", debitor(*_hof())).json()
    pid = db.execute(text("SELECT business_partner_id FROM domain_crm.customers WHERE id = :i"),
                     {"i": kunde["id"]}).scalar()
    svc = BusinessPartnerService(db, tenant)
    row = svc.get_partner(pid)
    bisher = {"debtor_account": row.debtor_account, "creditor_account": row.creditor_account}
    row.debtor_account = None  # PUT ohne Konto im Rumpf
    with pytest.raises(ConflictError, match="bleibt unveraendert"):
        svc.assign_account_numbers(row, bisher)
    row.debtor_account = bisher["debtor_account"]
    row.is_supplier = True  # neue Lieferantenrolle ueber den Partnerstamm
    svc.assign_account_numbers(row, bisher)
    assert row.debtor_account == bisher["debtor_account"] and 70000 <= int(row.creditor_account) <= 99999


def _migration():
    path = Path(__file__).resolve().parents[1] / "alembic/versions/partner_kontonummern_20261102.py"
    spec = importlib.util.spec_from_file_location("partner_kontonummern", path)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def test_rueckfuellung_vergibt_nur_fehlende_konten_und_downgrade_nimmt_nur_eigenes_zurueck(require_db):
    from app.core.database import engine

    tid = "pk-" + uuid4().hex[:8]
    with engine.connect() as c:
        t = c.begin()
        x = lambda sql, **p: c.execute(sa.text(sql), p)  # noqa: E731
        x("INSERT INTO domain_shared.tenants (id, name) VALUES (:t, :t)", t=tid)

        def partner(name, kunde, lieferant, debitor=None):
            pid = str(uuid4())
            x("INSERT INTO domain_crm.business_partners (partner_id, tenant_id, partner_number, name_1, "
              "is_customer, is_supplier, debtor_account) VALUES (:p, :t, :n, :name, :k, :l, :d)",
              p=pid, t=tid, n="P-" + pid[:12], name=name, k=kunde, l=lieferant, d=debitor)
            return pid

        landwirt = partner("Landwirt", True, True)
        vorhanden = partner("Altkunde", True, False, debitor="10000")
        ohne_rolle = partner("Interessent", False, False)
        mandat = str(uuid4())
        x("INSERT INTO domain_shared.sepa_mandates (id, tenant_id, debitor_id, mandate_reference) "
          "VALUES (:i, :t, :d, :r)", i=mandat, t=tid, d=landwirt, r="M-" + mandat[:8])

        m = _migration()
        with Operations.context(MigrationContext.configure(c)):
            m.upgrade()
        konto = lambda pid: x("SELECT debtor_account, creditor_account FROM domain_crm.business_partners "  # noqa: E731
                              "WHERE partner_id = :p", p=pid).one()
        assert tuple(konto(landwirt)) == ("10001", "70000")  # 10000 ist schon vergeben
        assert tuple(konto(vorhanden)) == ("10000", None)
        assert tuple(konto(ohne_rolle)) == (None, None)
        assert x("SELECT current_value FROM domain_shared.number_ranges WHERE tenant_id = :t "
                 "AND range_type = 'debtor_account'", t=tid).scalar() == 10002
        assert x("SELECT partner_id FROM domain_shared.sepa_mandates WHERE id = :i", i=mandat).scalar() == landwirt

        with Operations.context(MigrationContext.configure(c)):
            m.downgrade()
        assert tuple(konto(landwirt)) == (None, None)
        assert tuple(konto(vorhanden)) == ("10000", None)
        assert x("SELECT count(*) FROM domain_shared.number_ranges WHERE tenant_id = :t", t=tid).scalar() == 0
        assert x("SELECT to_regclass('domain_crm.partner_konto_protokoll')").scalar() is None
        t.rollback()
