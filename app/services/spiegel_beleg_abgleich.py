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

import json
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.uuid7 import uuid7
from app.services.legacy_interface_adapter_service import LegacyAdapterError, LegacyInterfaceAdapterService

OBJEKTART = "beleg"
QUELLSYSTEM = "l3"
BELEGARTEN = frozenset({
    "sales_offer", "sales_order", "sales_delivery", "sales_invoice", "sales_credit_memo",
    "purchase_order", "goods_receipt", "purchase_invoice", "purchase_credit_memo",
})


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


def abgleichen(db: Session, tenant_id: str, batch_id: str, *, actor: str, reason: str) -> dict[str, Any]:
    """Gleicht die L3-Belege eines freigegebenen Batches mit den nachvollzogenen VALEO-Belegen ab."""
    batch = db.execute(text(
        "SELECT profile_key, status FROM domain_integration.legacy_adapter_batches "
        "WHERE id = :id AND tenant_id = :t"), {"id": batch_id, "t": tenant_id}).mappings().first()
    if not batch or batch["status"] != "approved" or batch["profile_key"] != "l3_spiegel":
        raise LegacyAdapterError("Nur freigegebene Batches mit Profil l3_spiegel sind abgleichsfaehig")
    zeilen = db.execute(text(
        "SELECT line_no, source_ref, canonical_payload FROM domain_integration.legacy_adapter_staging "
        "WHERE tenant_id = :t AND batch_id = :b AND validation_status = 'valid' AND record_type = :o "
        "ORDER BY line_no"), {"t": tenant_id, "b": batch_id, "o": OBJEKTART}).mappings().all()

    zaehler = {"neu": 0, "geaendert": 0, "unveraendert": 0, "fehler": 0}
    summen: dict[str, dict[str, Decimal]] = defaultdict(lambda: {"l3": Decimal("0"), "valeo": Decimal("0")})
    gesehen: set[tuple[str, str]] = set()
    zeitraum: list[str] = []
    for z in zeilen:
        p = dict(z["canonical_payload"] or {})
        art, nr = str(p.get("belegart") or "").strip(), str(p.get("belegnummer") or "").strip()
        ergebnis, differenzen, fehler = "unveraendert", {}, None
        try:
            if art not in BELEGARTEN:
                raise ValueError(f"Belegart {art or '-'} ist nicht zugeordnet")
            l3 = {"datum": _datum(p.get("datum")), "netto": _betrag(p.get("netto")), "brutto": _betrag(p.get("brutto"))}
            if l3["datum"]:
                zeitraum.append(l3["datum"])
            gesehen.add((art, nr))
            summen[art]["l3"] += l3["brutto"] or Decimal("0")
            valeo = db.execute(text(
                "SELECT document_date::date AS datum, total_net AS netto, total_gross AS brutto "
                "FROM domain_docflow.document_headers WHERE tenant_id = :t AND source_system = :q AND source_ref = :nr "
                "AND doc_type = :art AND deleted_at IS NULL ORDER BY created_at DESC LIMIT 1"),
                {"t": tenant_id, "q": QUELLSYSTEM, "nr": nr, "art": art}).mappings().first()
            if valeo is None:
                raise ValueError(f"Beleg {art} {nr} ist in VALEO nicht nachvollzogen")
            ist = {"datum": valeo["datum"].isoformat() if valeo["datum"] else None,
                   "netto": _betrag(valeo["netto"]), "brutto": _betrag(valeo["brutto"])}
            summen[art]["valeo"] += ist["brutto"] or Decimal("0")
            differenzen = {f: {"valeo": str(ist[f]) if ist[f] is not None else None,
                               "l3": str(l3[f]) if l3[f] is not None else None}
                           for f in ("datum", "netto", "brutto") if l3[f] is not None and ist[f] != l3[f]}
            if differenzen:
                ergebnis = "geaendert"
        except ValueError as exc:
            ergebnis, fehler = "fehler", str(exc)
        zaehler[ergebnis] += 1
        db.execute(text(
            "INSERT INTO domain_integration.spiegel_protokoll (id, tenant_id, batch_id, line_no, objektart, "
            "quellschluessel, ergebnis, differenzen, fehler) VALUES (:id, :t, :b, :n, :o, :k, :e, CAST(:d AS JSONB), :f)"),
            {"id": str(uuid7()), "t": tenant_id, "b": batch_id, "n": z["line_no"], "o": OBJEKTART,
             "k": z["source_ref"], "e": ergebnis, "d": json.dumps(differenzen), "f": fehler})

    fehlt_in_l3: list[dict[str, str]] = []
    if zeitraum:
        for art, nr in db.execute(text(
                "SELECT doc_type, source_ref FROM domain_docflow.document_headers WHERE tenant_id = :t "
                "AND source_system = :q AND deleted_at IS NULL AND document_date::date BETWEEN :von AND :bis "
                "ORDER BY doc_type, source_ref"),
                {"t": tenant_id, "q": QUELLSYSTEM, "von": min(zeitraum), "bis": max(zeitraum)}).fetchall():
            if (str(art), str(nr)) not in gesehen:
                fehlt_in_l3.append({"belegart": str(art), "belegnummer": str(nr)})
    LegacyInterfaceAdapterService(db, tenant_id)._audit(
        batch["profile_key"], "mirror_documents_reconciled", actor, reason, batch_id=batch_id,
        details={**zaehler, "fehlt_in_l3": len(fehlt_in_l3)})
    db.commit()
    return {"batch_id": batch_id, **zaehler, "fehlt_in_l3": fehlt_in_l3,
            "summen": {a: {k: str(v) for k, v in s.items()} for a, s in sorted(summen.items())},
            "zeitraum": [min(zeitraum), max(zeitraum)] if zeitraum else None,
            "abweichungsfrei": zaehler["geaendert"] == 0 and zaehler["fehler"] == 0 and not fehlt_in_l3}
