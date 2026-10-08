"""Artikelnummer je Mandant; Dokumentspeicher ohne Rueckfall in den Prozessspeicher.

Bis zum 08.10.2026:

* war ``article_number`` systemweit eindeutig (``001_initial_schema``): Fuehrte ein
  Mandant "KAS-27", konnte kein zweiter den Artikel je anlegen — die Anlage prueft
  Dubletten je Mandant, die Datenbank lehnte trotzdem ab. Der Inventar-Seed suchte
  den Artikel ueber die Nummer allein und haengte ihn dem seedenden Mandanten um.
* fiel ``_list_docs`` auf den Prozessspeicher zurueck, sobald die Datenbank fuer
  den Mandanten nichts lieferte.
"""

from __future__ import annotations

import os
import uuid

import pytest

pytestmark = pytest.mark.integration

DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    os.environ.get("DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe"),
)
os.environ.setdefault("DATABASE_URL", DB_URL)

HAUS_A = f"an-a-{uuid.uuid4().hex[:6]}"
HAUS_B = f"an-b-{uuid.uuid4().hex[:6]}"


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as v:
            vorhanden = v.execute(text(
                "SELECT 1 FROM pg_constraint WHERE conname = 'uq_articles_mandant_nummer'"
            )).scalar()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    if not vorhanden:
        pytest.skip("Migration artikelnummer_mandant_20261008 nicht angewandt")
    return motor


@pytest.fixture
def verbindung(engine):
    """Aeussere Transaktion, am Ende verworfen."""
    from sqlalchemy import text

    v = engine.connect()
    aussen = v.begin()
    for haus in (HAUS_A, HAUS_B):
        v.execute(text("INSERT INTO domain_shared.tenants (id, name) VALUES (:i, :n) ON CONFLICT (id) DO NOTHING"),
                  {"i": haus, "n": f"Pruefbetrieb {haus}"})
    yield v
    aussen.rollback()
    v.close()


def artikel(v, haus: str, nummer: str) -> str:
    from sqlalchemy import text

    kennung = str(uuid.uuid4())
    v.execute(text("INSERT INTO domain_inventory.articles (id, article_number, name, tenant_id, is_active) "
                   "VALUES (:i, :n, 'KAS 27', :h, true)"), {"i": kennung, "n": nummer, "h": haus})
    return kennung


class TestArtikelnummer:
    def test_zwei_mandanten_fuehren_dieselbe_nummer(self, verbindung):
        nummer = f"KAS-{uuid.uuid4().hex[:6]}"
        artikel(verbindung, HAUS_A, nummer)
        artikel(verbindung, HAUS_B, nummer)

    def test_im_selben_mandanten_bleibt_sie_eindeutig(self, verbindung):
        from sqlalchemy.exc import IntegrityError

        nummer = f"KAS-{uuid.uuid4().hex[:6]}"
        artikel(verbindung, HAUS_A, nummer)
        punkt = verbindung.begin_nested()
        with pytest.raises(IntegrityError):
            artikel(verbindung, HAUS_A, nummer)
        punkt.rollback()

    def test_die_nummer_findet_den_eigenen_artikel(self, verbindung):
        from sqlalchemy.orm import Session

        from app.services.articles_service import get_article_or_404

        nummer = f"KAS-{uuid.uuid4().hex[:6]}"
        artikel(verbindung, HAUS_A, nummer)
        eigener = artikel(verbindung, HAUS_B, nummer)
        with Session(bind=verbindung, join_transaction_mode="create_savepoint") as db:
            assert str(get_article_or_404(db, nummer, HAUS_B).id) == eigener

    def test_der_seed_haengt_keinen_fremden_artikel_um(self, verbindung):
        from sqlalchemy import text

        from app.seeds.inventory_seed import ARTICLES, ensure_articles

        nummer = ARTICLES[0]["article_number"]
        verbindung.execute(text("DELETE FROM domain_inventory.articles WHERE article_number = :n "
                                "AND tenant_id IN (:a, :b)"), {"n": nummer, "a": HAUS_A, "b": HAUS_B})
        fremd = artikel(verbindung, HAUS_A, nummer)
        ensure_articles(verbindung, HAUS_B)
        besitzer = dict(verbindung.execute(text(
            "SELECT id, tenant_id FROM domain_inventory.articles WHERE article_number = :n "
            "AND tenant_id IN (:a, :b)"), {"n": nummer, "a": HAUS_A, "b": HAUS_B}).all())
        assert besitzer[fremd] == HAUS_A
        assert sorted(besitzer.values()) == sorted([HAUS_A, HAUS_B])


class TestDokumentspeicher:
    def test_ein_leerer_mandant_sieht_keine_belege_aus_dem_prozessspeicher(self, verbindung):
        from sqlalchemy.orm import Session

        from app.api.v1.endpoints.compat import _list_docs
        from app.documents.router_helpers import save_to_store

        nummer = f"PO-MEM-{uuid.uuid4().hex[:6]}"
        save_to_store("purchase_order", nummer, {"purchaseOrderNumber": nummer, "tenantId": HAUS_A})
        with Session(bind=verbindung, join_transaction_mode="create_savepoint") as db:
            assert _list_docs(db, "purchase_order", tenant_id=HAUS_A) == []
