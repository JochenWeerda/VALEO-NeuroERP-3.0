"""
Wave 5 Paket A — Business-Command-Layer Tests.

21 Tests ohne DB, ohne FastAPI-Client.
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
from app.core.agent_command_manifest import build_agent_command_manifest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_command(
    command_name: str,
    aggregate_type: str = "ap_invoice",
    aggregate_id: str = "inv-001",
    requires_human_confirmation: bool = False,
) -> BusinessCommand:
    return BusinessCommand(
        command_id=str(uuid.uuid4()),
        tenant_id="tenant-test",
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        command_name=command_name,
        issued_by="user-42",
        idempotency_key=str(uuid.uuid4()),
        requires_human_confirmation=requires_human_confirmation,
    )


# ---------------------------------------------------------------------------
# BusinessCommand / CommandResult / CommandError — schema_version
# ---------------------------------------------------------------------------

def test_business_command_schema_version():
    cmd = _make_command("ApproveAPInvoice")
    assert cmd.schema_version == 1


def test_command_result_accepted_schema_version():
    result = CommandResult(
        command_id="cmd-1",
        status=CommandStatus.ACCEPTED,
        aggregate_type="ap_invoice",
        aggregate_id="inv-001",
    )
    assert result.schema_version == 1


def test_command_error_schema_version():
    err = CommandError(code="NOT_FOUND", message="Nicht gefunden")
    assert err.schema_version == 1


# ---------------------------------------------------------------------------
# CommandPrecondition.evaluate
# ---------------------------------------------------------------------------

def test_command_precondition_evaluate_eq_true():
    pc = CommandPrecondition(field="status", operator="eq", expected="FREIGEGEBEN")
    assert pc.evaluate("FREIGEGEBEN") is True


def test_command_precondition_evaluate_eq_false():
    pc = CommandPrecondition(field="status", operator="eq", expected="FREIGEGEBEN")
    assert pc.evaluate("DRAFT") is False


def test_command_precondition_evaluate_in_true():
    pc = CommandPrecondition(
        field="status",
        operator="in",
        expected=["ZUR_FREIGABE", "TEILWEISE_FREIGEGEBEN"],
    )
    assert pc.evaluate("ZUR_FREIGABE") is True


def test_command_precondition_evaluate_not_in():
    pc = CommandPrecondition(
        field="approved_by",
        operator="not_in",
        expected=["", None],
    )
    assert pc.evaluate("user-99") is True
    assert pc.evaluate("") is False
    assert pc.evaluate(None) is False


def test_command_precondition_evaluate_gte():
    pc = CommandPrecondition(field="amount", operator="gte", expected=100)
    assert pc.evaluate(100) is True
    assert pc.evaluate(200) is True
    assert pc.evaluate(99) is False


# ---------------------------------------------------------------------------
# CommandDefinition / Katalog
# ---------------------------------------------------------------------------

def test_build_core_command_catalog_not_empty():
    catalog = build_core_command_catalog()
    assert len(catalog) >= 9


def test_approve_ap_invoice_in_catalog():
    catalog = build_core_command_catalog()
    names = [cd.command_name for cd in catalog]
    assert "ApproveAPInvoice" in names


def test_execute_payment_run_requires_human_confirmation():
    catalog = build_core_command_catalog()
    epr = next(cd for cd in catalog if cd.command_name == "ExecutePaymentRun")
    assert epr.requires_human_confirmation is True


def test_execute_payment_run_blocked_for_agents():
    catalog = build_core_command_catalog()
    epr = next(cd for cd in catalog if cd.command_name == "ExecutePaymentRun")
    assert epr.allowed_agent_types == []


# ---------------------------------------------------------------------------
# CommandDispatcher
# ---------------------------------------------------------------------------

def test_dispatcher_accepts_valid_command():
    cmd = _make_command("ApproveAPInvoice", aggregate_type="ap_invoice")
    dispatcher = CommandDispatcher()
    result = dispatcher.dispatch(
        cmd,
        aggregate_state={"status": "ZUR_FREIGABE"},
        issuer_role="finance_manager",
    )
    assert result.status == CommandStatus.ACCEPTED
    assert result.error is None


def test_dispatcher_rejects_unknown_command():
    cmd = _make_command("NonExistentCommand")
    dispatcher = CommandDispatcher()
    result = dispatcher.dispatch(cmd, aggregate_state={})
    assert result.status == CommandStatus.REJECTED
    assert result.error is not None
    assert result.error.code == "UNKNOWN_COMMAND"


def test_dispatcher_rejects_wrong_role():
    cmd = _make_command("ApproveAPInvoice", aggregate_type="ap_invoice")
    dispatcher = CommandDispatcher()
    result = dispatcher.dispatch(
        cmd,
        aggregate_state={"status": "ZUR_FREIGABE"},
        issuer_role="warehouse_manager",
    )
    assert result.status == CommandStatus.REJECTED
    assert result.error is not None
    assert result.error.code == "ROLE_DENIED"


def test_dispatcher_rejects_precondition_failed():
    cmd = _make_command("ApproveAPInvoice", aggregate_type="ap_invoice")
    dispatcher = CommandDispatcher()
    result = dispatcher.dispatch(
        cmd,
        aggregate_state={"status": "STORNIERT"},
        issuer_role="finance_manager",
    )
    assert result.status == CommandStatus.REJECTED
    assert result.error is not None
    assert result.error.code == "WRONG_STATUS"


def test_dispatcher_requires_human_confirmation_pending():
    # ExecutePaymentRun requires human confirmation but command flag is False
    cmd = _make_command(
        "ExecutePaymentRun",
        aggregate_type="payment_run",
        requires_human_confirmation=False,
    )
    dispatcher = CommandDispatcher()
    result = dispatcher.dispatch(
        cmd,
        aggregate_state={"status": "FREIGEGEBEN"},
        issuer_role="treasury_manager",
    )
    assert result.status == CommandStatus.PENDING_APPROVAL
    assert result.error is not None
    assert result.error.code == "HUMAN_CONFIRMATION_REQUIRED"


def test_dispatcher_no_role_filter_allows_any():
    # CommandDefinition mit leerem allowed_roles → kein Filter
    custom_catalog = [
        CommandDefinition(
            command_name="OpenCommand",
            aggregate_type="any_aggregate",
            preconditions=[],
            allowed_roles=[],   # kein Filter
            allowed_agent_types=[],
        )
    ]
    dispatcher = CommandDispatcher(catalog=custom_catalog)
    cmd = _make_command("OpenCommand", aggregate_type="any_aggregate")
    result = dispatcher.dispatch(cmd, aggregate_state={}, issuer_role="random_role")
    assert result.status == CommandStatus.ACCEPTED


# ---------------------------------------------------------------------------
# AgentCommandManifest
# ---------------------------------------------------------------------------

def test_agent_manifest_build_default():
    manifest = build_agent_command_manifest()
    assert len(manifest.commands) >= 9
    assert manifest.schema_version == 1


def test_agent_manifest_restricted_commands_include_execute_payment():
    manifest = build_agent_command_manifest()
    assert "ExecutePaymentRun" in manifest.agent_restricted_commands


def test_agent_manifest_blocked_fully_includes_post_invoice():
    manifest = build_agent_command_manifest()
    assert "PostAPInvoice" in manifest.fully_blocked_for_agents
