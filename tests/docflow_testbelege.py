"""Testbelege direkt in DocFlow anlegen und wieder entfernen (BELEG-052).

``domain_crm.sales_orders``/``sales_order_items`` sind seit ``docflow_auftraege_uebernahme_20261109`` eine Sicht auf
DocFlow. Fixtures, die einen Auftrag als Vorbedingung brauchen, legen ihn hier an - so, wie er nach der Uebernahme
aussieht: Kopf und Positionen in ``domain_docflow``, ohne angenommene Steuer.
"""
from __future__ import annotations

import json
import uuid
from decimal import Decimal
from typing import Any, Iterable, Optional

from sqlalchemy import text


def lege_auftrag_an(verbindung, mandant: str, kunde: Optional[str], nummer: str, *, status: str = "open",
                    brutto: float | None = None, positionen: Iterable[dict[str, Any]] = (),
                    bausteine: Optional[dict[str, Any]] = None, kennung: Optional[str] = None,
                    belegdatum: Optional[str] = None) -> str:
    """Ein DocFlow-Auftrag. ``positionen``: ``artikel``, ``menge``, ``preis``, optional ``einheit``/``rabatt``/
    ``bezeichnung``. Ohne Positionen traegt der Kopf ``brutto`` als Summe."""
    kennung = kennung or str(uuid.uuid4())
    zeilen = []
    for nr, p in enumerate(positionen, start=1):
        netto = (Decimal(str(p["menge"])) * Decimal(str(p.get("preis", 0)))
                 * (1 - Decimal(str(p.get("rabatt", 0))) / 100)).quantize(Decimal("0.01"))
        zeilen.append((nr, p, netto))
    summe = sum((z[2] for z in zeilen), Decimal("0")) if zeilen else Decimal(str(brutto or 0))
    verbindung.execute(text(
        "INSERT INTO domain_docflow.document_headers (id, tenant_id, doc_type, doc_number, status, source_system, "
        "customer_id, currency, total_net, total_tax, total_gross, document_date, version, created_by, updated_by, "
        "created_at, updated_at, bausteine) VALUES (:id, :t, 'sales_order', :nr, :st, 'test', :k, 'EUR', :s, 0, :s, "
        "COALESCE(CAST(:datum AS timestamptz), NOW()), 1, 'test', 'test', NOW(), NOW(), CAST(:b AS jsonb))"),
        {"id": kennung, "t": mandant, "nr": nummer, "st": status, "k": kunde, "s": summe, "datum": belegdatum,
         "b": json.dumps(bausteine or {})})
    for nr, p, netto in zeilen:
        verbindung.execute(text(
            "INSERT INTO domain_docflow.document_items (id, tenant_id, header_id, line_number, article_number, "
            "description, quantity, unit, unit_price, discount_percent, tax_rate, line_total_net, line_total_tax, "
            "line_total_gross, created_at, updated_at) VALUES (:id, :t, :h, :nr, :a, :d, :m, :e, :p, :r, 0, :n, 0, :n, "
            "NOW(), NOW())"),
            {"id": str(uuid.uuid4()), "t": mandant, "h": kennung, "nr": nr, "a": p["artikel"],
             "d": p.get("bezeichnung"), "m": p["menge"], "e": p.get("einheit"), "p": p.get("preis", 0),
             "r": p.get("rabatt", 0), "n": netto})
    return kennung


def entferne_belege(verbindung, kennungen: Iterable[str]) -> None:
    """Testbelege samt Positionen, Verknuepfungen und Statushistorie entfernen (Wartungsschalter von DocFlow)."""
    ids = [str(k) for k in kennungen]
    if not ids:
        return
    verbindung.execute(text("SELECT set_config('valeo.docflow_wartung', 'loeschen', true)"))
    for sql in (
        "DELETE FROM domain_docflow.document_links WHERE from_header_id = ANY(:ids) OR to_header_id = ANY(:ids)",
        "DELETE FROM domain_docflow.document_status_history WHERE header_id = ANY(:ids)",
        "DELETE FROM domain_docflow.document_items WHERE header_id = ANY(:ids)",
        "DELETE FROM domain_docflow.document_headers WHERE id = ANY(:ids)",
    ):
        verbindung.execute(text(sql), {"ids": ids})
