"""Referenzen in Maskenkoepfen lesbar machen.

Belege speichern ihre Bezuege als Schluessel: Kunde, Lieferant, Lager,
Niederlassung, Kontrakt, Artikel, Auftrag. Im Umlauf sind zwei Formen — die
technische ID und die fachliche Nummer (aus Importen, MCP oder Altdaten). Die
Maske zeigt keinen technischen Schluessel, sondern Name und Nummer.

Verkaufsbelege: Auftrag und Lieferschein fuehren die CRM-ID
(``domain_crm.customers.id``), Rechnungen uebernehmen, was der Aufrufer mitgibt —
aus dem Lieferschein die CRM-ID, aus MCP und Importen oft die Kundennummer.
"""

from __future__ import annotations

import re
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


@dataclass(frozen=True)
class ReferenceDisplay:
    #: ``None``, wenn die Referenz keinen Stammsatz trifft oder dieser keinen Namen fuehrt.
    name: str | None
    #: Fachliche Nummer; ohne Treffer die Referenz selbst, sofern sie keine UUID ist.
    number: str | None
    #: ``True``, wenn die Referenz einen Stammsatz getroffen hat.
    found: bool = False


@dataclass(frozen=True)
class _ReferenceTable:
    table: str
    id_column: str
    name_column: str | None
    number_column: str | None


# Identifiers are fixed here, never taken from the caller, so the f-string SQL below stays safe.
_REFERENCE_TABLES: dict[str, _ReferenceTable] = {
    "business_partner": _ReferenceTable("domain_crm.business_partners", "partner_id", "name_1", "partner_number"),
    "supplier": _ReferenceTable("domain_einkauf.lieferanten", "id", "firmenname", "lieferantennummer"),
    "warehouse": _ReferenceTable("domain_inventory.warehouses", "id", "name", "warehouse_code"),
    "branch": _ReferenceTable("domain_shared.branches", "id", "name", "branch_number"),
    "einkauf_contract": _ReferenceTable("domain_einkauf.kontrakte", "id", "bezeichnung", "kontraktnummer"),
    "agrar_contract": _ReferenceTable("domain_inventory.agrar_contracts", "id", None, "contract_number"),
    "article": _ReferenceTable("domain_inventory.articles", "id", "name", "article_number"),
    "sales_order": _ReferenceTable("domain_crm.sales_orders", "id", None, "order_number"),
    "harvest_campaign": _ReferenceTable("domain_agrar.ernte_kampagnen", "kampagne_id", "bezeichnung", None),
}

_UUID_PATTERN = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE)


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


def resolve_reference(db: Session, tenant_id: str, kind: str, reference: object | None) -> ReferenceDisplay:
    """Name und Nummer zu einer ID oder Nummer der Stammdatenart ``kind``.

    Trifft die Referenz sowohl eine ID als auch eine fremde Nummer, gilt die ID.
    """
    spec = _REFERENCE_TABLES[kind]
    ref = str(reference).strip() if reference is not None else ""
    if not ref:
        return ReferenceDisplay(name=None, number=None)
    name_sql = f"{spec.name_column}::text" if spec.name_column else "NULL"
    number_sql = f"{spec.number_column}::text" if spec.number_column else "NULL"
    match_number = f" OR {spec.number_column}::text = :ref" if spec.number_column else ""
    row = db.execute(
        text(
            f"""
            SELECT {name_sql} AS name, {number_sql} AS number
            FROM {spec.table}
            WHERE tenant_id::text = :tid AND ({spec.id_column}::text = :ref{match_number})
            ORDER BY ({spec.id_column}::text = :ref) DESC
            LIMIT 1
            """
        ),
        {"tid": tenant_id, "ref": ref},
    ).mappings().first()
    if row is None:
        return ReferenceDisplay(name=None, number=None if _UUID_PATTERN.match(ref) else ref)
    return ReferenceDisplay(name=row["name"] or None, number=row["number"] or None, found=True)
