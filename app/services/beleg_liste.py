"""Belegliste aus DocFlow: eine Quelle fuer Maske (Familie ``beleg-liste``), CLI, MCP (``beleg_suchen``) und REST.

Nutzerentscheidung 08.11.2026 (BELEG-052): DocFlow ist der einzige Belegspeicher. Die Listen lesen deshalb nicht
mehr die Eigenspeicher (``/sales/offers``, ``/sales/orders``, ``/sales/delivery-notes``, ``/sales/invoices``,
``/einkauf/bestellungen``, ``/finance/ap/invoices``, ``/einkauf/rechnungseingaenge``), sondern ``document_headers``.

Rechte wie beim Einzelbeleg: Gezeigt werden nur Belegarten, die die Anmeldung lesen darf; Betraege nur mit
Preisrecht und nur in Varianten mit Preisen.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any, Callable, Optional

from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.orm import Session

from app.core.belegvertrag import BELEGARTEN

Darf = Callable[[str, str], bool]


def _datum(wert: Any) -> Optional[str]:
    if isinstance(wert, datetime):
        return wert.date().isoformat()
    if isinstance(wert, date):
        return wert.isoformat()
    return None


def _abfrage(db: Session, sql: str, werte: dict) -> list[dict]:
    """Eigener Sicherungspunkt wie im Einzelbeleg: Fehlen Stammdatentabellen, bleibt die Lesetransaktion gesund."""
    try:
        with db.begin_nested():
            return [dict(r) for r in db.execute(text(sql), werte).mappings()]
    except (OperationalError, ProgrammingError):
        return []


def _partnernamen(db: Session, tenant: str, kunden: set[str], lieferanten: set[str]) -> dict[tuple[str, str], tuple]:
    """(rolle, kennung) -> (nummer, name); gesucht wie im Einzelbeleg (Kennung oder Kunden-/Lieferantennummer)."""
    namen: dict[tuple[str, str], tuple] = {}
    if lieferanten:
        for r in _abfrage(db, "SELECT id::text AS id, lieferantennummer AS nr, firmenname AS name "
                              "FROM domain_einkauf.lieferanten "
                              "WHERE tenant_id = :t AND (id::text = ANY(:p) OR lieferantennummer = ANY(:p))",
                          {"t": tenant, "p": sorted(lieferanten)}):
            for kennung in (r["id"], r["nr"]):
                if kennung:
                    namen[("lieferant", str(kennung))] = (r["nr"], r["name"])
    if kunden:
        for r in _abfrage(db, "SELECT c.id::text AS id, c.customer_number AS nr, "
                              "COALESCE(NULLIF(bp.name_1, ''), c.company_name) AS name "
                              "FROM domain_crm.customers c LEFT JOIN domain_crm.business_partners bp "
                              "ON bp.partner_id = c.business_partner_id AND bp.tenant_id = c.tenant_id "
                              "WHERE c.tenant_id = :t AND (c.id::text = ANY(:p) OR c.customer_number = ANY(:p))",
                          {"t": tenant, "p": sorted(kunden)}):
            for kennung in (r["id"], r["nr"]):
                if kennung:
                    namen[("kunde", str(kennung))] = (r["nr"], r["name"])
    return namen


def beleg_zeilen(db: Session, tenant: str, darf: Darf, *, arten: Optional[list[str]] = None,
                 status: Optional[str] = None, beleg_nr: Optional[str] = None, partner: Optional[str] = None,
                 limit: int = 200) -> list[dict[str, Any]]:
    """Belege der lesbaren Belegarten, neueste zuerst. ``darf(recht, belegart)`` ist das Recht der Anmeldung."""
    lesbar = sorted(a for a in (arten or list(BELEGARTEN)) if a in BELEGARTEN and darf("lesen", a))
    if not lesbar:
        return []
    zeilen = db.execute(
        text(
            """
            SELECT id, doc_type, doc_number, status, document_date, posting_date, customer_id, supplier_id,
                   currency, total_net, total_tax, total_gross, version, source_ref
            FROM domain_docflow.document_headers
            WHERE tenant_id = :tenant AND deleted_at IS NULL AND source_system <> 'gobd_artifact'
              AND doc_type = ANY(:arten)
              AND (CAST(:status AS text) IS NULL OR status = :status)
              AND (CAST(:nr AS text) IS NULL OR doc_number ILIKE '%' || :nr || '%')
              AND (CAST(:partner AS text) IS NULL OR customer_id = :partner OR supplier_id = :partner)
            ORDER BY document_date DESC, doc_number DESC
            LIMIT :lim
            """
        ),
        {"tenant": tenant, "arten": lesbar, "status": status, "nr": beleg_nr, "partner": partner,
         "lim": max(1, min(int(limit), 500))},
    ).mappings().all()
    kunden = {str(z["customer_id"]) for z in zeilen if z["customer_id"]}
    lieferanten = {str(z["supplier_id"]) for z in zeilen if z["supplier_id"]}
    namen = _partnernamen(db, tenant, kunden, lieferanten)
    preisrecht = {a: BELEGARTEN[a].mit_preisen and darf("preise", a) for a in lesbar}
    items = []
    for z in zeilen:
        variante = BELEGARTEN[str(z["doc_type"])]
        rolle = variante.partnerrolle
        kennung = z["supplier_id"] if rolle == "lieferant" else z["customer_id"]
        nummer, name = namen.get((rolle, str(kennung)), (kennung, None)) if kennung else (None, None)
        mit_betrag = preisrecht[variante.belegart]
        items.append({
            "id": str(z["id"]),
            "beleg_id": str(z["id"]),
            "belegart": variante.belegart,
            "bezeichnung": variante.bezeichnung,
            "beleg_nr": str(z["doc_number"]),
            "status": str(z["status"]),
            "belegdatum": _datum(z["document_date"]),
            "buchungsdatum": _datum(z["posting_date"]),
            "partner_nr": str(kennung) if kennung else None,
            "partner_nummer": str(nummer) if nummer else None,
            "partner_name": name,
            "referenz": z["source_ref"],
            "version": int(z["version"] or 1),
            # Ohne Preise in der Variante oder ohne Preisrecht auch kein Betrag in der Liste (Werte als Decimal).
            "netto": z["total_net"] if mit_betrag else None,
            "steuer": z["total_tax"] if mit_betrag else None,
            "brutto": z["total_gross"] if mit_betrag else None,
            "waehrung": str(z["currency"] or "EUR") if mit_betrag else None,
        })
    return items
