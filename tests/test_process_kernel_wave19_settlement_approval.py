"""
Wave 19 — Settlement Approval Flow Tests (AP1)

Prueft die Freigabe-Zustandsmaschine fuer Abrechnungen:
- Erlaubte Uebergaenge
- Rollenbasierte Zugriffskontrollen
- Human-Gate fuer KI-Agenten
- Audit-Entry-Struktur
- Terminal-Status-Erkennung
"""
from __future__ import annotations

import pytest

from app.core.settlement_approval import (
    SettlementActorType,
    SettlementApprovalRequest,
    SettlementApprovalStatus,
    evaluate_settlement_approval,
    get_allowed_transitions,
    is_terminal,
)


# ---------------------------------------------------------------------------
# Hilfsfunktion
# ---------------------------------------------------------------------------

def _req(
    target: SettlementApprovalStatus,
    actor_type: SettlementActorType = SettlementActorType.SACHBEARBEITER,
    settlement_id: str = "S-001",
    tenant_id: str = "tenant-1",
    actor_id: str = "user-1",
) -> SettlementApprovalRequest:
    return SettlementApprovalRequest(
        settlement_id=settlement_id,
        tenant_id=tenant_id,
        actor_id=actor_id,
        actor_type=actor_type,
        target_status=target,
    )


# ---------------------------------------------------------------------------
# AP1-01: Erlaubte Uebergaenge
# ---------------------------------------------------------------------------

def test_entwurf_to_zur_freigabe():
    result = evaluate_settlement_approval(
        _req(SettlementApprovalStatus.ZUR_FREIGABE),
        SettlementApprovalStatus.ENTWURF,
    )
    assert result.allowed
    assert result.new_status == SettlementApprovalStatus.ZUR_FREIGABE


def test_zur_freigabe_to_freigegeben_by_abteilungsleiter():
    result = evaluate_settlement_approval(
        _req(SettlementApprovalStatus.FREIGEGEBEN, SettlementActorType.ABTEILUNGSLEITER),
        SettlementApprovalStatus.ZUR_FREIGABE,
    )
    assert result.allowed
    assert result.new_status == SettlementApprovalStatus.FREIGEGEBEN


def test_zur_freigabe_to_teilweise_freigegeben():
    result = evaluate_settlement_approval(
        _req(SettlementApprovalStatus.TEILWEISE_FREIGEGEBEN),
        SettlementApprovalStatus.ZUR_FREIGABE,
    )
    assert result.allowed


def test_freigegeben_to_verbucht_by_sachbearbeiter():
    result = evaluate_settlement_approval(
        _req(SettlementApprovalStatus.VERBUCHT),
        SettlementApprovalStatus.FREIGEGEBEN,
    )
    assert result.allowed
    assert result.new_status == SettlementApprovalStatus.VERBUCHT


def test_abgelehnt_back_to_entwurf():
    result = evaluate_settlement_approval(
        _req(SettlementApprovalStatus.ENTWURF),
        SettlementApprovalStatus.ABGELEHNT,
    )
    assert result.allowed


def test_zur_freigabe_rueckzug_to_entwurf():
    result = evaluate_settlement_approval(
        _req(SettlementApprovalStatus.ENTWURF),
        SettlementApprovalStatus.ZUR_FREIGABE,
    )
    assert result.allowed


# ---------------------------------------------------------------------------
# AP1-02: Verbotene Uebergaenge
# ---------------------------------------------------------------------------

def test_entwurf_to_verbucht_verboten():
    result = evaluate_settlement_approval(
        _req(SettlementApprovalStatus.VERBUCHT),
        SettlementApprovalStatus.ENTWURF,
    )
    assert not result.allowed


def test_verbucht_is_terminal_no_transition():
    result = evaluate_settlement_approval(
        _req(SettlementApprovalStatus.ABGELEHNT),
        SettlementApprovalStatus.VERBUCHT,
    )
    assert not result.allowed


# ---------------------------------------------------------------------------
# AP1-03: Rollenbasierte Zugriffskontrollen
# ---------------------------------------------------------------------------

def test_sachbearbeiter_cannot_freigeben():
    result = evaluate_settlement_approval(
        _req(SettlementApprovalStatus.FREIGEGEBEN, SettlementActorType.SACHBEARBEITER),
        SettlementApprovalStatus.ZUR_FREIGABE,
    )
    assert not result.allowed
    assert "Aktor-Typ" in result.reason or "Berechtigung" in result.reason


def test_agent_cannot_freigeben():
    result = evaluate_settlement_approval(
        _req(SettlementApprovalStatus.FREIGEGEBEN, SettlementActorType.AGENT),
        SettlementApprovalStatus.ZUR_FREIGABE,
    )
    assert not result.allowed


def test_prokurist_can_freigeben():
    result = evaluate_settlement_approval(
        _req(SettlementApprovalStatus.FREIGEGEBEN, SettlementActorType.PROKURIST),
        SettlementApprovalStatus.ZUR_FREIGABE,
    )
    assert result.allowed


def test_system_can_verbuchen():
    result = evaluate_settlement_approval(
        _req(SettlementApprovalStatus.VERBUCHT, SettlementActorType.SYSTEM),
        SettlementApprovalStatus.FREIGEGEBEN,
    )
    assert result.allowed


# ---------------------------------------------------------------------------
# AP1-04: Human-Gate — AGENT darf nie VERBUCHT setzen
# ---------------------------------------------------------------------------

def test_agent_cannot_verbuchen():
    result = evaluate_settlement_approval(
        _req(SettlementApprovalStatus.VERBUCHT, SettlementActorType.AGENT),
        SettlementApprovalStatus.FREIGEGEBEN,
    )
    assert not result.allowed
    # AGENT ist nicht in _REQUIRED_ACTOR[VERBUCHT] → blockiert durch Rollenregel
    assert result.new_status == SettlementApprovalStatus.FREIGEGEBEN


# ---------------------------------------------------------------------------
# AP1-05: Audit-Entry-Struktur
# ---------------------------------------------------------------------------

def test_audit_entry_structure():
    result = evaluate_settlement_approval(
        _req(SettlementApprovalStatus.ZUR_FREIGABE),
        SettlementApprovalStatus.ENTWURF,
    )
    entry = result.audit_entry
    assert entry["settlement_id"] == "S-001"
    assert "event" in entry
    assert entry["process_definition_key"] == "agrar_settlement"
    assert entry["workflow_version"] == "1.0"
    assert "decided_at" in entry
    assert entry["allowed"] is True


def test_audit_entry_includes_actor():
    result = evaluate_settlement_approval(
        _req(SettlementApprovalStatus.ZUR_FREIGABE, actor_id="user-42"),
        SettlementApprovalStatus.ENTWURF,
    )
    entry = result.audit_entry
    assert entry["actor_id"] == "user-42"
    assert entry["actor_type"] == "SACHBEARBEITER"
    assert entry["previous_status"] == "ENTWURF"
    assert entry["new_status"] == "ZUR_FREIGABE"


# ---------------------------------------------------------------------------
# AP1-06: Hilfsfunktionen
# ---------------------------------------------------------------------------

def test_get_allowed_transitions_entwurf():
    allowed = get_allowed_transitions(SettlementApprovalStatus.ENTWURF)
    assert SettlementApprovalStatus.ZUR_FREIGABE in allowed
    assert SettlementApprovalStatus.ABGELEHNT in allowed


def test_get_allowed_transitions_verbucht_empty():
    allowed = get_allowed_transitions(SettlementApprovalStatus.VERBUCHT)
    assert allowed == []


def test_is_terminal_verbucht():
    assert is_terminal(SettlementApprovalStatus.VERBUCHT) is True


def test_is_terminal_entwurf():
    assert is_terminal(SettlementApprovalStatus.ENTWURF) is False


def test_canonical_process_metadata_carried_through():
    req = _req(SettlementApprovalStatus.ZUR_FREIGABE)
    result = evaluate_settlement_approval(req, SettlementApprovalStatus.ENTWURF)
    assert result.process_definition_key == "agrar_settlement"
    assert result.workflow_version == "1.0"
