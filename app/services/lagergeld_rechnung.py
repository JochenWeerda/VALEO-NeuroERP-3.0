"""Lagergeld als Ausgangsrechnung an den Einlagerer (M3, 24.11.2026).

Der Lagergeld-Lauf (``/inventory/storage-fees/run``) berechnet und protokolliert das Lagergeld je Eigentuemer, bucht
aber nicht: Lagergeld ist eine Leistung und wird wie jede Leistung ueber die Ausgangsrechnung gebucht (Umsatzsteuer,
offener Posten). Bis 24.11.2026 fehlte dieser Schritt - ein Lauf stand auf "posted", ohne Rechnung, Erloes oder Posten.

Hier entsteht je Einlagerer genau ein DocFlow-Rechnungsentwurf (``sales_invoice``) mit einer Position je Lagergeld-
Zeile. Freigabe und Buchung laufen danach wie bei jeder Rechnung ueber die Belegmaske. Der Verkaufs-Steuerschluessel
wird ausdruecklich angegeben (keine Vorgabe 19 %); eine Wiederholung legt nichts doppelt an.
"""
from __future__ import annotations

from collections import defaultdict

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError

QUELLE = "lagergeld"


def _pruefe_steuerschluessel(db: Session, tenant_id: str, code: str) -> None:
    gueltig = db.execute(text(
        "SELECT 1 FROM domain_erp.tax_keys WHERE tenant_id = :t AND code = :c AND active "
        "AND COALESCE(TRIM(revenue_account), '') <> '' AND COALESCE(reverse_charge, FALSE) = FALSE "
        "AND gueltig_von <= CURRENT_DATE AND (gueltig_bis IS NULL OR gueltig_bis >= CURRENT_DATE)"),
        {"t": tenant_id, "c": code}).first()
    if not gueltig:
        raise ValidationFailedError(f"Steuerschluessel {code} ist kein gueltiger Verkaufs-Steuerschluessel des Mandanten")


def rechnungen_zum_lauf(db: Session, tenant_id: str, run_id: str, *, steuerschluessel: str, artikel_nr: str,
                        akteur: str) -> list[dict]:
    """Legt je Einlagerer einen Rechnungsentwurf an und liefert ``[{partner_id, beleg_id, betrag, positionen}]``."""
    from app.services.beleg_anlage import Position, lege_beleg_an

    lauf = db.execute(text(
        "SELECT status, period_month FROM domain_inventory.consignment_storage_fee_runs "
        "WHERE id = :r AND tenant_id = :t"), {"r": run_id, "t": tenant_id}).mappings().first()
    if not lauf:
        raise EntityNotFoundError("Lagergeld-Lauf", run_id)
    if str(lauf["status"]) != "posted":
        raise ConflictError(f"Lagergeld-Lauf steht auf {lauf['status']} - Rechnungen nur aus einem abgeschlossenen Lauf")
    _pruefe_steuerschluessel(db, tenant_id, steuerschluessel)

    zeilen = db.execute(text(
        "SELECT owner_partner_id, article_id, warehouse_id, charge, basis_quantity, monthly_rate, amount "
        "FROM domain_inventory.consignment_storage_fee_charges WHERE run_id = :r AND tenant_id = :t "
        "ORDER BY owner_partner_id, article_id, warehouse_id, charge"), {"r": run_id, "t": tenant_id}).mappings().all()
    je_partner: dict[str, list] = defaultdict(list)
    for zeile in zeilen:
        je_partner[str(zeile["owner_partner_id"])].append(zeile)
    monat = lauf["period_month"].strftime("%m/%Y") if hasattr(lauf["period_month"], "strftime") else str(lauf["period_month"])

    ergebnis = []
    for partner_id, posten in je_partner.items():
        positionen = [Position(
            artikel_nr=artikel_nr, menge=float(z["basis_quantity"]), einzelpreis=float(z["monthly_rate"]),
            steuerschluessel=steuerschluessel,
            bezeichnung=f"Lagergeld {monat} - Artikel {z['article_id']}, Lager {z['warehouse_id']}"
                        + (f", Charge {z['charge']}" if z["charge"] else ""))
            for z in posten]
        beleg_id = lege_beleg_an(
            db, tenant_id, "sales_invoice", partner_id=partner_id, positionen=positionen, quelle=QUELLE,
            referenz=f"{run_id}:{partner_id}", akteur=akteur, entwurf_nr=f"LG-{monat.replace('/', '')}",
            idempotenz=f"{QUELLE}:{run_id}:{partner_id}")
        ergebnis.append({"partner_id": partner_id, "beleg_id": str(beleg_id), "positionen": len(positionen),
                         "betrag_netto": float(sum(float(z["amount"]) for z in posten))})
    db.commit()
    return ergebnis
