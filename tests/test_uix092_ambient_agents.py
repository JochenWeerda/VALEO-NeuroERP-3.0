"""UIX-092: Ambient-Agent-Framework + 4 v1-Agenten (deterministisch).

Reine Unit-Tests (kein DB): `pytest tests/test_uix092_ambient_agents.py --noconftest -p no:cacheprovider --no-cov -q -o addopts=""`.
"""
from __future__ import annotations

import pytest

from app.services.ambient_agents import (
    ALL_AGENTS,
    active_agents,
    get_agent,
    reconcile,
)
from app.services.ambient_agents.agents import (
    KontraktUntererfuellungAgent,
    OpEskalationAgent,
    PreisabweichungEinkaufAgent,
    QsFristenAgent,
)

pytestmark = pytest.mark.unit
T = "tenant-a"


# ── Kontrakt-Untererfuellung ─────────────────────────────────────────────────

def test_kontrakt_positiv_grenzwert_kein_treffer():
    a = KontraktUntererfuellungAgent()
    assert len(a.evaluate([{"contract_id": "K1", "angedient_pct": 79, "andienung_frist_days": 20}], T)) == 1
    # Grenzwerte: 80% ODER 21 Tage → kein Treffer
    assert a.evaluate([{"contract_id": "K2", "angedient_pct": 80, "andienung_frist_days": 20}], T) == []
    assert a.evaluate([{"contract_id": "K3", "angedient_pct": 79, "andienung_frist_days": 21}], T) == []


def test_preisabweichung_positiv_grenzwert():
    a = PreisabweichungEinkaufAgent(toleranz=0.02)
    assert len(a.evaluate([{"invoice_id": "R1", "rechnungspreis": 103, "bestellpreis": 100}], T)) == 1
    # genau an der Toleranzgrenze (102) → kein Treffer
    assert a.evaluate([{"invoice_id": "R2", "rechnungspreis": 102, "bestellpreis": 100}], T) == []


def test_op_eskalation_regelkombination():
    a = OpEskalationAgent()
    assert len(a.evaluate([{"op_id": "O1", "overdue_days": 31, "days_since_mahnung": None}], T)) == 1
    assert len(a.evaluate([{"op_id": "O2", "overdue_days": 31, "days_since_mahnung": 15}], T)) == 1
    assert a.evaluate([{"op_id": "O3", "overdue_days": 30, "days_since_mahnung": None}], T) == []  # nicht > 30
    assert a.evaluate([{"op_id": "O4", "overdue_days": 31, "days_since_mahnung": 14}], T) == []  # frisch gemahnt
    assert a.evaluate([{"op_id": "O5", "overdue_days": 31, "days_since_mahnung": 10}], T) == []


def test_qs_fristen_positiv_grenzwert():
    a = QsFristenAgent()
    assert len(a.evaluate([{"cert_id": "Z1", "expires_in_days": 29}], T)) == 1
    assert a.evaluate([{"cert_id": "Z2", "expires_in_days": 30}], T) == []


# ── Proposal-Vertrag ─────────────────────────────────────────────────────────

def test_proposal_ist_erklaert_und_deterministisch():
    prop = OpEskalationAgent().evaluate([{"op_id": "O1", "overdue_days": 40, "days_since_mahnung": None, "beleg_nr": "OP-7"}], T)[0]
    assert prop.reason  # Begruendung Pflicht
    assert prop.source_ref == "open_item:O1"
    assert prop.dedupe_key == "op_eskalation:O1"
    assert prop.confidence == 1.0
    assert prop.severity == "critical"
    assert prop.target_route.endswith("/O1")


# ── Reconcile: Dedupe + Auto-Resolve ─────────────────────────────────────────

def test_dedupe_doppellauf_identisch():
    a = QsFristenAgent()
    rows = [{"cert_id": "Z1", "expires_in_days": 10}]
    keys1 = {p.dedupe_key for p in a.evaluate(rows, T)}
    keys2 = {p.dedupe_key for p in a.evaluate(rows, T)}
    assert keys1 == keys2 == {"qs_fristen:Z1"}


def test_reconcile_auto_resolved_entfallene_sachverhalte():
    props = QsFristenAgent().evaluate([{"cert_id": "Z1", "expires_in_days": 10}], T)
    # Z2 war offen, ist aber nicht mehr in der aktuellen Menge → auto-resolve
    result = reconcile(props, existing_open_keys={"qs_fristen:Z1", "qs_fristen:Z2"})
    assert result.auto_resolve_keys == ["qs_fristen:Z2"]
    assert {p.dedupe_key for p in result.upserts} == {"qs_fristen:Z1"}


# ── Registry + Kill-Switch + Tenant ──────────────────────────────────────────

def test_registry_enthaelt_vier_agenten():
    ids = {a.agent_id for a in ALL_AGENTS}
    assert ids == {"kontrakt_untererfuellung", "preisabweichung_einkauf", "op_eskalation", "qs_fristen"}
    assert get_agent("op_eskalation") is not None
    assert get_agent("gibtsnicht") is None


def test_kill_switch_deaktiviert_je_tenant_und_wildcard():
    disabled = {"tenant-a": ["op_eskalation"], "*": ["qs_fristen"]}
    active_a = {a.agent_id for a in active_agents("tenant-a", disabled)}
    assert "op_eskalation" not in active_a and "qs_fristen" not in active_a
    # tenant-b nur vom Wildcard betroffen
    active_b = {a.agent_id for a in active_agents("tenant-b", disabled)}
    assert "op_eskalation" in active_b and "qs_fristen" not in active_b


def test_tenant_isolation_proposal_traegt_tenant():
    props = QsFristenAgent().evaluate([{"cert_id": "Z1", "expires_in_days": 5}], "tenant-x")
    assert all(p.tenant_id == "tenant-x" for p in props)


def test_agenten_mutieren_nie_ohne_treffer_leer():
    # Kein Treffer → leere Liste (Agent schlaegt nie etwas ohne Grund vor).
    for agent in ALL_AGENTS:
        assert agent.evaluate([], T) == []
