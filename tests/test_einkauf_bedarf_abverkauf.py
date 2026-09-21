"""Der Bedarf kommt aus dem Abverkauf, nicht aus einem gepflegten Sollbestand.

``engine_lager`` vergleicht den Bestand mit Melde- und Sollbestand. Das ist
eine Annahme aus dem Stammsatz: Sie weiss nicht, ob ein Artikel gerade laeuft
oder steht. ``engine_bedarf`` rechnet aus den Bewegungen — was rausgegangen
ist, auf den Horizont hochgerechnet, plus Wiederbeschaffungszeit, minus dem,
was da ist.

Geprueft wird an einem Artikel mit bekanntem Abverkauf: 2 t am Tag, 90 Tage
lang. Damit ist jede Zahl im Ergebnis nachrechenbar, statt nur plausibel.

Ohne erreichbare Datenbank wird uebersprungen, nicht als gruen gewertet.
"""

from __future__ import annotations

import os
import uuid
from datetime import date, timedelta

import pytest

pytestmark = pytest.mark.integration

DB_URL = os.environ.get(
    "DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_neuro_erp"
)
os.environ.setdefault("DATABASE_URL", DB_URL)

#: Der Artikel geht mit zwei Tonnen am Tag raus — 180 t in 90 Tagen.
ABVERKAUF_PRO_TAG = 2.0
TAGE_MIT_ABVERKAUF = 90


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        e = create_engine(DB_URL)
        with e.connect() as c:
            c.execute(text("SELECT 1"))
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    return e


@pytest.fixture()
def artikel_mit_abverkauf(engine):
    """Ein Artikel, ein Lagerparameter, 90 Tage taeglicher Abgang."""
    from sqlalchemy import text

    mandant = f"test-{uuid.uuid4().hex[:8]}"
    artikel_id = str(uuid.uuid4())
    lager_id = str(uuid.uuid4())
    heute = date.today()

    with engine.begin() as v:
        v.execute(
            text(
                "INSERT INTO domain_shared.tenants (id, name, domain, is_active) "
                "VALUES (:id, :id, :d, true) ON CONFLICT (id) DO NOTHING"
            ),
            {"id": mandant, "d": f"{mandant}.test"},
        )
        v.execute(
            text(
                "INSERT INTO domain_inventory.warehouses "
                "(id, tenant_id, warehouse_code, name, address, city, postal_code) "
                "VALUES (:id, :t, :code, 'Testlager', 'Teststrasse 1', 'Testdorf', '00000')"
            ),
            {"id": lager_id, "t": mandant, "code": f"L-{uuid.uuid4().hex[:5].upper()}"},
        )
        v.execute(
            text(
                "INSERT INTO domain_inventory.articles "
                "(id, tenant_id, article_number, name, mhd_erforderlich, lagerartikel, "
                " lagerorte, chargenpflicht, qs_pruefung_erforderlich, bio_kennzeichnung, "
                " gmp_plus_relevanz, unit, category, sales_price, warengruppe) "
                "VALUES (:id, :t, :nr, :name, false, true, '[]'::jsonb, false, false, "
                "        false, false, 't', 'Futtermittel', 0, 'Futtermittel')"
            ),
            {
                "id": artikel_id,
                "t": mandant,
                "nr": f"ART-{uuid.uuid4().hex[:6].upper()}",
                "name": "Testweizen",
            },
        )
        v.execute(
            text(
                "INSERT INTO domain_einkauf.artikel_lager_parameter "
                "(id, tenant_id, article_id, mindestbestand, maximalbestand, meldebestand, "
                " wiederbeschaffungs_tage, std_einheit, aktiv) "
                "VALUES (:id, :t, :a, 100, 100000, 150, 10, 't', true)"
            ),
            {"id": str(uuid.uuid4()), "t": mandant, "a": artikel_id},
        )

        # Erst ein Zugang, damit ein Bestand dasteht, dann der taegliche Abgang.
        v.execute(
            text(
                "INSERT INTO domain_inventory.inventory_stock_movements "
                "(id, tenant_id, article_id, warehouse_id, movement_type, quantity, "
                " previous_stock, new_stock, auto_created, ownership_type, "
                " storage_fee_relevant, movement_date, created_at) "
                # Nur 250 t Anfangsbestand: Nach 180 t Abverkauf bleiben 70 t,
                # und damit liegt der Artikel unter dem Mindestbestand — sonst
                # gibt es keine Fehlmenge und nichts zu optimieren.
                "VALUES (:id, :t, :a, :w, 'in', 250, 0, 250, false, 'own', false, "
                "        :d, :d)"
            ),
            {
                "id": str(uuid.uuid4()),
                "t": mandant,
                "a": artikel_id,
                "w": lager_id,
                "d": heute - timedelta(days=TAGE_MIT_ABVERKAUF + 1),
            },
        )
        for tag in range(TAGE_MIT_ABVERKAUF):
            datum = heute - timedelta(days=TAGE_MIT_ABVERKAUF - tag)
            v.execute(
                text(
                    "INSERT INTO domain_inventory.inventory_stock_movements "
                    "(id, tenant_id, article_id, warehouse_id, movement_type, quantity, "
                    " previous_stock, new_stock, auto_created, ownership_type, "
                    " storage_fee_relevant, movement_date, created_at) "
                    "VALUES (:id, :t, :a, :w, 'out', :menge, :vor, :nach, false, 'own', "
                    "        false, :d, :d)"
                ),
                {
                    "id": str(uuid.uuid4()),
                    "t": mandant,
                    "a": artikel_id,
                    "w": lager_id,
                    "menge": ABVERKAUF_PRO_TAG,
                    "vor": 250 - tag * ABVERKAUF_PRO_TAG,
                    "nach": 250 - (tag + 1) * ABVERKAUF_PRO_TAG,
                    "d": datum,
                },
            )

    try:
        yield {"mandant": mandant, "artikel_id": artikel_id, "lager_id": lager_id}
    finally:
        with engine.begin() as v:
            for sql in (
                "DELETE FROM domain_inventory.inventory_stock_movements WHERE tenant_id = :t",
                "DELETE FROM domain_einkauf.artikel_lager_parameter WHERE tenant_id = :t",
                "DELETE FROM domain_inventory.articles WHERE tenant_id = :t",
                "DELETE FROM domain_inventory.warehouses WHERE tenant_id = :t",
                "DELETE FROM domain_shared.tenants WHERE id = :t",
            ):
                v.execute(text(sql), {"t": mandant})


@pytest.fixture()
def db(engine):
    from sqlalchemy.orm import sessionmaker

    sitzung = sessionmaker(bind=engine)()
    try:
        yield sitzung
    finally:
        sitzung.close()


def rechne(db, mandant: str, **kwargs) -> list[dict]:
    from modules.einkauf.services.bestellvorschlag_service import engine_bedarf

    return engine_bedarf(db, tenant_id=mandant, nur_mit_bedarf=False, **kwargs)


def test_der_abverkauf_wird_aus_den_bewegungen_gelesen(db, artikel_mit_abverkauf) -> None:
    zeilen = rechne(db, artikel_mit_abverkauf["mandant"], horizont="monatlich")
    assert len(zeilen) == 1
    zeile = zeilen[0]

    # Rueckschau 90 Tage, 2 t am Tag.
    assert zeile["abverkauf_menge"] == pytest.approx(180.0, abs=0.01)
    assert zeile["abverkauf_pro_tag"] == pytest.approx(2.0, abs=0.01)


def test_der_horizont_aendert_den_bedarf(db, artikel_mit_abverkauf) -> None:
    """Taeglich, woechentlich, monatlich — derselbe Abverkauf, andere Deckung."""
    mandant = artikel_mit_abverkauf["mandant"]
    bedarf = {
        h: rechne(db, mandant, horizont=h)[0]["bedarf"]
        for h in ("taeglich", "woechentlich", "monatlich")
    }

    # Deckung ist Horizont plus Wiederbeschaffungszeit (10 Tage), mal 2 t.
    # Taeglich rechnet ueber 28 Tage Rueckschau, dort ist der Schnitt anders.
    assert bedarf["monatlich"] > bedarf["woechentlich"] > bedarf["taeglich"], bedarf
    assert bedarf["monatlich"] == pytest.approx((30 + 10) * 2.0, rel=0.05)


def test_saisonal_schaut_ins_vorjahr_nicht_auf_den_letzten_monat(db, artikel_mit_abverkauf) -> None:
    """Im Duengergeschaeft sagt der November nichts ueber den Maerz.

    Der Testartikel hat **kein** Vorjahr — saisonal muss deshalb 0 Abverkauf
    sehen, waehrend monatlich 180 t sieht. Genau daran zeigt sich, dass das
    Fenster wirklich verschoben wird und nicht nur anders skaliert.
    """
    mandant = artikel_mit_abverkauf["mandant"]
    saisonal = rechne(db, mandant, horizont="saisonal")[0]
    monatlich = rechne(db, mandant, horizont="monatlich")[0]

    assert monatlich["abverkauf_menge"] > 0
    assert saisonal["abverkauf_menge"] == 0.0
    assert saisonal["abverkauf_fenster_von"] < monatlich["abverkauf_fenster_von"]


def test_ohne_kostensaetze_wird_nicht_optimiert(db, artikel_mit_abverkauf) -> None:
    """Eine erfundene Losgroesse waere schlimmer als keine."""
    zeile = rechne(db, artikel_mit_abverkauf["mandant"], horizont="monatlich")[0]
    assert zeile["lagerkosten"] == 0.0
    assert zeile["frachtkosten"] == 0.0
    assert "keine Optimierung" in zeile["begruendung"]


def test_mit_kostensaetzen_kommt_die_losgroesse(db, artikel_mit_abverkauf) -> None:
    """sqrt(2 · Bedarf · Fracht / Lagerkosten) — nachgerechnet."""
    zeile = rechne(
        db,
        artikel_mit_abverkauf["mandant"],
        horizont="monatlich",
        lagerkosten_satz=0.05,
        frachtkosten_fix=200.0,
    )[0]

    fehlmenge = zeile["bedarf"] + zeile["mindestbestand"] - zeile["ist_bestand"] + zeile["offene_auftraege"]
    erwartet = (2 * fehlmenge * 200.0 / 0.05) ** 0.5
    assert zeile["vorschlag_menge"] == pytest.approx(erwartet, rel=0.01), zeile["begruendung"]
    assert zeile["lagerkosten"] > 0 and zeile["frachtkosten"] > 0


def test_ein_artikel_ohne_abverkauf_bekommt_keine_losgroesse(db, engine) -> None:
    """Sonst raet die Formel zu einem Lager, das niemand leert."""
    from sqlalchemy import text
    from modules.einkauf.services.bestellvorschlag_service import engine_bedarf

    mandant = f"test-{uuid.uuid4().hex[:8]}"
    artikel_id = str(uuid.uuid4())
    with engine.begin() as v:
        v.execute(
            text(
                "INSERT INTO domain_shared.tenants (id, name, domain, is_active) "
                "VALUES (:id, :id, :d, true) ON CONFLICT (id) DO NOTHING"
            ),
            {"id": mandant, "d": f"{mandant}.test"},
        )
        v.execute(
            text(
                "INSERT INTO domain_inventory.articles "
                "(id, tenant_id, article_number, name, mhd_erforderlich, lagerartikel, "
                " lagerorte, chargenpflicht, qs_pruefung_erforderlich, bio_kennzeichnung, "
                " gmp_plus_relevanz, unit, category, sales_price) "
                "VALUES (:id, :t, :nr, 'Ladenhueter', false, true, '[]'::jsonb, false, "
                "        false, false, false, 't', 'Futtermittel', 0)"
            ),
            {"id": artikel_id, "t": mandant, "nr": f"ART-{uuid.uuid4().hex[:6].upper()}"},
        )
        v.execute(
            text(
                "INSERT INTO domain_einkauf.artikel_lager_parameter "
                "(id, tenant_id, article_id, mindestbestand, maximalbestand, aktiv) "
                "VALUES (:id, :t, :a, 1000, 5000, true)"
            ),
            {"id": str(uuid.uuid4()), "t": mandant, "a": artikel_id},
        )

    from sqlalchemy.orm import sessionmaker

    sitzung = sessionmaker(bind=engine)()
    try:
        zeilen = engine_bedarf(
            sitzung, tenant_id=mandant, horizont="monatlich", nur_mit_bedarf=False,
            lagerkosten_satz=0.02, frachtkosten_fix=250.0,
        )
        assert len(zeilen) == 1
        # Nur die Fehlmenge zum Mindestbestand, nicht das Ergebnis der Formel.
        assert zeilen[0]["vorschlag_menge"] == pytest.approx(1000.0, abs=0.01)
        assert "Kein Abverkauf" in zeilen[0]["begruendung"]
    finally:
        sitzung.close()
        with engine.begin() as v:
            for sql in (
                "DELETE FROM domain_einkauf.artikel_lager_parameter WHERE tenant_id = :t",
                "DELETE FROM domain_inventory.articles WHERE tenant_id = :t",
                "DELETE FROM domain_shared.tenants WHERE id = :t",
            ):
                v.execute(text(sql), {"t": mandant})


def test_die_offene_auftragsmenge_vergiftet_die_sitzung_nicht(db, artikel_mit_abverkauf) -> None:
    """Der Helfer las ein Schema, das es nicht gibt — und riss alles mit.

    Eine gescheiterte Anweisung macht die Transaktion unbrauchbar; jede
    folgende Abfrage derselben Sitzung scheitert an einem Fehler, den sie nicht
    verursacht hat. Das ``except`` verschluckte beides. Hier wird geprueft,
    dass nach dem Aufruf noch gearbeitet werden kann.
    """
    from sqlalchemy import text
    from modules.einkauf.services.bestellvorschlag_service import _open_sales_quantity

    menge = _open_sales_quantity(db, artikel_mit_abverkauf["artikel_id"], artikel_mit_abverkauf["mandant"])
    assert menge >= 0
    # Die Sitzung muss danach noch brauchbar sein.
    assert db.execute(text("SELECT 1")).scalar() == 1
