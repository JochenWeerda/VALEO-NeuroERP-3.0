"""Beschaffungs-Abgleich / 3-Wege-Match (DOM-PROC-004).

Gleicht Bestellung, Wareneingang und Eingangsrechnung ab. Quelle ist DocFlow, der einzige Belegspeicher (BELEG-052):

* Bestellung = ``purchase_order`` mit ihren Positionen.
* Geliefert = was die Belegverknuepfung ``order_to_receipt`` je Position (``document_links.quantity_linked``) an
  nicht stornierte Wareneingaenge uebergeben hat - genau die Menge der Umwandlung.
* Rechnung = ``purchase_invoice`` aus der Bestellung (``order_to_purchase_invoice``) oder aus ihren Wareneingaengen
  (``receipt_to_purchase_invoice``); auch der Entwurf zaehlt, denn geprueft wird vor dem Buchen. Gibt es keine,
  zaehlen die der Bestellnummer zugeordneten Eingaenge des E-Rechnungs-Postfachs (``finance_erechnungen``).

Je Bestellposition: bestellt vs. geliefert → offene Menge, Ueber-/Unterlieferung (Toleranz), Wertabweichung. Liefert
zusaetzlich Luecken (kein WE, Teil-/Ueberlieferung). Die Vergleichslogik ist rein (ohne DB) und damit
deterministisch testbar.
"""

from __future__ import annotations

import json
import uuid
from decimal import Decimal
from typing import Any, Mapping, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

# Mengen-Toleranz (%) bevor Über-/Unterlieferung als Abweichung gilt.
_MENGE_TOLERANZ_PCT = Decimal("1.0")
# Wert-Toleranz (%) für Rechnungsabgleich gegen gelieferten Wert.
_WERT_TOLERANZ_PCT = Decimal("2.0")
_FOLLOW_UP_ACTIONS = frozenset({"nachforderung", "reklamation", "eskalation", "freigabe"})


def _f(v):
    return float(v) if isinstance(v, Decimal) else v


def _follow_up_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        'id': str(row['id']), 'action_type': row['action_type'],
        'ausnahme_code': row['ausnahme_code'], 'grund': row['grund'],
        'eskalationsstufe': int(row['eskalationsstufe'] or 1),
        'created_at': row['created_at'].isoformat() if row['created_at'] else None,
        'created_by': row['created_by'],
    }


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


def match_three_way_value(
    bezug: Decimal,
    fakturiert: Decimal,
    toleranz_pct: Decimal = _WERT_TOLERANZ_PCT,
) -> dict:
    """Reiner Wert-Abgleich gelieferter Bezug vs. fakturierter Betrag."""
    bezug = Decimal(str(bezug or 0))
    fakturiert = Decimal(str(fakturiert or 0))
    if bezug <= 0 and fakturiert <= 0:
        return {
            "bezug": 0.0,
            "fakturiert": 0.0,
            "differenz": 0.0,
            "abweichung_pct": 0.0,
            "status": "ohne_bezug",
            "abweichung": False,
        }
    if bezug <= 0:
        return {
            "bezug": 0.0,
            "fakturiert": _f(fakturiert),
            "differenz": _f(fakturiert),
            "abweichung_pct": 100.0,
            "status": "rechnung_ohne_bezug",
            "abweichung": True,
        }
    differenz = fakturiert - bezug
    abw_pct = (differenz / bezug * 100).quantize(Decimal("0.01"))
    abs_pct = abs(abw_pct)
    if abs_pct <= toleranz_pct:
        status = "abgeglichen"
        abweichung = False
    else:
        status = "wertabweichung"
        abweichung = True
    return {
        "bezug": _f(bezug),
        "fakturiert": _f(fakturiert),
        "differenz": _f(differenz),
        "abweichung_pct": _f(abw_pct),
        "status": status,
        "abweichung": abweichung,
    }


def calculate_ers_credit(
    positionen: list[dict],
    three_way: Optional[dict] = None,
) -> dict[str, Any]:
    """Berechnet ERS-Gutschrift aus Überlieferung und Rechnungsüberzahlung (reine Logik)."""
    lines: list[dict] = []
    total = Decimal("0")

    for pos in positionen:
        if pos.get("status") != "ueberliefert":
            continue
        offen = Decimal(str(pos.get("offen") or 0))
        preis = Decimal(str(pos.get("einzelpreis") or 0))
        excess = abs(offen) if offen < 0 else Decimal("0")
        if excess <= 0 or preis <= 0:
            continue
        amount = (excess * preis).quantize(Decimal("0.01"))
        total += amount
        lines.append({
            "pos_nr": pos.get("pos_nr"),
            "artikel_nr": pos.get("artikel_nr"),
            "typ": "ueberlieferung",
            "menge": _f(excess),
            "einzelpreis": _f(preis),
            "betrag_netto": _f(amount),
        })

    if three_way and three_way.get("abweichung") and three_way.get("status") == "wertabweichung":
        diff = Decimal(str(three_way.get("differenz") or 0))
        if diff > 0:
            total += diff
            lines.append({
                "typ": "rechnungsueberzahlung",
                "betrag_netto": _f(diff),
                "bezug": three_way.get("bezug"),
                "fakturiert": three_way.get("fakturiert"),
            })

    return {
        "betrag_netto": _f(total),
        "positionen": lines,
        "berechtigt": total > 0,
        "anzahl_zeilen": len(lines),
    }


class ProcurementMatchService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        self.db = db
        if not tenant_id:  # kein Rueckfall auf den Standardmandanten (bis 28.10.2026)
            raise ValueError("Mandant fehlt")
        self.tenant_id = tenant_id

    # ── Belege aus DocFlow ─────────────────────────────────────────────────────
    def _delivered_by_item(self, po_id: str) -> dict[str, Decimal]:
        """Gelieferte Menge je Bestellposition: Summe der Umwandlungen in nicht stornierte Wareneingaenge."""
        rows = self.db.execute(
            text(
                "SELECT l.from_item_id AS pos, COALESCE(SUM(l.quantity_linked), 0) AS menge "
                "FROM domain_docflow.document_links l "
                "JOIN domain_docflow.document_headers z ON z.id = l.to_header_id AND z.tenant_id = l.tenant_id "
                "WHERE l.tenant_id = :t AND l.from_header_id = :pid AND l.relation_type = 'order_to_receipt' "
                "AND z.deleted_at IS NULL AND z.status NOT IN ('cancelled', 'reversed') "
                "GROUP BY l.from_item_id"
            ),
            {"t": self.tenant_id, "pid": po_id},
        ).mappings().all()
        return {str(r["pos"]): Decimal(str(r["menge"] or 0)) for r in rows}

    def _goods_receipts(self, po_id: str) -> list[dict]:
        rows = self.db.execute(
            text(
                "SELECT z.id, z.doc_number, z.document_date, z.status, "
                "z.bausteine #>> '{referenzen,fremde_referenz}' AS lieferschein "
                "FROM domain_docflow.document_header_links k "
                "JOIN domain_docflow.document_headers z ON z.id = k.to_header_id AND z.tenant_id = k.tenant_id "
                "WHERE k.tenant_id = :t AND k.from_header_id = :pid AND k.relation_type = 'order_to_receipt' "
                "AND z.deleted_at IS NULL AND z.status NOT IN ('cancelled', 'reversed') "
                "ORDER BY z.document_date, z.created_at"
            ),
            {"t": self.tenant_id, "pid": po_id},
        ).mappings().all()
        return [{"id": str(r["id"]), "gr_number": r["doc_number"],
                 "datum": r["document_date"].isoformat() if r["document_date"] else None,
                 "status": r["status"], "lieferschein": r["lieferschein"]} for r in rows]

    def _resolve_po(self, bestellung: str) -> Optional[dict]:
        r = self.db.execute(
            text(
                "SELECT id, doc_number AS bestellnummer, supplier_id AS lieferant_id, status, "
                "total_net AS netto_summe, total_gross AS brutto_summe, document_date AS bestelldatum "
                "FROM domain_docflow.document_headers "
                "WHERE tenant_id = :t AND doc_type = 'purchase_order' AND deleted_at IS NULL "
                "AND (id::text = :v OR doc_number = :v) LIMIT 1"
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
                "SELECT id, line_number AS pos_nr, article_number AS artikel_nr, "
                "description AS artikel_bezeichnung, quantity AS menge, unit_price AS einzelpreis, "
                "line_total_net AS netto_betrag, unit AS einheit "
                "FROM domain_docflow.document_items WHERE header_id = :bid AND tenant_id = :t "
                "ORDER BY line_number"
            ),
            {"bid": po["id"], "t": self.tenant_id},
        ).mappings().all()
        delivered = self._delivered_by_item(str(po["id"]))

        zeilen: list[dict] = []
        luecken: list[dict] = []
        for p in positionen:
            geliefert = delivered.get(str(p["id"]), Decimal("0"))
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

        wareneingaenge = self._goods_receipts(str(po["id"]))
        vollstaendig = bool(zeilen) and all(z["status"] in ("vollstaendig", "ueberliefert") for z in zeilen)
        return {
            "found": True,
            "bestellung_id": str(po["id"]),
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
                "SELECT b.id, b.doc_number AS bestellnummer, b.document_date AS bestelldatum, b.status, "
                "b.total_net AS netto_summe, "
                "(SELECT count(*) FROM domain_docflow.document_items p "
                "  WHERE p.header_id = b.id AND p.tenant_id = b.tenant_id) AS pos, "
                "EXISTS(SELECT 1 FROM domain_docflow.document_header_links k "
                "       JOIN domain_docflow.document_headers z ON z.id = k.to_header_id AND z.tenant_id = k.tenant_id "
                "       WHERE k.tenant_id = b.tenant_id AND k.from_header_id = b.id "
                "       AND k.relation_type = 'order_to_receipt' AND z.deleted_at IS NULL "
                "       AND z.status NOT IN ('cancelled', 'reversed')) AS hat_we "
                "FROM domain_docflow.document_headers b "
                "WHERE b.tenant_id = :t AND b.doc_type = 'purchase_order' AND b.deleted_at IS NULL "
                "ORDER BY b.document_date DESC NULLS LAST, b.created_at DESC LIMIT :lim"
            ),
            {"t": self.tenant_id, "lim": max(1, min(limit, 500))},
        ).mappings().all()
        return [{"bestellnummer": r["bestellnummer"],
                 "datum": r["bestelldatum"].isoformat() if r["bestelldatum"] else None,
                 "status": r["status"], "netto_summe": _f(r["netto_summe"]),
                 "positionen": int(r["pos"]), "hat_wareneingang": bool(r["hat_we"])} for r in rows]

    def _docflow_invoices(self, po_id: str, bestellnummer: str) -> list[dict]:
        """Eingangsrechnungen der Bestellung aus DocFlow - direkt oder ueber ihre Wareneingaenge."""
        rows = self.db.execute(
            text(
                "SELECT DISTINCT z.id, z.doc_number, z.document_date, z.total_net, z.total_gross, z.status, "
                "z.created_at, "
                "(SELECT w.doc_number FROM domain_docflow.document_headers w "
                "  WHERE w.id = k.from_header_id AND w.tenant_id = k.tenant_id "
                "  AND k.relation_type = 'receipt_to_purchase_invoice') AS wareneingang "
                "FROM domain_docflow.document_header_links k "
                "JOIN domain_docflow.document_headers z ON z.id = k.to_header_id AND z.tenant_id = k.tenant_id "
                "WHERE k.tenant_id = :t AND z.doc_type = 'purchase_invoice' AND z.deleted_at IS NULL "
                "AND z.status NOT IN ('cancelled', 'reversed') "
                "AND ((k.relation_type = 'order_to_purchase_invoice' AND k.from_header_id = :pid) "
                "  OR (k.relation_type = 'receipt_to_purchase_invoice' AND k.from_header_id IN ( "
                "        SELECT kw.to_header_id FROM domain_docflow.document_header_links kw "
                "         WHERE kw.tenant_id = :t AND kw.from_header_id = :pid "
                "           AND kw.relation_type = 'order_to_receipt'))) "
                "ORDER BY z.document_date DESC NULLS LAST, z.created_at DESC"
            ),
            {"t": self.tenant_id, "pid": po_id},
        ).mappings().all()
        return [
            {
                "id": str(r["id"]),
                "rechnungsnummer": r["doc_number"],
                "datum": r["document_date"].isoformat() if r["document_date"] else None,
                "gesamt_netto": _f(r["total_net"]),
                "gesamt_brutto": _f(r["total_gross"]),
                "zugeordneter_auftrag": bestellnummer,
                "zugeordneter_lieferschein": r["wareneingang"],
                "status": r["status"],
                "quelle": "docflow",
            }
            for r in rows
        ]

    def _invoices_for_po(self, bestellnummer: str) -> list[dict]:
        rows = self.db.execute(
            text(
                "SELECT id, rechnungsnummer, rechnungsdatum, gesamt_netto, gesamt_brutto, "
                "zugeordneter_auftrag, zugeordneter_lieferschein, status "
                "FROM public.finance_erechnungen "
                "WHERE tenant_id = :t AND zugeordneter_auftrag = :po "
                "ORDER BY rechnungsdatum DESC NULLS LAST, created_at DESC"
            ),
            {"t": self.tenant_id, "po": bestellnummer},
        ).mappings().all()
        return [
            {
                "id": str(r["id"]),
                "rechnungsnummer": r["rechnungsnummer"],
                "datum": r["rechnungsdatum"].isoformat() if r["rechnungsdatum"] else None,
                "gesamt_netto": _f(r["gesamt_netto"]),
                "gesamt_brutto": _f(r["gesamt_brutto"]),
                "zugeordneter_auftrag": r["zugeordneter_auftrag"],
                "zugeordneter_lieferschein": r["zugeordneter_lieferschein"],
                "status": r["status"],
                "quelle": "e-rechnung-postfach",
            }
            for r in rows
        ]

    def match_three_way(self, bestellung: str) -> dict[str, Any]:
        """Bestellung ↔ Wareneingang ↔ Eingangsrechnung (Kopfebene)."""
        base = self.match(bestellung)
        if not base.get("found"):
            return base

        positionen = base.get("positionen") or []
        geliefert_wert = Decimal("0")
        for pos in positionen:
            menge = Decimal(str(pos.get("geliefert") or 0))
            preis = Decimal(str(pos.get("einzelpreis") or 0))
            geliefert_wert += menge * preis

        # DocFlow fuehrt die Eingangsrechnung; nur ohne sie zaehlt das E-Rechnungs-Postfach (sonst doppelt).
        rechnungen = (self._docflow_invoices(base["bestellung_id"], base["bestellnummer"])
                      or self._invoices_for_po(base["bestellnummer"]))
        fakturiert_netto = sum(Decimal(str(r.get("gesamt_netto") or 0)) for r in rechnungen)
        wert_match = match_three_way_value(geliefert_wert, fakturiert_netto)

        ausnahmen: list[dict] = list(base.get("luecken") or [])
        if not rechnungen:
            ausnahmen.append({
                "schwere": "warnung",
                "code": "keine_rechnung",
                "text": "Keine Eingangsrechnung der Bestellung zugeordnet.",
            })
        elif wert_match["abweichung"]:
            ausnahmen.append({
                "schwere": "blocker",
                "code": "rechnungswert_abweichung",
                "text": (
                    f"Rechnungswert ({wert_match['fakturiert']}) weicht vom gelieferten "
                    f"Wert ({wert_match['bezug']}) um {wert_match['abweichung_pct']} % ab."
                ),
            })

        po_netto = Decimal(str(base.get("netto_summe") or 0))
        # Rechnungsstufe: gelieferter Wert vs. fakturiert (PO-Mengenabweichung bleibt in base.summary).
        drei_wege_ok = bool(rechnungen) and not wert_match["abweichung"]

        return {
            **base,
            "rechnungen": rechnungen,
            "three_way": {
                "bestellt_wert": _f(po_netto),
                "geliefert_wert": _f(geliefert_wert),
                "fakturiert_netto": _f(fakturiert_netto),
                **wert_match,
                "drei_wege_abgeglichen": drei_wege_ok,
            },
            "ausnahmen": ausnahmen,
            "summary": {
                **base["summary"],
                "rechnungen": len(rechnungen),
                "drei_wege_abgeglichen": drei_wege_ok,
                "hat_ausnahme": len(ausnahmen) > 0,
            },
            "follow_ups": self.list_follow_ups(base["bestellnummer"]),
            "ers_preview": calculate_ers_credit(positionen, {
                **wert_match,
                "drei_wege_abgeglichen": drei_wege_ok,
            }),
            "ers_credits": self.list_ers_credits(base["bestellnummer"]),
        }

    def list_follow_ups(self, bestellnummer: str, limit: int = 50) -> list[dict]:
        rows = self.db.execute(
            text(
                "SELECT id, action_type, ausnahme_code, grund, eskalationsstufe, created_at, created_by "
                "FROM domain_einkauf.procurement_follow_up "
                "WHERE tenant_id = :t AND bestellnummer = :po "
                "ORDER BY created_at DESC, eskalationsstufe DESC, id DESC LIMIT :lim"
            ),
            {"t": self.tenant_id, "po": bestellnummer, "lim": max(1, min(limit, 200))},
        ).mappings().all()
        return [_follow_up_row(row) for row in rows]

    def create_follow_up(
        self,
        *,
        bestellnummer: str,
        action_type: str,
        grund: str,
        ausnahme_code: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> dict:
        action = (action_type or "").strip().lower()
        reason = (grund or "").strip()
        if action not in _FOLLOW_UP_ACTIONS:
            raise ValueError(f"Unbekannte Folgeaktion: {action_type}")
        if not reason:
            raise ValueError("Grund ist Pflicht.")

        order = self._resolve_po(bestellnummer)
        if order is None:
            raise ValueError("Bestellung nicht auflösbar.")
        bestellnummer = order["bestellnummer"]

        eskalationsstufe = 1
        if action == "eskalation":
            row = self.db.execute(
                text(
                    "SELECT COALESCE(MAX(eskalationsstufe), 0) AS max_stufe "
                    "FROM domain_einkauf.procurement_follow_up "
                    "WHERE tenant_id = :t AND bestellnummer = :po AND action_type = 'eskalation'"
                ),
                {"t": self.tenant_id, "po": bestellnummer},
            ).mappings().first()
            eskalationsstufe = int((row or {}).get("max_stufe") or 0) + 1

        entry_id = str(uuid.uuid4())
        inserted = self.db.execute(
            text(
                "INSERT INTO domain_einkauf.procurement_follow_up "
                "(id, tenant_id, bestellnummer, action_type, ausnahme_code, grund, eskalationsstufe, created_by) "
                "VALUES (:id, :t, :po, :action, :code, :grund, :stufe, :by) "
                "RETURNING id, action_type, ausnahme_code, grund, eskalationsstufe, created_at, created_by"
            ),
            {
                "id": entry_id,
                "t": self.tenant_id,
                "po": bestellnummer,
                "action": action,
                "code": ausnahme_code,
                "grund": reason,
                "stufe": eskalationsstufe,
                "by": created_by,
            },
        ).mappings().one()
        return _follow_up_row(inserted)

    def list_ers_credits(self, bestellnummer: str, limit: int = 20) -> list[dict]:
        rows = self.db.execute(
            text(
                "SELECT id, gutschrift_nummer, betrag_netto, grund, ausnahme_code, status, "
                "positionen_json, created_at, created_by "
                "FROM domain_einkauf.procurement_ers_credits "
                "WHERE tenant_id = :t AND bestellnummer = :po "
                "ORDER BY created_at DESC LIMIT :lim"
            ),
            {"t": self.tenant_id, "po": bestellnummer, "lim": max(1, min(limit, 100))},
        ).mappings().all()
        out = []
        for r in rows:
            pos_json = r["positionen_json"]
            if isinstance(pos_json, str):
                try:
                    pos_json = json.loads(pos_json)
                except json.JSONDecodeError:
                    pos_json = []
            out.append({
                "id": str(r["id"]),
                "gutschrift_nummer": r["gutschrift_nummer"],
                "betrag_netto": _f(r["betrag_netto"]),
                "grund": r["grund"],
                "ausnahme_code": r["ausnahme_code"],
                "status": r["status"],
                "positionen": pos_json or [],
                "created_at": r["created_at"].isoformat() if r["created_at"] else None,
                "created_by": r["created_by"],
            })
        return out

    def preview_ers(self, bestellung: str) -> dict[str, Any]:
        match = self.match_three_way(bestellung)
        if not match.get("found"):
            return match
        preview = match.get("ers_preview") or calculate_ers_credit(
            match.get("positionen") or [],
            match.get("three_way"),
        )
        return {**match, "ers_preview": preview}

    def create_ers_credit(
        self,
        *,
        bestellnummer: str,
        grund: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> dict:
        match = self.match_three_way(bestellnummer)
        if not match.get("found"):
            raise ValueError(match.get("detail") or "Bestellung nicht gefunden.")

        preview = calculate_ers_credit(match.get("positionen") or [], match.get("three_way"))
        if not preview["berechtigt"]:
            raise ValueError("Keine ERS-Gutschrift berechtigt (keine Überlieferung/Rechnungsüberzahlung).")

        reason = (grund or "").strip()
        if not reason:
            codes = [a.get("code") for a in (match.get("ausnahmen") or []) if a.get("code")]
            reason = f"ERS aus Match-Ausnahme ({', '.join(codes) or 'Abweichung'})"

        ausnahme_code = None
        for a in match.get("ausnahmen") or []:
            if a.get("code"):
                ausnahme_code = a["code"]
                break

        row = self.db.execute(
            text(
                "SELECT count(*) AS c FROM domain_einkauf.procurement_ers_credits "
                "WHERE tenant_id = :t AND bestellnummer = :po"
            ),
            {"t": self.tenant_id, "po": bestellnummer},
        ).mappings().first()
        count = int((row or {}).get("c") or 0)

        entry_id = str(uuid.uuid4())
        gs_nr = f"ERS-{bestellnummer}-{count + 1:03d}"
        pos_json = json.dumps(preview["positionen"], ensure_ascii=False)

        self.db.execute(
            text(
                "INSERT INTO domain_einkauf.procurement_ers_credits "
                "(id, tenant_id, bestellnummer, gutschrift_nummer, betrag_netto, grund, "
                "ausnahme_code, status, positionen_json, created_by) "
                "VALUES (:id, :t, :po, :nr, :betrag, :grund, :code, 'entwurf', CAST(:pos AS JSONB), :by)"
            ),
            {
                "id": entry_id,
                "t": self.tenant_id,
                "po": bestellnummer,
                "nr": gs_nr,
                "betrag": preview["betrag_netto"],
                "grund": reason,
                "code": ausnahme_code,
                "pos": pos_json,
                "by": created_by,
            },
        )
        self.db.commit()
        items = self.list_ers_credits(bestellnummer, limit=1)
        return items[0] if items else {
            "id": entry_id,
            "gutschrift_nummer": gs_nr,
            "betrag_netto": preview["betrag_netto"],
            "grund": reason,
            "status": "entwurf",
            "positionen": preview["positionen"],
        }
