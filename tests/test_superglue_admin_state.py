"""COV-INT-002: Tests fuer superglue_admin_state.py.

Abdeckung: get_superglue_admin_state, update_connector_override,
update_policy_override, update_wizard_state.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from app.integrations.services.superglue_admin_state import (
    get_superglue_admin_state,
    get_superglue_connector_override,
    get_superglue_policy_override,
    update_superglue_connector_override,
    update_superglue_policy_override,
    update_superglue_wizard_state,
)


def _patch_state_path(tmp_path: Path):
    """Context manager that redirects state reads/writes to a temp file."""
    return patch(
        "app.integrations.services.superglue_admin_state._state_path",
        return_value=tmp_path / "admin-state.json",
    )


# ---------------------------------------------------------------------------
# get_superglue_admin_state — empty state
# ---------------------------------------------------------------------------

def test_get_admin_state_empty(tmp_path):
    with _patch_state_path(tmp_path):
        state = get_superglue_admin_state("t1")
    assert state["tenant_id"] == "t1"
    assert state["connector_overrides"] == {}
    assert state["policy_overrides"] == {}
    assert state["schema_version"] == 1


# ---------------------------------------------------------------------------
# update_superglue_connector_override
# ---------------------------------------------------------------------------

def test_update_connector_override_stores_url(tmp_path):
    with _patch_state_path(tmp_path):
        result = update_superglue_connector_override(
            "t1", "conn-A", system_url="https://example.com"
        )
        override = get_superglue_connector_override("t1", "conn-A")
    assert result["connector_key"] == "conn-A"
    assert override["system_url"] == "https://example.com"


def test_update_connector_override_partial_update(tmp_path):
    with _patch_state_path(tmp_path):
        update_superglue_connector_override("t1", "conn-B", system_url="https://a.com")
        update_superglue_connector_override("t1", "conn-B", system_name="My System")
        override = get_superglue_connector_override("t1", "conn-B")
    assert override["system_url"] == "https://a.com"
    assert override["system_name"] == "My System"


def test_update_connector_override_noop_when_no_kwargs(tmp_path):
    with _patch_state_path(tmp_path):
        result = update_superglue_connector_override("t1", "conn-C")
    assert result["connector_key"] == "conn-C"


def test_get_connector_override_returns_empty_for_unknown(tmp_path):
    with _patch_state_path(tmp_path):
        override = get_superglue_connector_override("t1", "nonexistent")
    assert override == {}


# ---------------------------------------------------------------------------
# update_superglue_policy_override
# ---------------------------------------------------------------------------

def test_update_policy_override_execution_enabled(tmp_path):
    with _patch_state_path(tmp_path):
        update_superglue_policy_override("t1", execution_enabled=False)
        policy = get_superglue_policy_override("t1")
    assert policy["execution_enabled"] is False


def test_update_policy_override_alert_thresholds(tmp_path):
    with _patch_state_path(tmp_path):
        update_superglue_policy_override("t1", alert_error_rate_pct=5.0, alert_open_quarantine_count=3)
        policy = get_superglue_policy_override("t1")
    assert policy["alert_error_rate_pct"] == 5.0
    assert policy["alert_open_quarantine_count"] == 3


def test_update_policy_override_retention_days(tmp_path):
    with _patch_state_path(tmp_path):
        update_superglue_policy_override("t1", run_retention_days=30, artifact_retention_days=90)
        policy = get_superglue_policy_override("t1")
    assert policy["run_retention_days"] == 30
    assert policy["artifact_retention_days"] == 90


# ---------------------------------------------------------------------------
# update_superglue_wizard_state
# ---------------------------------------------------------------------------

def test_wizard_state_current_step(tmp_path):
    with _patch_state_path(tmp_path):
        result = update_superglue_wizard_state("t1", current_step="credentials")
    assert result["tenant_id"] == "t1"


def test_wizard_state_persists_completed_steps(tmp_path):
    with _patch_state_path(tmp_path):
        update_superglue_wizard_state("t1", completed_step="credentials")
        update_superglue_wizard_state("t1", completed_step="tools")
        state = get_superglue_admin_state("t1")
    completed = state.get("wizard", {}).get("completed_steps", [])
    assert "credentials" in completed
    assert "tools" in completed


# ---------------------------------------------------------------------------
# Isolation: separate tenants do not share state
# ---------------------------------------------------------------------------

def test_tenant_isolation(tmp_path):
    with _patch_state_path(tmp_path):
        update_superglue_connector_override("t1", "conn-X", system_url="https://t1.example.com")
        override_t2 = get_superglue_connector_override("t2", "conn-X")
    assert override_t2 == {}
