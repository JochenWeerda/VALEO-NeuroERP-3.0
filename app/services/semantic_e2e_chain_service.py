"""SEMANTIC-E2E-MATRIX-001 — Semantische Prozessketten-Validierung.

Prüft Business-Outcomes (nicht nur API-Erreichbarkeit) der 6 kritischen
ERP-Prozessketten. Jede Chain-Klasse ist ein leichtgewichtiger State-Graph,
der ohne DB-Session betrieben werden kann (gut für Unit-Tests).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class ChainStepStatus(str, Enum):
    pending = "pending"
    ok = "ok"
    failed = "failed"
    blocked = "blocked"


@dataclass
class ChainStep:
    name: str
    status: ChainStepStatus = ChainStepStatus.pending
    result_id: Optional[str] = None
    error: Optional[str] = None
    invariants_ok: bool = True
    invariant_errors: list[str] = field(default_factory=list)


@dataclass
class ChainResult:
    chain_id: str
    steps: list[ChainStep]

    @property
    def all_ok(self) -> bool:
        return all(s.status == ChainStepStatus.ok for s in self.steps)

    @property
    def failed_steps(self) -> list[ChainStep]:
        return [s for s in self.steps if s.status != ChainStepStatus.ok]

    @property
    def invariant_violations(self) -> list[str]:
        errs: list[str] = []
        for s in self.steps:
            errs.extend(s.invariant_errors)
        return errs


# ── Invariant-Helpers ─────────────────────────────────────────────────────────

def _assert_field(step: ChainStep, obj: dict, key: str, expected=None) -> None:
    if key not in obj:
        step.invariant_errors.append(f"{step.name}: Pflichtfeld '{key}' fehlt")
        step.invariants_ok = False
    elif expected is not None and obj[key] != expected:
        step.invariant_errors.append(
            f"{step.name}: '{key}' erwartet={expected!r}, ist={obj[key]!r}"
        )
        step.invariants_ok = False


def _assert_not_none(step: ChainStep, obj: dict, key: str) -> None:
    if obj.get(key) is None:
        step.invariant_errors.append(f"{step.name}: '{key}' darf nicht None sein")
        step.invariants_ok = False


def _assert_positive(step: ChainStep, obj: dict, key: str) -> None:
    val = obj.get(key)
    if val is None or (isinstance(val, (int, float)) and val <= 0):
        step.invariant_errors.append(f"{step.name}: '{key}' muss > 0 sein (ist {val!r})")
        step.invariants_ok = False


# ── O2C: CRM360 Kunde → Angebot → Auftrag → LS → Rechnung → Zahlung ──────────

class O2CChain:
    """Order-to-Cash semantische Prozesskette."""

    CHAIN_ID = "o2c-crm360"

    def run(self, ctx: dict[str, Any]) -> ChainResult:
        """
        ctx-Keys: customer, offer, order, delivery_note, invoice, payment
        Jeder Wert ist ein dict mit den relevanten Feldern.
        """
        steps: list[ChainStep] = []

        # 1 — Kundenstamm
        step = ChainStep("kunde")
        c = ctx.get("customer", {})
        _assert_field(step, c, "id")
        _assert_field(step, c, "customer_number")
        _assert_not_none(step, c, "id")
        step.result_id = c.get("id")
        step.status = ChainStepStatus.ok if step.invariants_ok else ChainStepStatus.failed
        steps.append(step)

        # 2 — Angebot
        step = ChainStep("angebot")
        o = ctx.get("offer", {})
        _assert_field(step, o, "id")
        _assert_field(step, o, "customer_id", expected=c.get("id"))
        _assert_field(step, o, "status")
        _assert_positive(step, o, "total_net")
        step.result_id = o.get("id")
        step.status = ChainStepStatus.ok if step.invariants_ok else ChainStepStatus.failed
        steps.append(step)

        # 3 — Auftrag (converted from Angebot)
        step = ChainStep("auftrag")
        order = ctx.get("order", {})
        _assert_field(step, order, "id")
        _assert_field(step, order, "customer_id", expected=c.get("id"))
        _assert_field(step, order, "source_offer_id", expected=o.get("id"))
        _assert_field(step, order, "status")
        _assert_positive(step, order, "total_net")
        step.result_id = order.get("id")
        step.status = ChainStepStatus.ok if step.invariants_ok else ChainStepStatus.failed
        steps.append(step)

        # 4 — Lieferschein
        step = ChainStep("lieferschein")
        dn = ctx.get("delivery_note", {})
        _assert_field(step, dn, "id")
        _assert_field(step, dn, "customer_id", expected=c.get("id"))
        _assert_not_none(step, dn, "sales_order_id")
        if dn.get("sales_order_id") != order.get("id"):
            step.invariant_errors.append(
                f"lieferschein: sales_order_id={dn.get('sales_order_id')!r} "
                f"stimmt nicht mit Auftrag-ID={order.get('id')!r} überein"
            )
            step.invariants_ok = False
        step.result_id = dn.get("id")
        step.status = ChainStepStatus.ok if step.invariants_ok else ChainStepStatus.failed
        steps.append(step)

        # 5 — Rechnung
        step = ChainStep("rechnung")
        inv = ctx.get("invoice", {})
        _assert_field(step, inv, "id")
        _assert_field(step, inv, "customer_id", expected=c.get("id"))
        _assert_not_none(step, inv, "delivery_note_id")
        _assert_positive(step, inv, "total_gross")
        # GoBD: Rechnungsnummer muss gesetzt sein
        _assert_not_none(step, inv, "invoice_number")
        step.result_id = inv.get("id")
        step.status = ChainStepStatus.ok if step.invariants_ok else ChainStepStatus.failed
        steps.append(step)

        # 6 — Zahlungseingang / OP-Auszifferung
        step = ChainStep("zahlungseingang")
        pay = ctx.get("payment", {})
        _assert_field(step, pay, "invoice_id", expected=inv.get("id"))
        _assert_positive(step, pay, "amount")
        _assert_field(step, pay, "op_status", expected="ausgeziffert")
        step.status = ChainStepStatus.ok if step.invariants_ok else ChainStepStatus.failed
        steps.append(step)

        return ChainResult(chain_id=self.CHAIN_ID, steps=steps)


# ── P2P: RFQ → Bestellung → Wareneingang → 3-Wege-Match → Rechnung ───────────

class P2PChain:
    """Procure-to-Pay semantische Prozesskette."""

    CHAIN_ID = "p2p-procure-to-pay"

    def run(self, ctx: dict[str, Any]) -> ChainResult:
        steps: list[ChainStep] = []

        # 1 — Lieferant / Bestellanforderung
        step = ChainStep("lieferant")
        supplier = ctx.get("supplier", {})
        _assert_field(step, supplier, "id")
        _assert_not_none(step, supplier, "id")
        step.result_id = supplier.get("id")
        step.status = ChainStepStatus.ok if step.invariants_ok else ChainStepStatus.failed
        steps.append(step)

        # 2 — Bestellung
        step = ChainStep("bestellung")
        po = ctx.get("purchase_order", {})
        _assert_field(step, po, "id")
        _assert_field(step, po, "supplier_id", expected=supplier.get("id"))
        _assert_field(step, po, "status")
        _assert_positive(step, po, "total_net")
        step.result_id = po.get("id")
        step.status = ChainStepStatus.ok if step.invariants_ok else ChainStepStatus.failed
        steps.append(step)

        # 3 — Wareneingang
        step = ChainStep("wareneingang")
        gr = ctx.get("goods_receipt", {})
        _assert_field(step, gr, "id")
        _assert_field(step, gr, "purchase_order_id", expected=po.get("id"))
        _assert_positive(step, gr, "received_qty")
        _assert_not_none(step, gr, "received_at")
        step.result_id = gr.get("id")
        step.status = ChainStepStatus.ok if step.invariants_ok else ChainStepStatus.failed
        steps.append(step)

        # 4 — 3-Wege-Match (Bestellung / Wareneingang / Rechnung)
        step = ChainStep("drei_wege_match")
        match = ctx.get("three_way_match", {})
        _assert_field(step, match, "purchase_order_id", expected=po.get("id"))
        _assert_field(step, match, "goods_receipt_id", expected=gr.get("id"))
        _assert_field(step, match, "match_status")
        # Toleranz: Preisabweichung <= 2 %
        deviation = abs(float(match.get("price_deviation_pct", 0)))
        if deviation > 2.0:
            step.invariant_errors.append(
                f"drei_wege_match: Preisabweichung {deviation:.2f} % > 2 % Toleranz"
            )
            step.invariants_ok = False
        step.status = ChainStepStatus.ok if step.invariants_ok else ChainStepStatus.failed
        steps.append(step)

        # 5 — Eingangsrechnung / Kreditoren-OP
        step = ChainStep("eingangsrechnung")
        ap_inv = ctx.get("ap_invoice", {})
        _assert_field(step, ap_inv, "id")
        _assert_field(step, ap_inv, "supplier_id", expected=supplier.get("id"))
        _assert_not_none(step, ap_inv, "op_id")  # Kreditoren-OP muss angelegt sein
        _assert_positive(step, ap_inv, "total_gross")
        step.result_id = ap_inv.get("id")
        step.status = ChainStepStatus.ok if step.invariants_ok else ChainStepStatus.failed
        steps.append(step)

        return ChainResult(chain_id=self.CHAIN_ID, steps=steps)


# ── FIBU: OP → Zahlung → Auszifferung → Mahnung → DATEV-Export ───────────────

class FiBuChain:
    """FiBu semantische Prozesskette."""

    CHAIN_ID = "fibu-op-to-datev"

    def run(self, ctx: dict[str, Any]) -> ChainResult:
        steps: list[ChainStep] = []

        # 1 — Offener Posten (Debitor)
        step = ChainStep("offener_posten")
        op = ctx.get("open_item", {})
        _assert_field(step, op, "id")
        _assert_field(step, op, "op_status", expected="offen")
        _assert_positive(step, op, "offen")
        _assert_not_none(step, op, "faelligkeit")
        step.result_id = op.get("id")
        step.status = ChainStepStatus.ok if step.invariants_ok else ChainStepStatus.failed
        steps.append(step)

        # 2 — Zahlungseingang
        step = ChainStep("zahlung")
        pay = ctx.get("payment", {})
        _assert_field(step, pay, "op_id", expected=op.get("id"))
        _assert_positive(step, pay, "amount")
        step.status = ChainStepStatus.ok if step.invariants_ok else ChainStepStatus.failed
        steps.append(step)

        # 3 — Auszifferung: OP-Saldo muss 0 sein
        step = ChainStep("auszifferung")
        cleared = ctx.get("cleared_op", {})
        _assert_field(step, cleared, "op_status", expected="ausgeziffert")
        remaining = float(cleared.get("offen", 1))
        if remaining != 0.0:
            step.invariant_errors.append(
                f"auszifferung: verbleibender Saldo {remaining:.2f} ≠ 0"
            )
            step.invariants_ok = False
        step.status = ChainStepStatus.ok if step.invariants_ok else ChainStepStatus.failed
        steps.append(step)

        # 4 — Periodenabschluss / Sperre (optional: nur wenn im ctx)
        if "closing" in ctx:
            step = ChainStep("periodenabschluss")
            closing = ctx["closing"]
            _assert_field(step, closing, "status", expected="closed")
            _assert_not_none(step, closing, "locked_at")
            if closing.get("balance") is None:
                step.invariant_errors.append("periodenabschluss: Saldo nicht berechnet")
                step.invariants_ok = False
            step.status = ChainStepStatus.ok if step.invariants_ok else ChainStepStatus.failed
            steps.append(step)

        # 5 — DATEV-Export
        step = ChainStep("datev_export")
        export = ctx.get("datev_export", {})
        _assert_field(step, export, "status", expected="exported")
        _assert_not_none(step, export, "file_path")
        _assert_positive(step, export, "entry_count")
        step.status = ChainStepStatus.ok if step.invariants_ok else ChainStepStatus.failed
        steps.append(step)

        return ChainResult(chain_id=self.CHAIN_ID, steps=steps)


# ── WMS/Agrar: Annahme → Waage → Lot → Silozelle → QS → Trace ───────────────

class WMSAgrChain:
    """WMS/Agrar semantische Prozesskette."""

    CHAIN_ID = "wms-agr-annahme-trace"

    def run(self, ctx: dict[str, Any]) -> ChainResult:
        steps: list[ChainStep] = []

        step = ChainStep("annahme")
        acc = ctx.get("harvest_acceptance", {})
        _assert_field(step, acc, "id")
        _assert_field(step, acc, "status")
        _assert_positive(step, acc, "netto_gewicht_kg")
        step.result_id = acc.get("id")
        step.status = ChainStepStatus.ok if step.invariants_ok else ChainStepStatus.failed
        steps.append(step)

        step = ChainStep("waage")
        w = ctx.get("weighing_ticket", {})
        _assert_field(step, w, "id")
        _assert_field(step, w, "harvest_acceptance_id", expected=acc.get("id"))
        _assert_positive(step, w, "netto_kg")
        step.status = ChainStepStatus.ok if step.invariants_ok else ChainStepStatus.failed
        steps.append(step)

        step = ChainStep("lot")
        lot = ctx.get("lot", {})
        _assert_field(step, lot, "id")
        _assert_field(step, lot, "weighing_ticket_id", expected=w.get("id"))
        _assert_not_none(step, lot, "lot_number")
        step.result_id = lot.get("id")
        step.status = ChainStepStatus.ok if step.invariants_ok else ChainStepStatus.failed
        steps.append(step)

        step = ChainStep("silozelle")
        cell = ctx.get("silo_cell", {})
        _assert_field(step, cell, "id")
        _assert_field(step, cell, "lot_id", expected=lot.get("id"))
        _assert_positive(step, cell, "current_stock_kg")
        # Kapazitätsprüfung
        if cell.get("current_stock_kg", 0) > cell.get("capacity_kg", float("inf")):
            step.invariant_errors.append("silozelle: Überfüllung (stock > capacity)")
            step.invariants_ok = False
        step.status = ChainStepStatus.ok if step.invariants_ok else ChainStepStatus.failed
        steps.append(step)

        step = ChainStep("qs_freigabe")
        qs = ctx.get("qs_result", {})
        _assert_field(step, qs, "lot_id", expected=lot.get("id"))
        _assert_field(step, qs, "status")
        if qs.get("status") not in ("freigegeben", "gesperrt", "bedingt"):
            step.invariant_errors.append(
                f"qs_freigabe: unbekannter Status {qs.get('status')!r}"
            )
            step.invariants_ok = False
        step.status = ChainStepStatus.ok if step.invariants_ok else ChainStepStatus.failed
        steps.append(step)

        step = ChainStep("traceability")
        trace = ctx.get("trace", {})
        _assert_field(step, trace, "lot_id", expected=lot.get("id"))
        _assert_not_none(step, trace, "harvest_acceptance_id")
        _assert_not_none(step, trace, "silo_cell_id")
        step.status = ChainStepStatus.ok if step.invariants_ok else ChainStepStatus.failed
        steps.append(step)

        return ChainResult(chain_id=self.CHAIN_ID, steps=steps)
