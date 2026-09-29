"""Kundenbezug eines Verkaufsbelegs lesbar machen.

Verkaufsbelege speichern den Kunden als Referenz in ``customer_id``. Zwei Formen
sind im Umlauf: Auftrag und Lieferschein fuehren die CRM-ID
(``domain_crm.customers.id``), Rechnungen uebernehmen, was der Aufrufer mitgibt —
aus dem Lieferschein die CRM-ID, aus MCP und Importen oft die Kundennummer.
Die Maske zeigt keinen der beiden Schluessel, sondern Name und Kundennummer.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.orm import Session


@dataclass(frozen=True)
class CustomerDisplay:
    #: ``None``, wenn die Referenz keinen CRM-Kunden trifft.
    name: str | None
    #: Kundennummer aus dem CRM; ohne Treffer die Referenz selbst, damit der
    #: Beleg nicht kundenlos aussieht.
    number: str | None


def resolve_customer(db: Session, tenant_id: str, reference: str | None) -> CustomerDisplay:
    """Name und Kundennummer zu einer CRM-ID oder Kundennummer.

    Trifft die Referenz sowohl eine ID als auch eine fremde Kundennummer, gilt die ID.
    """
    if not reference:
        return CustomerDisplay(name=None, number=None)
    row = db.execute(
        text(
            """
            SELECT company_name, customer_number
            FROM domain_crm.customers
            WHERE tenant_id::text = :tid AND (id::text = :ref OR customer_number = :ref)
            ORDER BY (id::text = :ref) DESC
            LIMIT 1
            """
        ),
        {"tid": tenant_id, "ref": reference},
    ).mappings().first()
    if row is None:
        return CustomerDisplay(name=None, number=reference)
    return CustomerDisplay(
        name=str(row["company_name"]) if row["company_name"] else None,
        number=str(row["customer_number"]) if row["customer_number"] else None,
    )
