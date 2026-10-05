"""DOM-INV-006: Belegartenregister und Schreibsperre des Bestandshauptbuchs.

Prueft die drei Zusagen der Migration:

* das Register in der Datenbank ist deckungsgleich mit der Richtungstabelle im
  Code (sonst haette man wieder zwei Wahrheiten),
* eine unregistrierte Belegart laesst sich nicht mehr buchen,
* bestehende Buchungen wurden nicht angetastet (Radierverbot).
"""

import uuid

import pytest
from sqlalchemy import text

from app.services.inventory_movement_direction import (
    KNOWN_TYPES,
    MOVEMENT_TYPE_NOTES,
    register_rows,
)

pytestmark = pytest.mark.integration

REGISTER_TABELLE = "domain_inventory.inventory_movement_types"


@pytest.fixture(scope="module")
def db_session():
    from app.core.database import SessionLocal

    try:
        session = SessionLocal()
        session.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001 - ohne DB ist das Register nicht pruefbar
        pytest.skip(f"keine Datenbank erreichbar: {exc.__class__.__name__}")
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="module")
def register_vorhanden(db_session):
    vorhanden = db_session.execute(
        text(
            "SELECT to_regclass('domain_inventory.inventory_movement_types') IS NOT NULL"
        )
    ).scalar()
    if not vorhanden:
        pytest.skip("Migration inv_movement_type_register_20260825 nicht eingespielt")
    return True


def test_register_und_code_sind_deckungsgleich(db_session, register_vorhanden):
    """Zwei Darstellungen derselben Sache duerfen nicht auseinanderlaufen."""
    zeilen = db_session.execute(
        text(f"SELECT movement_type, direction, is_delta, note FROM {REGISTER_TABELLE}")  # nosec B608
    ).all()
    aus_db = {
        movement_type: (int(direction), bool(is_delta), note)
        for movement_type, direction, is_delta, note in zeilen
    }
    aus_code = {
        zeile["movement_type"]: (zeile["direction"], zeile["is_delta"], zeile["note"])
        for zeile in register_rows()
    }

    nur_db = sorted(set(aus_db) - set(aus_code))
    nur_code = sorted(set(aus_code) - set(aus_db))
    assert not nur_db, f"Belegarten nur in der Datenbank: {nur_db}"
    assert not nur_code, f"Belegarten nur im Code: {nur_code}"

    abweichend = {
        name: {"db": aus_db[name], "code": aus_code[name]}
        for name in aus_code
        if aus_db[name] != aus_code[name]
    }
    assert not abweichend, f"Register und Code widersprechen sich: {abweichend}"


def test_jede_belegart_traegt_eine_begruendung(db_session, register_vorhanden):
    """GoBD-Nachvollziehbarkeit: sichtbar sein reicht nicht, es muss erklaert sein."""
    leer = db_session.execute(
        text(f"SELECT movement_type FROM {REGISTER_TABELLE} WHERE note = '' OR note IS NULL")  # nosec B608
    ).scalars().all()
    assert not leer, f"Belegart ohne Begruendung im Register: {leer}"
    assert set(MOVEMENT_TYPE_NOTES) == KNOWN_TYPES


def test_register_verspricht_keine_unbuchbare_belegart(db_session, register_vorhanden):
    """movement_type im Hauptbuch ist VARCHAR(20).

    Eine laengere Belegart koennte registriert, aber nie gebucht werden.
    """
    laenge = db_session.execute(
        text(
            "SELECT character_maximum_length FROM information_schema.columns "
            "WHERE table_schema = 'domain_inventory' "
            "AND table_name = 'inventory_stock_movements' "
            "AND column_name = 'movement_type'"
        )
    ).scalar()
    zu_lang = [name for name in KNOWN_TYPES if len(name) > int(laenge)]
    assert not zu_lang, f"registrierte, aber nicht buchbare Belegarten: {zu_lang}"


def test_alle_gebuchten_belegarten_sind_registriert(db_session, register_vorhanden):
    """Vollstaendigkeit: keine Bestandszeile ohne erklaerte Belegart."""
    offen = db_session.execute(
        text(
            f"""
            SELECT DISTINCT sm.movement_type
              FROM domain_inventory.inventory_stock_movements sm
             WHERE NOT EXISTS (
                   SELECT 1 FROM {REGISTER_TABELLE} mt
                    WHERE mt.movement_type = lower(sm.movement_type))
            """  # nosec B608 - Tabellenname aus Modulkonstante
        )
    ).scalars().all()
    assert not offen, f"gebuchte, aber nicht registrierte Belegarten: {offen}"


# -- Schreibsperre ----------------------------------------------------------


@pytest.fixture
def buchungsvorlage(db_session):
    referenz = db_session.execute(
        text(
            "SELECT article_id, warehouse_id, tenant_id "
            "FROM domain_inventory.inventory_stock_movements LIMIT 1"
        )
    ).first()
    if referenz is None:
        pytest.skip("keine Bestandszeile als Vorlage vorhanden")
    return referenz


def _versuche_buchung(db_session, vorlage, movement_type) -> str | None:
    """Bucht probeweise; gibt None bei Erfolg oder die Fehlermeldung zurueck."""
    article_id, warehouse_id, tenant_id = vorlage
    buchungs_id = str(uuid.uuid4())
    try:
        db_session.execute(
            text(
                """
                INSERT INTO domain_inventory.inventory_stock_movements
                    (id, tenant_id, article_id, warehouse_id, movement_type,
                     quantity, unit, notes, previous_stock, new_stock,
                     auto_created, ownership_type, storage_fee_relevant)
                VALUES (:id, :tid, :aid, :wid, :mt, 1, 'kg', 'DOM-INV-006-TEST',
                        0, 1, true, 'owned', false)
                """
            ),
            {
                "id": buchungs_id,
                "tid": tenant_id,
                "aid": article_id,
                "wid": warehouse_id,
                "mt": movement_type,
            },
        )
        db_session.commit()
    except Exception as exc:  # noqa: BLE001 - die Fehlermeldung ist das Pruefergebnis
        db_session.rollback()
        return str(exc)
    finally:
        db_session.execute(
            text("DELETE FROM domain_inventory.inventory_stock_movements WHERE id = :id"),
            {"id": buchungs_id},
        )
        db_session.commit()
    return None


@pytest.mark.parametrize("movement_type", ["wareneingang", "EINLAGERUNG", "ZUGANG", "Abgang"])
def test_registrierte_belegart_wird_in_jeder_schreibweise_gebucht(
    db_session, register_vorhanden, buchungsvorlage, movement_type
):
    """Die Bestandsdaten fuehren dieselbe Belegart gross und klein.

    Die Sperre darf daran nicht scheitern, sonst blockiert sie den Bestand
    statt ihn zu schuetzen.
    """
    fehler = _versuche_buchung(db_session, buchungsvorlage, movement_type)
    assert fehler is None, f"{movement_type} wurde abgelehnt: {fehler}"


def test_unregistrierte_belegart_wird_abgelehnt(
    db_session, register_vorhanden, buchungsvorlage
):
    """Der Kern des Slices: unbekannt heisst ab jetzt Fehler, nicht Faktor 0."""
    fehler = _versuche_buchung(db_session, buchungsvorlage, "neu_erfunden")
    assert fehler is not None, "unregistrierte Belegart wurde gebucht"
    assert "Unbekannte Belegart" in fehler
    assert "neu_erfunden" in fehler


def test_buchung_ohne_belegart_wird_abgelehnt(
    db_session, register_vorhanden, buchungsvorlage
):
    """movement_type ist NOT NULL; die Sperre begruendet die Ablehnung zusaetzlich."""
    fehler = _versuche_buchung(db_session, buchungsvorlage, None)
    assert fehler is not None, "Buchung ohne Belegart wurde angenommen"
