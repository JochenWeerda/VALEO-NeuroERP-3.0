"""Supply-Chain-Traceability (DOM-SUPPLY-004) — durchgängige, prüfbare Kette.

Stitcht die heute getrennt geführten Stufen zu einer einzigen, status- und
mengen-annotierten Genealogie je Lieferung zusammen. Rückgrat ist die
``weighing_tickets.id`` (Wiegeschein), auf die alle Folgeobjekte zeigen:

    Wiegung (weighing_tickets)
      └─ Annahme (harvest_acceptances.weighing_ticket_id)
      └─ Lager   (silo_lots.source_ticket_id  + silo_lot_movements)
      └─ Abrechnung (agrar_settlements.ticket_id)

Liefert je Stufe Status + Menge (kg) und prüft die **Mengen-Konsistenz** über die
Kette (Schwund/Abweichung) sowie **Lücken** (fehlende Folgeobjekte, nicht
freigegeben, nicht alloziert). Read-only und nicht-invasiv — keine Änderung an den
heißen Stufen-Tabellen; macht die Durchgängigkeit sichtbar und revisionsprüfbar.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

_DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"

# Toleranz für Mengen-Abweichung zwischen Stufen, bevor sie als Schwund/Differenz
# markiert wird (Trocknung/Reinigung verursachen legitime Differenzen).
_MENGE_TOLERANZ_PCT = Decimal("2.0")


def _f(v) -> Optional[float]:
    if v is None:
        return None
    if isinstance(v, Decimal):
        return float(v)
    return v


class SupplyChainTraceService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        self.db = db
        self.tenant_id = tenant_id or _DEFAULT_TENANT

    # ── Auflösung: Eingabe → weighing_ticket-Rückgrat ─────────────────────────
    def _resolve_ticket_id(
        self,
        *,
        ticket: Optional[str] = None,
        acceptance: Optional[str] = None,
        lot: Optional[str] = None,
        settlement: Optional[str] = None,
    ) -> Optional[str]:
        if ticket:
            r = self.db.execute(
                text(
                    "SELECT id FROM domain_inventory.weighing_tickets "
                    "WHERE tenant_id = :t AND (id::text = :v OR ticket_number = :v) LIMIT 1"
                ),
                {"t": self.tenant_id, "v": ticket},
            ).first()
            if r:
                return str(r[0])
        if acceptance:
            r = self.db.execute(
                text(
                    "SELECT weighing_ticket_id FROM domain_inventory.harvest_acceptances "
                    "WHERE tenant_id = :t AND (id::text = :v OR acceptance_number = :v) LIMIT 1"
                ),
                {"t": self.tenant_id, "v": acceptance},
            ).first()
            if r and r[0]:
                return str(r[0])
        if lot:
            r = self.db.execute(
                text(
                    "SELECT source_ticket_id FROM domain_inventory.silo_lots "
                    "WHERE tenant_id = :t AND (id::text = :v OR virtual_lot_number = :v) LIMIT 1"
                ),
                {"t": self.tenant_id, "v": lot},
            ).first()
            if r and r[0]:
                return str(r[0])
        if settlement:
            r = self.db.execute(
                text(
                    "SELECT ticket_id FROM domain_inventory.agrar_settlements "
                    "WHERE tenant_id = :t AND (id::text = :v OR settlement_number = :v) LIMIT 1"
                ),
                {"t": self.tenant_id, "v": settlement},
            ).first()
            if r and r[0]:
                return str(r[0])
        return None

    # ── Einzelne Stufen ───────────────────────────────────────────────────────
    def _wiegung(self, ticket_id: str) -> Optional[dict]:
        r = self.db.execute(
            text(
                "SELECT id, ticket_number, weighing_date, net_weight, billing_weight, "
                "gross_weight, tare_weight, status, allocation_status, vehicle_plate, "
                "moisture_pct, direction FROM domain_inventory.weighing_tickets "
                "WHERE id::text = :id AND tenant_id = :t LIMIT 1"
            ),
            {"id": ticket_id, "t": self.tenant_id},
        ).mappings().first()
        if not r:
            return None
        return {
            "stage": "wiegung",
            "label": "Wiegung",
            "ref": r["ticket_number"],
            "ref_id": str(r["id"]),
            "status": r["status"],
            "menge_kg": _f(r["billing_weight"]) or _f(r["net_weight"]),
            "zeitpunkt": r["weighing_date"].isoformat() if r["weighing_date"] else None,
            "facts": {
                "brutto_kg": _f(r["gross_weight"]),
                "tara_kg": _f(r["tare_weight"]),
                "netto_kg": _f(r["net_weight"]),
                "abrechnungsgewicht_kg": _f(r["billing_weight"]),
                "kennzeichen": r["vehicle_plate"],
                "feuchte_pct": _f(r["moisture_pct"]),
                "richtung": r["direction"],
                "allokation": r["allocation_status"],
            },
        }

    def _annahmen(self, ticket_id: str) -> list[dict]:
        rows = self.db.execute(
            text(
                "SELECT id, acceptance_number, delivery_date, release_status, contract_id, "
                "customer_id, article_id, invoice_id, invoice_number, total_gross_amount_eur, "
                "quality_protocol_id, stock_movement_id "
                "FROM domain_inventory.harvest_acceptances "
                "WHERE weighing_ticket_id::text = :id AND tenant_id = :t ORDER BY created_at"
            ),
            {"id": ticket_id, "t": self.tenant_id},
        ).mappings().all()
        out = []
        for r in rows:
            out.append({
                "stage": "annahme",
                "label": "Annahme",
                "ref": r["acceptance_number"],
                "ref_id": str(r["id"]),
                "status": r["release_status"],
                "menge_kg": None,
                "zeitpunkt": r["delivery_date"].isoformat() if r["delivery_date"] else None,
                "facts": {
                    "kontrakt_id": str(r["contract_id"]) if r["contract_id"] else None,
                    "kunde_id": str(r["customer_id"]) if r["customer_id"] else None,
                    "artikel_id": str(r["article_id"]) if r["article_id"] else None,
                    "rechnung": r["invoice_number"] or (str(r["invoice_id"]) if r["invoice_id"] else None),
                    "brutto_eur": _f(r["total_gross_amount_eur"]),
                    "qs_protokoll_id": str(r["quality_protocol_id"]) if r["quality_protocol_id"] else None,
                    "lagerbewegung_id": str(r["stock_movement_id"]) if r["stock_movement_id"] else None,
                },
            })
        return out

    def _lager(self, ticket_id: str) -> list[dict]:
        rows = self.db.execute(
            text(
                "SELECT id, silo_id, virtual_lot_number, quantity_tons, status, moisture_pct, "
                "protein_pct, impurities_pct, created_at FROM domain_inventory.silo_lots "
                "WHERE source_ticket_id::text = :id AND tenant_id = :t ORDER BY created_at"
            ),
            {"id": ticket_id, "t": self.tenant_id},
        ).mappings().all()
        out = []
        for r in rows:
            movements = self.db.execute(
                text(
                    "SELECT movement_type, quantity_tons, note, created_at "
                    "FROM domain_inventory.silo_lot_movements "
                    "WHERE silo_lot_id = :lid AND tenant_id = :t ORDER BY created_at"
                ),
                {"lid": r["id"], "t": self.tenant_id},
            ).mappings().all()
            out.append({
                "stage": "lager",
                "label": "Lager (Silo-Lot)",
                "ref": r["virtual_lot_number"],
                "ref_id": str(r["id"]),
                "status": r["status"],
                "menge_kg": _f(r["quantity_tons"]) * 1000 if r["quantity_tons"] is not None else None,
                "zeitpunkt": r["created_at"].isoformat() if r["created_at"] else None,
                "facts": {
                    "silo_id": str(r["silo_id"]) if r["silo_id"] else None,
                    "menge_t": _f(r["quantity_tons"]),
                    "feuchte_pct": _f(r["moisture_pct"]),
                    "protein_pct": _f(r["protein_pct"]),
                    "besatz_pct": _f(r["impurities_pct"]),
                    "bewegungen": [
                        {"typ": m["movement_type"], "menge_t": _f(m["quantity_tons"]),
                         "notiz": m["note"], "zeitpunkt": m["created_at"].isoformat() if m["created_at"] else None}
                        for m in movements
                    ],
                },
            })
        return out

    def _abrechnungen(self, ticket_id: str) -> list[dict]:
        rows = self.db.execute(
            text(
                "SELECT id, settlement_number, status, gross_quantity_kg, billing_quantity_kg, "
                "net_amount_eur, total_deductions_eur, posted_at, created_at "
                "FROM domain_inventory.agrar_settlements "
                "WHERE ticket_id::text = :id AND tenant_id = :t ORDER BY created_at"
            ),
            {"id": ticket_id, "t": self.tenant_id},
        ).mappings().all()
        out = []
        for r in rows:
            out.append({
                "stage": "abrechnung",
                "label": "Abrechnung",
                "ref": r["settlement_number"],
                "ref_id": str(r["id"]),
                "status": r["status"],
                "menge_kg": _f(r["billing_quantity_kg"]) or _f(r["gross_quantity_kg"]),
                "zeitpunkt": (r["posted_at"] or r["created_at"]).isoformat() if (r["posted_at"] or r["created_at"]) else None,
                "facts": {
                    "brutto_menge_kg": _f(r["gross_quantity_kg"]),
                    "abrechnungsmenge_kg": _f(r["billing_quantity_kg"]),
                    "abzuege_eur": _f(r["total_deductions_eur"]),
                    "netto_eur": _f(r["net_amount_eur"]),
                    "gebucht_am": r["posted_at"].isoformat() if r["posted_at"] else None,
                },
            })
        return out

    # ── Konsistenz & Lücken ───────────────────────────────────────────────────
    def _mengen_check(self, nodes: list[dict]) -> list[dict]:
        """Vergleicht die kg-Mengen benachbarter Stufen; markiert Schwund/Differenz."""
        checks: list[dict] = []
        relevant = [n for n in nodes if n.get("menge_kg") is not None]
        for prev, cur in zip(relevant, relevant[1:]):
            a = Decimal(str(prev["menge_kg"]))
            b = Decimal(str(cur["menge_kg"]))
            if a == 0:
                continue
            diff = b - a
            pct = (diff / a * 100).quantize(Decimal("0.01"))
            abweichung = abs(pct) > _MENGE_TOLERANZ_PCT
            checks.append({
                "von": prev["label"], "nach": cur["label"],
                "menge_von_kg": _f(a), "menge_nach_kg": _f(b),
                "differenz_kg": _f(diff), "differenz_pct": _f(pct),
                "abweichung": abweichung,
                "hinweis": ("Mengen-Abweichung über Toleranz (Schwund/Differenz prüfen)"
                            if abweichung else "innerhalb Toleranz"),
            })
        return checks

    def _luecken(self, wiegung: Optional[dict], annahmen: list[dict],
                 lager: list[dict], abrechnungen: list[dict]) -> list[dict]:
        g: list[dict] = []
        if wiegung and wiegung["facts"].get("allokation") == "unallocated":
            g.append({"stufe": "wiegung", "schwere": "warnung",
                      "text": "Wiegeschein ist noch keinem Kontrakt/Beleg zugeordnet (unallocated)."})
        if not annahmen:
            g.append({"stufe": "annahme", "schwere": "warnung",
                      "text": "Keine Annahme zum Wiegeschein gefunden."})
        for a in annahmen:
            if a["status"] != "released":
                g.append({"stufe": "annahme", "schwere": "warnung",
                          "text": f"Annahme {a['ref']} ist nicht freigegeben (Status {a['status']})."})
        if not lager:
            g.append({"stufe": "lager", "schwere": "info",
                      "text": "Keine Lager-/Silo-Buchung zum Wiegeschein gefunden."})
        if not abrechnungen:
            g.append({"stufe": "abrechnung", "schwere": "info",
                      "text": "Keine Abrechnung zum Wiegeschein gefunden."})
        return g

    # ── Öffentlich ─────────────────────────────────────────────────────────────
    def trace(
        self,
        *,
        ticket: Optional[str] = None,
        acceptance: Optional[str] = None,
        lot: Optional[str] = None,
        settlement: Optional[str] = None,
    ) -> dict[str, Any]:
        ticket_id = self._resolve_ticket_id(ticket=ticket, acceptance=acceptance, lot=lot, settlement=settlement)
        if not ticket_id:
            return {"found": False, "detail": "Kein Wiegeschein zur Eingabe auflösbar."}

        wiegung = self._wiegung(ticket_id)
        annahmen = self._annahmen(ticket_id)
        lager = self._lager(ticket_id)
        abrechnungen = self._abrechnungen(ticket_id)

        nodes: list[dict] = []
        if wiegung:
            nodes.append(wiegung)
        nodes.extend(annahmen)
        nodes.extend(lager)
        nodes.extend(abrechnungen)

        mengen = self._mengen_check(nodes)
        luecken = self._luecken(wiegung, annahmen, lager, abrechnungen)
        vollstaendig = bool(wiegung and annahmen and lager and abrechnungen)
        hat_abweichung = any(c["abweichung"] for c in mengen)

        # Ereignis-Log + kanonischer Übergabestatus (read-only; Befüllung via sync).
        ereignisse: list[dict] = []
        kanon_status = {"status": "offen", "rang": 0}
        try:
            from app.services.supply_chain_event_service import SupplyChainEventService

            evt = SupplyChainEventService(self.db, self.tenant_id)
            ereignisse = evt.timeline(ticket_id)
            kanon_status = evt.derive_status(ticket_id)
        except Exception:
            # Ereignis-Log ist additiv; Fehler hier darf die Kettensicht nicht brechen.
            self.db.rollback()

        return {
            "found": True,
            "ticket_id": ticket_id,
            "ticket_nr": wiegung["ref"] if wiegung else None,
            "kette": nodes,
            "mengen_konsistenz": mengen,
            "luecken": luecken,
            "ereignisse": ereignisse,
            "kanon_status": kanon_status,
            "summary": {
                "stufen": len(nodes),
                "vollstaendig": vollstaendig,
                "hat_mengen_abweichung": hat_abweichung,
                "offene_luecken": len(luecken),
                "status": kanon_status.get("status"),
            },
        }

    def list_tickets(self, limit: int = 50) -> list[dict]:
        """Übersicht der jüngsten Wiegescheine mit Ketten-Vollständigkeit (für Picker)."""
        rows = self.db.execute(
            text(
                """
                SELECT w.id, w.ticket_number, w.weighing_date, w.net_weight, w.billing_weight,
                       w.status, w.allocation_status,
                       EXISTS(SELECT 1 FROM domain_inventory.harvest_acceptances a
                              WHERE a.weighing_ticket_id = w.id AND a.tenant_id = w.tenant_id) AS hat_annahme,
                       EXISTS(SELECT 1 FROM domain_inventory.silo_lots l
                              WHERE l.source_ticket_id = w.id AND l.tenant_id = w.tenant_id) AS hat_lager,
                       EXISTS(SELECT 1 FROM domain_inventory.agrar_settlements s
                              WHERE s.ticket_id = w.id AND s.tenant_id = w.tenant_id) AS hat_abrechnung
                FROM domain_inventory.weighing_tickets w
                WHERE w.tenant_id = :t
                ORDER BY w.weighing_date DESC NULLS LAST, w.created_at DESC
                LIMIT :lim
                """
            ),
            {"t": self.tenant_id, "lim": max(1, min(limit, 500))},
        ).mappings().all()
        out = []
        for r in rows:
            out.append({
                "ticket_id": str(r["id"]),
                "ticket_nr": r["ticket_number"],
                "datum": r["weighing_date"].isoformat() if r["weighing_date"] else None,
                "menge_kg": _f(r["billing_weight"]) or _f(r["net_weight"]),
                "status": r["status"],
                "allokation": r["allocation_status"],
                "hat_annahme": bool(r["hat_annahme"]),
                "hat_lager": bool(r["hat_lager"]),
                "hat_abrechnung": bool(r["hat_abrechnung"]),
                "vollstaendig": bool(r["hat_annahme"] and r["hat_lager"] and r["hat_abrechnung"]),
            })
        return out
