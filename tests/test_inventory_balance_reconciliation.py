"""DOM-INV-006: Abstimmbericht Bestandshauptbuch.

Der Bericht macht das Abgleich-Gate aus DOM-INV-005 pruefbar. Sein Wert steht
und faellt damit, dass er zwei Dinge zeigt, die eine blosse Saldozahl verbirgt:
woraus der Saldo entsteht, und was im Hauptbuch steht, aber nicht eingeht.
"""

import uuid

import pytest
from sqlalchemy import text

from app.services.inventory_balance_reconciliation import als_text, erstelle_bericht

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
def bewegungsprobe(db_session):
    """Bekannte Probe: Saldo +100, dazu eine nicht bestandswirksame Zeile."""
    referenz = db_session.execute(
        text(
            "SELECT article_id, warehouse_id, tenant_id "
            "FROM domain_inventory.inventory_stock_movements LIMIT 1"
        )
    ).first()
    if referenz is None:
        pytest.skip("keine Bestandszeile als Vorlage vorhanden")
    article_id, warehouse_id, tenant_id = referenz
    marke = f"DOM-INV-006-ABST-{uuid.uuid4()}"

    zeilen = [
        ("wareneingang", 100),
        ("ZUGANG", 50),
        ("warenausgang", 30),
        ("ABGANG", 20),
        ("reservation", 999),
    ]
    for movement_type, menge in zeilen:
        db_session.execute(
            text(
                """
                INSERT INTO domain_inventory.inventory_stock_movements
                    (id, tenant_id, article_id, warehouse_id, movement_type,
                     quantity, unit, notes, previous_stock, new_stock,
                     auto_created, ownership_type, storage_fee_relevant)
                VALUES (:id, :tid, :aid, :wid, :mt, :qty, 'kg', :notes,
                        0, 0, true, 'owned', false)
                """
            ),
            {
                "id": str(uuid.uuid4()),
                "tid": tenant_id,
                "aid": article_id,
                "wid": warehouse_id,
                "mt": movement_type,
                "qty": menge,
                "notes": marke,
            },
        )
    db_session.commit()
    try:
        yield {"tenant_id": str(tenant_id), "marke": marke}
    finally:
        db_session.rollback()
        db_session.execute(
            text("DELETE FROM domain_inventory.inventory_stock_movements WHERE notes = :m"),
            {"m": marke},
        )
        db_session.commit()


def test_bericht_weist_nicht_bestandswirksame_zeilen_getrennt_aus(db_session, bewegungsprobe):
    """Der Kern des Berichts.

    Die Reservierung ueber 999 steht im Hauptbuch und geht nicht in den Saldo
    ein. Wer sie verschweigt, liefert eine Zahl, die ein Pruefer nicht gegen die
    Zeilenliste nachrechnen kann.
    """
    bericht = erstelle_bericht(db_session, bewegungsprobe["tenant_id"])

    reservierungen = [
        z for z in bericht.nicht_bestandswirksam if z.movement_type == "reservation"
    ]
    assert reservierungen, "Reservierung fehlt in der Ausweisung"
    assert reservierungen[0].menge_roh >= 999
    assert reservierungen[0].beitrag_saldo == 0

    wirksame_belegarten = {z.movement_type for z in bericht.nach_belegart}
    assert "reservation" not in wirksame_belegarten


def test_summe_der_belegarten_ergibt_den_gesamtsaldo(db_session, bewegungsprobe):
    """Nachvollziehbarkeit: der Saldo muss aus der Herkunft rekonstruierbar sein."""
    bericht = erstelle_bericht(db_session, bewegungsprobe["tenant_id"])
    aus_belegarten = sum(z.beitrag_saldo for z in bericht.nach_belegart)
    assert aus_belegarten == pytest.approx(bericht.saldo_gesamt)


def test_richtungen_stimmen_mit_dem_register_ueberein(db_session, bewegungsprobe):
    bericht = erstelle_bericht(db_session, bewegungsprobe["tenant_id"])
    nach_typ = {z.movement_type: z for z in bericht.nach_belegart}
    if "wareneingang" in nach_typ:
        assert nach_typ["wareneingang"].richtung == 1
    if "warenausgang" in nach_typ:
        assert nach_typ["warenausgang"].richtung == -1
        assert nach_typ["warenausgang"].beitrag_saldo < 0


def test_bericht_ist_abstimmbar_wenn_alle_belegarten_registriert_sind(
    db_session, bewegungsprobe
):
    bericht = erstelle_bericht(db_session, bewegungsprobe["tenant_id"])
    assert bericht.unbekannte_belegarten == {}
    assert bericht.ist_abstimmbar is True


def test_textausgabe_nennt_saldo_herkunft_und_ausgeschlossenes(db_session, bewegungsprobe):
    """Die Textform ist das, was ein Pruefer tatsaechlich liest."""
    bericht = erstelle_bericht(db_session, bewegungsprobe["tenant_id"])
    ausgabe = als_text(bericht)

    assert "Abstimmbericht Bestandshauptbuch" in ausgabe
    assert "Herkunft nach Belegart" in ausgabe
    assert "Nicht bestandswirksam" in ausgabe
    assert "Vollstaendig erklaerbar: ja" in ausgabe
    assert "reservation" in ausgabe


def test_bericht_ohne_mandantenfilter_laeuft(db_session):
    """Der Betriebslauf ohne --tenant darf nicht an der Filterlogik scheitern."""
    bericht = erstelle_bericht(db_session, None)
    assert bericht.tenant_id is None
    assert bericht.buchungen_gesamt >= 0
    assert isinstance(als_text(bericht), str)
