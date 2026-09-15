"""Die Rechnung und ihre Position als eigenes Objekt.

Bisher war die Ausgangsrechnung im Belegfluss **kein Gegenstand**: Aus einem
Lieferschein wurde ein Journalsatz und ein offener Posten, beide ueber den
ganzen Beleg. Es gab nichts, worauf eine Positionszuordnung haette zeigen
koennen — und deshalb auch keine Stelle, an der ein Sachbearbeiter haette
nachlesen koennen, woher die berechnete Menge kommt.

Warum die Position eine eigene Zeile braucht
---------------------------------------------

Weil die Mengenrechnung an ihr haengt. „Lieferschein A, Position 1: 100 dt,
davon 60 dt auf Rechnung X" setzt voraus, dass es *Position 1 der Rechnung X*
gibt. Ohne sie bliebe nur der Beleg als Ganzes, und damit waeren Teilmengen,
Sammelrechnungen und Gutschriften ueber einzelne Positionen nicht abbildbar —
genau die Faelle, um die es im Landhandel geht.

Was hier **nicht** steht
------------------------

**Keine Herkunftsspalte.** Es waere naheliegend, an die Rechnungsposition ein
``source_document_id`` zu schreiben. Das waere aber wieder die 1:1-Annahme, die
das Mengenmodell gerade aufloest: Eine Rechnungsposition kann aus **mehreren**
Lieferscheinpositionen gespeist sein, und eine Lieferscheinposition auf mehrere
Rechnungen gehen. Die Beziehung lebt in ``doc_allocations``; sie hat dort ihre
Menge, ihre Einheit und ihre Restmengenfuehrung. Eine zusaetzliche Spalte waere
eine zweite Wahrheit.

**Keine Buchungslogik.** Journalsatz, offener Posten und Steuerfindung bleiben,
wo sie sind. Diese Tabellen sind der Beleg, nicht seine Verbuchung.
"""

from __future__ import annotations

from uuid import uuid4

from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.sql import func

from app.core.database import Base


def _new_id() -> str:
    return str(uuid4())


class SalesInvoice(Base):
    """Der Rechnungskopf.

    ``status`` folgt den uebrigen Verkaufsbelegen: ``entwurf`` -> ``gebucht``
    -> ``bezahlt``, dazu ``storniert``. Die Summen werden mitgefuehrt, weil die
    Maske sie ohne Nachrechnen ueber alle Positionen zeigen koennen muss; die
    Wahrheit sind trotzdem die Positionen.
    """

    __tablename__ = "sales_invoices"
    __table_args__ = (
        UniqueConstraint("tenant_id", "invoice_number", name="uq_sales_invoice_number"),
        Index("ix_sales_invoice_customer", "tenant_id", "customer_id"),
        {"schema": "domain_sales", "extend_existing": True},
    )

    id = Column(String, primary_key=True, default=_new_id)
    tenant_id = Column(String(120), nullable=False, index=True)
    invoice_number = Column(String(60), nullable=False)
    customer_id = Column(String(120), nullable=False)
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=True)
    currency = Column(String(3), nullable=False, server_default="EUR")
    status = Column(String(20), nullable=False, server_default="entwurf")
    net_amount = Column(Numeric(18, 2), nullable=False, server_default="0")
    vat_amount = Column(Numeric(18, 2), nullable=False, server_default="0")
    gross_amount = Column(Numeric(18, 2), nullable=False, server_default="0")
    note = Column(Text, nullable=True)
    created_by = Column(String(120), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class SalesInvoiceLine(Base):
    """Eine Rechnungsposition.

    ``line_no`` ist die fachliche Positionsnummer und zugleich der Schluessel,
    unter dem die Zuordnungen auf diese Position zeigen (``target_line_id`` in
    ``doc_allocations``). Sie ist deshalb je Rechnung eindeutig und wird nicht
    nachtraeglich umnummeriert: Eine Umnummerierung wuerde bestehende
    Zuordnungen ins Leere zeigen lassen.
    """

    __tablename__ = "sales_invoice_lines"
    __table_args__ = (
        UniqueConstraint("tenant_id", "invoice_id", "line_no", name="uq_sales_invoice_line_no"),
        CheckConstraint("quantity > 0", name="ck_sales_invoice_line_qty_positive"),
        {"schema": "domain_sales", "extend_existing": True},
    )

    id = Column(String, primary_key=True, default=_new_id)
    tenant_id = Column(String(120), nullable=False, index=True)
    invoice_id = Column(
        String,
        ForeignKey("domain_sales.sales_invoices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    #: Fachliche Positionsnummer; Ziel der Mengenzuordnungen.
    line_no = Column(String(120), nullable=False)
    article_id = Column(String(120), nullable=True, index=True)
    article_number = Column(String(80), nullable=True)
    description = Column(String(255), nullable=True)
    quantity = Column(Numeric(18, 6), nullable=False)
    unit = Column(String(20), nullable=False)
    unit_price = Column(Numeric(18, 4), nullable=False, server_default="0")
    net_amount = Column(Numeric(18, 2), nullable=False, server_default="0")
    vat_rate = Column(Numeric(5, 2), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
