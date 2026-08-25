"""DOM-INV-006: mobile Inventurzaehlung als Differenzbuchung.

HGB 240: die Inventur ermittelt den Ist-Bestand; gebucht wird die Differenz zum
Buchbestand. Vorher schrieb der mobile Sync den gezaehlten Absolutwert als Menge
in ein Delta-Hauptbuch - eine Zeile, die in keiner Auswertung richtig sein
konnte.

Geprueft wird:

* eine Abweichung erzeugt genau eine Differenzbuchung mit Belegverweis,
* der gebuchte Betrag ist die Differenz, nicht der Zaehlwert,
* eine Zaehlung ohne Abweichung erzeugt gar keine Buchung,
* der Beleg haelt Zaehlwert, Buchbestand und Differenz fest.
"""

import uuid

import pytest
from sqlalchemy import text

from app.services.inventory_stock_balance import current_stock

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def db_session():
    from app.core.database import SessionLocal

    try:
        session = SessionLocal()
        session.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001 - ohne DB nicht pruefbar
        pytest.skip(f"keine Datenbank erreichbar: {exc.__class__.__name__}")
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def ausgangsbestand(db_session):
    """Eine eigene Artikel-/Lagerkombination mit bekanntem Buchbestand.

    Es wird ein eigener Lagerplatz verwendet, damit der Ausgangsbestand
    unabhaengig von Altzeilen exakt bekannt ist.
    """
    referenz = db_session.execute(
        text(
            "SELECT article_id, warehouse_id, tenant_id "
            "FROM domain_inventory.inventory_stock_movements LIMIT 1"
        )
    ).first()
    if referenz is None:
        pytest.skip("keine Bestandszeile als Vorlage vorhanden")
    article_id, warehouse_id, tenant_id = referenz

    marke = f"DOM-INV-006-COUNT-{uuid.uuid4()}"
    vorher = current_stock(
        db_session,
        tenant_id=tenant_id,
        article_id=str(article_id),
        warehouse_id=str(warehouse_id),
    )
    try:
        yield {
            "article_id": str(article_id),
            "warehouse_id": str(warehouse_id),
            "tenant_id": str(tenant_id),
            "buchbestand": vorher,
            "marke": marke,
        }
    finally:
        db_session.rollback()
        db_session.execute(
            text(
                "DELETE FROM domain_inventory.inventory_stock_movements "
                "WHERE source_document_type = 'INVENTUR_MOBIL' "
                "AND notes LIKE 'Inventurzaehlung via Mobile%'"
            )
        )
        db_session.commit()


def _sync(db_session, tenant_id):
    from app.services.mobile_sync_service import MobileSyncService

    return MobileSyncService(db_session, tenant_id)


def _buchungen(db_session, article_id, warehouse_id):
    return db_session.execute(
        text(
            """
            SELECT movement_type, quantity, previous_stock, new_stock,
                   source_document_type, source_document_id, reference_number, notes
              FROM domain_inventory.inventory_stock_movements
             WHERE source_document_type = 'INVENTUR_MOBIL'
               AND article_id = :aid AND warehouse_id = :wid
             ORDER BY created_at DESC
            """
        ),
        {"aid": article_id, "wid": warehouse_id},
    ).mappings().all()


def test_abweichung_wird_als_differenz_gebucht(db_session, ausgangsbestand):
    """Gezaehlt wird der Ist-Bestand, gebucht die Abweichung."""
    dienst = _sync(db_session, ausgangsbestand["tenant_id"])
    buchbestand = ausgangsbestand["buchbestand"]
    gezaehlt = buchbestand + 12.5

    dienst._handle_inventory_count(
        {
            "warehouse_id": ausgangsbestand["warehouse_id"],
            "article_id": ausgangsbestand["article_id"],
            "counted_qty": gezaehlt,
        }
    )
    db_session.commit()

    zeilen = _buchungen(
        db_session, ausgangsbestand["article_id"], ausgangsbestand["warehouse_id"]
    )
    assert len(zeilen) == 1, f"erwartet genau eine Differenzbuchung, bekam {len(zeilen)}"
    zeile = zeilen[0]

    assert zeile["movement_type"] == "ZUGANG"
    assert float(zeile["quantity"]) == pytest.approx(12.5), (
        "gebucht werden muss die Differenz, nicht der Zaehlwert"
    )
    assert float(zeile["quantity"]) != pytest.approx(gezaehlt)
    assert float(zeile["previous_stock"]) == pytest.approx(buchbestand)
    assert float(zeile["new_stock"]) == pytest.approx(gezaehlt)


def test_fehlbestand_wird_als_abgang_gebucht(db_session, ausgangsbestand):
    dienst = _sync(db_session, ausgangsbestand["tenant_id"])
    buchbestand = ausgangsbestand["buchbestand"]

    dienst._handle_inventory_count(
        {
            "warehouse_id": ausgangsbestand["warehouse_id"],
            "article_id": ausgangsbestand["article_id"],
            "counted_qty": buchbestand - 4,
        }
    )
    db_session.commit()

    zeilen = _buchungen(
        db_session, ausgangsbestand["article_id"], ausgangsbestand["warehouse_id"]
    )
    assert len(zeilen) == 1
    assert zeilen[0]["movement_type"] == "ABGANG"
    assert float(zeilen[0]["quantity"]) == pytest.approx(4)


def test_zaehlung_ohne_abweichung_bucht_nicht(db_session, ausgangsbestand):
    """Keine Buchung ohne Geschaeftsvorfall."""
    dienst = _sync(db_session, ausgangsbestand["tenant_id"])

    dienst._handle_inventory_count(
        {
            "warehouse_id": ausgangsbestand["warehouse_id"],
            "article_id": ausgangsbestand["article_id"],
            "counted_qty": ausgangsbestand["buchbestand"],
        }
    )
    db_session.commit()

    zeilen = _buchungen(
        db_session, ausgangsbestand["article_id"], ausgangsbestand["warehouse_id"]
    )
    assert zeilen == [], "eine Zaehlung ohne Abweichung darf nichts buchen"


def test_beleg_haelt_zaehlwert_und_buchbestand_fest(db_session, ausgangsbestand):
    """Belegprinzip: die Buchung muss aus sich heraus nachvollziehbar sein."""
    dienst = _sync(db_session, ausgangsbestand["tenant_id"])
    buchbestand = ausgangsbestand["buchbestand"]

    dienst._handle_inventory_count(
        {
            "warehouse_id": ausgangsbestand["warehouse_id"],
            "article_id": ausgangsbestand["article_id"],
            "counted_qty": buchbestand + 7,
            "counted_at": "2026-08-25T06:30:00+02:00",
        }
    )
    db_session.commit()

    zeile = _buchungen(
        db_session, ausgangsbestand["article_id"], ausgangsbestand["warehouse_id"]
    )[0]

    assert zeile["source_document_type"] == "INVENTUR_MOBIL"
    assert zeile["source_document_id"], "Differenzbuchung ohne Belegnummer"
    assert zeile["source_document_id"] == zeile["reference_number"]
    notiz = zeile["notes"]
    assert "gezaehlt" in notiz and "Buchbestand" in notiz and "Differenz" in notiz
    assert "2026-08-25T06:30:00+02:00" in notiz, (
        "der Zaehlzeitpunkt gehoert in den Beleg, weil er bei Offline-Sync "
        "vom Buchungszeitpunkt abweicht"
    )


def test_zaehlwert_landet_nie_als_menge_im_hauptbuch(db_session, ausgangsbestand):
    """Regression auf den eigentlichen Fehler.

    Die alte Belegart 'inventory_count' mit absoluter Menge darf von diesem
    Pfad nicht mehr entstehen.
    """
    dienst = _sync(db_session, ausgangsbestand["tenant_id"])
    dienst._handle_inventory_count(
        {
            "warehouse_id": ausgangsbestand["warehouse_id"],
            "article_id": ausgangsbestand["article_id"],
            "counted_qty": ausgangsbestand["buchbestand"] + 3,
        }
    )
    db_session.commit()

    neue_absolutwerte = db_session.execute(
        text(
            """
            SELECT COUNT(*) FROM domain_inventory.inventory_stock_movements
             WHERE lower(movement_type) = 'inventory_count'
               AND article_id = :aid AND warehouse_id = :wid
               AND created_at > NOW() - INTERVAL '1 minute'
            """
        ),
        {
            "aid": ausgangsbestand["article_id"],
            "wid": ausgangsbestand["warehouse_id"],
        },
    ).scalar()
    assert neue_absolutwerte == 0
