"""
Settlement Human Gate — Wave 19 AP3

Regeln, wann ein KI-Agent eine Abrechnung NICHT selbst ausfuehren darf
und stattdessen eine menschliche Freigabe anfordern muss.
Integriert in DelegationPolicy (Wave 2 AP5) und Canonical Process Definitions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from decimal import Decimal


class HumanGateVerdict(str, Enum):
    PASS = "PASS"           # Agent darf fortfahren
    HOLD = "HOLD"           # Mensch muss freigeben
    BLOCK = "BLOCK"         # Abgelehnt, auch Mensch kann nicht direkt fortfahren


@dataclass
class HumanGateContext:
    """Context passed to the Human-Gate evaluation."""

    settlement_id: str
    tenant_id: str
    gross_amount: Decimal
    actor_type: str          # "AGENT" | "SACHBEARBEITER" | ...
    process_definition_key: str = "agrar_settlement"
    workflow_version: str = "1.0"
    # Optional risk signals
    has_quality_exception: bool = False
    has_price_override: bool = False
    days_overdue: int = 0
    verbund_cross_tenant: bool = False


@dataclass
class HumanGateRule:
    rule_id: str
    description: str
    verdict: HumanGateVerdict
    # Filled during evaluation
    triggered: bool = False
    detail: str = ""


@dataclass
class HumanGateDecision:
    settlement_id: str
    verdict: HumanGateVerdict
    triggered_rules: list[HumanGateRule] = field(default_factory=list)
    process_definition_key: str = "agrar_settlement"
    workflow_version: str = "1.0"

    @property
    def requires_human(self) -> bool:
        return self.verdict in (HumanGateVerdict.HOLD, HumanGateVerdict.BLOCK)

    @property
    def summary(self) -> str:
        if not self.triggered_rules:
            return "Kein Human-Gate ausgeloest — Agent darf fortfahren."
        parts = [r.detail for r in self.triggered_rules if r.triggered]
        return "; ".join(parts)


# ---------------------------------------------------------------------------
# Default gate rules (ordered by priority — first BLOCK wins, then HOLD)
# ---------------------------------------------------------------------------

# Betrag-Schwellwerte
_AGENT_MAX_AMOUNT = Decimal("10000.00")    # > 10.000 EUR → HOLD
_AGENT_BLOCK_AMOUNT = Decimal("100000.00") # > 100.000 EUR → BLOCK


def evaluate_settlement_human_gate(ctx: HumanGateContext) -> HumanGateDecision:
    """
    Evaluate all Human-Gate rules for a settlement context.

    Priority: BLOCK > HOLD > PASS
    """
    rules: list[HumanGateRule] = []

    # Rule HG-01: sehr hoher Betrag → immer BLOCK
    r01 = HumanGateRule(
        rule_id="HG-01",
        description=f"Betrag > {_AGENT_BLOCK_AMOUNT} EUR — immer menschliche Freigabe",
        verdict=HumanGateVerdict.BLOCK,
    )
    if ctx.gross_amount > _AGENT_BLOCK_AMOUNT:
        r01.triggered = True
        r01.detail = (
            f"HG-01: Betrag {ctx.gross_amount} EUR ueberschreitet BLOCK-Schwelle "
            f"{_AGENT_BLOCK_AMOUNT} EUR."
        )
    rules.append(r01)

    # Rule HG-02: hoher Betrag + Agent → HOLD
    r02 = HumanGateRule(
        rule_id="HG-02",
        description=f"Agent + Betrag > {_AGENT_MAX_AMOUNT} EUR → HOLD",
        verdict=HumanGateVerdict.HOLD,
    )
    if ctx.actor_type == "AGENT" and ctx.gross_amount > _AGENT_MAX_AMOUNT:
        r02.triggered = True
        r02.detail = (
            f"HG-02: KI-Agent, Betrag {ctx.gross_amount} EUR > {_AGENT_MAX_AMOUNT} EUR."
        )
    rules.append(r02)

    # Rule HG-03: Qualitaetsausnahme → HOLD
    r03 = HumanGateRule(
        rule_id="HG-03",
        description="Qualitaetsausnahme erfordert menschliche Pruefung",
        verdict=HumanGateVerdict.HOLD,
    )
    if ctx.has_quality_exception:
        r03.triggered = True
        r03.detail = "HG-03: Qualitaetsausnahme vorhanden — menschliche Pruefung erforderlich."
    rules.append(r03)

    # Rule HG-04: manueller Preisoverride → HOLD
    r04 = HumanGateRule(
        rule_id="HG-04",
        description="Manueller Preis-Override erfordert Genehmigung",
        verdict=HumanGateVerdict.HOLD,
    )
    if ctx.has_price_override:
        r04.triggered = True
        r04.detail = "HG-04: Manueller Preis-Override — Freigabe durch Abteilungsleiter noetig."
    rules.append(r04)

    # Rule HG-05: ueberfaellige Abrechnung → HOLD
    r05 = HumanGateRule(
        rule_id="HG-05",
        description="Abrechnung > 30 Tage ueberfaellig",
        verdict=HumanGateVerdict.HOLD,
    )
    if ctx.days_overdue > 30:
        r05.triggered = True
        r05.detail = f"HG-05: Abrechnung ist {ctx.days_overdue} Tage ueberfaellig."
    rules.append(r05)

    # Rule HG-06: Verbund-Cross-Tenant → HOLD
    r06 = HumanGateRule(
        rule_id="HG-06",
        description="Verbund-ueberschreitende Buchung erfordert Genehmigung",
        verdict=HumanGateVerdict.HOLD,
    )
    if ctx.verbund_cross_tenant:
        r06.triggered = True
        r06.detail = "HG-06: Mandantenueberschreitende Buchung im Verbund."
    rules.append(r06)

    # Determine final verdict
    triggered = [r for r in rules if r.triggered]
    if any(r.verdict == HumanGateVerdict.BLOCK for r in triggered):
        verdict = HumanGateVerdict.BLOCK
    elif any(r.verdict == HumanGateVerdict.HOLD for r in triggered):
        verdict = HumanGateVerdict.HOLD
    else:
        verdict = HumanGateVerdict.PASS

    return HumanGateDecision(
        settlement_id=ctx.settlement_id,
        verdict=verdict,
        triggered_rules=triggered,
        process_definition_key=ctx.process_definition_key,
        workflow_version=ctx.workflow_version,
    )


def get_default_gate_rules() -> list[dict]:
    """Return the default Human-Gate rules as serializable dicts."""
    return [
        {"rule_id": "HG-01", "verdict": "BLOCK",
         "description": f"Betrag > {_AGENT_BLOCK_AMOUNT} EUR"},
        {"rule_id": "HG-02", "verdict": "HOLD",
         "description": f"Agent + Betrag > {_AGENT_MAX_AMOUNT} EUR"},
        {"rule_id": "HG-03", "verdict": "HOLD",
         "description": "Qualitaetsausnahme vorhanden"},
        {"rule_id": "HG-04", "verdict": "HOLD",
         "description": "Manueller Preis-Override"},
        {"rule_id": "HG-05", "verdict": "HOLD",
         "description": "Abrechnung > 30 Tage ueberfaellig"},
        {"rule_id": "HG-06", "verdict": "HOLD",
         "description": "Verbund-Cross-Tenant-Buchung"},
    ]
