"""
Wave 19 — Human-Gate Tests (AP3)

Prueft die 6 Human-Gate-Regeln fuer KI-Agenten bei Abrechnungen:
HG-01 BLOCK > 100k EUR
HG-02 HOLD Agent + > 10k EUR
HG-03 Qualitaetsausnahme
HG-04 Preis-Override
HG-05 > 30 Tage ueberfaellig
HG-06 Verbund-Cross-Tenant
"""
from __future__ import annotations

from decimal import Decimal

import pytest

from app.core.settlement_human_gate import (
    HumanGateContext,
    HumanGateVerdict,
    evaluate_settlement_human_gate,
    get_default_gate_rules,
)


# ---------------------------------------------------------------------------
# Hilfsfunktion
# ---------------------------------------------------------------------------

def _ctx(**kwargs) -> HumanGateContext:
    defaults = dict(
        settlement_id="S-001",
        tenant_id="tenant-1",
        gross_amount=Decimal("1000.00"),
        actor_type="SACHBEARBEITER",
    )
    defaults.update(kwargs)
    return HumanGateContext(**defaults)


# ---------------------------------------------------------------------------
# HG-01: BLOCK bei sehr hohem Betrag
# ---------------------------------------------------------------------------

def test_hg01_block_above_100k():
    ctx = _ctx(gross_amount=Decimal("150000.00"), actor_type="AGENT")
    decision = evaluate_settlement_human_gate(ctx)
    assert decision.verdict == HumanGateVerdict.BLOCK
    assert any(r.rule_id == "HG-01" for r in decision.triggered_rules)


def test_hg01_not_triggered_below_100k():
    ctx = _ctx(gross_amount=Decimal("99999.99"), actor_type="AGENT")
    decision = evaluate_settlement_human_gate(ctx)
    assert not any(r.rule_id == "HG-01" for r in decision.triggered_rules)


# ---------------------------------------------------------------------------
# HG-02: HOLD fuer Agent + Betrag > 10k
# ---------------------------------------------------------------------------

def test_hg02_hold_agent_above_10k():
    ctx = _ctx(gross_amount=Decimal("15000.00"), actor_type="AGENT")
    decision = evaluate_settlement_human_gate(ctx)
    assert decision.verdict in (HumanGateVerdict.HOLD, HumanGateVerdict.BLOCK)
    assert any(r.rule_id == "HG-02" for r in decision.triggered_rules)


def test_hg02_not_triggered_sachbearbeiter():
    ctx = _ctx(gross_amount=Decimal("15000.00"), actor_type="SACHBEARBEITER")
    decision = evaluate_settlement_human_gate(ctx)
    assert not any(r.rule_id == "HG-02" for r in decision.triggered_rules)


def test_hg02_not_triggered_below_10k_agent():
    ctx = _ctx(gross_amount=Decimal("5000.00"), actor_type="AGENT")
    decision = evaluate_settlement_human_gate(ctx)
    assert not any(r.rule_id == "HG-02" for r in decision.triggered_rules)


# ---------------------------------------------------------------------------
# HG-03: HOLD bei Qualitaetsausnahme
# ---------------------------------------------------------------------------

def test_hg03_hold_quality_exception():
    ctx = _ctx(has_quality_exception=True)
    decision = evaluate_settlement_human_gate(ctx)
    assert decision.verdict == HumanGateVerdict.HOLD
    assert any(r.rule_id == "HG-03" for r in decision.triggered_rules)


def test_hg03_pass_without_exception():
    ctx = _ctx(has_quality_exception=False)
    decision = evaluate_settlement_human_gate(ctx)
    assert not any(r.rule_id == "HG-03" for r in decision.triggered_rules)


# ---------------------------------------------------------------------------
# HG-04: HOLD bei manuellem Preis-Override
# ---------------------------------------------------------------------------

def test_hg04_hold_price_override():
    ctx = _ctx(has_price_override=True)
    decision = evaluate_settlement_human_gate(ctx)
    assert decision.verdict == HumanGateVerdict.HOLD
    assert any(r.rule_id == "HG-04" for r in decision.triggered_rules)


# ---------------------------------------------------------------------------
# HG-05: HOLD bei > 30 Tage ueberfaellig
# ---------------------------------------------------------------------------

def test_hg05_hold_overdue_31_days():
    ctx = _ctx(days_overdue=31)
    decision = evaluate_settlement_human_gate(ctx)
    assert decision.verdict == HumanGateVerdict.HOLD
    assert any(r.rule_id == "HG-05" for r in decision.triggered_rules)


def test_hg05_pass_30_days_exactly():
    ctx = _ctx(days_overdue=30)
    decision = evaluate_settlement_human_gate(ctx)
    assert not any(r.rule_id == "HG-05" for r in decision.triggered_rules)


# ---------------------------------------------------------------------------
# HG-06: HOLD bei Verbund-Cross-Tenant
# ---------------------------------------------------------------------------

def test_hg06_hold_verbund_cross_tenant():
    ctx = _ctx(verbund_cross_tenant=True)
    decision = evaluate_settlement_human_gate(ctx)
    assert decision.verdict == HumanGateVerdict.HOLD
    assert any(r.rule_id == "HG-06" for r in decision.triggered_rules)


# ---------------------------------------------------------------------------
# Prioritaet: BLOCK > HOLD > PASS
# ---------------------------------------------------------------------------

def test_block_wins_over_hold():
    ctx = _ctx(
        gross_amount=Decimal("200000.00"),  # HG-01 BLOCK
        has_quality_exception=True,         # HG-03 HOLD
        actor_type="AGENT",
    )
    decision = evaluate_settlement_human_gate(ctx)
    assert decision.verdict == HumanGateVerdict.BLOCK


def test_pass_when_no_rules_triggered():
    ctx = _ctx(
        gross_amount=Decimal("1000.00"),
        actor_type="SACHBEARBEITER",
        has_quality_exception=False,
        has_price_override=False,
        days_overdue=0,
        verbund_cross_tenant=False,
    )
    decision = evaluate_settlement_human_gate(ctx)
    assert decision.verdict == HumanGateVerdict.PASS
    assert decision.triggered_rules == []


# ---------------------------------------------------------------------------
# requires_human property
# ---------------------------------------------------------------------------

def test_requires_human_true_for_hold():
    ctx = _ctx(has_quality_exception=True)
    decision = evaluate_settlement_human_gate(ctx)
    assert decision.requires_human is True


def test_requires_human_false_for_pass():
    ctx = _ctx()
    decision = evaluate_settlement_human_gate(ctx)
    assert decision.requires_human is False


# ---------------------------------------------------------------------------
# Summary und Metadaten
# ---------------------------------------------------------------------------

def test_decision_carries_process_metadata():
    ctx = _ctx(has_quality_exception=True)
    decision = evaluate_settlement_human_gate(ctx)
    assert decision.process_definition_key == "agrar_settlement"
    assert decision.workflow_version == "1.0"
    assert decision.settlement_id == "S-001"


def test_summary_non_empty_when_triggered():
    ctx = _ctx(has_quality_exception=True)
    decision = evaluate_settlement_human_gate(ctx)
    assert len(decision.summary) > 0
    assert "HG-03" in decision.summary


def test_summary_default_when_no_trigger():
    ctx = _ctx()
    decision = evaluate_settlement_human_gate(ctx)
    assert "Agent darf fortfahren" in decision.summary


# ---------------------------------------------------------------------------
# get_default_gate_rules
# ---------------------------------------------------------------------------

def test_default_gate_rules_returns_6():
    rules = get_default_gate_rules()
    assert len(rules) == 6


def test_default_gate_rules_serializable():
    rules = get_default_gate_rules()
    for rule in rules:
        assert "rule_id" in rule
        assert "verdict" in rule
        assert "description" in rule


def test_default_gate_rules_has_hg01_block():
    rules = get_default_gate_rules()
    hg01 = next(r for r in rules if r["rule_id"] == "HG-01")
    assert hg01["verdict"] == "BLOCK"
