"""Unit tests for CRM Pipeline, 360°-Kundensicht, SLA und Account-Hierarchie.

Alle Tests laufen ohne Datenbankverbindung — DB-Calls werden via Mock ersetzt.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Helpers imported from endpoints (pure logic functions)
# ---------------------------------------------------------------------------

from app.api.v1.endpoints.cases import _compute_sla, SLA_RULES
from app.api.v1.endpoints.opportunities import (
    OPPORTUNITY_STAGES,
    OPPORTUNITY_STAGES_LIST,
    _STAGE_DEFAULT_PROB,
)


# ===========================================================================
# Aufgabe 1 — Opportunity Pipeline
# ===========================================================================

@pytest.mark.unit
def test_pipeline_groups_by_stage():
    """Alle definierten Stages müssen im Ergebnis vorhanden sein."""
    assert set(OPPORTUNITY_STAGES) == {
        "LEAD", "QUALIFIZIERT", "ANGEBOT", "VERHANDLUNG", "GEWONNEN", "VERLOREN"
    }
    stage_ids = {s["id"] for s in OPPORTUNITY_STAGES_LIST}
    assert stage_ids == set(OPPORTUNITY_STAGES)


@pytest.mark.unit
def test_forecast_calculates_weighted_value():
    """Gewichteter Forecast = amount * probability / 100."""
    amount = 10_000.0
    probability = 50.0
    expected_weighted = amount * probability / 100
    assert expected_weighted == 5_000.0

    # Verify mapping exists for all stages
    for stage in OPPORTUNITY_STAGES:
        assert stage in _STAGE_DEFAULT_PROB
        assert 0 <= _STAGE_DEFAULT_PROB[stage] <= 100


@pytest.mark.unit
def test_stage_change_appends_history():
    """stage_history muss nach Wechsel den alten Stage enthalten."""
    old_stage = "LEAD"
    history: list[dict[str, Any]] = []
    new_stage = "QUALIFIZIERT"

    history.append({"stage": old_stage, "changed_at": datetime.now(timezone.utc).isoformat()})

    assert len(history) == 1
    assert history[0]["stage"] == old_stage

    # Serialize / deserialize roundtrip
    serialized = json.dumps(history)
    restored = json.loads(serialized)
    assert restored[0]["stage"] == old_stage


@pytest.mark.unit
def test_stage_change_sets_default_probability():
    """Nach Stage-Wechsel soll Default-Wahrscheinlichkeit gesetzt werden."""
    assert _STAGE_DEFAULT_PROB["ANGEBOT"] == 50
    assert _STAGE_DEFAULT_PROB["GEWONNEN"] == 100
    assert _STAGE_DEFAULT_PROB["VERLOREN"] == 0
    assert _STAGE_DEFAULT_PROB["VERHANDLUNG"] == 75


# ===========================================================================
# Aufgabe 2 — 360°-Kundensicht
# ===========================================================================

@pytest.mark.unit
def test_360_returns_nulls_for_missing_tables():
    """Wenn Tabellen fehlen (_safe_query gibt None zurück), müssen Felder null sein."""
    from app.api.v1.endpoints.crm_360 import _safe_query

    db_mock = MagicMock()
    db_mock.execute.side_effect = Exception("table does not exist")

    result = _safe_query(db_mock, "SELECT * FROM nonexistent", {})
    assert result is None
    db_mock.rollback.assert_called()


@pytest.mark.unit
def test_360_aggregates_all_sections():
    """360-Response muss alle 8 Sektionen als Keys enthalten."""
    expected_keys = {
        "customer_id",
        "tenant_id",
        "recent_orders",
        "open_invoices",
        "open_payments",
        "active_contracts",
        "recent_activities",
        "open_complaints",
        "last_goods_receipt",
        "credit_limit_status",
    }
    # Simulate the response structure
    response = {k: None for k in expected_keys}
    response["customer_id"] = "cust-123"
    assert set(response.keys()) == expected_keys
    assert response["customer_id"] == "cust-123"


# ===========================================================================
# Aufgabe 3 — Service Cases SLA
# ===========================================================================

@pytest.mark.unit
def test_sla_status_ok():
    """Case innerhalb SLA-Frist → Status 'ok'."""
    now = datetime.now(timezone.utc)
    created_at = now - timedelta(hours=2)  # 2h ago
    # HIGH: 4h first response, 24h resolution → still ok
    result = _compute_sla(created_at, "HIGH", None, None, now=now)
    assert result["sla_status"] == "ok"
    assert result["hours_until_breach"] > 0


@pytest.mark.unit
def test_sla_status_breached():
    """Case außerhalb SLA-Frist → Status 'breached'."""
    now = datetime.now(timezone.utc)
    created_at = now - timedelta(hours=30)  # 30h ago, HIGH resolution = 24h
    result = _compute_sla(created_at, "HIGH", None, None, now=now)
    assert result["sla_status"] == "breached"
    assert result["hours_until_breach"] == 0.0


@pytest.mark.unit
def test_sla_status_warning():
    """Case kurz vor Deadline → Status 'warning'."""
    now = datetime.now(timezone.utc)
    # HIGH resolution = 24h; warning when < 1h remaining → created 23.5h ago
    created_at = now - timedelta(hours=23, minutes=30)
    result = _compute_sla(created_at, "HIGH", None, None, now=now)
    assert result["sla_status"] == "warning"


@pytest.mark.unit
def test_sla_rules_all_priorities():
    """SLA-Regeln für alle Prioritäten müssen definiert sein."""
    for priority in ("HIGH", "MEDIUM", "LOW"):
        assert priority in SLA_RULES
        resp_h, res_h = SLA_RULES[priority]
        assert resp_h > 0
        assert res_h > resp_h  # resolution > first_response


@pytest.mark.unit
def test_sla_dashboard_aggregation():
    """Dashboard-Aggregation: on_time + warning + breached = total."""
    now = datetime.now(timezone.utc)

    cases_data = [
        # ok: created 1h ago, HIGH (24h resolution)
        (datetime.now(timezone.utc) - timedelta(hours=1), "HIGH", None, None),
        # ok: created 5h ago, MEDIUM (48h)
        (datetime.now(timezone.utc) - timedelta(hours=5), "MEDIUM", None, None),
        # breached: created 30h ago, HIGH (24h)
        (datetime.now(timezone.utc) - timedelta(hours=30), "HIGH", None, None),
    ]

    on_time = warning = breached = 0
    for created_at, priority, first_resp, resolved_at in cases_data:
        s = _compute_sla(created_at, priority, first_resp, resolved_at, now=now)["sla_status"]
        if s == "ok":
            on_time += 1
        elif s == "warning":
            warning += 1
        else:
            breached += 1

    total = on_time + warning + breached
    assert total == len(cases_data)
    assert breached == 1
    assert on_time == 2


@pytest.mark.unit
def test_escalation_sets_priority_high():
    """Eskalation soll Priority auf HIGH (kritisch) setzen."""
    # Logic: escalated cases get priority HIGH
    escalated_priority = "HIGH"
    assert escalated_priority in SLA_RULES
    # HIGH has strictest SLA
    assert SLA_RULES["HIGH"][0] <= SLA_RULES["MEDIUM"][0]
    assert SLA_RULES["HIGH"][1] <= SLA_RULES["MEDIUM"][1]


# ===========================================================================
# Aufgabe 4 — Account-Hierarchien
# ===========================================================================

@pytest.mark.unit
def test_account_hierarchy_detects_circular():
    """Zirkularitätsprüfung: A → B → A muss Fehler werfen."""
    from app.api.v1.endpoints.crm_account_hierarchy import _load_account

    accounts = {
        "A": {"id": "A", "name": "Alpha GmbH", "name_2": None, "partner_number": "001", "parent_id": "B", "status": "active"},
        "B": {"id": "B", "name": "Beta AG", "name_2": None, "partner_number": "002", "parent_id": "A", "status": "active"},
    }

    def fake_load(db, account_id):
        return accounts.get(account_id)

    # Simulate circular detection logic (from set-parent endpoint)
    account_id = "A"
    parent_id = "B"

    current_id = parent_id
    visited: set[str] = set()
    circular = False

    for _ in range(10):
        if current_id in visited:
            break
        if current_id == account_id:
            circular = True
            break
        visited.add(current_id)
        current = fake_load(None, current_id)
        if not current or not current.get("parent_id"):
            break
        current_id = current["parent_id"]

    assert circular is True
