"""SPEC-P1-04 — Mask commandEndpoint Inventur + ActionRuntime Modi."""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from app.core.screen_definitions import get_screen_definition


pytestmark = pytest.mark.unit


class TestSpecP104CommandInventory:
    def test_no_stub_reason_on_native_screens(self):
        from scripts.check_mask_command_endpoint_inventory import main

        assert main() == 0

    @pytest.mark.parametrize("screen_id,action_key", [
        ("sales/delivery-note", "drucken"),
        ("agrar/harvest-settlement", "drucken"),
        ("crm/opportunity", "create_activity"),
        ("finance/payment-run", "freigeben"),
    ])
    def test_new_endpoints_wired(self, screen_id: str, action_key: str):
        sd = get_screen_definition(screen_id)
        actions = {a["key"]: a for a in sd.get("actions", [])}
        assert action_key in actions
        assert "commandEndpoint" in actions[action_key]
        assert "stubReason" not in actions[action_key]


class TestSpecP104ActionRuntimeModes:
    @pytest.mark.asyncio
    async def test_stornieren_dry_run_no_commit(self):
        from app.api.v1.endpoints.mask_actions import action_lager_stornieren

        db = MagicMock()
        result = await action_lager_stornieren("mov-1", body={"_mode": "dryRun"}, db=db, tenant_id="t1")
        assert result.success is True
        assert result.mode == "dryRun"
        assert result.proposedChanges is not None
        db.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_payment_run_requires_audit_reason(self):
        from app.api.v1.endpoints.mask_actions import action_payment_run_freigeben

        db = MagicMock()
        result = await action_payment_run_freigeben("pr-1", body={"_mode": "execute"}, db=db, tenant_id="t1")
        assert result.success is False
        assert "auditReason" in (result.error or "")
