"""Duenne Admin-Ops-Masken (Batch 28b): ScreenDefinitions + admin_workbench-Bindung."""
from __future__ import annotations

from typing import Any


def _ops_shell(
    *,
    screen_id: str,
    title: str,
    subtitle: str,
    purpose: str,
    prompts: list[str],
    fields: list[dict[str, Any]],
    data_sources: list[dict[str, Any]],
    actions: list[dict[str, Any]],
    test_id: str,
    domain: str = "admin",
) -> dict[str, Any]:
    return {
        "schemaVersion": 1,
        "id": screen_id,
        "domain": domain,
        "mode": "cockpit",
        "title": title,
        "subtitle": subtitle,
        "adapter": {"type": "native", "sourceId": screen_id, "temporary": False},
        "layout": {
            "floorplan": "cockpit",
            "density": "compact",
            "contextRail": "audit",
            "tableProfile": "audit",
        },
        "fields": fields,
        "dataSources": data_sources,
        "actions": actions,
        "specialized": {"type": "admin_workbench", "id": screen_id},
        "noWorkflowReason": "Admin-Ops-Leitstand ohne eigenen Beleg-Lebenszyklus.",
        "noProcessChainReason": "Ops-Konsole, keine Belegkette.",
        "performance": {
            "initialPayloadBudgetKb": 120,
            "requiresLazyTabs": True,
            "requiresVirtualTables": False,
            "lookupMinChars": 2,
            "bundleGroup": "admin",
        },
        "agentContract": {
            "businessPurpose": purpose,
            "examplePrompts": prompts,
            "sensitiveFields": [],
            "forbiddenAgentTasks": ["Admin-Ops ohne Audit mutieren"],
            "testSelectors": {"screenRoot": f"[data-testid='{test_id}']"},
        },
    }


def _refresh(permission: str = "studio.admin-ops.read") -> dict[str, Any]:
    return {
        "key": "refresh",
        "label": "Aktualisieren",
        "kind": "secondary",
        "zone": "header",
        "dangerLevel": "safe",
        "permission": permission,
        "localEffect": "refetch",
    }


def build_admin_gap_pipeline() -> dict[str, Any]:
    return _ops_shell(
        screen_id="admin/GapPipelineConsole",
        title="GAP Pipeline Console",
        subtitle="Steuerung und Status der GAP-Pipeline",
        purpose="GAP-Pipeline starten und Status einsehen.",
        prompts=["Wie ist der GAP-Pipeline-Status?"],
        fields=[
            {"key": "year", "label": "Jahr", "type": "number"},
            {"key": "pipeline_complete", "label": "Pipeline fertig", "type": "boolean", "readOnly": True},
            {"key": "gap_payments_count", "label": "GAP-Zahlungen", "type": "number", "readOnly": True},
        ],
        data_sources=[
            # year ist Query-Pflicht am Status-Endpunkt; ohne Default liefert die Liste 422.
            {"key": "entity", "endpoint": "/api/v1/gap/pipeline/status?year=2026", "staleTimeMs": 15_000},
        ],
        actions=[
            _refresh(),
            {
                "key": "run_pipeline",
                "label": "Pipeline starten",
                "kind": "primary",
                "zone": "header",
                "dangerLevel": "moderate",
                "forbiddenForAgents": True,
                "permission": "studio.admin-ops.gap",
                "commandEndpoint": "/api/v1/gap/pipeline/run-year",
                "method": "POST",
                "surfaceOnly": True,
                "inputFields": [{"key": "year", "label": "Jahr", "type": "number", "required": True}],
            },
            {
                "key": "import_pipeline",
                "label": "Import",
                "kind": "secondary",
                "zone": "header",
                "dangerLevel": "moderate",
                "forbiddenForAgents": True,
                "permission": "studio.admin-ops.gap",
                "commandEndpoint": "/api/v1/gap/pipeline/import",
                "method": "POST",
                "surfaceOnly": True,
            },
        ],
        test_id="native-cockpit-admin-GapPipelineConsole",
    )


def build_admin_agenten_integration() -> dict[str, Any]:
    return _ops_shell(
        screen_id="admin/agenten-integration",
        title="Agenten-Integration",
        subtitle="NeuroASSIST Workspace fuer Agenten und Integrationen",
        purpose="Agenten-Integrationsleitstand bedienen.",
        prompts=["Zeig den Agenten-Integrationsstand."],
        fields=[
            {"key": "tenant_id", "label": "Mandant", "type": "text", "readOnly": True},
            {"key": "section", "label": "Bereich", "type": "text", "readOnly": True},
        ],
        data_sources=[],
        actions=[_refresh()],
        test_id="native-cockpit-admin-agenten-integration",
    )


def build_admin_postfaecher_anmeldung_rueckruf() -> dict[str, Any]:
    return _ops_shell(
        screen_id="admin/postfaecher-anmeldung-rueckruf",
        title="Postfaecher Anmeldung Rueckruf",
        subtitle="OAuth-Rueckruf fuer Postfach-Anmeldung abschliessen",
        purpose="Postfach-OAuth-Anmeldung abschliessen.",
        prompts=["Schliesse die Postfach-Anmeldung ab."],
        fields=[
            {"key": "code", "label": "Code", "type": "text"},
            {"key": "state", "label": "State", "type": "text"},
        ],
        data_sources=[],
        actions=[
            _refresh(),
            {
                "key": "callback",
                "label": "Anmeldung abschliessen",
                "kind": "primary",
                "zone": "header",
                "dangerLevel": "moderate",
                "forbiddenForAgents": True,
                "permission": "studio.admin-ops.postfaecher",
                "commandEndpoint": "/api/v1/admin/postfaecher/anmeldung/abschluss",
                "method": "POST",
                "surfaceOnly": True,
                "inputFields": [
                    {"key": "code", "label": "Code", "type": "text", "required": True},
                    {"key": "state", "label": "State", "type": "text", "required": True},
                ],
            },
        ],
        test_id="native-cockpit-admin-postfaecher-anmeldung-rueckruf",
    )


def build_admin_screen_studio() -> dict[str, Any]:
    return _ops_shell(
        screen_id="admin/screen-studio",
        title="Screen Studio",
        subtitle="Studio-Editor fuer ScreenDefinitions",
        purpose="ScreenDefinitions im Studio bearbeiten.",
        prompts=["Oeffne das Screen Studio."],
        fields=[
            {"key": "screen_id", "label": "Screen-ID", "type": "text", "readOnly": True},
            {"key": "status", "label": "Status", "type": "text", "readOnly": True},
        ],
        data_sources=[],
        actions=[_refresh()],
        test_id="native-cockpit-admin-screen-studio",
    )


def build_admin_setup() -> dict[str, Any]:
    return _ops_shell(
        screen_id="admin/setup",
        title="Admin Setup",
        subtitle="Einrichtungsleitstand fuer Mandanten-Setup",
        purpose="Admin-Setup-Schritte einsehen.",
        prompts=["Welcher Setup-Schritt ist offen?"],
        fields=[
            {"key": "step", "label": "Schritt", "type": "text", "readOnly": True},
            {"key": "status", "label": "Status", "type": "text", "readOnly": True},
        ],
        data_sources=[],
        actions=[_refresh()],
        test_id="native-cockpit-admin-setup",
    )


def build_admin_setup_dms() -> dict[str, Any]:
    return _ops_shell(
        screen_id="admin/setup/dms-integration",
        title="Setup DMS-Integration",
        subtitle="Paperless/DMS Bootstrap und Verbindungstest",
        purpose="DMS-Integration im Setup steuern.",
        prompts=["Ist DMS verbunden?"],
        fields=[
            {"key": "status", "label": "Status", "type": "text", "readOnly": True},
            {"key": "connected", "label": "Verbunden", "type": "boolean", "readOnly": True},
        ],
        data_sources=[
            {"key": "entity", "endpoint": "/api/v1/admin/dms/status", "staleTimeMs": 15_000},
        ],
        actions=[
            _refresh(),
            {
                "key": "bootstrap",
                "label": "DMS bootstrap",
                "kind": "primary",
                "zone": "header",
                "dangerLevel": "moderate",
                "forbiddenForAgents": True,
                "permission": "studio.admin-ops.dms",
                "commandEndpoint": "/api/v1/admin/dms/bootstrap",
                "method": "POST",
                "surfaceOnly": True,
            },
            {
                "key": "test",
                "label": "Verbindung testen",
                "kind": "secondary",
                "zone": "header",
                "dangerLevel": "safe",
                "forbiddenForAgents": True,
                "permission": "studio.admin-ops.dms",
                "commandEndpoint": "/api/v1/admin/dms/test",
                "method": "POST",
                "surfaceOnly": True,
            },
        ],
        test_id="native-cockpit-admin-setup-dms-integration",
    )


def build_admin_voice_channel() -> dict[str, Any]:
    return _ops_shell(
        screen_id="admin/voice-channel",
        title="Voice-Kanal",
        subtitle="Sprachbefehle testen und konfigurieren",
        purpose="Voice-Kanal Konfiguration und Test.",
        prompts=["Teste den Voice-Kanal."],
        fields=[
            {"key": "enabled", "label": "Aktiv", "type": "boolean", "readOnly": True},
            {"key": "last_utterance", "label": "Letzte Eingabe", "type": "text", "readOnly": True},
        ],
        data_sources=[],
        actions=[_refresh()],
        test_id="native-cockpit-admin-voice-channel",
    )


def build_admin_vordruck_editor() -> dict[str, Any]:
    return _ops_shell(
        screen_id="admin/vordruck-editor",
        title="Vordruck-Editor",
        subtitle="Beleg-Vordrucke anlegen, speichern und duplizieren",
        purpose="Beleg-Vordrucke verwalten.",
        prompts=["Welche Vordrucke gibt es?"],
        fields=[
            {"key": "id", "label": "ID", "type": "text", "readOnly": True},
            {"key": "name", "label": "Name", "type": "text"},
            {"key": "kategorie", "label": "Kategorie", "type": "text"},
        ],
        data_sources=[
            {"key": "entity", "endpoint": "/api/v1/admin/vordrucke", "staleTimeMs": 15_000},
        ],
        actions=[
            _refresh(),
            {
                "key": "anlegen",
                "label": "Vordruck anlegen",
                "kind": "primary",
                "zone": "header",
                "dangerLevel": "moderate",
                "forbiddenForAgents": True,
                "permission": "studio.admin-ops.vordruck",
                "commandEndpoint": "/api/v1/admin/vordrucke",
                "method": "POST",
                "surfaceOnly": True,
            },
            {
                "key": "speichern",
                "label": "Vordruck speichern",
                "kind": "secondary",
                "zone": "header",
                "dangerLevel": "moderate",
                "forbiddenForAgents": True,
                "permission": "studio.admin-ops.vordruck",
                "commandEndpoint": "/api/v1/admin/vordrucke/{entity_id}",
                "method": "PUT",
                "surfaceOnly": True,
            },
            {
                "key": "duplizieren",
                "label": "Duplizieren",
                "kind": "secondary",
                "zone": "header",
                "dangerLevel": "safe",
                "forbiddenForAgents": True,
                "permission": "studio.admin-ops.vordruck",
                "commandEndpoint": "/api/v1/admin/vordrucke/{entity_id}/duplizieren",
                "method": "POST",
                "surfaceOnly": True,
            },
            {
                "key": "loeschen",
                "label": "Loeschen",
                "kind": "secondary",
                "zone": "header",
                "dangerLevel": "critical",
                "requiresConfirmation": True,
                "forbiddenForAgents": True,
                "permission": "studio.admin-ops.vordruck",
                "commandEndpoint": "/api/v1/admin/vordrucke/{entity_id}",
                "method": "DELETE",
                "surfaceOnly": True,
            },
            {
                "key": "seed_standard",
                "label": "Standard-Vordrucke seeden",
                "kind": "secondary",
                "zone": "header",
                "dangerLevel": "moderate",
                "forbiddenForAgents": True,
                "permission": "studio.admin-ops.vordruck",
                "commandEndpoint": "/api/v1/admin/vordrucke/seed-standard",
                "method": "POST",
                "surfaceOnly": True,
            },
        ],
        test_id="native-cockpit-admin-vordruck-editor",
    )


def build_studio_workspace_composition_preview() -> dict[str, Any]:
    """Lokale Studio-Preview (localStorage) — kein Server-Write."""
    return _ops_shell(
        screen_id="studio/workspace-composition-preview",
        domain="studio",
        title="Workspace-Composition Preview",
        subtitle="Arbeitsraum lokal aus Metadaten zusammensetzen",
        purpose="Studio-Arbeitsraum lokal vorschauen (kein Server-Write).",
        prompts=["Zeig die Workspace-Composition-Vorschau."],
        fields=[
            {"key": "draft_id", "label": "Entwurf", "type": "text", "readOnly": True},
            {"key": "status", "label": "Status", "type": "text", "readOnly": True},
        ],
        data_sources=[],
        actions=[_refresh()],
        test_id="native-cockpit-studio-workspace-composition-preview",
    )


ADMIN_OPS_THIN_BUILDERS: dict[str, Any] = {
    "admin/GapPipelineConsole": build_admin_gap_pipeline,
    "admin/agenten-integration": build_admin_agenten_integration,
    "admin/postfaecher-anmeldung-rueckruf": build_admin_postfaecher_anmeldung_rueckruf,
    "admin/screen-studio": build_admin_screen_studio,
    "admin/setup": build_admin_setup,
    "admin/setup/dms-integration": build_admin_setup_dms,
    "admin/voice-channel": build_admin_voice_channel,
    "admin/vordruck-editor": build_admin_vordruck_editor,
    "studio/workspace-composition-preview": build_studio_workspace_composition_preview,
}

ADMIN_OPS_THIN_ROUTEN = {
    "admin/GapPipelineConsole": "/admin/GapPipelineConsole",
    "admin/gap-pipeline": "/admin/gap-pipeline",
    "admin/agenten-integration": "/admin/agenten-integration",
    "admin/postfaecher-anmeldung-rueckruf": "/admin/postfaecher/anmeldung-rueckruf",
    "admin/screen-studio": "/admin/screen-studio",
    "admin/setup": "/admin/setup",
    "admin/setup/dms-integration": "/admin/setup/dms-integration",
    "admin/voice-channel": "/admin/voice-channel",
    "admin/vordruck-editor": "/admin/vordruck-editor",
    "studio/workspace-composition-preview": "/studio/workspace-composition-preview",
}
