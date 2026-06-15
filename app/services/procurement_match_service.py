"""Beschaffungs-Abgleich / 3-Wege-Match (DOM-PROC-004).

Gleicht Bestellung (domain_einkauf.bestellungen/_positionen) gegen Wareneingang
(einkauf_wareneingaenge/_positionen) ab — Basis für den 3-Wege-Match; die
Rechnungs-Stufe wird ergänzt, sobald ein PO-Bezug am Eingangsrechnungs-Modell
vorliegt.

Je Bestellposition: bestellt vs. geliefert (aggregiert aus WE-Zeilen) → offene
Menge, Über-/Unterlieferung (Toleranz), Wertabweichung. Liefert zusätzlich Lücken
(kein WE, Teil-/Überlieferung). Die Vergleichslogik ist rein (ohne DB) und damit
deterministisch testbar.
"""

from __future__ import annotations

import json
import uuid
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

_DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"
# Mengen-Toleranz (%) bevor Über-/Unterlieferung als Abweichung gilt.
_MENGE_TOLERANZ_PCT = Decimal("1.0")
# Wert-Toleranz (%) für Rechnungsabgleich gegen gelieferten Wert.
_WERT_TOLERANZ_PCT = Decimal("2.0")
_FOLLOW_UP_ACTIONS = frozenset({"nachforderung", "reklamation", "eskalation", "freigabe"})


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
        self.tenant_id = tenant_id or _DEFAULT_TENANT

    # ── Geliefert-Mengen je PO-Position aus Wareneingängen ─────────────────────
    def _delivered_by_line(self, po_id: Optional[str], po_number: Optional[str]) -> dict[str, Decimal]:
        """Summiert WE-Zeilenmengen je PO-Positionsnummer (po_line_number)."""
        rows = self.db.execute(
            text(
                "SELECT bp.pos_nr AS posnr, COALESCE(SUM(l.received_quantity),0) AS menge "
                "FROM einkauf_wareneingaenge gr "
                "JOIN domain_einkauf.bestellungen b ON b.id::text = gr.purchase_order_id "
                "JOIN einkauf_wareneingang_positionen l ON l.wareneingang_id = gr.id "
                "JOIN domain_einkauf.bestellung_positionen bp "
                "  ON bp.id::text = l.purchase_order_item_id "
                "WHERE b.tenant_id = :t "
                "  AND (b.id::text = :pid OR b.bestellnummer = :pnum) "
                "GROUP BY bp.pos_nr"
            ),
            {"t": self.tenant_id, "pid": str(po_id) if po_id else "", "pnum": po_number or ""},
        ).mappings().all()
        return {str(r["posnr"]): Decimal(str(r["menge"] or 0)) for r in rows}

    def _goods_receipts(self, po_id: Optional[str], po_number: Optional[str]) -> list[dict]:
        rows = self.db.execute(
            text(
                "SELECT gr.id, COALESCE(gr.delivery_note_number, gr.id) AS gr_number, "
                "gr.received_date AS receipt_date, "
                "gr.quality_inspection_status AS status, gr.delivery_note_number "
                "FROM einkauf_wareneingaenge gr "
                "JOIN domain_einkauf.bestellungen b ON b.id::text = gr.purchase_order_id "
                "WHERE b.tenant_id = :t "
                "  AND (b.id::text = :pid OR b.bestellnummer = :pnum) "
                "ORDER BY gr.received_date"
            ),
            {"t": self.tenant_id, "pid": str(po_id) if po_id else "", "pnum": po_number or ""},
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
                "EXISTS(SELECT 1 FROM einkauf_wareneingaenge gr "
                "       WHERE gr.purchase_order_id = b.id::text) AS hat_we "
                "FROM domain_einkauf.bestellungen b WHERE b.tenant_id = :t "
                "ORDER BY b.bestelldatum DESC NULLS LAST, b.created_at DESC LIMIT :lim"
            ),
            {"t": self.tenant_id, "lim": max(1, min(limit, 500))},
        ).mappings().all()
        return [{"bestellnummer": r["bestellnummer"],
                 "datum": r["bestelldatum"].isoformat() if r["bestelldatum"] else None,
                 "status": r["status"], "netto_summe": _f(r["netto_summe"]),
                 "positionen": int(r["pos"]), "hat_wareneingang": bool(r["hat_we"])} for r in rows]

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

        rechnungen = self._invoices_for_po(base["bestellnummer"])
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
                "ORDER BY created_at DESC LIMIT :lim"
            ),
            {"t": self.tenant_id, "po": bestellnummer, "lim": max(1, min(limit, 200))},
        ).mappings().all()
        return [
            {
                "id": str(r["id"]),
                "action_type": r["action_type"],
                "ausnahme_code": r["ausnahme_code"],
                "grund": r["grund"],
                "eskalationsstufe": int(r["eskalationsstufe"] or 1),
                "created_at": r["created_at"].isoformat() if r["created_at"] else None,
                "created_by": r["created_by"],
            }
            for r in rows
        ]

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
        self.db.execute(
            text(
                "INSERT INTO domain_einkauf.procurement_follow_up "
                "(id, tenant_id, bestellnummer, action_type, ausnahme_code, grund, eskalationsstufe, created_by) "
                "VALUES (:id, :t, :po, :action, :code, :grund, :stufe, :by)"
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
        )
        self.db.commit()
        items = self.list_follow_ups(bestellnummer, limit=1)
        return items[0] if items else {
            "id": entry_id,
            "action_type": action,
            "ausnahme_code": ausnahme_code,
            "grund": reason,
            "eskalationsstufe": eskalationsstufe,
            "created_by": created_by,
        }

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
