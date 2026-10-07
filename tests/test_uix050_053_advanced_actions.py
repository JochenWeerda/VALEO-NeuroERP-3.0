"""
UIX-050: auditReasonRequired-Prüfung in ScreenDefinitions.
UIX-051: proposedChanges-Format der Backend-Action-Stubs.
UIX-052: BFF mask-actions Route registriert (Import-Smoke).
UIX-053: Alle neuen CommandEndpoints aktiviert + Backend erreichbar.
"""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock

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
        assert actions["freigeben"].get("auditReasonRequired") is True
        assert actions["freigeben"].get("commandEndpoint")
        assert "stubReason" not in actions["freigeben"]

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
    """Die frueheren Stubs meldeten im Trockenlauf Erfolg und in der Ausfuehrung
    ebenso — ohne fachliche Wirkung (Befund 07.10.2026). Sie sind entfernt; die
    Aktionen mit Fachweg pruefen im Trockenlauf gegen die Datenbank
    (``tests/test_mask_aktionen_wirkung.py``)."""

    @pytest.mark.parametrize("fn_name", [
        "action_einkauf_bestellen",
        "action_lager_wareneingang",
        "action_crm_qualifizieren",
        "action_harvest_settlement_drucken",
    ])
    def test_kein_handler_ohne_fachweg(self, fn_name: str):
        from app.api.v1.endpoints import mask_actions
        assert not hasattr(mask_actions, fn_name)

    @pytest.mark.asyncio
    async def test_trockenlauf_erfindet_keinen_erfolg(self):
        from app.api.v1.endpoints import mask_actions
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None
        result = await mask_actions.action_reklamation_abschliessen(
            "gibt-es-nicht", body={"_mode": "dryRun"}, db=db, tenant_id="test"
        )
        assert result.success is False
        assert result.proposedChanges is None


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
        ("qualitaet/reklamation", "abschliessen", "/reklamationen/"),
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

    @pytest.mark.parametrize("screen_id,action_key", [
        ("crm/lead", "qualifizieren"),
    ])
    def test_ohne_fachweg_sagt_die_maske_nicht_verfuegbar(self, screen_id: str, action_key: str):
        # Diese Aktionen waren "aktiviert" und meldeten Erfolg ohne Wirkung
        # (Befund 07.10.2026). Ohne Fachweg: stubReason, kein Endpunkt.
        a = self._get_actions(screen_id)[action_key]
        assert "commandEndpoint" not in a
        assert a.get("stubReason", "").startswith("Noch kein Fachweg")
