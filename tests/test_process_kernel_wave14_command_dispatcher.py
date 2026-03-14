"""
Wave-14 Contract Tests: Business-Command-Dispatcher und Agent-Command-Manifest

AP1: CommandPrecondition.evaluate() — alle 5 Operatoren
AP2: CommandDispatcher.check_role() + check_preconditions()
AP3: CommandDispatcher.dispatch() — accept, reject (role/precond/human)
AP4: build_core_command_catalog() — 9 Commands, Preconditions, Rollen
AP5: AgentCommandManifest — restricted + blocked lists
AP6: Agent-sicheres Dispatch — agent_types + human_confirmation
"""
from __future__ import annotations

import uuid

import pytest

from app.core.business_commands import (
    BusinessCommand,
    CommandDefinition,
    CommandError,
    CommandPrecondition,
    CommandResult,
    CommandStatus,
    build_core_command_catalog,
)
from app.core.command_dispatcher import CommandDispatcher
from app.core.agent_command_manifest import (
    AgentCommandManifest,
    build_agent_command_manifest,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _cmd(name: str, aggregate_type: str = "ap_invoice", aggregate_id: str = "INV-1",
         requires_human: bool = False) -> BusinessCommand:
    return BusinessCommand(
        command_id=str(uuid.uuid4()),
        tenant_id="t1",
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        command_name=name,
        issued_by="user-1",
        idempotency_key=str(uuid.uuid4()),
        requires_human_confirmation=requires_human,
    )


# ---------------------------------------------------------------------------
# AP1: CommandPrecondition.evaluate()
# ---------------------------------------------------------------------------

def test_precondition_eq_operator_true():
    p = CommandPrecondition(field="status", operator="eq", expected="FREIGEGEBEN")
    assert p.evaluate("FREIGEGEBEN") is True


def test_precondition_eq_operator_false():
    p = CommandPrecondition(field="status", operator="eq", expected="FREIGEGEBEN")
    assert p.evaluate("ENTWURF") is False


def test_precondition_in_operator():
    p = CommandPrecondition(field="status", operator="in", expected=["A", "B", "C"])
    assert p.evaluate("B") is True
    assert p.evaluate("D") is False


def test_precondition_not_in_operator():
    p = CommandPrecondition(field="approved_by", operator="not_in", expected=["", None])
    assert p.evaluate("user-42") is True
    assert p.evaluate("") is False


def test_precondition_gt_operator():
    p = CommandPrecondition(field="amount", operator="gt", expected=0)
    assert p.evaluate(100) is True
    assert p.evaluate(0) is False


def test_precondition_gte_operator():
    p = CommandPrecondition(field="quantity", operator="gte", expected=10)
    assert p.evaluate(10) is True
    assert p.evaluate(9) is False


# ---------------------------------------------------------------------------
# AP2: check_role + check_preconditions
# ---------------------------------------------------------------------------

def test_dispatcher_check_role_authorized():
    dispatcher = CommandDispatcher()
    cmd = _cmd("ApproveAPInvoice")
    assert dispatcher.check_role(cmd, "finance_manager") is True


def test_dispatcher_check_role_denied():
    dispatcher = CommandDispatcher()
    cmd = _cmd("ApproveAPInvoice")
    assert dispatcher.check_role(cmd, "warehouse_manager") is False


def test_dispatcher_check_role_unknown_command_returns_false():
    dispatcher = CommandDispatcher()
    cmd = _cmd("NonExistentCommand")
    assert dispatcher.check_role(cmd, "finance_manager") is False


def test_dispatcher_check_preconditions_ok():
    dispatcher = CommandDispatcher()
    cmd = _cmd("ApproveAPInvoice")
    state = {"status": "ZUR_FREIGABE"}
    error = dispatcher.check_preconditions(cmd, state)
    assert error is None


def test_dispatcher_check_preconditions_fails_wrong_status():
    dispatcher = CommandDispatcher()
    cmd = _cmd("ApproveAPInvoice")
    state = {"status": "ENTWURF"}
    error = dispatcher.check_preconditions(cmd, state)
    assert error is not None
    assert error.code == "WRONG_STATUS"


# ---------------------------------------------------------------------------
# AP3: dispatch() — all paths
# ---------------------------------------------------------------------------

def test_dispatch_accepts_valid_command():
    dispatcher = CommandDispatcher()
    cmd = _cmd("ApproveAPInvoice")
    result = dispatcher.dispatch(cmd, {"status": "ZUR_FREIGABE"}, issuer_role="ap_approver")
    assert result.status == CommandStatus.ACCEPTED
    assert result.error is None
    assert result.schema_version == 1


def test_dispatch_rejects_unknown_command():
    dispatcher = CommandDispatcher()
    cmd = _cmd("DeleteEverything")
    result = dispatcher.dispatch(cmd, {}, issuer_role="admin")
    assert result.status == CommandStatus.REJECTED
    assert result.error.code == "UNKNOWN_COMMAND"


def test_dispatch_rejects_unauthorized_role():
    dispatcher = CommandDispatcher()
    cmd = _cmd("PostAPInvoice")
    result = dispatcher.dispatch(cmd, {"status": "FREIGEGEBEN"}, issuer_role="warehouse_manager")
    assert result.status == CommandStatus.REJECTED
    assert result.error.code == "ROLE_DENIED"


def test_dispatch_rejects_failed_precondition():
    dispatcher = CommandDispatcher()
    cmd = _cmd("PostAPInvoice")
    state = {"status": "ZUR_FREIGABE"}   # needs FREIGEGEBEN
    result = dispatcher.dispatch(cmd, state, issuer_role="accountant")
    assert result.status == CommandStatus.REJECTED
    assert result.error.code == "NOT_APPROVED"


def test_dispatch_requires_human_confirmation():
    dispatcher = CommandDispatcher()
    cmd = _cmd("PostAPInvoice", requires_human=False)  # defn requires_human=True
    result = dispatcher.dispatch(cmd, {"status": "FREIGEGEBEN"}, issuer_role="finance_manager")
    assert result.status == CommandStatus.PENDING_APPROVAL
    assert result.error.code == "HUMAN_CONFIRMATION_REQUIRED"


def test_dispatch_accepted_with_human_confirmation_set():
    dispatcher = CommandDispatcher()
    cmd = _cmd("PostAPInvoice", requires_human=True)
    result = dispatcher.dispatch(cmd, {"status": "FREIGEGEBEN"}, issuer_role="finance_manager")
    assert result.status == CommandStatus.ACCEPTED


# ---------------------------------------------------------------------------
# AP4: build_core_command_catalog
# ---------------------------------------------------------------------------

def test_core_command_catalog_has_nine_commands():
    catalog = build_core_command_catalog()
    assert len(catalog) == 9


def test_core_command_catalog_includes_all_aggregate_types():
    catalog = build_core_command_catalog()
    types = {cd.aggregate_type for cd in catalog}
    assert "ap_invoice" in types
    assert "harvest_acceptance" in types
    assert "quality_protocol" in types
    assert "agrar_settlement" in types
    assert "payment_run" in types
    assert "direct_debit_run" in types


def test_execute_payment_run_requires_human_confirmation():
    catalog = build_core_command_catalog()
    cmd = next(c for c in catalog if c.command_name == "ExecutePaymentRun")
    assert cmd.requires_human_confirmation is True
    assert cmd.idempotent is True


def test_approve_ap_invoice_has_post_event():
    catalog = build_core_command_catalog()
    cmd = next(c for c in catalog if c.command_name == "ApproveAPInvoice")
    assert cmd.post_event == "APInvoiceApproved"


def test_finalize_agrar_settlement_needs_draft_status():
    catalog = build_core_command_catalog()
    defn = next(c for c in catalog if c.command_name == "FinalizeAgrarSettlement")
    assert len(defn.preconditions) == 1
    assert defn.preconditions[0].expected == "DRAFT"


# ---------------------------------------------------------------------------
# AP5: AgentCommandManifest
# ---------------------------------------------------------------------------

def test_agent_manifest_schema_version():
    manifest = build_agent_command_manifest()
    assert manifest.schema_version == 1


def test_agent_manifest_restricted_commands_include_payment_run():
    manifest = build_agent_command_manifest()
    assert "ExecutePaymentRun" in manifest.agent_restricted_commands
    assert "ExecuteDirectDebit" in manifest.agent_restricted_commands


def test_agent_manifest_blocked_commands_have_empty_agent_types():
    manifest = build_agent_command_manifest()
    catalog = build_core_command_catalog()
    blocked_in_catalog = {c.command_name for c in catalog if not c.allowed_agent_types}
    assert set(manifest.fully_blocked_for_agents) == blocked_in_catalog


def test_agent_manifest_entries_count_matches_catalog():
    catalog = build_core_command_catalog()
    manifest = build_agent_command_manifest(catalog)
    assert len(manifest.commands) == len(catalog)


# ---------------------------------------------------------------------------
# AP6: Agent-sicheres Dispatch
# ---------------------------------------------------------------------------

def test_approve_ap_invoice_allows_audit_agent():
    catalog = build_core_command_catalog()
    defn = next(c for c in catalog if c.command_name == "ApproveAPInvoice")
    assert "audit_agent" in defn.allowed_agent_types


def test_reject_ap_invoice_blocks_all_agents():
    catalog = build_core_command_catalog()
    defn = next(c for c in catalog if c.command_name == "RejectAPInvoice")
    assert defn.allowed_agent_types == []


def test_finalize_harvest_acceptance_allows_acceptance_agent():
    catalog = build_core_command_catalog()
    defn = next(c for c in catalog if c.command_name == "FinalizeHarvestAcceptance")
    assert "acceptance_agent" in defn.allowed_agent_types


def test_release_quality_protocol_allows_quality_agent():
    catalog = build_core_command_catalog()
    defn = next(c for c in catalog if c.command_name == "ReleaseQualityProtocol")
    assert "quality_agent" in defn.allowed_agent_types


def test_execute_payment_run_blocks_all_agents():
    manifest = build_agent_command_manifest()
    entry = next(e for e in manifest.commands if e.command_name == "ExecutePaymentRun")
    assert entry.allowed_agent_types == []
    assert entry.requires_human_confirmation is True
