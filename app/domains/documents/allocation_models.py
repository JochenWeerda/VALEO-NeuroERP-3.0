"""FSX-MENGENMODELL — positionsbezogene n:m-Zuordnung zwischen Belegen.

Grundlage: ``docs/design/agrar-mengen-gebinde-modell.md``.

Der Fall, um den es geht (aus dem Belegfluss-Befund):

    Lieferschein A, Position 1: 100 dt
    Rechnung X uebernimmt davon 60 dt
    Rechnung Y die uebrigen 40 dt sowie 20 dt aus Lieferschein B

Zwei Tabellen, und die Aufteilung ist kein Zufall:

``DocumentAllocationSource``
    **Eine** Zeile je Quellposition mit Gesamtmenge und bereits zugeordneter
    Menge. Sie ist der Ort, an dem die Restmenge lebt — und der Ort, den eine
    Transaktion sperrt, bevor sie zuordnet.

``DocumentAllocation``
    Die eigentlichen n:m-Zeilen: Quellposition, Zielposition, Menge, Einheit.

**Warum zwei und nicht eine:** Die Regel „parallele Zuordnungen duerfen dieselbe
Restmenge nicht doppelt vergeben" laesst sich ueber eine reine Zuordnungstabelle
nicht durchsetzen. Zwei gleichzeitige Transaktionen wuerden beide die vorhandenen
Zeilen lesen, beide auf dieselbe Restmenge kommen und beide einfuegen — das
klassische Phantom. Erst eine **Summenzeile**, die gesperrt und fortgeschrieben
wird, macht die Grenze erzwingbar; eine ``CHECK``-Bedingung darauf gibt die
Zusicherung dann die Datenbank, nicht die Anwendung.

Das ist dieselbe Lektion wie FSX-011: Nachschlagen genuegt nicht.
"""

from __future__ import annotations

from uuid import uuid4

from sqlalchemy import (
    CheckConstraint,
    Column,
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


class DocumentAllocationSource(Base):
    """Eine Quellposition mit ihrer Restmengenfuehrung.

    ``quantity`` ist die Positionsmenge in ``unit``; ``allocated_quantity`` die
    Summe aller Zuordnungen, **in derselben Einheit**. Die Umrechnung passiert
    beim Zuordnen, nicht hier — gespeichert wird immer in der Einheit der
    Quellposition, damit die Summe vergleichbar bleibt.
    """

    __tablename__ = "doc_allocation_sources"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "document_type",
            "document_id",
            "line_id",
            name="uq_doc_allocation_source",
        ),
        CheckConstraint("quantity > 0", name="ck_doc_allocation_source_qty_positive"),
        CheckConstraint(
            "allocated_quantity >= 0", name="ck_doc_allocation_source_alloc_nonneg"
        ),
        # Die eigentliche Zusicherung: nie mehr zuordnen als vorhanden.
        # Sie steht hier und nicht in der Anwendung, weil nur die Datenbank sie
        # unter Nebenlaeufigkeit halten kann.
        CheckConstraint(
            "allocated_quantity <= quantity",
            name="ck_doc_allocation_source_not_overallocated",
        ),
        {"schema": "domain_docs", "extend_existing": True},
    )

    id = Column(String, primary_key=True, default=_new_id)
    tenant_id = Column(String(120), nullable=False, index=True)
    document_type = Column(String(80), nullable=False)
    document_id = Column(String(120), nullable=False)
    line_id = Column(String(120), nullable=False)
    article_id = Column(String(120), nullable=True, index=True)
    quantity = Column(Numeric(18, 6), nullable=False)
    allocated_quantity = Column(Numeric(18, 6), nullable=False, server_default="0")
    unit = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class DocumentAllocation(Base):
    """Eine Zuordnung von einer Quell- auf eine Zielposition.

    ``quantity``/``unit`` sind die zugeordnete Menge **in der Einheit der
    Quellposition**. Was der Anwender eingegeben hat, steht in
    ``entered_quantity``/``entered_unit`` — die Anzeige soll sagen koennen
    „2 Big Bag (= 12 dt)", ohne die Eingabe zu verlieren.
    """

    __tablename__ = "doc_allocations"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "source_id",
            "target_document_type",
            "target_document_id",
            "target_line_id",
            name="uq_doc_allocation_pair",
        ),
        CheckConstraint("quantity > 0", name="ck_doc_allocation_qty_positive"),
        Index(
            "ix_doc_allocation_target",
            "tenant_id",
            "target_document_type",
            "target_document_id",
        ),
        {"schema": "domain_docs", "extend_existing": True},
    )

    id = Column(String, primary_key=True, default=_new_id)
    tenant_id = Column(String(120), nullable=False, index=True)
    source_id = Column(
        String,
        ForeignKey("domain_docs.doc_allocation_sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_document_type = Column(String(80), nullable=False)
    target_document_id = Column(String(120), nullable=False)
    target_line_id = Column(String(120), nullable=False)
    quantity = Column(Numeric(18, 6), nullable=False)
    unit = Column(String(20), nullable=False)
    entered_quantity = Column(Numeric(18, 6), nullable=True)
    entered_unit = Column(String(20), nullable=True)
    #: Warum diese Zuordnung besteht — z. B. "teilrechnung", "sammelrechnung".
    reason = Column(String(80), nullable=True)
    note = Column(Text, nullable=True)
    created_by = Column(String(120), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
