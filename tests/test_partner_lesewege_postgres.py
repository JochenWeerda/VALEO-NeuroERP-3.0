"""Stufe 4 Geschaeftspartnerstamm: offene Posten gehoeren dem Debitor/Kreditor, auf den ihre Kennung zeigt; der
Name entscheidet nur ohne Kennung und nur, wenn er eindeutig ist. Alles rollt zurueck."""
from uuid import uuid4

import pytest
from sqlalchemy import text

from app.api.v1.endpoints import finance_stammdaten
from test_gdpr_subject_boundary import subject_data, keys, probe  # noqa: F401

pytestmark = [pytest.mark.integration, pytest.mark.needs_live_db]


@pytest.fixture(scope="session", autouse=True)
def _seed_contract_test_tenants():
    """Dedicated probe test owns only rollback-scoped rows."""
    yield


@pytest.fixture
def welt(require_db, subject_data):
    client, db, provider, tenant, foreign, *_ = subject_data
    from app.api.v1.endpoints import mask_screen_definition

    client.app.include_router(finance_stammdaten.router, prefix="/api/v1")
    client.app.include_router(mask_screen_definition.router, prefix="/api/v1")

    def get(path, *, selected=tenant):
        token = provider.token(selected, changes={"roles": ["FINANCE_LESEN"], "identity_type": "human",
                                                 "sub": "human-a"})
        r = client.get(path, headers={"Authorization": "Bearer " + token})
        assert r.status_code == 200, r.text
        return r.json()

    def kunde(name, tid=tenant):
        cid = str(uuid4())
        db.execute(text("INSERT INTO domain_crm.customers (id, tenant_id, customer_number, company_name) "
                        "VALUES (:i, :t, :n, :name)"), {"i": cid, "t": tid, "n": "K-" + cid[:12], "name": name})
        return cid

    def op(betrag, *, name, tid=tenant, konto="debitoren", **kennung):
        spalten = "".join(f", {k}" for k in kennung)
        werte = "".join(f", :{k}" for k in kennung)
        db.execute(text(f"INSERT INTO domain_erp.offene_posten (id, tenant_id, konto_typ, kunde_name, betrag, offen"
                        f"{spalten}) VALUES (:i, :t, :k, :n, :b, :b{werte})"),
                   {"i": str(uuid4()), "t": tid, "k": konto, "n": name, "b": betrag, **kennung})

    return db, get, kunde, op, tenant, foreign


def _offen(liste, cid):
    return next(r for r in liste if r["id"] == cid)["offenerBetrag"]


def test_gleichnamige_kunden_teilen_keine_forderungen(welt):
    _, get, kunde, op, *_ = welt
    name = "Hof Gleich " + uuid4().hex[:6]
    a, b = kunde(name), kunde(name)
    op(100, name=name, kunde_id=a)
    op(30, name=name, debtor_id=b)
    op(999, name=name)  # nur Name, zwei Kandidaten: niemandem zuordnen
    liste = get("/api/v1/finance/debitoren")
    assert (_offen(liste, a), _offen(liste, b)) == (100.0, 30.0)
    assert get(f"/api/v1/finance/debitoren/{a}")["offenerBetrag"] == 100.0


def test_nummer_und_eindeutiger_name_als_rueckfall(welt):
    db, get, kunde, op, tenant, foreign = welt
    name = "Hof Einzig " + uuid4().hex[:6]
    cid = kunde(name)
    nummer = db.execute(text("SELECT customer_number FROM domain_crm.customers WHERE id = :i"), {"i": cid}).scalar()
    op(10, name="anders geschrieben", kunde_id=nummer)
    op(5, name=name)  # ohne Kennung, Name eindeutig
    op(7, name=name, kunde_id="unbekannt-" + uuid4().hex[:6])  # Kennung zeigt nirgends hin -> Name entscheidet
    kunde(name, tid=foreign)  # gleichnamig im fremden Mandanten zaehlt nicht
    assert _offen(get("/api/v1/finance/debitoren"), cid) == 22.0



def test_register_offene_posten_zeigt_nur_eigene_posten(welt):
    db, get, kunde, op, tenant, foreign = welt
    name = "Hof Register " + uuid4().hex[:6]
    a, b = kunde(name), kunde(name)
    op(100, name=name, kunde_id=a)
    op(30, name=name, debtor_id=b)
    op(999, name=name)
    op(55, name=name, tid=foreign, kunde_id=a)  # gleiche Kennung im fremden Mandanten
    seite = get(f"/api/v1/masks/finance/debitoren/entity/{a}/tabs/offene-posten")
    assert (seite["total"], [i["betrag"] for i in seite["items"]]) == (1, [100.0])
    assert get(f"/api/v1/masks/finance/debitoren/entity/{b}/tabs/offene-posten")["total"] == 1
