"""Beschaffungs-Abgleich / 3-Wege-Match (DOM-PROC-004).

Gleicht Bestellung (domain_einkauf.bestellungen/_positionen) gegen Wareneingang
(public.inventory_goods_receipts/_lines) ab — Basis für den 3-Wege-Match; die
Rechnungs-Stufe wird ergänzt, sobald ein PO-Bezug am Eingangsrechnungs-Modell
vorliegt.

Je Bestellposition: bestellt vs. geliefert (aggregiert aus WE-Zeilen) → offene
Menge, Über-/Unterlieferung (Toleranz), Wertabweichung. Liefert zusätzlich Lücken
(kein WE, Teil-/Überlieferung). Die Vergleichslogik ist rein (ohne DB) und damit
deterministisch testbar.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

_DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"
# Mengen-Toleranz (%) bevor Über-/Unterlieferung als Abweichung gilt.
_MENGE_TOLERANZ_PCT = Decimal("1.0")


def _f(v):
    return float(v) if isinstance(v, Decimal) else v


def match_position(bestellt: Decimal, geliefert: Decimal,
                   toleranz_pct: Decimal = _MENGE_TOLERANZ_PCT) -> dict:
    """Reiner Mengen-Abgleich einer Position. Liefert Status + Abweichung.

    Status: offen (0 geliefert) · teilgeliefert · vollstaendig · ueberliefert."""
    bestellt = Decimal(str(bestellt or 0))
    geliefert = Decimal(str(geliefert or 0))
    offen = bestellt - geliefert
    if bestellt <= 0:
        status = "ohne_menge"
        abw_pct = Decimal("0")
    else:
        abw_pct = ((geliefert - bestellt) / bestellt * 100).quantize(Decimal("0.01"))
        if geliefert <= 0:
            status = "offen"
        elif geliefert < bestellt * (1 - toleranz_pct / 100):
            status = "teilgeliefert"
        elif geliefert > bestellt * (1 + toleranz_pct / 100):
            status = "ueberliefert"
        else:
            status = "vollstaendig"
    return {
        "bestellt": _f(bestellt),
        "geliefert": _f(geliefert),
        "offen": _f(offen),
        "status": status,
        "abweichung_pct": _f(abw_pct),
        "abweichung": status in ("teilgeliefert", "ueberliefert"),
    }


class ProcurementMatchService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        self.db = db
        self.tenant_id = tenant_id or _DEFAULT_TENANT

    # ── Geliefert-Mengen je PO-Position aus Wareneingängen ─────────────────────
    def _delivered_by_line(self, po_id: Optional[str], po_number: Optional[str]) -> dict[str, Decimal]:
        """Summiert WE-Zeilenmengen je PO-Positionsnummer (po_line_number)."""
        rows = self.db.execute(
            text(
                "SELECT l.po_line_number AS posnr, COALESCE(SUM(l.received_quantity),0) AS menge "
                "FROM public.inventory_goods_receipts gr "
                "JOIN public.inventory_goods_receipt_lines l ON l.goods_receipt_id = gr.id "
                "WHERE gr.tenant_id = :t AND (gr.po_id::text = :pid OR gr.po_number = :pnum) "
                "GROUP BY l.po_line_number"
            ),
            {"t": self.tenant_id, "pid": po_id or "", "pnum": po_number or ""},
        ).mappings().all()
        return {str(r["posnr"]): Decimal(str(r["menge"] or 0)) for r in rows}

    def _goods_receipts(self, po_id: Optional[str], po_number: Optional[str]) -> list[dict]:
        rows = self.db.execute(
            text(
                "SELECT id, gr_number, receipt_date, status, delivery_note_number "
                "FROM public.inventory_goods_receipts "
                "WHERE tenant_id = :t AND (po_id::text = :pid OR po_number = :pnum) "
                "ORDER BY receipt_date"
            ),
            {"t": self.tenant_id, "pid": po_id or "", "pnum": po_number or ""},
        ).mappings().all()
        return [{"id": str(r["id"]), "gr_number": r["gr_number"],
                 "datum": r["receipt_date"].isoformat() if r["receipt_date"] else None,
                 "status": r["status"], "lieferschein": r["delivery_note_number"]} for r in rows]

    def _resolve_po(self, bestellung: str) -> Optional[dict]:
        r = self.db.execute(
            text(
                "SELECT id, bestellnummer, lieferant_id, status, netto_summe, brutto_summe, "
                "bestelldatum FROM domain_einkauf.bestellungen "
                "WHERE tenant_id = :t AND (id::text = :v OR bestellnummer = :v) LIMIT 1"
            ),
            {"t": self.tenant_id, "v": bestellung},
        ).mappings().first()
        return dict(r) if r else None

    def match(self, bestellung: str) -> dict[str, Any]:
        po = self._resolve_po(bestellung)
        if not po:
            return {"found": False, "detail": "Bestellung nicht auflösbar."}
        positionen = self.db.execute(
            text(
                "SELECT pos_nr, artikel_nr, artikel_bezeichnung, menge, menge_geliefert, "
                "einzelpreis, netto_betrag, einheit, status "
                "FROM domain_einkauf.bestellung_positionen WHERE bestellung_id = :bid ORDER BY pos_nr"
            ),
            {"bid": po["id"]},
        ).mappings().all()
        delivered = self._delivered_by_line(po["id"], po["bestellnummer"])

        zeilen: list[dict] = []
        luecken: list[dict] = []
        for p in positionen:
            posnr = str(p["pos_nr"])
            # Geliefert: WE-Zeilen bevorzugt, sonst die am Beleg geführte Liefermenge.
            geliefert = delivered.get(posnr)
            if geliefert is None:
                geliefert = Decimal(str(p["menge_geliefert"] or 0))
            m = match_position(p["menge"], geliefert)
            preis = _f(p["einzelpreis"])
            wert_offen = (m["offen"] or 0) * (preis or 0) if preis is not None else None
            zeilen.append({
                "pos_nr": p["pos_nr"], "artikel_nr": p["artikel_nr"],
                "bezeichnung": p["artikel_bezeichnung"], "einheit": p["einheit"],
                "einzelpreis": preis, "wert_offen": wert_offen, **m,
            })
            if m["status"] == "offen":
                luecken.append({"pos_nr": p["pos_nr"], "schwere": "info",
                                "text": f"Position {p['pos_nr']} ohne Wareneingang."})
            elif m["status"] == "teilgeliefert":
                luecken.append({"pos_nr": p["pos_nr"], "schwere": "warnung",
                                "text": f"Position {p['pos_nr']} nur teilgeliefert ({m['geliefert']}/{m['bestellt']})."})
            elif m["status"] == "ueberliefert":
                luecken.append({"pos_nr": p["pos_nr"], "schwere": "warnung",
                                "text": f"Position {p['pos_nr']} überliefert ({m['geliefert']}/{m['bestellt']})."})

        wareneingaenge = self._goods_receipts(po["id"], po["bestellnummer"])
        vollstaendig = bool(zeilen) and all(z["status"] in ("vollstaendig", "ueberliefert") for z in zeilen)
        return {
            "found": True,
            "bestellnummer": po["bestellnummer"],
            "status": po["status"],
            "lieferant_id": str(po["lieferant_id"]) if po["lieferant_id"] else None,
            "netto_summe": _f(po["netto_summe"]),
            "positionen": zeilen,
            "wareneingaenge": wareneingaenge,
            "luecken": luecken,
            "summary": {
                "positionen": len(zeilen),
                "wareneingaenge": len(wareneingaenge),
                "vollstaendig_geliefert": vollstaendig,
                "hat_abweichung": any(z["abweichung"] for z in zeilen),
                "offene_luecken": len(luecken),
            },
        }

    def list_orders(self, limit: int = 50) -> list[dict]:
        rows = self.db.execute(
            text(
                "SELECT b.id, b.bestellnummer, b.bestelldatum, b.status, b.netto_summe, "
                "(SELECT count(*) FROM domain_einkauf.bestellung_positionen p WHERE p.bestellung_id = b.id) AS pos, "
                "EXISTS(SELECT 1 FROM public.inventory_goods_receipts gr "
                "       WHERE gr.tenant_id = b.tenant_id AND (gr.po_id = b.id OR gr.po_number = b.bestellnummer)) AS hat_we "
                "FROM domain_einkauf.bestellungen b WHERE b.tenant_id = :t "
                "ORDER BY b.bestelldatum DESC NULLS LAST, b.created_at DESC LIMIT :lim"
            ),
            {"t": self.tenant_id, "lim": max(1, min(limit, 500))},
        ).mappings().all()
        return [{"bestellnummer": r["bestellnummer"],
                 "datum": r["bestelldatum"].isoformat() if r["bestelldatum"] else None,
                 "status": r["status"], "netto_summe": _f(r["netto_summe"]),
                 "positionen": int(r["pos"]), "hat_wareneingang": bool(r["hat_we"])} for r in rows]
