"""
UIX-046: CommandEndpoint-Aktivierung für neue_bestellung und mahnen.
UIX-048: Agent Safety — forbiddenForAgents/humanApprovalRequired/dangerousActions Contract.
"""

from __future__ import annotations

import pytest

from app.core.screen_definitions import get_screen_definition


pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# UIX-046 — CommandEndpoints aktiviert (kein stubReason mehr)
# ---------------------------------------------------------------------------

class TestUIX046CommandEndpoints:
    def _get_actions(self, screen_id: str) -> dict[str, dict]:
        sd = get_screen_definition(screen_id)
        assert sd is not None, f"ScreenDefinition '{screen_id}' nicht gefunden"
        return {a["key"]: a for a in sd.get("actions", [])}

    def test_crm_customer_360_create_activity_has_command_endpoint(self):
        actions = self._get_actions("crm/customer-360")
        a = actions["create_activity"]
        assert "commandEndpoint" in a, "create_activity muss commandEndpoint haben"
        assert "stubReason" not in a, "create_activity darf keinen stubReason mehr haben"
        assert "/crm/customers/" in a["commandEndpoint"]

    def test_einkauf_supplier_neue_bestellung_has_command_endpoint(self):
        actions = self._get_actions("einkauf/supplier")
        a = actions["neue_bestellung"]
        assert "commandEndpoint" in a, "neue_bestellung muss commandEndpoint haben"
        assert "stubReason" not in a, "neue_bestellung darf keinen stubReason mehr haben"
        assert "/einkauf/lieferanten/" in a["commandEndpoint"]
        assert "{entity_id}" in a["commandEndpoint"]

    def test_finance_ar_open_item_mahnen_has_command_endpoint(self):
        actions = self._get_actions("finance/ar-open-item")
        a = actions["mahnen"]
        assert "commandEndpoint" in a, "mahnen muss commandEndpoint haben"
        assert "stubReason" not in a, "mahnen darf keinen stubReason mehr haben"
        assert "/open-items/" in a["commandEndpoint"]
        assert "{entity_id}" in a["commandEndpoint"]

    def test_mahnen_requires_confirmation(self):
        actions = self._get_actions("finance/ar-open-item")
        assert actions["mahnen"].get("requiresConfirmation") is True

    def test_mahnen_danger_level_moderate(self):
        actions = self._get_actions("finance/ar-open-item")
        assert actions["mahnen"]["dangerLevel"] == "moderate"

    def test_finance_ap_invoice_freigeben_has_command_endpoint(self):
        actions = self._get_actions("finance/ap-invoice")
        a = actions["freigeben"]
        assert "commandEndpoint" in a, "freigeben muss commandEndpoint haben"
        assert "stubReason" not in a, "freigeben darf keinen stubReason mehr haben"
        assert "/ap/invoices/" in a["commandEndpoint"]
        assert "{entity_id}" in a["commandEndpoint"]

    def test_freigeben_requires_confirmation(self):
        actions = self._get_actions("finance/ap-invoice")
        assert actions["freigeben"].get("requiresConfirmation") is True

    def test_freigeben_danger_level_moderate(self):
        actions = self._get_actions("finance/ap-invoice")
        assert actions["freigeben"]["dangerLevel"] == "moderate"


# ---------------------------------------------------------------------------
# UIX-048 — Agent Safety Contract
# ---------------------------------------------------------------------------

ALL_SCREEN_IDS = [
    "crm/customer-360",
    "sales/sales-order",
    "agrar/kontrakte",
    "einkauf/supplier",
    "crm/opportunity",
    "lager/article-stock",
    "sales/delivery-note",
    "einkauf/purchase-order",
    "finance/ap-invoice",
    "finance/ar-open-item",
    "lager/stock-movement",
    "agrar/harvest-settlement",
    "finance/payment-run",
]


class TestUIX048AgentSafety:
    @pytest.mark.parametrize("screen_id", ALL_SCREEN_IDS)
    def test_screen_definition_loadable(self, screen_id: str):
        sd = get_screen_definition(screen_id)
        assert sd is not None, f"ScreenDefinition '{screen_id}' nicht abrufbar"

    @pytest.mark.parametrize("screen_id", ALL_SCREEN_IDS)
    def test_agent_contract_present(self, screen_id: str):
        sd = get_screen_definition(screen_id)
        assert "agentContract" in sd, f"{screen_id}: agentContract fehlt"
        contract = sd["agentContract"]
        assert "businessPurpose" in contract, f"{screen_id}: businessPurpose fehlt"

    @pytest.mark.parametrize("screen_id", ALL_SCREEN_IDS)
    def test_actions_have_danger_level(self, screen_id: str):
        sd = get_screen_definition(screen_id)
        for action in sd.get("actions", []):
            assert "dangerLevel" in action, (
                f"{screen_id}/{action['key']}: dangerLevel fehlt"
            )
            assert action["dangerLevel"] in {"safe", "moderate", "high", "critical"}, (
                f"{screen_id}/{action['key']}: ungueltiger dangerLevel '{action['dangerLevel']}'"
            )

    @pytest.mark.parametrize("screen_id", ALL_SCREEN_IDS)
    def test_high_danger_actions_require_human_approval(self, screen_id: str):
        sd = get_screen_definition(screen_id)
        for action in sd.get("actions", []):
            if action.get("dangerLevel") in {"high", "critical"}:
                assert action.get("humanApprovalRequired") is True or action.get("forbiddenForAgents") is True, (
                    f"{screen_id}/{action['key']}: high/critical ohne humanApprovalRequired oder forbiddenForAgents"
                )

    @pytest.mark.parametrize("screen_id", ALL_SCREEN_IDS)
    def test_no_forbidden_agent_action_has_command_endpoint_without_guard(self, screen_id: str):
        """forbiddenForAgents-Actions dürfen commandEndpoint haben, aber Contract muss es signalisieren."""
        sd = get_screen_definition(screen_id)
        contract = sd.get("agentContract", {})
        dangerous_keys = {a["key"] for a in contract.get("dangerousActions", [])}
        for action in sd.get("actions", []):
            if action.get("forbiddenForAgents"):
                # Wenn verboten, sollte es in dangerousActions ODER kein commandEndpoint haben
                has_endpoint = "commandEndpoint" in action and "stubReason" not in action
                if has_endpoint:
                    assert action["key"] in dangerous_keys, (
                        f"{screen_id}/{action['key']}: forbiddenForAgents mit aktivem commandEndpoint "
                        f"muss in agentContract.dangerousActions gelistet sein"
                    )

    def test_payment_run_is_critical(self):
        sd = get_screen_definition("finance/payment-run")
        actions = {a["key"]: a for a in sd.get("actions", [])}
        # payment-run hat ausloesen als critical
        critical_actions = [a for a in sd.get("actions", []) if a.get("dangerLevel") == "critical"]
        assert len(critical_actions) >= 1, "finance/payment-run muss mindestens eine critical-Action haben"
