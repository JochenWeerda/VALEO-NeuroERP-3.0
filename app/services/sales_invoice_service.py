"""Aus Lieferscheinpositionen wird eine Rechnung mit eigenen Positionen.

Der Schritt, der bisher fehlte. Die Umwandlung schrieb einen Journalsatz ueber
den ganzen Beleg; die Rechnung hatte keine Positionen, und damit gab es kein
Ziel fuer die Mengenzuordnung. Hier entsteht beides in einem Zug:

1. Je offener Lieferscheinposition eine **Rechnungsposition**.
2. Je Rechnungsposition eine **Zuordnung** ueber den vorhandenen
   ``document_allocation_service`` — kein zweiter Zuordnungsmechanismus.

Die Menge ist die **offene**, nicht die gelieferte
-------------------------------------------------

Eine Position, die schon teilweise berechnet wurde, geht nur mit ihrem Rest in
die neue Rechnung. Die Liefermenge zu nehmen waere eine Doppelberechnung, und
zwar eine, die niemandem auffiele: Der Betrag stimmte fuer sich genommen.

Ist eine Position vollstaendig berechnet, entsteht **keine** Rechnungsposition —
nicht eine mit Menge null. Eine Nullposition waere eine Zeile, die behauptet,
etwas zu berechnen.

Restmengen sind sichtbar, nicht still
-------------------------------------

Was nicht in die Rechnung kommt und warum, steht im Ergebnis
(``skipped``). Eine Sammelrechnung, die zwei von fuenf Lieferscheinen
stillschweigend auslaesst, ist der Fehler, den das Mengenmodell verhindern
soll.

Diese Schicht bucht nicht
-------------------------

Journalsatz, offener Posten und Steuerfindung bleiben, wo sie sind. Hier
entsteht der Beleg, nicht seine Verbuchung — und die Rechnung beginnt als
``entwurf``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.agrar_units import normalisiere
from app.domains.documents.sales_invoice_models import SalesInvoice, SalesInvoiceLine
from app.services.document_allocation_service import (
    AllocationError,
    DocumentAllocationService,
    PositionRef,
)


class InvoiceCreationError(RuntimeError):
    """Fachlicher Grund, warum keine Rechnung entstehen kann."""


@dataclass(frozen=True)
class SourceLine:
    """Eine zu berechnende Belegposition."""

    document_type: str
    document_id: str
    line_id: str
    article_id: str | None
    article_number: str | None
    description: str | None
    #: Menge laut Beleg. Berechnet wird die **offene**, siehe Modulbeschreibung.
    quantity: Decimal
    unit: str
    unit_price: Decimal = Decimal(0)
    vat_rate: Decimal | None = None


@dataclass
class SkippedLine:
    source: SourceLine
    reason: str


@dataclass
class InvoiceResult:
    invoice: SalesInvoice
    lines: list[SalesInvoiceLine] = field(default_factory=list)
    #: Positionen, die nicht in die Rechnung kamen — mit Grund.
    skipped: list[SkippedLine] = field(default_factory=list)


class SalesInvoiceService:
    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id
        self.allocations = DocumentAllocationService(db, tenant_id)

    def create_from_sources(
        self,
        *,
        invoice_number: str,
        customer_id: str,
        invoice_date: date,
        sources: list[SourceLine] | tuple[SourceLine, ...],
        due_date: date | None = None,
        reason: str = "rechnung_aus_lieferschein",
        user_id: str | None = None,
        note: str | None = None,
    ) -> InvoiceResult:
        """Rechnung mit Positionen anlegen und die Mengen zuordnen.

        Legt **keine** Rechnung an, wenn keine einzige Position etwas Offenes
        beitraegt: Eine Rechnung ueber nichts ist kein Beleg, sondern eine
        Nummer. Der Aufrufer bekommt dann einen Fehler mit den Gruenden.
        """
        if not sources:
            raise InvoiceCreationError("Ohne Positionen entsteht keine Rechnung.")

        rechnung = SalesInvoice(
            tenant_id=self.tenant_id,
            invoice_number=invoice_number,
            customer_id=customer_id,
            invoice_date=invoice_date,
            due_date=due_date,
            status="entwurf",
            note=note,
            created_by=user_id,
        )

        ergebnis = InvoiceResult(invoice=rechnung)
        offene: list[tuple[SourceLine, Decimal, str]] = []

        for quelle in sources:
            ref = PositionRef(quelle.document_type, quelle.document_id, quelle.line_id)
            stand = self.allocations.source_state(ref)
            if stand is None:
                # Der Beleg wurde gespeichert, ohne dass seine Positionen als
                # Quellen bekannt wurden. Hier still die Liefermenge zu nehmen
                # hiesse, die Restmengenfuehrung zu umgehen.
                ergebnis.skipped.append(
                    SkippedLine(
                        quelle,
                        "Position ist nicht als Quelle registriert — ohne "
                        "Restmengenfuehrung wird sie nicht berechnet.",
                    )
                )
                continue

            offen = Decimal(str(stand["open_quantity"]))
            if offen <= 0:
                ergebnis.skipped.append(
                    SkippedLine(quelle, "Position ist bereits vollstaendig berechnet.")
                )
                continue
            offene.append((quelle, offen, str(stand["unit"])))

        if not offene:
            gruende = "; ".join(eintrag.reason for eintrag in ergebnis.skipped)
            raise InvoiceCreationError(
                f"Keine offene Menge zu berechnen. {gruende}"
            )

        self.db.add(rechnung)
        self.db.flush()

        netto = Decimal(0)
        steuer = Decimal(0)
        for nummer, (quelle, offen, einheit) in enumerate(offene, start=1):
            betrag = (offen * quelle.unit_price).quantize(Decimal("0.01"))
            position = SalesInvoiceLine(
                tenant_id=self.tenant_id,
                invoice_id=rechnung.id,
                line_no=str(nummer),
                article_id=quelle.article_id,
                article_number=quelle.article_number,
                description=quelle.description,
                quantity=offen,
                unit=normalisiere(einheit),
                unit_price=quelle.unit_price,
                net_amount=betrag,
                vat_rate=quelle.vat_rate,
            )
            self.db.add(position)
            ergebnis.lines.append(position)

            netto += betrag
            if quelle.vat_rate is not None:
                steuer += (betrag * quelle.vat_rate / Decimal(100)).quantize(Decimal("0.01"))

            try:
                self.allocations.allocate(
                    PositionRef(quelle.document_type, quelle.document_id, quelle.line_id),
                    PositionRef("sales_invoice", rechnung.id, position.line_no),
                    offen,
                    einheit,
                    reason=reason,
                    user_id=user_id,
                )
            except AllocationError as fehler:
                # Zwischen Lesen und Zuordnen kann eine parallele Rechnung die
                # Menge verbraucht haben. Dann entsteht hier keine halbe
                # Rechnung: Der Aufrufer rollt zurueck und liest neu.
                raise InvoiceCreationError(
                    f"Position {quelle.line_id} aus {quelle.document_id} konnte "
                    f"nicht zugeordnet werden: {fehler}"
                ) from fehler

        rechnung.net_amount = netto
        rechnung.vat_amount = steuer
        rechnung.gross_amount = netto + steuer
        self.db.flush()
        return ergebnis

    def get_with_lines(self, invoice_id: str) -> tuple[SalesInvoice, list[SalesInvoiceLine]] | None:
        rechnung = (
            self.db.query(SalesInvoice)
            .filter(
                SalesInvoice.id == invoice_id,
                SalesInvoice.tenant_id == self.tenant_id,
            )
            .first()
        )
        if rechnung is None:
            return None
        positionen = (
            self.db.query(SalesInvoiceLine)
            .filter(
                SalesInvoiceLine.invoice_id == invoice_id,
                SalesInvoiceLine.tenant_id == self.tenant_id,
            )
            .order_by(SalesInvoiceLine.line_no.asc())
            .all()
        )
        return rechnung, positionen
