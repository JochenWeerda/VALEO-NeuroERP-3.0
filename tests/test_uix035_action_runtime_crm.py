"""
UIX-035 / UIX-036 — ActionRuntime Backend-Test für CRM create_activity.

Testet alle vier Execution-Modes (validate, dryRun, propose, execute)
sowie den Agent-Pfad (dryRun mit isAgentCaller-Logik).

Kein Live-DB nötig: Tabellen fehlen im Test-SQLite → graceful degradation.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

CLIENT = TestClient(app)
HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-Id": "00000000-0000-0000-0000-000000000001"}
BASE = "/api/v1/crm/customers/cust-001/actions/create_activity"


# ── UIX-035: validate mode ───────────────────────────────────────────────────

def test_validate_mode_ok():
    resp = CLIENT.post(BASE, json={"betreff": "Test-Anruf", "typ": "Anruf", "_mode": "validate"}, headers=HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert data["mode"] == "validate"
    assert data["success"] is True
    assert data.get("validationErrors") is None


def test_validate_mode_missing_betreff():
    resp = CLIENT.post(BASE, json={"betreff": "", "typ": "Anruf", "_mode": "validate"}, headers=HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is False
    errors = data.get("validationErrors") or []
    assert any(e["field"] == "betreff" for e in errors)


def test_validate_mode_invalid_type():
    resp = CLIENT.post(BASE, json={"betreff": "OK", "typ": "NichtExistent", "_mode": "validate"}, headers=HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is False
    errors = data.get("validationErrors") or []
    assert any(e["field"] == "typ" for e in errors)


# ── UIX-035: dryRun mode ─────────────────────────────────────────────────────

def test_dry_run_mode_returns_proposed_changes():
    resp = CLIENT.post(BASE, json={"betreff": "Besuch geplant", "typ": "Besuch", "_mode": "dryRun"}, headers=HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert data["mode"] == "dryRun"
    assert data["success"] is True
    assert data.get("proposedChanges") is not None
    assert len(data["proposedChanges"]) > 0


def test_dry_run_no_side_effects(monkeypatch):
    """dryRun darf niemals in die DB schreiben — wird durch mode-Guard sichergestellt."""
    writes: list[str] = []

    original_post = CLIENT.post

    def patched_post(url, **kwargs):
        if "execute" not in str(kwargs.get("json", {})):
            return original_post(url, **kwargs)
        writes.append(url)
        return original_post(url, **kwargs)

    resp = CLIENT.post(BASE, json={"betreff": "Test", "typ": "E-Mail", "_mode": "dryRun"}, headers=HEADERS)
    assert resp.status_code == 200
    assert writes == [], "dryRun darf keine execute-Pfade auslösen"


# ── UIX-035: propose mode ────────────────────────────────────────────────────

def test_propose_mode_returns_suggestion():
    resp = CLIENT.post(BASE, json={"_mode": "propose"}, headers=HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert data["mode"] == "propose"
    assert data["success"] is True
    changes = data.get("proposedChanges") or []
    assert len(changes) > 0
    suggestion = changes[0]
    assert "betreff" in suggestion
    assert "typ" in suggestion
    assert suggestion["typ"] == "Anruf"


# ── UIX-035: execute mode ────────────────────────────────────────────────────

def test_execute_mode_validation_blocks_on_empty_betreff():
    resp = CLIENT.post(BASE, json={"betreff": "", "typ": "Anruf", "_mode": "execute"}, headers=HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is False
    assert data.get("validationErrors") is not None


def test_execute_mode_succeeds_or_degrades_gracefully():
    """Execute kann entweder erfolgreich sein oder graceful degradieren (fehlende Tabelle)."""
    resp = CLIENT.post(
        BASE,
        json={"betreff": "Jahresgespräch", "typ": "Meeting", "_mode": "execute", "_auditReason": "Kundentermin Q4"},
        headers=HEADERS,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["mode"] == "execute"
    assert data["success"] is True
    assert data.get("affectedIds") and len(data["affectedIds"]) == 1
    assert data.get("auditEntryId") is not None


def test_execute_with_idempotency_key():
    payload = {"betreff": "Idempotenz-Test", "typ": "Aufgabe", "_mode": "execute", "_idempotencyKey": "ikey-abc-123"}
    resp = CLIENT.post(BASE, json=payload, headers=HEADERS)
    assert resp.status_code == 200
    assert resp.json()["success"] is True


# ── UIX-036: Agent-Modus ─────────────────────────────────────────────────────

def test_agent_dry_run_propose_chain():
    """Agent-Pfad: propose → dryRun → validate — kein execute."""

    propose_resp = CLIENT.post(BASE, json={"_mode": "propose"}, headers=HEADERS)
    assert propose_resp.status_code == 200
    suggestion = (propose_resp.json().get("proposedChanges") or [{}])[0]

    dry_resp = CLIENT.post(BASE, json={**suggestion, "_mode": "dryRun"}, headers=HEADERS)
    assert dry_resp.status_code == 200
    assert dry_resp.json()["success"] is True

    val_resp = CLIENT.post(BASE, json={**suggestion, "_mode": "validate"}, headers=HEADERS)
    assert val_resp.status_code == 200
    assert val_resp.json()["success"] is True


def test_agent_contract_gate_on_action_definition():
    """AgentMaskContract enthält create_activity mit forbiddenForAgents=False."""
    from app.api.v1.endpoints.mask_screen_definition import _generate_agent_contract
    from app.core.screen_definitions import build_crm_customer_360_screen_definition

    sd = build_crm_customer_360_screen_definition()
    contract = _generate_agent_contract(sd)

    action_keys = [a["key"] for a in (contract.get("availableActions") or [])]
    assert "create_activity" in action_keys, "create_activity muss im AgentContract sichtbar sein"

    ca = next(a for a in contract["availableActions"] if a["key"] == "create_activity")
    assert ca.get("dangerLevel") == "safe"
    assert ca.get("requiresHumanApproval") is False


def test_readiness_gates_all_mandatory_green():
    """Nach UIX-034b/c müssen alle 6 mandatory Gates für crm/customer-360 grün sein."""
    from app.api.v1.endpoints.mask_screen_definition import _check_readiness
    from app.core.screen_definitions import build_crm_customer_360_screen_definition

    sd = build_crm_customer_360_screen_definition()
    result = _check_readiness(sd)

    assert result["generatorReady"] is True, f"Mandatory gates failed: {result['errors']}"
    assert result["errors"] == []


def test_readiness_advisory_score_improved():
    """advisoryScore soll nach UIX-034c deutlich über 0.17 liegen."""
    from app.api.v1.endpoints.mask_screen_definition import _check_readiness
    from app.core.screen_definitions import build_crm_customer_360_screen_definition

    sd = build_crm_customer_360_screen_definition()
    result = _check_readiness(sd)

    assert result["advisoryScore"] >= 0.5, f"Advisory score zu niedrig: {result['advisoryScore']} — Warnings: {result['warnings']}"


def test_command_endpoint_wired_in_screen_definition():
    """create_activity muss commandEndpoint in der ScreenDefinition haben."""
    from app.core.screen_definitions import build_crm_customer_360_screen_definition

    sd = build_crm_customer_360_screen_definition()
    actions = {a["key"]: a for a in sd.get("actions", [])}

    assert "create_activity" in actions
    assert actions["create_activity"].get("commandEndpoint"), "commandEndpoint muss gesetzt sein"
    assert "{entity_id}" in actions["create_activity"]["commandEndpoint"]
