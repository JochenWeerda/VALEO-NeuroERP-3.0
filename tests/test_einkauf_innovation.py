"""Eine Artikelprobe wird nachgeschaut, nicht nur bestellt.

Ein neuer Artikel hat keine Historie — genau deshalb ist er ein eigener
Bestellfall und keine Bedarfsrechnung. Was er stattdessen braucht, ist eine
Nachschau: Was wurde zur Probe bestellt, was ist davon verkauft, und reicht
das fuer eine Entscheidung?

Geprueft wird an drei Proben mit bekanntem Ausgang: eine, die laeuft, eine,
die liegen bleibt, und eine, die noch gar nicht geliefert ist. Damit ist jede
Empfehlung nachvollziehbar statt plausibel.

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


def _artikel(v, mandant: str, name: str) -> tuple[str, str]:
    from sqlalchemy import text

    artikel_id = str(uuid.uuid4())
    nummer = f"ART-{uuid.uuid4().hex[:6].upper()}"
    v.execute(
        text(
            "INSERT INTO domain_inventory.articles "
            "(id, tenant_id, article_number, name, mhd_erforderlich, lagerartikel, "
            " lagerorte, chargenpflicht, qs_pruefung_erforderlich, bio_kennzeichnung, "
            " gmp_plus_relevanz, unit, category, sales_price) "
            "VALUES (:id, :t, :nr, :name, false, true, '[]'::jsonb, false, false, "
            "        false, false, 't', 'Futtermittel', 0)"
        ),
        {"id": artikel_id, "t": mandant, "nr": nummer, "name": name},
    )
    return artikel_id, nummer


def _bewegung(v, mandant: str, artikel_id: str, lager_id: str, art: str,
              menge: float, datum: date) -> None:
    from sqlalchemy import text

    v.execute(
        text(
            "INSERT INTO domain_inventory.inventory_stock_movements "
            "(id, tenant_id, article_id, warehouse_id, movement_type, quantity, "
            " previous_stock, new_stock, auto_created, ownership_type, "
            " storage_fee_relevant, movement_date, created_at) "
            "VALUES (:id, :t, :a, :w, :art, :menge, 0, 0, false, 'own', false, :d, :d)"
        ),
        {
            "id": str(uuid.uuid4()), "t": mandant, "a": artikel_id, "w": lager_id,
            "art": art, "menge": menge, "d": datum,
        },
    )


@pytest.fixture()
def proben(engine):
    """Drei Proben: eine laeuft, eine bleibt liegen, eine ist nicht da."""
    from sqlalchemy import text

    mandant = f"test-{uuid.uuid4().hex[:8]}"
    lager_id = str(uuid.uuid4())
    lieferant_id = str(uuid.uuid4())
    heute = date.today()
    geliefert_am = heute - timedelta(days=60)

    daten: dict[str, str] = {}
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
                "VALUES (:id, :t, :c, 'Testlager', 'Weg 1', 'Testdorf', '00000')"
            ),
            {"id": lager_id, "t": mandant, "c": f"L-{uuid.uuid4().hex[:5].upper()}"},
        )
        v.execute(
            text(
                "INSERT INTO domain_einkauf.lieferanten "
                "(id, tenant_id, lieferantennummer, firmenname) "
                "VALUES (:id, :t, :nr, 'Probenlieferant')"
            ),
            {"id": lieferant_id, "t": mandant, "nr": f"LF-{uuid.uuid4().hex[:5].upper()}"},
        )

        laeuft_id, laeuft_nr = _artikel(v, mandant, "Laeufer")
        liegt_id, liegt_nr = _artikel(v, mandant, "Ladenhueter")
        wartet_id, wartet_nr = _artikel(v, mandant, "Noch unterwegs")
        daten.update(laeuft_nr=laeuft_nr, liegt_nr=liegt_nr, wartet_nr=wartet_nr)

        # Der Laeufer: 100 bestellt, 80 verkauft (80 %).
        _bewegung(v, mandant, laeuft_id, lager_id, "wareneingang", 100, geliefert_am)
        _bewegung(v, mandant, laeuft_id, lager_id, "out", 80, geliefert_am + timedelta(days=20))
        # Der Ladenhueter: 100 bestellt, 10 verkauft (10 %).
        _bewegung(v, mandant, liegt_id, lager_id, "wareneingang", 100, geliefert_am)
        _bewegung(v, mandant, liegt_id, lager_id, "out", 10, geliefert_am + timedelta(days=30))
        # Der Wartende bekommt keine Bewegung.

        for artikel_id, nummer, name in (
            (laeuft_id, laeuft_nr, "Laeufer"),
            (liegt_id, liegt_nr, "Ladenhueter"),
            (wartet_id, wartet_nr, "Noch unterwegs"),
        ):
            bestell_id = str(uuid.uuid4())
            v.execute(
                text(
                    "INSERT INTO domain_einkauf.bestellungen "
                    "(id, tenant_id, bestellnummer, lieferant_id, bestelldatum, status, "
                    " bestellfall, neuer_artikel, innovationshinweis) "
                    "VALUES (:id, :t, :nr, :lf, :d, 'entwurf', 'innovation', true, "
                    "        'Vertrieb will es testen')"
                ),
                {
                    "id": bestell_id, "t": mandant,
                    "nr": f"EK-{uuid.uuid4().hex[:8].upper()}",
                    "lf": lieferant_id, "d": geliefert_am - timedelta(days=5),
                },
            )
            v.execute(
                text(
                    "INSERT INTO domain_einkauf.bestellung_positionen "
                    "(id, bestellung_id, pos_nr, article_id, artikel_nr, "
                    " artikel_bezeichnung, menge, einheit) "
                    "VALUES (:id, :b, 1, :a, :nr, :bez, 100, 't')"
                ),
                {
                    "id": str(uuid.uuid4()), "b": bestell_id, "a": artikel_id,
                    "nr": nummer, "bez": name,
                },
            )

    try:
        yield {"mandant": mandant, **daten}
    finally:
        with engine.begin() as v:
            for sql in (
                "DELETE FROM domain_einkauf.bestellung_positionen WHERE bestellung_id IN "
                "(SELECT id FROM domain_einkauf.bestellungen WHERE tenant_id = :t)",
                "DELETE FROM domain_einkauf.bestellungen WHERE tenant_id = :t",
                "DELETE FROM domain_einkauf.lieferanten WHERE tenant_id = :t",
                "DELETE FROM domain_inventory.inventory_stock_movements WHERE tenant_id = :t",
                "DELETE FROM domain_inventory.articles WHERE tenant_id = :t",
                "DELETE FROM domain_inventory.warehouses WHERE tenant_id = :t",
                "DELETE FROM domain_shared.tenants WHERE id = :t",
            ):
                v.execute(text(sql), {"t": mandant})


@pytest.fixture()
def stand(engine, proben):
    from sqlalchemy.orm import sessionmaker
    from app.services.procurement_service import ProcurementService

    sitzung = sessionmaker(bind=engine)()
    try:
        zeilen = ProcurementService(sitzung, proben["mandant"]).innovationen_bewerten()
    finally:
        sitzung.close()
    return {z["artikel_nr"]: z for z in zeilen}


def test_jede_probe_taucht_auf(stand, proben) -> None:
    assert set(stand) == {proben["laeuft_nr"], proben["liegt_nr"], proben["wartet_nr"]}


def test_was_laeuft_soll_ins_sortiment(stand, proben) -> None:
    zeile = stand[proben["laeuft_nr"]]
    assert zeile["verkauft"] == pytest.approx(80.0, abs=0.01)
    assert zeile["abverkaufsquote"] == pytest.approx(0.8, abs=0.01)
    assert zeile["stand"] == "aufnehmen"
    # Die Begruendung gehoert zur Empfehlung, sonst ist sie ein Orakel.
    assert "80%" in zeile["empfehlung"] or "80 %" in zeile["empfehlung"]


def test_was_liegen_bleibt_bindet_platz(stand, proben) -> None:
    zeile = stand[proben["liegt_nr"]]
    assert zeile["abverkaufsquote"] == pytest.approx(0.1, abs=0.01)
    assert zeile["stand"] == "auslisten"
    assert "Platz" in zeile["empfehlung"]


def test_was_nicht_da_ist_wird_nicht_beurteilt(stand, proben) -> None:
    """Solange die Ware fehlt, kann sie sich nicht verkaufen."""
    zeile = stand[proben["wartet_nr"]]
    assert zeile["stand"] == "wartet_auf_lieferung"
    assert zeile["erste_lieferung"] is None
    assert zeile["tage_im_regal"] == 0


def test_gerechnet_wird_ab_der_lieferung_nicht_ab_der_bestellung(stand, proben) -> None:
    """Die Bestellung lag fuenf Tage vor der Lieferung — die zaehlen nicht mit."""
    zeile = stand[proben["laeuft_nr"]]
    assert zeile["tage_im_regal"] == 60, zeile
    assert zeile["erste_lieferung"] > zeile["bestelldatum"]


def test_vor_der_mindestzeit_gibt_es_kein_urteil(engine, proben) -> None:
    """Ein Urteil nach drei Tagen sagt mehr ueber den Zufall als den Artikel."""
    from sqlalchemy import text
    from sqlalchemy.orm import sessionmaker
    from app.services.procurement_service import ProcurementService

    # Die Lieferung auf vorgestern schieben.
    with engine.begin() as v:
        v.execute(
            text(
                "UPDATE domain_inventory.inventory_stock_movements "
                "SET movement_date = CURRENT_DATE - 2 "
                "WHERE tenant_id = :t AND lower(movement_type) = 'wareneingang'"
            ),
            {"t": proben["mandant"]},
        )

    sitzung = sessionmaker(bind=engine)()
    try:
        zeilen = ProcurementService(sitzung, proben["mandant"]).innovationen_bewerten()
    finally:
        sitzung.close()

    beurteilt = {z["artikel_nr"]: z["stand"] for z in zeilen}
    assert beurteilt[proben["laeuft_nr"]] == "zu_frueh"
    assert beurteilt[proben["liegt_nr"]] == "zu_frueh"
