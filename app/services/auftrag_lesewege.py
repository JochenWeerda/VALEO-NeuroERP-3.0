"""SQL-Bausteine fuer Leser des Verkaufsauftrags in DocFlow (BELEG-052 S4).

Bis 17.11.2026 lasen diese Stellen die Uebergangssicht der Auftraege im CRM-Schema. Was die
Sicht rechnete, steht hier einmal - die Leser lesen ``domain_docflow.document_headers``/``document_items`` direkt.
Die Ausdruecke enthalten nur Aliase aus dem Code, nie Eingaben.
"""
from __future__ import annotations


def liefertermin_sql(kopf: str) -> str:
    """Liefertermin des Auftrags (Baustein lieferung) als Datum; unlesbare Eingaben bleiben leer."""
    feld = f"{kopf}.bausteine #>> '{{lieferung,liefertermin}}'"
    return f"(CASE WHEN {feld} ~ '^[0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}}' THEN left({feld}, 10)::date END)"


def offene_menge_sql(position: str) -> str:
    """Noch in keinen Folgebeleg gegangene Menge einer Auftragsposition.

    Wie die Belegmaske: der groessere der Wege Lieferschein/Rechnung; stornierte Folgebelege geben ihre Menge frei.
    """
    def weg(beziehung: str) -> str:
        return (f"COALESCE((SELECT sum(l.quantity_linked) FROM domain_docflow.document_links l "
                f"JOIN domain_docflow.document_headers z ON z.id = l.to_header_id AND z.tenant_id = l.tenant_id "
                f"WHERE l.tenant_id = {position}.tenant_id AND l.from_header_id = {position}.header_id "
                f"AND l.from_item_id = {position}.id AND l.relation_type = '{beziehung}' "
                f"AND z.deleted_at IS NULL AND z.status NOT IN ('reversed', 'cancelled')), 0)")

    return (f"GREATEST({position}.quantity - GREATEST({weg('order_to_delivery')}, {weg('order_to_invoice')}), 0)")


#: Offene (weder abgeschlossene noch stornierte) Verkaufsauftraege; Kopf-Alias ``so``.
OFFENE_AUFTRAEGE = ("so.doc_type = 'sales_order' AND so.deleted_at IS NULL "
                    "AND so.status NOT IN ('cancelled', 'completed', 'reversed')")
