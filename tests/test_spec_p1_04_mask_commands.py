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

    # Ernte-Abrechnung drucken und Opportunity-Aktivitaet sind seit 07.10.2026 ehrliche
    # Luecken (BEKANNTE_LUECKEN im Gate) statt Endpunkte ohne Wirkung.
    @pytest.mark.parametrize("screen_id,action_key", [
        ("sales/delivery-note", "drucken"),
        ("finance/payment-run", "freigeben"),
        ("einkauf/angebot", "bestellen"),
    ])
    def test_new_endpoints_wired(self, screen_id: str, action_key: str):
        sd = get_screen_definition(screen_id)
        actions = {a["key"]: a for a in sd.get("actions", [])}
        assert action_key in actions
        assert "commandEndpoint" in actions[action_key]
        assert "stubReason" not in actions[action_key]


class TestSpecP104ActionRuntimeModes:
    def test_stornieren_hat_keinen_vorgetaeuschten_handler(self):
        # Bis 07.10.2026 meldete der Trockenlauf Erfolg und die Ausfuehrung auch —
        # ohne Storno. Es gibt keinen Storno-Dienst; die Maske nennt die Luecke.
        from app.api.v1.endpoints import mask_actions

        assert not hasattr(mask_actions, "action_lager_stornieren")

    @pytest.mark.asyncio
    async def test_payment_run_requires_audit_reason(self):
        from app.api.v1.endpoints.mask_actions import action_payment_run_freigeben

        db = MagicMock()
        result = await action_payment_run_freigeben(
            "pr-1", body={"_mode": "execute"}, db=db, tenant_id="t1", user={"sub": "kasse", "roles": ["FINANCE_ADMIN"]}
        )
        assert result.success is False
        assert "auditReason" in (result.error or "")
        db.execute.assert_not_called()
