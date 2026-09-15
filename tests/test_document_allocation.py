"""FSX-MENGENMODELL — n:m-Zuordnung, gegen die echte Datenbank.

Diese Tests laufen bewusst **nicht** gegen Attrappen. Die wichtigste Zusicherung
des Modells — „parallele Zuordnungen duerfen dieselbe Restmenge nicht doppelt
vergeben" — ist eine Eigenschaft der Datenbank, keine der Anwendungslogik. Ein
Test mit Mocks wuerde sie bestaetigen, ohne sie zu pruefen.

Ohne erreichbare Datenbank werden sie uebersprungen, nicht stillschweigend als
gruen gewertet.

Der Leitfall aus dem Belegfluss-Befund:

    Lieferschein A, Position 1: 100 dt
    Rechnung X uebernimmt 60 dt
    Rechnung Y die uebrigen 40 dt sowie 20 dt aus Lieferschein B
"""

from __future__ import annotations

import os
import uuid
from decimal import Decimal

import pytest

from app.core.agrar_units import ArtikelEinheiten, Gebinde
from app.services.document_allocation_service import (
    DocumentAllocationService,
    LineToRegister,
    NotDivisibleError,
    OverAllocationError,
    PositionRef,
    UnitNotConvertibleError,
)

pytestmark = pytest.mark.integration

DB_URL = os.environ.get(
    "DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_neuro_erp"
)


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    eng = create_engine(DB_URL)
    try:
        with eng.connect() as conn:
            vorhanden = conn.execute(
                text("SELECT to_regclass('domain_docs.doc_allocation_sources')")
            ).scalar()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    if not vorhanden:
        pytest.skip("Migration doc_allocations_20260915 nicht angewandt")
    return eng


@pytest.fixture()
def session(engine):
    from sqlalchemy.orm import sessionmaker

    Session = sessionmaker(bind=engine)
    sitzung = Session()
    try:
        yield sitzung
    finally:
        sitzung.rollback()
        sitzung.close()


@pytest.fixture()
def tenant() -> str:
    """Eigener Mandant je Test — so bleiben die Faelle voneinander unabhaengig."""
    return f"test-{uuid.uuid4().hex[:8]}"


@pytest.fixture()
def service(session, tenant) -> DocumentAllocationService:
    return DocumentAllocationService(session, tenant)


def ls(nummer: str = "LS-A", zeile: str = "1") -> PositionRef:
    return PositionRef("delivery_note", nummer, zeile)


def re(nummer: str, zeile: str = "1") -> PositionRef:
    return PositionRef("sales_invoice", nummer, zeile)


def duenger() -> ArtikelEinheiten:
    return ArtikelEinheiten(
        basis_einheit="kg",
        handels_einheit="dt",
        gebinde=(Gebinde("big_bag", Decimal(600), bezeichnung="Big Bag 600 kg"),),
    )


# -- Der Leitfall: ein Lieferschein, zwei Rechnungen ---------------------------


def test_split_ueber_zwei_rechnungen(service, session) -> None:
    service.register_source(ls(), Decimal(100), "dt")

    erste = service.allocate(ls(), re("RE-X"), Decimal(60), "dt", reason="teilrechnung")
    assert erste.quantity == Decimal(60)
    assert erste.remaining == Decimal(40)
    assert erste.status == "teilweise"

    zweite = service.allocate(ls(), re("RE-Y"), Decimal(40), "dt", reason="teilrechnung")
    assert zweite.remaining == Decimal(0)
    assert zweite.status == "vollstaendig"


def test_merge_zwei_lieferscheine_auf_eine_rechnung(service) -> None:
    """Sammelrechnung: die Zielposition zieht aus zwei Quellen."""
    service.register_source(ls("LS-A"), Decimal(40), "dt")
    service.register_source(ls("LS-B"), Decimal(20), "dt")

    a = service.allocate(ls("LS-A"), re("RE-Y"), Decimal(40), "dt")
    b = service.allocate(ls("LS-B"), re("RE-Y"), Decimal(20), "dt")

    assert a.status == "vollstaendig"
    assert b.status == "vollstaendig"


def test_stand_zeigt_geliefert_berechnet_offen(service) -> None:
    """Genau die drei Zahlen, die die Maske an der Position zeigen soll."""
    service.register_source(ls(), Decimal(100), "dt")
    service.allocate(ls(), re("RE-X"), Decimal(60), "dt")

    stand = service.source_state(ls())
    assert stand["quantity"] == Decimal(100)
    assert stand["allocated_quantity"] == Decimal(60)
    assert stand["open_quantity"] == Decimal(40)
    assert stand["status"] == "teilweise"
    assert len(stand["allocations"]) == 1


# -- Ueberbuchung --------------------------------------------------------------


def test_ueberbuchung_wird_abgewiesen(service) -> None:
    service.register_source(ls(), Decimal(100), "dt")
    service.allocate(ls(), re("RE-X"), Decimal(60), "dt")

    with pytest.raises(OverAllocationError) as fehler:
        service.allocate(ls(), re("RE-Y"), Decimal(50), "dt")
    # Die Meldung nennt die offene Menge — sonst muss der Anwender raten.
    assert "40" in str(fehler.value)


def test_datenbank_haelt_die_grenze_auch_ohne_die_anwendung(service, session, tenant) -> None:
    """Die eigentliche Zusicherung: die CHECK-Bedingung, nicht der Python-Code.

    Hier wird die Anwendungslogik bewusst umgangen und direkt geschrieben. Faellt
    dieser Test, ist die Grenze nur noch eine Absprache.
    """
    from sqlalchemy import text
    from sqlalchemy.exc import IntegrityError

    service.register_source(ls(), Decimal(100), "dt")
    session.flush()

    with pytest.raises(IntegrityError):
        session.execute(
            text(
                "UPDATE domain_docs.doc_allocation_sources "
                "SET allocated_quantity = 150 "
                "WHERE tenant_id = :t AND document_id = 'LS-A'"
            ),
            {"t": tenant},
        )
        session.flush()
    session.rollback()


def test_quellmenge_kann_nicht_unter_die_zuordnung_gesenkt_werden(service) -> None:
    service.register_source(ls(), Decimal(100), "dt")
    service.allocate(ls(), re("RE-X"), Decimal(60), "dt")

    with pytest.raises(OverAllocationError):
        service.register_source(ls(), Decimal(50), "dt")


# -- Einheiten -----------------------------------------------------------------


def test_zuordnung_in_anderer_masseeinheit_wird_umgerechnet(service) -> None:
    service.register_source(ls(), Decimal(100), "dt")

    ergebnis = service.allocate(ls(), re("RE-X"), Decimal(2000), "kg")
    # 2000 kg sind 20 dt — gespeichert wird in der Einheit der Quelle.
    assert ergebnis.quantity == Decimal(20)
    assert ergebnis.unit == "dt"
    assert ergebnis.remaining == Decimal(80)

    stand = service.source_state(ls())
    # Die Eingabe bleibt erhalten, damit die Anzeige "2000 kg (= 20 dt)" kann.
    assert stand["allocations"][0]["entered_quantity"] == Decimal(2000)
    assert stand["allocations"][0]["entered_unit"] == "kg"


def test_gebinde_wird_ueber_den_artikel_umgerechnet(service) -> None:
    service.register_source(ls(), Decimal(100), "dt", article_id="ART-NPK")

    ergebnis = service.allocate(
        ls(), re("RE-X"), Decimal(2), "big_bag", article_units=duenger()
    )
    # 2 Big Bag = 1200 kg = 12 dt.
    assert ergebnis.quantity == Decimal(12)


def test_zaehleinheit_ohne_artikelprofil_wird_abgewiesen(service) -> None:
    """Ohne hinterlegten Faktor wird nicht geraten."""
    service.register_source(ls(), Decimal(100), "dt")

    with pytest.raises(UnitNotConvertibleError) as fehler:
        service.allocate(ls(), re("RE-X"), Decimal(2), "big_bag")
    assert "Gebindefaktor" in str(fehler.value)


def test_masse_und_volumen_werden_nicht_vermischt(service) -> None:
    service.register_source(ls(), Decimal(100), "dt")
    with pytest.raises(UnitNotConvertibleError):
        service.allocate(ls(), re("RE-X"), Decimal(10), "l")


# -- Teilbarkeit ---------------------------------------------------------------


def psm() -> ArtikelEinheiten:
    return ArtikelEinheiten(
        basis_einheit="l",
        gebinde=(Gebinde("kanister", Decimal(10), bezeichnung="Kanister 10 l"),),
        teilbar=False,
    )


def test_halber_kanister_ist_keine_zulaessige_menge(service) -> None:
    """PSM duerfen nur in der Originalverpackung abgegeben werden."""
    service.register_source(PositionRef("delivery_note", "LS-PSM", "1"), Decimal(100), "l")

    with pytest.raises(NotDivisibleError):
        service.allocate(
            PositionRef("delivery_note", "LS-PSM", "1"),
            re("RE-PSM"),
            Decimal("0.5"),
            "kanister",
            article_units=psm(),
        )


def test_ganze_kanister_gehen(service) -> None:
    service.register_source(PositionRef("delivery_note", "LS-PSM", "1"), Decimal(100), "l")
    ergebnis = service.allocate(
        PositionRef("delivery_note", "LS-PSM", "1"),
        re("RE-PSM"),
        Decimal(3),
        "kanister",
        article_units=psm(),
    )
    assert ergebnis.quantity == Decimal(30)


# -- Gutschrift: keine automatische Freigabe -----------------------------------


def test_gutschrift_gibt_die_menge_nicht_von_selbst_frei(service) -> None:
    """Die fachlich heikelste Stelle des Modells.

    Eine Gutschrift kann eine Warenrueckgabe sein — dann wird die Menge wieder
    berechenbar — oder ein Preisnachlass, dann nicht. Das Modell verlangt die
    Entscheidung und trifft sie nicht selbst.
    """
    service.register_source(ls(), Decimal(100), "dt")
    zuordnung = service.allocate(ls(), re("RE-X"), Decimal(60), "dt")

    # Preisnachlass: die Ware bleibt beim Kunden, die Menge bleibt berechnet.
    nachlass = service.release(zuordnung.allocation_id, frees_quantity=False)
    assert nachlass.remaining == Decimal(40)
    assert service.source_state(ls())["allocated_quantity"] == Decimal(60)


def test_warenrueckgabe_gibt_die_menge_frei(service) -> None:
    service.register_source(ls(), Decimal(100), "dt")
    zuordnung = service.allocate(ls(), re("RE-X"), Decimal(60), "dt")

    rueckgabe = service.release(zuordnung.allocation_id, frees_quantity=True)
    assert rueckgabe.remaining == Decimal(100)
    assert service.source_state(ls())["status"] == "offen"


def test_freigabe_verlangt_eine_ausdrueckliche_entscheidung(service) -> None:
    """``frees_quantity`` hat keinen Vorgabewert — wer raet, verrechnet sich."""
    service.register_source(ls(), Decimal(100), "dt")
    zuordnung = service.allocate(ls(), re("RE-X"), Decimal(60), "dt")

    with pytest.raises(TypeError):
        service.release(zuordnung.allocation_id)  # type: ignore[call-arg]


# -- Dieselbe Paarung nicht zweimal --------------------------------------------


def test_dieselbe_quelle_nicht_zweimal_auf_dieselbe_zielposition(service, session) -> None:
    """Zwei Zeilen fuer dieselbe Paarung wuerden doppelt zaehlen."""
    from sqlalchemy.exc import IntegrityError

    service.register_source(ls(), Decimal(100), "dt")
    service.allocate(ls(), re("RE-X"), Decimal(30), "dt")

    with pytest.raises(IntegrityError):
        service.allocate(ls(), re("RE-X"), Decimal(20), "dt")
    session.rollback()


# -- Registrierung beim Speichern ----------------------------------------------


def position(nr: str, menge: str, einheit: str = "dt", artikel: str = "ART-WEIZEN") -> dict:
    """Eine Positionszeile, wie die Belegendpunkte sie fuehren."""
    return {"pos_nr": nr, "menge": Decimal(menge), "einheit": einheit, "artikel_id": artikel}


def zeilen(*positionen: dict) -> list[LineToRegister]:
    return [LineToRegister.from_mapping(p) for p in positionen]


def test_belegpositionen_werden_beim_speichern_zu_quellen(service) -> None:
    """Der Schritt, der bisher fehlte.

    Ohne ihn blieb die Quelltabelle leer: Das Mengenmodell war vorhanden, aber
    an keiner Position sichtbar, und ``allocate`` fand nichts, worauf es sich
    beziehen konnte.
    """
    service.register_document_lines(
        "delivery_note", "LS-A", zeilen(position("1", "100"), position("2", "40"))
    )

    assert service.source_state(ls("LS-A", "1"))["quantity"] == Decimal(100)
    assert service.source_state(ls("LS-A", "2"))["quantity"] == Decimal(40)


def test_erneutes_speichern_schreibt_die_menge_fort(service) -> None:
    """Ein Entwurf darf sich aendern — die Zuordnung darf nicht verloren gehen."""
    service.register_document_lines("delivery_note", "LS-A", zeilen(position("1", "100")))
    service.allocate(ls("LS-A", "1"), re("RE-X"), Decimal(60), "dt")

    service.register_document_lines("delivery_note", "LS-A", zeilen(position("1", "120")))

    stand = service.source_state(ls("LS-A", "1"))
    assert stand["quantity"] == Decimal(120)
    assert stand["allocated_quantity"] == Decimal(60)
    assert stand["open_quantity"] == Decimal(60)


def test_menge_unter_das_bereits_berechnete_zu_senken_schlaegt_fehl(service) -> None:
    """Sonst waere nach dem Speichern mehr berechnet als geliefert."""
    service.register_document_lines("delivery_note", "LS-A", zeilen(position("1", "100")))
    service.allocate(ls("LS-A", "1"), re("RE-X"), Decimal(60), "dt")

    with pytest.raises(OverAllocationError):
        service.register_document_lines("delivery_note", "LS-A", zeilen(position("1", "50")))


def test_position_ohne_menge_oder_einheit_wird_uebersprungen(service) -> None:
    """Eine Quellposition mit geratener Menge waere schlimmer als eine fehlende.

    Sie liesse sich zuordnen — und zwar auf eine Zahl, die niemand angegeben hat.
    """
    service.register_document_lines(
        "delivery_note",
        "LS-A",
        zeilen(
            {"pos_nr": "1", "menge": None, "einheit": "dt"},
            {"pos_nr": "2", "menge": Decimal(10), "einheit": None},
            {"pos_nr": "3", "menge": Decimal(0), "einheit": "dt"},
            position("4", "25"),
        ),
    )

    assert service.source_state(ls("LS-A", "1")) is None
    assert service.source_state(ls("LS-A", "2")) is None
    assert service.source_state(ls("LS-A", "3")) is None
    assert service.source_state(ls("LS-A", "4"))["quantity"] == Decimal(25)


def test_geloeschte_position_ohne_zuordnung_wird_aufgeraeumt(service) -> None:
    service.register_document_lines(
        "delivery_note", "LS-A", zeilen(position("1", "100"), position("2", "40"))
    )
    service.register_document_lines("delivery_note", "LS-A", zeilen(position("1", "100")))

    assert service.source_state(ls("LS-A", "2")) is None


def test_geloeschte_position_mit_zuordnung_bleibt_stehen(service) -> None:
    """Sie stillschweigend zu entfernen hiesse, eine Rechnung ihrer Grundlage zu berauben.

    Sie bleibt stehen und faellt im Mengenstand auf — das ist der Zweck.
    """
    service.register_document_lines(
        "delivery_note", "LS-A", zeilen(position("1", "100"), position("2", "40"))
    )
    service.allocate(ls("LS-A", "2"), re("RE-X"), Decimal(40), "dt")

    service.register_document_lines("delivery_note", "LS-A", zeilen(position("1", "100")))

    stand = service.source_state(ls("LS-A", "2"))
    assert stand is not None
    assert stand["allocated_quantity"] == Decimal(40)


def test_die_positionsnummer_ist_der_schluessel_nicht_die_datensatz_id() -> None:
    """Beim Speichern werden Positionen geloescht und neu eingefuegt.

    Die Datensatz-ID wechselt dabei, die Positionsnummer bleibt — und mit ihr
    die Zuordnung.
    """
    zeile = LineToRegister.from_mapping(
        {"id": "neue-uuid", "pos_nr": "1", "menge": Decimal(5), "einheit": "dt"}
    )
    assert zeile.line_id == "1"
