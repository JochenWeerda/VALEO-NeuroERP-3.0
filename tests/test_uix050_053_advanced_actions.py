"""
UIX-050: auditReasonRequired-Prüfung in ScreenDefinitions.
UIX-051: proposedChanges-Format der Backend-Action-Stubs.
UIX-052: BFF mask-actions Route registriert (Import-Smoke).
UIX-053: Alle neuen CommandEndpoints aktiviert + Backend erreichbar.
"""

from __future__ import annotations

import pytest

from app.core.screen_definitions import get_screen_definition


pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# UIX-050 — auditReasonRequired ist korrekt gesetzt
# ---------------------------------------------------------------------------

class TestUIX050AuditReason:
    def test_payment_run_freigeben_has_audit_reason_required(self):
        sd = get_screen_definition("finance/payment-run")
        actions = {a["key"]: a for a in sd.get("actions", [])}
        assert "freigeben" in actions, "finance/payment-run muss freigeben-Action haben"
        # freigeben hat noch stubReason — auditReasonRequired trotzdem gesetzt
        assert actions["freigeben"].get("auditReasonRequired") is True

    def test_only_critical_actions_require_audit_reason(self):
        """auditReasonRequired sollte nur bei critical/high gesetzt sein."""
        screen_ids = [
            "crm/customer-360", "sales/sales-order", "einkauf/supplier",
            "finance/ar-open-item", "lager/stock-movement", "finance/payment-run",
        ]
        for sid in screen_ids:
            sd = get_screen_definition(sid)
            for action in sd.get("actions", []):
                if action.get("auditReasonRequired"):
                    assert action.get("dangerLevel") in {"high", "critical"}, (
                        f"{sid}/{action['key']}: auditReasonRequired aber dangerLevel={action.get('dangerLevel')}"
                    )


# ---------------------------------------------------------------------------
# UIX-051 — Backend Stubs liefern proposedChanges
# ---------------------------------------------------------------------------

class TestUIX051DryRunFormat:
    """Prüft dass Action-Stub-Responses proposedChanges enthalten (Coroutine-Inspection)."""

    @pytest.mark.parametrize("screen_id,action_key,fn_name", [
        ("lager/stock-movement", "stornieren", "action_lager_stornieren"),
        ("einkauf/purchase-order", "bestellen", "action_einkauf_bestellen"),
        ("lager/article-stock", "wareneingang", "action_lager_wareneingang"),
        ("qualitaet/reklamation", "abschliessen", "action_reklamation_abschliessen"),
        ("crm/lead", "qualifizieren", "action_crm_qualifizieren"),
    ])
    @pytest.mark.asyncio
    async def test_stub_returns_proposed_changes(self, screen_id: str, action_key: str, fn_name: str):
        from app.api.v1.endpoints import mask_actions
        fn = getattr(mask_actions, fn_name)
        result = await fn("test-id-123", tenant_id="test")
        assert result["success"] is True
        assert "proposedChanges" in result, f"{screen_id}/{action_key}: kein proposedChanges"
        assert isinstance(result["proposedChanges"], dict)
        assert result["entityId"] == "test-id-123"


# ---------------------------------------------------------------------------
# UIX-052 — BFF maskActions Service importierbar
# ---------------------------------------------------------------------------

class TestUIX052BffMaskActions:
    def test_mask_actions_service_importable(self):
        """Smoke: BFF maskActions Service kann importiert werden."""
        # Kein echter Node-Import möglich aus Python, aber wir prüfen die Datei
        import pathlib
        service_file = pathlib.Path("packages/bff/bff-web/src/services/maskActions.ts")
        assert service_file.exists(), "maskActions.ts Service-Datei fehlt"

    def test_mask_actions_service_exports_execute(self):
        """executeMaskAction ist in der Service-Datei definiert."""
        import pathlib
        content = pathlib.Path("packages/bff/bff-web/src/services/maskActions.ts").read_text()
        assert "executeMaskAction" in content
        assert "MaskActionRequest" in content
        assert "commandEndpoint" in content

    def test_bff_server_handles_mask_actions_route(self):
        """BFF server.ts hat mask-actions:execute case."""
        import pathlib
        content = pathlib.Path("packages/bff/bff-web/src/server.ts").read_text()
        assert "mask-actions:execute" in content
        assert "executeMaskAction" in content


# ---------------------------------------------------------------------------
# UIX-053 — Alle neuen CommandEndpoints aktiviert
# ---------------------------------------------------------------------------

class TestUIX053CommandEndpoints:
    def _get_actions(self, screen_id: str) -> dict[str, dict]:
        sd = get_screen_definition(screen_id)
        assert sd is not None
        return {a["key"]: a for a in sd.get("actions", [])}

    @pytest.mark.parametrize("screen_id,action_key,endpoint_fragment", [
        ("lager/stock-movement", "stornieren", "/lager/stock-movements/"),
        ("einkauf/angebot", "bestellen", "/einkauf/bestellungen/"),
        ("qualitaet/reklamation", "abschliessen", "/reklamationen/"),
        ("crm/lead", "qualifizieren", "/crm/leads/"),
    ])
    def test_command_endpoint_activated(self, screen_id: str, action_key: str, endpoint_fragment: str):
        actions = self._get_actions(screen_id)
        a = actions[action_key]
        assert "commandEndpoint" in a, f"{screen_id}/{action_key}: commandEndpoint fehlt"
        assert "stubReason" not in a, f"{screen_id}/{action_key}: stubReason noch vorhanden"
        assert endpoint_fragment in a["commandEndpoint"], (
            f"{screen_id}/{action_key}: endpoint '{a['commandEndpoint']}' enthält '{endpoint_fragment}' nicht"
        )
        assert "{entity_id}" in a["commandEndpoint"]

    def test_stornieren_still_requires_human_approval(self):
        actions = self._get_actions("lager/stock-movement")
        assert actions["stornieren"].get("humanApprovalRequired") is True
        assert actions["stornieren"].get("requiresConfirmation") is True

    def test_wareneingang_anlieferavis_command_endpoint(self):
        # anlieferavis-SD (falls vorhanden) — wareneingang aktiviert
        from app.core.screen_definitions import _SCREEN_DEFINITIONS
        # wareneingang ist in einkauf/anlieferavis-SD definiert
        sd_keys = list(_SCREEN_DEFINITIONS.keys())
        avis_key = next((k for k in sd_keys if "anlieferavis" in k or "avis" in k), None)
        if avis_key:
            actions = self._get_actions(avis_key)
            if "wareneingang" in actions:
                a = actions["wareneingang"]
                assert "commandEndpoint" in a
                assert "stubReason" not in a
