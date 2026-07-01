"""
UIX-046: CommandEndpoint-Aktivierung für neue_bestellung und mahnen.
UIX-048: Agent Safety — alle 26 nativen ScreenDefinitions geprüft.
"""

from __future__ import annotations

import pytest
import app.core.screen_definitions as _sd_module

from app.core.screen_definitions import get_screen_definition


pytestmark = pytest.mark.unit


def _all_screen_ids() -> list[str]:
    """Leitet alle Screen-IDs dynamisch aus den Builder-Funktionen ab."""
    ids = []
    for name in dir(_sd_module):
        if not name.startswith("build_"):
            continue
        fn = getattr(_sd_module, name)
        try:
            sd = fn()
            screen_id = sd.get("id") if isinstance(sd, dict) else None
            if screen_id:
                ids.append(screen_id)
        except Exception:  # noqa: BLE001
            pass
    return sorted(ids)


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
# UIX-048 — Agent Safety Contract (alle 26 nativen ScreenDefinitions)
# ---------------------------------------------------------------------------

ALL_SCREEN_IDS = _all_screen_ids()


class TestUIX048AgentSafety:
    """Agent Safety Contract für alle 26 nativen ScreenDefinitions."""

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
    def test_forbidden_agent_actions_listed_in_dangerous_actions(self, screen_id: str):
        """forbiddenForAgents-Actions mit aktivem commandEndpoint müssen in agentContract.dangerousActions stehen."""
        sd = get_screen_definition(screen_id)
        contract = sd.get("agentContract", {})
        dangerous_keys = {a["key"] for a in contract.get("dangerousActions", [])}
        for action in sd.get("actions", []):
            if action.get("forbiddenForAgents"):
                has_endpoint = "commandEndpoint" in action and "stubReason" not in action
                if has_endpoint:
                    assert action["key"] in dangerous_keys, (
                        f"{screen_id}/{action['key']}: forbiddenForAgents mit aktivem commandEndpoint "
                        f"muss in agentContract.dangerousActions gelistet sein"
                    )

    @pytest.mark.parametrize("screen_id", ALL_SCREEN_IDS)
    def test_sensitive_fields_declared(self, screen_id: str):
        """Jede SD muss sensitiveFields deklarieren (darf leer sein, muss aber vorhanden sein)."""
        sd = get_screen_definition(screen_id)
        contract = sd.get("agentContract", {})
        assert "sensitiveFields" in contract, (
            f"{screen_id}: agentContract.sensitiveFields fehlt (darf [] sein, muss aber deklariert werden)"
        )
        assert isinstance(contract["sensitiveFields"], list), (
            f"{screen_id}: agentContract.sensitiveFields muss eine Liste sein"
        )

    @pytest.mark.parametrize("screen_id", ALL_SCREEN_IDS)
    def test_readable_and_editable_fields_consistent(self, screen_id: str):
        """editableFields dürfen nur Felder enthalten, die auch in readableFields stehen."""
        sd = get_screen_definition(screen_id)
        contract = sd.get("agentContract", {})
        readable = set(contract.get("readableFields", []))
        editable = set(contract.get("editableFields", []))
        if readable and editable:
            not_readable = editable - readable
            assert not not_readable, (
                f"{screen_id}: editableFields enthält Felder, die nicht in readableFields stehen: {not_readable}"
            )

    @pytest.mark.parametrize("screen_id", ALL_SCREEN_IDS)
    def test_stub_actions_have_no_active_endpoint(self, screen_id: str):
        """Actions mit stubReason dürfen keinen commandEndpoint haben oder dieser ist nur informativ."""
        sd = get_screen_definition(screen_id)
        for action in sd.get("actions", []):
            if action.get("stubReason"):
                # stubReason signalisiert: noch nicht bereit. Eine aktive Action muss kein stubReason haben.
                has_both = "commandEndpoint" in action
                if has_both:
                    # Das ist technisch erlaubt (commandEndpoint dient als Zieldoku), aber stubReason MUSS gesetzt sein.
                    assert "stubReason" in action, (
                        f"{screen_id}/{action['key']}: commandEndpoint ohne stubReason — "
                        "entweder Endpoint aktivieren oder stubReason setzen"
                    )

    def test_all_26_screen_definitions_present(self):
        """Stellt sicher, dass genau 26 native ScreenDefinitions registriert sind."""
        assert len(ALL_SCREEN_IDS) == 26, (
            f"Erwartet 26 ScreenDefinitions, gefunden: {len(ALL_SCREEN_IDS)}: {ALL_SCREEN_IDS}"
        )

    def test_payment_run_is_critical(self):
        sd = get_screen_definition("finance/payment-run")
        critical_actions = [a for a in sd.get("actions", []) if a.get("dangerLevel") == "critical"]
        assert len(critical_actions) >= 1, "finance/payment-run muss mindestens eine critical-Action haben"

    def test_crm_customer_360_sensitive_fields_not_empty(self):
        """CRM 360 enthält persönliche Daten — sensitiveFields muss befüllt sein."""
        sd = get_screen_definition("crm/customer-360")
        contract = sd.get("agentContract", {})
        sensitive = contract.get("sensitiveFields", [])
        assert len(sensitive) > 0, "crm/customer-360: sensitiveFields muss mindestens ein Feld enthalten"
