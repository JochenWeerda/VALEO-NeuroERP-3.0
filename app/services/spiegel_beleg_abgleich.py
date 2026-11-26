"""Spiegelbetrieb L3 -> VALEO: taeglicher Belegabgleich (M6, 26.11.2026) - liest nur, bucht nie.

Im Spiegelbetrieb werden L3-Belege nicht kopiert, sondern in VALEO ueber die eigenen Ablaeufe nachvollzogen. Regel fuer
den Nachweis: Ein nachvollzogener Beleg traegt ``source_system = 'l3'`` und ``source_ref = <L3-Belegnummer>``
(``domain_docflow.document_headers``; der Anlage-Befehl nimmt beide Felder an).

Quelle: L3-Belegkoepfe (``WWS_VERKAUF1``, ``WWS_VLIEFER1``, ``WWS_ARECHNUNG1``, ``WWS_ELIEFER1``, ``WWS_EINKAUF1``,
``WWS_BESTELLUNG1`` ...) als Objektart ``beleg`` ueber die Adapterstrecke (Profil ``l3_spiegel``, freigegeben).
Kanonisch: ``belegart`` (VALEO-Belegart, z. B. ``sales_invoice`` - die Zuordnung L3-Tabelle -> Belegart steht in der
Abzugsabfrage), ``belegnummer``, ``datum``, ``netto``, ``brutto``.

Ergebnis je L3-Beleg im Spiegelprotokoll: ``unveraendert`` (Datum und Betraege gleich), ``geaendert``
(Felddifferenzen), ``fehler`` (nicht nachvollzogen oder Belegart unbekannt). Dazu ``fehlt_in_l3``: L3-Belege in VALEO
im Zeitraum des Abzugs, die der Abzug nicht enthaelt. Summen je Belegart fuer den Tagesabgleich "Belege, Betraege".
"""
from __future__ import annotations

from collections import defaultdict
from decimal import Decimal, InvalidOperation
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.spiegel_abgleich_basis import abschliessen, freigegebene_zeilen, neuer_zaehler, protokolliere

OBJEKTART = "beleg"
QUELLSYSTEM = "l3"
BELEGARTEN = frozenset({
    "sales_offer", "sales_order", "sales_delivery", "sales_invoice", "sales_credit_memo",
    "purchase_order", "goods_receipt", "purchase_invoice", "purchase_credit_memo",
})
FELDER = ("datum", "netto", "brutto")


def _betrag(roh: Any) -> Decimal | None:
    wert = str(roh or "").strip()
    if not wert:
        return None
    if "," in wert and "." not in wert:
        wert = wert.replace(",", ".")
    try:
        return Decimal(wert).quantize(Decimal("0.01"))
    except InvalidOperation as fehler:
        raise ValueError(f"Betrag {roh!r} ist keine Zahl") from fehler


def _datum(roh: Any) -> str | None:
    wert = str(roh or "").strip()
    if not wert:
        return None
    if len(wert) >= 10 and wert[2] == "." and wert[5] == ".":
        return f"{wert[6:10]}-{wert[3:5]}-{wert[0:2]}"
    return wert[:10]


def _valeo_beleg(db: Session, tenant_id: str, art: str, nr: str) -> dict[str, Any] | None:
    zeile = db.execute(text(
        "SELECT document_date::date AS datum, total_net AS netto, total_gross AS brutto "
        "FROM domain_docflow.document_headers WHERE tenant_id = :t AND source_system = :q AND source_ref = :nr "
        "AND doc_type = :art AND deleted_at IS NULL ORDER BY created_at DESC LIMIT 1"),
        {"t": tenant_id, "q": QUELLSYSTEM, "nr": nr, "art": art}).mappings().first()
    if zeile is None:
        return None
    return {"datum": zeile["datum"].isoformat() if zeile["datum"] else None,
            "netto": _betrag(zeile["netto"]), "brutto": _betrag(zeile["brutto"])}


def _vergleiche(l3: dict[str, Any], ist: dict[str, Any]) -> dict[str, Any]:
    def text_(wert: Any) -> str | None:
        return None if wert is None else str(wert)

    return {f: {"valeo": text_(ist[f]), "l3": text_(l3[f])} for f in FELDER if l3[f] is not None and ist[f] != l3[f]}


def _fehlt_in_l3(db: Session, tenant_id: str, zeitraum: list[str], gesehen: set[tuple[str, str]]) -> list[dict[str, str]]:
    if not zeitraum:
        return []
    zeilen = db.execute(text(
        "SELECT doc_type, source_ref FROM domain_docflow.document_headers WHERE tenant_id = :t "
        "AND source_system = :q AND deleted_at IS NULL AND document_date::date BETWEEN :von AND :bis "
        "ORDER BY doc_type, source_ref"),
        {"t": tenant_id, "q": QUELLSYSTEM, "von": min(zeitraum), "bis": max(zeitraum)}).fetchall()
    return [{"belegart": str(art), "belegnummer": str(nr)} for art, nr in zeilen if (str(art), str(nr)) not in gesehen]


class _Lauf:
    """Zustand eines Abgleichslaufs: Summen, gesehene Belege, Zeitraum."""

    def __init__(self) -> None:
        self.summen: dict[str, dict[str, Decimal]] = defaultdict(lambda: {"l3": Decimal("0"), "valeo": Decimal("0")})
        self.gesehen: set[tuple[str, str]] = set()
        self.zeitraum: list[str] = []

    def bewerte(self, db: Session, tenant_id: str, p: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        art, nr = str(p.get("belegart") or "").strip(), str(p.get("belegnummer") or "").strip()
        if art not in BELEGARTEN:
            raise ValueError(f"Belegart {art or '-'} ist nicht zugeordnet")
        l3 = {"datum": _datum(p.get("datum")), "netto": _betrag(p.get("netto")), "brutto": _betrag(p.get("brutto"))}
        if l3["datum"]:
            self.zeitraum.append(l3["datum"])
        self.gesehen.add((art, nr))
        self.summen[art]["l3"] += l3["brutto"] or Decimal("0")
        ist = _valeo_beleg(db, tenant_id, art, nr)
        if ist is None:
            raise ValueError(f"Beleg {art} {nr} ist in VALEO nicht nachvollzogen")
        self.summen[art]["valeo"] += ist["brutto"] or Decimal("0")
        differenzen = _vergleiche(l3, ist)
        return ("geaendert" if differenzen else "unveraendert"), differenzen


def abgleichen(db: Session, tenant_id: str, batch_id: str, *, actor: str, reason: str) -> dict[str, Any]:
    """Gleicht die L3-Belege eines freigegebenen Batches mit den nachvollzogenen VALEO-Belegen ab."""
    profil, zeilen = freigegebene_zeilen(db, tenant_id, batch_id, OBJEKTART)
    zaehler, lauf = neuer_zaehler(), _Lauf()
    for z in zeilen:
        differenzen: dict[str, Any] = {}
        fehler = None
        try:
            ergebnis, differenzen = lauf.bewerte(db, tenant_id, dict(z["canonical_payload"] or {}))
        except ValueError as exc:
            ergebnis, fehler = "fehler", str(exc)
        zaehler[ergebnis] += 1
        protokolliere(db, tenant_id, batch_id, z, OBJEKTART, ergebnis, differenzen, fehler)
    fehlt = _fehlt_in_l3(db, tenant_id, lauf.zeitraum, lauf.gesehen)
    abschliessen(db, tenant_id, batch_id, profil, "mirror_documents_reconciled", actor, reason,
                 {**zaehler, "fehlt_in_l3": len(fehlt)})
    return {"batch_id": batch_id, **zaehler, "fehlt_in_l3": fehlt,
            "summen": {a: {k: str(v) for k, v in s.items()} for a, s in sorted(lauf.summen.items())},
            "zeitraum": [min(lauf.zeitraum), max(lauf.zeitraum)] if lauf.zeitraum else None,
            "abweichungsfrei": zaehler["geaendert"] == 0 and zaehler["fehler"] == 0 and not fehlt}
