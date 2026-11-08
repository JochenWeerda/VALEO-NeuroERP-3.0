"""Stufe 2 Geschaeftspartnerstamm: die Rueckfuellung ordnet den Bestand nach der Regel der Partnerbruecke zu
und legt Zweifelsfaelle in die Klaerliste. Laeuft auf dem frischen Pruefstand in einer Transaktion, die am
Ende zurueckgerollt wird."""
import importlib.util
from pathlib import Path
from uuid import uuid4

import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations

pytestmark = [pytest.mark.integration, pytest.mark.needs_live_db]


@pytest.fixture(scope="session", autouse=True)
def _seed_contract_test_tenants():
    """Dedicated probe test owns only rollback-scoped rows."""
    yield


def _migration():
    path = Path(__file__).resolve().parents[1] / "alembic/versions/partner_rueckfuellung_20261101.py"
    spec = importlib.util.spec_from_file_location("partner_rueckfuellung", path)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


@pytest.fixture
def bestand(require_db):
    from app.core.database import engine

    a, b = "pr-a-" + uuid4().hex[:8], "pr-b-" + uuid4().hex[:8]
    with engine.connect() as c:
        t = c.begin()
        x = lambda sql, **p: c.execute(sa.text(sql), p)  # noqa: E731
        for tid in (a, b):
            x("INSERT INTO domain_shared.tenants (id, name) VALUES (:t, :t)", t=tid)
        p1, fremd = str(uuid4()), str(uuid4())
        x("INSERT INTO domain_crm.business_partners (partner_id, tenant_id, partner_number, name_1, vat_id) "
          "VALUES (:p, :t, :n, 'Hof A', 'DE 111.111.111')", p=p1, t=a, n="P-" + p1[:8])
        x("INSERT INTO domain_crm.business_partners (partner_id, tenant_id, partner_number, name_1) "
          "VALUES (:p, :t, :n, 'Fremd')", p=fremd, t=b, n="P-" + fremd[:8])

        def kunde(tid, name, ust=None, bp=None):
            cid = str(uuid4())
            x("INSERT INTO domain_crm.customers (id, tenant_id, customer_number, company_name, tax_id, "
              "business_partner_id) VALUES (:i, :t, :n, :name, :u, :bp)",
              i=cid, t=tid, n="K-" + cid[:12], name=name, u=ust, bp=bp)
            return cid

        def lieferant(tid, name, ust=None):
            lid = str(uuid4())
            x("INSERT INTO domain_einkauf.lieferanten (id, tenant_id, lieferantennummer, firmenname, ust_id, land) "
              "VALUES (:i, :t, :n, :name, :u, 'Deutschland')", i=lid, t=tid, n="L-" + lid[:12], name=name, u=ust)
            return lid

        ids = {
            "passt_p1": kunde(a, "Hof A", "DE111111111"),
            "kunde_b": kunde(a, "Hof B", "DE222222222"), "lief_b": lieferant(a, "hof b ", "de 222222222"),
            "dublette_1": kunde(a, "Hof C", "DE333333333"), "dublette_2": kunde(a, "Hof C", "DE333333333"),
            "name_wie_p1": kunde(a, "Hof A"),
            "ust_anderer_name": kunde(a, "Anderer Hof", "DE111111111"),
            "mandant_b": kunde(b, "Hof A", "DE111111111"),
            "fremd_verknuepft": kunde(a, "Hof F", bp=fremd),
            "neu_ohne_ust": lieferant(a, "Hof G"),
            "zweiter_gleichnamig": kunde(a, "Hof G"),
        }
        m = _migration()
        with Operations.context(MigrationContext.configure(c)):
            m.upgrade()
        yield x, m, c, ids, p1, a, b
        t.rollback()


def _partner(x, quelle, satz_id):
    if quelle == "kunde":
        return x("SELECT business_partner_id FROM domain_crm.customers WHERE id = :i", i=satz_id).scalar()
    return x("SELECT partner_id FROM domain_einkauf.lieferanten WHERE id = :i", i=satz_id).scalar()


def _klaerfall(x, satz_id):
    return x("SELECT grund FROM domain_crm.partner_klaerfaelle WHERE satz_id = :i", i=satz_id).scalar()


def test_regeln_der_rueckfuellung(bestand):
    x, _, _, ids, p1, a, b = bestand
    assert _partner(x, "kunde", ids["passt_p1"]) == p1
    gemeinsam = _partner(x, "kunde", ids["kunde_b"])
    assert gemeinsam and _partner(x, "lieferant", ids["lief_b"]) == gemeinsam
    rollen = x("SELECT tenant_id, is_customer, is_supplier, country FROM domain_crm.business_partners "
               "WHERE partner_id = :p", p=gemeinsam).one()
    assert (rollen.tenant_id, rollen.is_customer, rollen.is_supplier) == (a, True, True)
    assert x("SELECT is_customer FROM domain_crm.business_partners WHERE partner_id = :p", p=p1).scalar() is True

    for schluessel in ("dublette_1", "dublette_2"):
        assert _partner(x, "kunde", ids[schluessel]) is None
        assert "Dublette" in _klaerfall(x, ids[schluessel])
    assert "gleichen Namens" in _klaerfall(x, ids["name_wie_p1"])
    assert "anderen Namens" in _klaerfall(x, ids["ust_anderer_name"])
    assert "anderen Mandanten" in _klaerfall(x, ids["fremd_verknuepft"])

    eigen_b = _partner(x, "kunde", ids["mandant_b"])
    assert eigen_b and eigen_b != p1
    assert x("SELECT tenant_id FROM domain_crm.business_partners WHERE partner_id = :p", p=eigen_b).scalar() == b

    # Ohne USt-IdNr.: genau einer der beiden gleichnamigen Saetze bekommt einen Partner, der andere wird
    # Klaerfall statt zweiter Partner gleichen Namens.
    zugeordnet = [_partner(x, "lieferant", ids["neu_ohne_ust"]), _partner(x, "kunde", ids["zweiter_gleichnamig"])]
    faelle = [_klaerfall(x, ids["neu_ohne_ust"]), _klaerfall(x, ids["zweiter_gleichnamig"])]
    assert sum(1 for p in zugeordnet if p) == 1
    assert sum(1 for f in faelle if f and "gleichen Namens" in f) == 1
    assert x("SELECT tenant_id FROM domain_crm.partner_klaerfaelle WHERE satz_id = :i",
             i=ids["mandant_b"]).scalar() is None


def test_belegnummern_bleiben_und_downgrade_nimmt_nur_eigenes_zurueck(bestand):
    x, m, c, ids, p1, *_ = bestand
    vorher = x("SELECT id, customer_number FROM domain_crm.customers WHERE id = ANY(:i) ORDER BY id",
               i=list(ids.values())).all()
    with Operations.context(MigrationContext.configure(c)):
        m.downgrade()
    assert x("SELECT id, customer_number FROM domain_crm.customers WHERE id = ANY(:i) ORDER BY id",
             i=list(ids.values())).all() == vorher
    assert _partner(x, "kunde", ids["passt_p1"]) is None
    assert _partner(x, "kunde", ids["fremd_verknuepft"]) is not None  # nicht von der Migration gesetzt
    assert x("SELECT count(*) FROM domain_crm.business_partners WHERE partner_id = :p", p=p1).scalar() == 1
    assert x("SELECT to_regclass('domain_crm.partner_klaerfaelle')").scalar() is None
