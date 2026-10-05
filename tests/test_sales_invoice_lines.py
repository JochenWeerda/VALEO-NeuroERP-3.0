"""Die Rechnungsposition als eigenes Objekt — gegen die echte Datenbank.

Der Befund, der diesen Slice ausgeloest hat: Die Ausgangsrechnung war im
Belegfluss kein Gegenstand. Aus einem Lieferschein wurde ein Journalsatz ueber
den ganzen Beleg; eine Positionszuordnung konnte auf nichts zeigen, und niemand
konnte nachlesen, woher eine berechnete Menge kommt.

Die drei Zusicherungen, um die es hier geht:

1. **Berechnet wird die offene Menge**, nicht die gelieferte. Sonst entstuende
   eine Doppelberechnung, die niemandem auffiele — der Betrag stimmte fuer sich
   genommen.
2. **Eine vollstaendig berechnete Position ergibt keine Nullposition.** Eine
   Zeile mit Menge null behauptet, etwas zu berechnen.
3. **Jede Rechnungsposition kennt ihre Herkunft** — ueber die Zuordnung, nicht
   ueber eine Spalte am Beleg.

Ohne erreichbare Datenbank wird uebersprungen, nicht als gruen gewertet.
"""

from __future__ import annotations

import os
import uuid
from datetime import date
from decimal import Decimal

import pytest

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
                text("SELECT to_regclass('domain_sales.sales_invoice_lines')")
            ).scalar()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    if not vorhanden:
        pytest.skip("Migration sales_invoice_lines_20260915 nicht angewandt")
    return eng


@pytest.fixture()
def session(engine):
    from sqlalchemy.orm import sessionmaker

    sitzung = sessionmaker(bind=engine)()
    try:
        yield sitzung
    finally:
        sitzung.rollback()
        sitzung.close()


@pytest.fixture()
def tenant() -> str:
    return f"test-{uuid.uuid4().hex[:8]}"


@pytest.fixture()
def dienste(session, tenant):
    from app.services.document_allocation_service import DocumentAllocationService
    from app.services.sales_invoice_service import SalesInvoiceService

    return SalesInvoiceService(session, tenant), DocumentAllocationService(session, tenant)


LS = "LS-A"


def quelle(zeile: str = "1", menge: str = "100", preis: str = "25.00"):
    from app.services.sales_invoice_service import SourceLine

    return SourceLine(
        document_type="delivery_note",
        document_id=LS,
        line_id=zeile,
        article_id="ART-WEIZEN",
        article_number="10001",
        description="Weizen A",
        quantity=Decimal(menge),
        unit="dt",
        unit_price=Decimal(preis),
        vat_rate=Decimal(7),
    )


def registriere(allocations, *zeilen) -> None:
    from app.services.document_allocation_service import LineToRegister

    allocations.register_document_lines(
        "delivery_note",
        LS,
        [
            LineToRegister(line_id=z.line_id, quantity=z.quantity, unit=z.unit, article_id=z.article_id)
            for z in zeilen
        ],
    )


def rechnung_anlegen(invoices, *quellen, nummer: str | None = None):
    return invoices.create_from_sources(
        invoice_number=nummer or f"RE-{uuid.uuid4().hex[:6].upper()}",
        customer_id="K-100",
        invoice_date=date(2026, 9, 15),
        sources=list(quellen),
    )


# -- Die Position entsteht -----------------------------------------------------


def test_je_offene_lieferposition_eine_rechnungsposition(dienste) -> None:
    invoices, allocations = dienste
    eins, zwei = quelle("1", "100"), quelle("2", "40")
    registriere(allocations, eins, zwei)

    ergebnis = rechnung_anlegen(invoices, eins, zwei)

    assert [z.line_no for z in ergebnis.lines] == ["1", "2"]
    assert [z.quantity for z in ergebnis.lines] == [Decimal(100), Decimal(40)]
    assert all(z.unit == "dt" for z in ergebnis.lines)
    assert ergebnis.skipped == []


def test_die_position_traegt_artikel_preis_und_betrag(dienste) -> None:
    """Sonst waere sie eine Mengenangabe, kein Beleg."""
    invoices, allocations = dienste
    eins = quelle("1", "100", "25.00")
    registriere(allocations, eins)

    ergebnis = rechnung_anlegen(invoices, eins)
    position = ergebnis.lines[0]

    assert position.article_number == "10001"
    assert position.description == "Weizen A"
    assert position.unit_price == Decimal("25.00")
    assert position.net_amount == Decimal("2500.00")
    assert ergebnis.invoice.net_amount == Decimal("2500.00")
    assert ergebnis.invoice.vat_amount == Decimal("175.00")
    assert ergebnis.invoice.gross_amount == Decimal("2675.00")


def test_die_rechnung_beginnt_als_entwurf(dienste) -> None:
    """Diese Schicht bucht nicht — Journalsatz und OP bleiben, wo sie sind."""
    invoices, allocations = dienste
    eins = quelle()
    registriere(allocations, eins)

    assert rechnung_anlegen(invoices, eins).invoice.status == "entwurf"


# -- Berechnet wird die offene Menge -------------------------------------------


def test_zweite_rechnung_nimmt_nur_die_restmenge(dienste) -> None:
    """Der Fall, der ohne Restmengenfuehrung doppelt berechnet wuerde.

    Die erste Rechnung nimmt die volle offene Menge. Wird danach eine Zuordnung
    geloest — Warenrueckgabe —, ist wieder etwas offen, und nur das kommt in die
    zweite Rechnung.
    """
    invoices, allocations = dienste
    eins = quelle("1", "100")
    registriere(allocations, eins)

    erste = rechnung_anlegen(invoices, eins)
    assert erste.lines[0].quantity == Decimal(100)

    from app.services.document_allocation_service import PositionRef

    stand = allocations.source_state(PositionRef("delivery_note", LS, "1"))
    allocations.release(stand["allocations"][0]["id"], frees_quantity=True)

    # 40 dt anderweitig berechnet, 60 dt bleiben offen.
    allocations.allocate(
        PositionRef("delivery_note", LS, "1"),
        PositionRef("sales_invoice", "RE-FREMD", "1"),
        Decimal(40),
        "dt",
    )

    zweite = rechnung_anlegen(invoices, eins)
    assert zweite.lines[0].quantity == Decimal(60)


def test_vollstaendig_berechnete_position_ergibt_keine_nullzeile(dienste) -> None:
    invoices, allocations = dienste
    eins, zwei = quelle("1", "100"), quelle("2", "40")
    registriere(allocations, eins, zwei)

    from app.services.document_allocation_service import PositionRef

    allocations.allocate(
        PositionRef("delivery_note", LS, "1"),
        PositionRef("sales_invoice", "RE-FREMD", "1"),
        Decimal(100),
        "dt",
    )

    ergebnis = rechnung_anlegen(invoices, eins, zwei)

    assert [z.line_no for z in ergebnis.lines] == ["1"]
    assert ergebnis.lines[0].quantity == Decimal(40)
    # Und der Grund steht da, statt dass stillschweigend weniger berechnet wird.
    assert len(ergebnis.skipped) == 1
    assert "bereits vollstaendig berechnet" in ergebnis.skipped[0].reason


def test_ohne_offene_menge_entsteht_keine_rechnung(dienste) -> None:
    """Eine Rechnung ueber nichts ist kein Beleg, sondern eine Nummer."""
    from app.services.sales_invoice_service import InvoiceCreationError

    invoices, allocations = dienste
    eins = quelle("1", "100")
    registriere(allocations, eins)

    from app.services.document_allocation_service import PositionRef

    allocations.allocate(
        PositionRef("delivery_note", LS, "1"),
        PositionRef("sales_invoice", "RE-FREMD", "1"),
        Decimal(100),
        "dt",
    )

    with pytest.raises(InvoiceCreationError) as fehler:
        rechnung_anlegen(invoices, eins)
    assert "bereits vollstaendig berechnet" in str(fehler.value)


def test_nicht_registrierte_position_wird_nicht_geraten(dienste) -> None:
    """Ohne Restmengenfuehrung wird nicht berechnet.

    Hier still die Liefermenge zu nehmen hiesse, die einzige Grenze zu umgehen,
    die vor Doppelberechnung schuetzt.
    """
    from app.services.sales_invoice_service import InvoiceCreationError

    invoices, _ = dienste
    with pytest.raises(InvoiceCreationError) as fehler:
        rechnung_anlegen(invoices, quelle("1", "100"))
    assert "nicht als Quelle registriert" in str(fehler.value)


# -- Herkunft ------------------------------------------------------------------


def test_jede_rechnungsposition_kennt_ihre_herkunft(dienste, session, tenant) -> None:
    """Der eigentliche Zweck des Slices.

    Die Beziehung steht in der Zuordnung, nicht als Spalte an der Position —
    eine Rechnungsposition kann aus mehreren Lieferscheinpositionen gespeist
    sein, und eine Lieferscheinposition auf mehrere Rechnungen gehen.
    """
    from app.domains.documents.allocation_models import (
        DocumentAllocation,
        DocumentAllocationSource,
    )

    invoices, allocations = dienste
    eins = quelle("1", "100")
    registriere(allocations, eins)
    ergebnis = rechnung_anlegen(invoices, eins)

    zuordnung, quellzeile = (
        session.query(DocumentAllocation, DocumentAllocationSource)
        .join(
            DocumentAllocationSource,
            DocumentAllocation.source_id == DocumentAllocationSource.id,
        )
        .filter(
            DocumentAllocation.tenant_id == tenant,
            DocumentAllocation.target_document_id == ergebnis.invoice.id,
        )
        .one()
    )

    assert zuordnung.target_line_id == ergebnis.lines[0].line_no
    assert quellzeile.document_type == "delivery_note"
    assert quellzeile.document_id == LS
    assert quellzeile.line_id == "1"
    assert zuordnung.quantity == Decimal(100)


def test_die_position_traegt_keine_herkunftsspalte() -> None:
    """Sie waere die 1:1-Annahme, die das Mengenmodell gerade aufloest.

    Eine zweite Wahrheit neben der Zuordnungstabelle wuerde spaetestens bei der
    ersten Sammelrechnung falsch.
    """
    from app.domains.documents.sales_invoice_models import SalesInvoiceLine

    spalten = set(SalesInvoiceLine.__table__.columns.keys())
    assert "source_document_id" not in spalten
    assert "source_line_id" not in spalten
    assert "delivery_note_id" not in spalten


def test_sammelrechnung_ist_nur_eine_laengere_quellenliste(dienste) -> None:
    """Mehrere Lieferscheine in eine Rechnung — kein Sonderfall."""
    from app.services.document_allocation_service import LineToRegister
    from app.services.sales_invoice_service import SourceLine

    invoices, allocations = dienste
    aus_b = SourceLine(
        document_type="delivery_note",
        document_id="LS-B",
        line_id="1",
        article_id="ART-WEIZEN",
        article_number="10001",
        description="Weizen A",
        quantity=Decimal(20),
        unit="dt",
        unit_price=Decimal("25.00"),
    )
    eins = quelle("1", "100")
    registriere(allocations, eins)
    allocations.register_document_lines(
        "delivery_note",
        "LS-B",
        [LineToRegister(line_id="1", quantity=Decimal(20), unit="dt", article_id="ART-WEIZEN")],
    )

    ergebnis = rechnung_anlegen(invoices, eins, aus_b)

    assert [z.quantity for z in ergebnis.lines] == [Decimal(100), Decimal(20)]
    assert ergebnis.invoice.net_amount == Decimal("3000.00")


# -- Grenzen des Belegs --------------------------------------------------------


def test_rechnungsnummer_gibt_es_je_mandant_nur_einmal(dienste, session) -> None:
    """Zwei Belege mit demselben Namen waeren nicht unterscheidbar."""
    from sqlalchemy.exc import IntegrityError

    invoices, allocations = dienste
    eins, zwei = quelle("1", "100"), quelle("2", "40")
    registriere(allocations, eins, zwei)

    rechnung_anlegen(invoices, eins, nummer="RE-DOPPELT")
    with pytest.raises(IntegrityError):
        rechnung_anlegen(invoices, zwei, nummer="RE-DOPPELT")
    session.rollback()


def test_positionsnummer_gibt_es_je_rechnung_nur_einmal(session, tenant) -> None:
    """Sie ist das Ziel der Zuordnungen; zweimal dieselbe waere mehrdeutig."""
    from sqlalchemy.exc import IntegrityError

    from app.domains.documents.sales_invoice_models import SalesInvoice, SalesInvoiceLine

    rechnung = SalesInvoice(
        tenant_id=tenant,
        invoice_number="RE-EINDEUTIG",
        customer_id="K-100",
        invoice_date=date(2026, 9, 15),
    )
    session.add(rechnung)
    session.flush()
    for _ in range(2):
        session.add(
            SalesInvoiceLine(
                tenant_id=tenant,
                invoice_id=rechnung.id,
                line_no="1",
                quantity=Decimal(1),
                unit="dt",
            )
        )
    with pytest.raises(IntegrityError):
        session.flush()
    session.rollback()
