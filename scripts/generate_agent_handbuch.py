#!/usr/bin/env python
"""Generiert das Agent-Handbuch (Prozessketten, Masken-API, Automatisierung).

Single Source of Truth ist der Code:
  - app/core/flow_spine_registry.py
  - app/core/screen_definitions.py
  - config/mcp_erp_tools.yaml
  - scripts/extract_events.py → events_raw.json
  - packages/frontend-web/.../route-inventory.gen.json

Usage:
  python scripts/generate_agent_handbuch.py
  python scripts/generate_agent_handbuch.py --check
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from agent_handbuch_sources import (  # noqa: E402
    MASK_TO_PROCESSES,
    PROCESS_API_BASE,
    derive_agent_contract,
    events_for_domain,
    load_events,
    load_flow_spine_catalog,
    load_flow_spine_workspaces,
    load_mcp_tools,
    load_routes,
    load_screen_definitions,
    load_workflow_specs,
    mask_rollout_route,
    mcp_tools_for_domain,
    risk_summary,
)

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "docs" / "agent-handbuch"
TODAY = date.today().isoformat()

GENERATED_FILES = [
    OUT / "index.md",
    OUT / "prozessketten.md",
    OUT / "masken-api-katalog.md",
    OUT / "automatisierung.md",
    OUT / "agent-process-manifest.json",
]

RISK_DE = {"low": "niedrig", "medium": "mittel", "high": "hoch", "safe": "niedrig", "moderate": "mittel"}


def _frontmatter(title: str, description: str, doc_type: str = "reference") -> list[str]:
    return [
        "---",
        f"title: {title}",
        f"type: {doc_type}",
        "audience: [ki-agent, entwickler, integrator]",
        "owner: Cursor",
        "status: aktiv",
        f"last_reviewed: {TODAY}",
        "version: 3.0.0",
        f"description: {description}",
        "---",
        "",
    ]


def _yesno(v: bool) -> str:
    return "ja" if v else "nein"


def render_index(
    catalog: list[dict[str, str]],
    masks: dict[str, dict[str, Any]],
    tools: list[dict[str, Any]],
    events: list[dict[str, Any]],
) -> str:
    lines = _frontmatter(
        "Agent-Handbuch",
        "Maschinenlesbare Bedienungsanleitung für KI-Agenten — Prozessketten, Masken-APIs, Automatisierung.",
        "explanation",
    )
    lines += [
        "# Agent-Handbuch",
        "",
        "> **Automatisch generiert** via `python scripts/generate_agent_handbuch.py`. "
        "**Nicht manuell bearbeiten.**",
        "",
        "Ergänzt das [Endnutzer-Benutzerhandbuch](../benutzerhandbuch/index.md) um die "
        "**Agent-Sicht**: Welche API wann, in welcher Prozesskette, mit welchem Risiko.",
        "",
        "## Schnellnavigation",
        "",
        "| Dokument | Inhalt |",
        "|---|---|",
        "| [Prozessketten](prozessketten.md) | 9 Flow-Spine E2E-Ketten mit Knoten, Deep-Links, Instanz-API |",
        f"| [Masken-API-Katalog](masken-api-katalog.md) | {len(masks)} ScreenDefinitions mit AgentContract, Endpoints, Actions |",
        f"| [Automatisierung](automatisierung.md) | {len(tools)} MCP-Tools, {len(events)} Domain-Events, ActionRuntime-Modi |",
        "| [agent-process-manifest.json](agent-process-manifest.json) | JSON-Manifest für SDK/Agent-Router |",
        "",
        "## Entscheidungsbaum für Agenten",
        "",
        "```text",
        "Aufgabe erhalten",
        "  ├─ Fachlicher Prozess / Belegkette? → Prozessketten.md + Flow-Spine Instanz",
        "  ├─ Einzelmaske / Stammdaten?       → Masken-API-Katalog + GET .../agent-contract",
        "  ├─ Idempotente Lesefrage?          → MCP-Tool (scope:read) bevorzugen",
        "  └─ Schreiben / Folgebeleg?         → dryRun → propose → Human-Approval → execute",
        "```",
        "",
        "## Authentifizierung (alle APIs)",
        "",
        "| Header | Wert |",
        "|---|---|",
        "| `Authorization` | `Bearer <token>` |",
        "| `X-Tenant-ID` | Mandanten-UUID |",
        "| `X-Correlation-ID` | optional, für Tracing |",
        "",
        "## ActionRuntime-Modi (Mask-Actions)",
        "",
        "| Modus | Body | Wirkung |",
        "|---|---|---|",
        "| `validate` | `_mode: \"validate\"` | Nur Validierung |",
        "| `dryRun` | `_mode: \"dryRun\"` | Simulation ohne Persistenz |",
        "| `propose` | `_mode: \"propose\"` | Vorschlag für Freigabe |",
        "| `execute` | (default) | Persistenz + Audit |",
        "",
        "Zusatzfelder: `_auditReason`, `_idempotencyKey`",
        "",
        "## Flow-Spine-Übersicht",
        "",
        "| process_key | Route | Domäne |",
        "|---|---|---|",
    ]
    for item in catalog:
        lines.append(
            f"| `{item['key']}` | `{item['route_path']}` | {item.get('domain', '')} |"
        )
    lines += [
        "",
        "## Verwandte Dokumentation",
        "",
        "- [Agent-Dokumentation (Governance)](../agent-docs/index.md)",
        "- [Guardrails](../agent-docs/guardrails.md)",
        "- [MCP-Tool-Referenz](../schnittstellen/mcp-tools.md)",
        "- [REST-API / OpenAPI](../schnittstellen/rest-api.md)",
        "- [Mask Runtime API](../entwickler/mask-runtime-api.md)",
        "- [Mask Runtime Agent-Runbook](../agent-docs/runbooks/mask-runtime-agent-modus.md)",
        "",
    ]
    return "\n".join(lines)


def render_prozessketten(
    catalog: list[dict[str, str]],
    workspaces: dict[str, dict[str, Any]],
    workflow_specs: dict[str, list[dict[str, str]]],
    masks: dict[str, dict[str, Any]],
) -> str:
    lines = _frontmatter(
        "Prozessketten (Flow Spine)",
        "End-to-End-Prozessräume mit Knoten, Masken-Deep-Links und Instanz-Lifecycle-API.",
    )
    lines += [
        "# Prozessketten (Flow Spine)",
        "",
        "> Generiert aus `app/core/flow_spine_registry.py` und `docs/workflows/`.",
        "",
        "Jeder **Flow Spine** ist ein agentenfähiger Steuerraum für eine E2E-Kette. "
        "Agenten arbeiten **instanzbasiert**: zuerst Instanz anlegen/laden, dann Knoten "
        "und verlinkte Masken bedienen.",
        "",
        "## Instanz-Lifecycle (gemeinsam für alle 9 Prozesse)",
        "",
        "| Aktion | Methode | Pfad |",
        "|---|---|---|",
        f"| Instanz anlegen | POST | `{PROCESS_API_BASE}/{{process_key}}/instances` |",
        f"| Instanzen listen | GET | `{PROCESS_API_BASE}/{{process_key}}/instances` |",
        f"| Instanz laden | GET | `{PROCESS_API_BASE}/{{process_key}}/instances/{{instance_id}}` |",
        f"| Speichern | POST | `.../instances/{{instance_id}}/save` |",
        f"| Fortsetzen | POST | `.../instances/{{instance_id}}/resume` |",
        f"| Pausieren | POST | `.../instances/{{instance_id}}/hold` |",
        f"| Abschließen | POST | `.../instances/{{instance_id}}/complete` |",
        f"| Abbrechen | POST | `.../instances/{{instance_id}}/cancel` |",
        f"| Fehlschlagen | POST | `.../instances/{{instance_id}}/fail` |",
        f"| Timeline | GET | `.../instances/{{instance_id}}/timeline` |",
        f"| Knotenwechsel | POST | `.../instances/{{instance_id}}/transitions` |",
        f"| Agent-Aktion | POST | `{PROCESS_API_BASE}/{{process_key}}/agent-action` |",
        "",
        "---",
        "",
    ]

    for item in catalog:
        key = item["key"]
        ws = workspaces.get(key, {})
        lines += [
            f"## {item.get('label', key)} (`{key}`)",
            "",
            f"**Route:** `{item.get('route_path', '')}`",
            f"**Domäne:** `{item.get('domain', '')}`",
            f"**Zusammenfassung:** {item.get('summary', ws.get('subtitle', ''))}",
            "",
            f"**Catalog:** `GET {PROCESS_API_BASE}/catalog`",
            f"**Workspace:** `GET {PROCESS_API_BASE}/{key}`",
            f"**Workspace (Instanz):** `GET {PROCESS_API_BASE}/{key}?instance_id={{id}}`",
            "",
        ]

        specs = workflow_specs.get(key, [])
        if specs:
            lines.append("**Fachliche Workflow-Specs:**")
            lines.append("")
            for spec in specs[:8]:
                lane = f" ({spec['lane']})" if spec.get("lane") else ""
                lines.append(f"- [{spec['title']}](../{spec['file']}){lane}")
            if len(specs) > 8:
                lines.append(f"- … und {len(specs) - 8} weitere")
            lines.append("")

        linked = ws.get("linked_modules") or []
        if linked:
            lines += ["**Verknüpfte Module:**", ""]
            for mod in linked:
                if isinstance(mod, (list, tuple)) and len(mod) >= 2:
                    lines.append(f"- {mod[0]} → `{mod[1]}`")
            lines.append("")

        nodes = ws.get("nodes") or []
        if nodes:
            lines += [
                "### Prozessknoten → Masken → APIs",
                "",
                "| Knoten | Status | Deep-Link | API (Primäraktion) |",
                "|---|---|---|---|",
            ]
            for node in nodes:
                actions = node.get("actions") or []
                primary = next((a for a in actions if a.get("variant") == "primary"), actions[0] if actions else {})
                href = primary.get("href", "—")
                api = primary.get("api_path", "—")
                lines.append(
                    f"| {node.get('label', node.get('id', ''))} | "
                    f"{node.get('status', '')} | `{href}` | `{api}` |"
                )
            lines.append("")

            lines += ["### Alle Knotenaktionen", ""]
            for node in nodes:
                lines.append(f"#### Knoten: {node.get('label', node.get('id'))}")
                lines.append("")
                if node.get("insight"):
                    lines.append(f"_{node['insight']}_")
                    lines.append("")
                for act in node.get("actions") or []:
                    lines.append(
                        f"- **{act.get('label')}** → `{act.get('href')}` "
                        f"(API: `{act.get('api_path', '—')}`, Variante: {act.get('variant', '—')})"
                    )
                agent = node.get("agent") or {}
                if agent.get("message"):
                    lines.append(f"- *Agent-Hinweis:* {agent.get('message')}")
                lines.append("")

        # Masken in dieser Kette
        chain_masks = [mid for mid, procs in MASK_TO_PROCESSES.items() if key in procs]
        if chain_masks:
            lines += ["### Registrierte Masken (ScreenDefinition)", ""]
            for mid in sorted(chain_masks):
                defn = masks.get(mid, {})
                title = defn.get("title", mid)
                lines.append(
                    f"- `{mid}` — {title} · "
                    f"Contract: `GET /api/v1/masks/{mid}/agent-contract` · "
                    f"Rollout: `{mask_rollout_route(mid)}`"
                )
            lines.append("")

        lines += ["---", ""]

    return "\n".join(lines)


def render_masken_katalog(
    masks: dict[str, dict[str, Any]],
    tools: list[dict[str, Any]],
    routes: list[dict[str, str]],
) -> str:
    lines = _frontmatter(
        "Masken-API-Katalog",
        "ScreenDefinitions mit AgentMaskContract, REST-Endpoints und Actions.",
    )
    lines += [
        "# Masken-API-Katalog",
        "",
        "> Generiert aus `app/core/screen_definitions.py` "
        f"({len(masks)} Masken).",
        "",
        "## Übersicht",
        "",
        "| mask_id | Titel | Domäne | Risiko | Prozessketten | Agent-Contract |",
        "|---|---|---|---|---|---|",
    ]

    by_domain: dict[str, list[tuple[str, dict[str, Any], dict[str, Any]]]] = {}
    manifest_masks: list[dict[str, Any]] = []

    for mask_id in sorted(masks.keys()):
        defn = masks[mask_id]
        contract = derive_agent_contract(defn)
        actions = contract.get("availableActions") or []
        risk = RISK_DE.get(risk_summary(actions), risk_summary(actions))
        procs = ", ".join(f"`{p}`" for p in MASK_TO_PROCESSES.get(mask_id, [])) or "—"
        lines.append(
            f"| `{mask_id}` | {defn.get('title', '')} | {defn.get('domain', '')} | "
            f"{risk} | {procs or '—'} | "
            f"`GET /api/v1/masks/{mask_id}/agent-contract` |"
        )
        domain = defn.get("domain") or "sonstige"
        by_domain.setdefault(domain, []).append((mask_id, defn, contract))

    lines += ["", "---", ""]

    for domain in sorted(by_domain.keys()):
        lines += [f"## Domäne: {domain}", ""]
        for mask_id, defn, contract in by_domain[domain]:
            lines += [
                f"### `{mask_id}` — {defn.get('title', mask_id)}",
                "",
                f"**Zweck:** {contract.get('businessPurpose', '')}",
                "",
                f"| | |",
                f"|---|---|",
                f"| ScreenDefinition | `GET /api/v1/masks/{mask_id}/screen-definition` |",
                f"| Agent-Contract | `GET /api/v1/masks/{mask_id}/agent-contract` |",
                f"| Readiness | `GET /api/v1/masks/{mask_id}/readiness` |",
                f"| Rollout-Route | `{mask_rollout_route(mask_id)}` |",
                f"| Adapter | `{defn.get('adapter', {}).get('type', 'n/a')}` "
                f"(temporary={_yesno(defn.get('adapter', {}).get('temporary', True))}) |",
                "",
            ]
            if contract.get("summaryEndpoint"):
                lines.append(f"**Summary:** `{contract['summaryEndpoint']}`")
                lines.append("")
            if contract.get("dataSources"):
                lines += ["**Data Sources:**", ""]
                for ds in contract["dataSources"]:
                    lines.append(f"- `{ds.get('key')}` → `{ds.get('endpoint')}`")
                lines.append("")

            mcp = mcp_tools_for_domain(defn.get("domain"), tools)
            if mcp:
                lines += ["**MCP-Tools (Domäne):**", ""]
                for t in mcp:
                    lines.append(
                        f"- `{t.get('tool_id')}` — scope `{t.get('scope')}`, "
                        f"Risiko {RISK_DE.get(t.get('risk_class', ''), t.get('risk_class'))}"
                    )
                lines.append("")

            if contract.get("examplePrompts"):
                lines += ["**Beispiel-Prompts:**", ""]
                for p in contract["examplePrompts"]:
                    lines.append(f"- {p}")
                lines.append("")

            sens = contract.get("sensitiveFields") or []
            if sens:
                lines.append(f"**Sensible Felder:** `{', '.join(sens[:12])}`"
                             + (" …" if len(sens) > 12 else ""))
                lines.append("")

            if actions := contract.get("availableActions"):
                lines += [
                    "**Actions:**",
                    "",
                    "| key | label | danger | Human-Approval | commandEndpoint |",
                    "|---|---|---|---|---|",
                ]
                for a in actions:
                    ep = a.get("commandEndpoint") or (a.get("stubReason") or "—")
                    lines.append(
                        f"| `{a.get('key')}` | {a.get('label')} | {a.get('dangerLevel')} | "
                        f"{_yesno(a.get('humanApprovalRequired'))} | `{ep}` |"
                    )
                lines.append("")

            manifest_masks.append(
                {
                    "mask_id": mask_id,
                    "title": defn.get("title"),
                    "domain": defn.get("domain"),
                    "process_keys": MASK_TO_PROCESSES.get(mask_id, []),
                    "rollout_route": mask_rollout_route(mask_id),
                    "agent_contract_url": f"/api/v1/masks/{mask_id}/agent-contract",
                    "screen_definition_url": f"/api/v1/masks/{mask_id}/screen-definition",
                    "readiness_url": f"/api/v1/masks/{mask_id}/readiness",
                    "risk_summary": risk_summary(actions) if actions else "low",
                    "actions": actions,
                    "sensitive_fields": sens,
                    "mcp_tool_ids": [t.get("tool_id") for t in mcp],
                }
            )
            lines += ["---", ""]

    return "\n".join(lines), manifest_masks


def render_automatisierung(tools: list[dict[str, Any]], events: list[dict[str, Any]]) -> str:
    lines = _frontmatter(
        "Automatisierung",
        "MCP-Tools, Domain-Events und Automatisierungsregeln für Agenten.",
    )
    lines += [
        "# Automatisierung",
        "",
        "> MCP aus `config/mcp_erp_tools.yaml`, Events aus `scripts/extract_events.py`.",
        "",
        "## Automatisierungstypen",
        "",
        "| Typ | Mechanismus | Agent-Regel |",
        "|---|---|---|",
        "| **Synchron lesen** | MCP-Tool / GET REST | Idempotent, kein Approval |",
        "| **Vorschlagen** | ActionRuntime `dryRun` / `propose` | Keine Persistenz ohne Freigabe |",
        "| **Ausführen** | ActionRuntime `execute` / POST commandEndpoint | Human-Approval bei HIGH-risk |",
        "| **Prozessgesteuert** | Flow-Spine Instanz + transitions | Nur erlaubte Knoten, Timeline auditieren |",
        "| **Eventgetrieben** | NATS/Outbox (AsyncAPI) | Idempotent reagieren, nicht doppelt auslösen |",
        "",
        "## MCP-Tools (Operator-Agent)",
        "",
        "Vollständige Referenz: [mcp-tools.md](../schnittstellen/mcp-tools.md)",
        "",
        "| tool_id | Domäne | scope | idempotent | Risiko | Human-Approval | endpoint |",
        "|---|---|---|---|---|---|---|",
    ]
    for t in sorted(tools, key=lambda x: x.get("tool_id", "")):
        lines.append(
            f"| `{t.get('tool_id')}` | {t.get('domain')} | `{t.get('scope')}` | "
            f"{_yesno(t.get('idempotent'))} | "
            f"{RISK_DE.get(t.get('risk_class', ''), t.get('risk_class', ''))} | "
            f"{_yesno(t.get('human_approval_required'))} | "
            f"`{t.get('endpoint', '—')}` |"
        )
    lines += [
        "",
        "## Domain-Events (Auszug)",
        "",
        "Vollständiger Katalog: [events.md](../schnittstellen/events.md)",
        "",
        "Namenskonvention: `tenant.{tenantId}.<domäne>.<aggregat>.<aktion>`",
        "",
    ]

    by_domain: dict[str, list[dict[str, Any]]] = {}
    for ev in events:
        by_domain.setdefault(ev.get("domain") or "Sonstige", []).append(ev)

    for dom in sorted(by_domain.keys()):
        lines += [f"### {dom}", "", "| Event-ID | Kanal | Quelle |", "|---|---|---|"]
        for ev in sorted(by_domain[dom], key=lambda e: e.get("id", ""))[:40]:
            lines.append(f"| `{ev.get('id')}` | {ev.get('channel', 'outbox')} | `{ev.get('source', '—')}` |")
        if len(by_domain[dom]) > 40:
            lines.append(f"| … | | {len(by_domain[dom]) - 40} weitere |")
        lines.append("")

    lines += [
        "## Verbotene Automatisierung",
        "",
        "- Kein `execute` bei `humanApprovalRequired=true` ohne menschliche Freigabe",
        "- Kein blindes Wiederholen nicht-idempotenter Tools/POSTs",
        "- Kein Umgehen der Mandantentrennung (`X-Tenant-ID`)",
        "- Zahlungslauf, Ernte-Abrechnung, Storno: nur nach expliziter Policy (siehe Guardrails)",
        "",
    ]
    return "\n".join(lines)


def build_manifest(
    catalog: list[dict[str, str]],
    workspaces: dict[str, dict[str, Any]],
    mask_entries: list[dict[str, Any]],
    tools: list[dict[str, Any]],
    events: list[dict[str, Any]],
) -> dict[str, Any]:
    processes = []
    for item in catalog:
        key = item["key"]
        ws = workspaces.get(key, {})
        nodes = []
        for node in ws.get("nodes") or []:
            nodes.append(
                {
                    "id": node.get("id"),
                    "label": node.get("label"),
                    "status": node.get("status"),
                    "actions": [
                        {
                            "label": a.get("label"),
                            "href": a.get("href"),
                            "api_path": a.get("api_path"),
                            "variant": a.get("variant"),
                        }
                        for a in (node.get("actions") or [])
                    ],
                }
            )
        processes.append(
            {
                "process_key": key,
                "label": item.get("label"),
                "route_path": item.get("route_path"),
                "domain": item.get("domain"),
                "summary": item.get("summary"),
                "api_base": f"{PROCESS_API_BASE}/{key}",
                "instance_api": f"{PROCESS_API_BASE}/{key}/instances",
                "agent_action_api": f"{PROCESS_API_BASE}/{key}/agent-action",
                "nodes": nodes,
                "mask_ids": [m for m, ps in MASK_TO_PROCESSES.items() if key in ps],
            }
        )

    return {
        "generatedAt": TODAY,
        "schemaVersion": 1,
        "sources": [
            "app/core/flow_spine_registry.py",
            "app/core/screen_definitions.py",
            "config/mcp_erp_tools.yaml",
            "scripts/extract_events.py",
        ],
        "processes": processes,
        "masks": mask_entries,
        "mcp_tools": [
            {
                "tool_id": t.get("tool_id"),
                "domain": t.get("domain"),
                "scope": t.get("scope"),
                "idempotent": t.get("idempotent"),
                "risk_class": t.get("risk_class"),
                "human_approval_required": t.get("human_approval_required"),
                "endpoint": t.get("endpoint"),
            }
            for t in tools
        ],
        "event_count": len(events),
    }


def write_outputs(outputs: dict[Path, str]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for path, content in outputs.items():
        sanitized = "\n".join(line.rstrip() for line in content.splitlines())
        if not sanitized.endswith("\n"):
            sanitized += "\n"
        path.write_text(sanitized, encoding="utf-8")


def content_fingerprint(outputs: dict[Path, str]) -> str:
    h = hashlib.sha256()
    for path in sorted(outputs.keys()):
        h.update(path.name.encode())
        h.update(normalize_for_check(outputs[path], path.suffix).encode("utf-8"))
    return h.hexdigest()


def normalize_for_check(content: str, suffix: str = ".md") -> str:
    """Ignoriert volatile Datumsfelder beim Drift-Vergleich."""
    if suffix == ".json":
        data = json.loads(content)
        data.pop("generatedAt", None)
        return json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    lines = [
        ln.rstrip()
        for ln in content.splitlines()
        if not ln.startswith("last_reviewed:")
    ]
    return "\n".join(lines) + "\n"


def check_outputs(outputs: dict[Path, str]) -> int:
    missing = [p for p in outputs if not p.is_file()]
    if missing:
        print("generate_agent_handbuch: fehlende Dateien (bitte Generator ausführen):")
        for p in missing:
            print(f"  - {p.relative_to(REPO)}")
        return 1
    drift = []
    for path, expected in outputs.items():
        actual = path.read_text(encoding="utf-8")
        exp = expected if expected.endswith("\n") else expected + "\n"
        if normalize_for_check(actual, path.suffix) != normalize_for_check(exp, path.suffix):
            drift.append(path)
    if drift:
        print("generate_agent_handbuch: Drift erkannt — bitte `python scripts/generate_agent_handbuch.py` ausführen:")
        for p in drift:
            print(f"  - {p.relative_to(REPO)}")
        return 1
    print(f"generate_agent_handbuch: {len(outputs)} Artefakte aktuell.")
    return 0


def generate() -> dict[Path, str]:
    catalog = load_flow_spine_catalog()
    workspaces = load_flow_spine_workspaces()
    masks = load_screen_definitions()
    tools = load_mcp_tools()
    events = load_events()
    workflow_specs = load_workflow_specs()
    routes = load_routes()

    mask_md, mask_manifest = render_masken_katalog(masks, tools, routes)
    manifest = build_manifest(catalog, workspaces, mask_manifest, tools, events)

    return {
        OUT / "index.md": render_index(catalog, masks, tools, events),
        OUT / "prozessketten.md": render_prozessketten(catalog, workspaces, workflow_specs, masks),
        OUT / "masken-api-katalog.md": mask_md,
        OUT / "automatisierung.md": render_automatisierung(tools, events),
        OUT / "agent-process-manifest.json": json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Agent-Handbuch generieren")
    parser.add_argument("--check", action="store_true", help="Drift-Prüfung ohne Schreiben")
    args = parser.parse_args()

    try:
        outputs = generate()
    except Exception as exc:
        print(f"generate_agent_handbuch: FEHLER — {exc}", file=sys.stderr)
        return 1

    if args.check:
        return check_outputs(outputs)

    write_outputs(outputs)
    print(
        f"generate_agent_handbuch: {len(outputs)} Dateien nach docs/agent-handbuch/ "
        f"({len(json.loads(outputs[OUT / 'agent-process-manifest.json'])['masks'])} Masken, "
        f"{len(json.loads(outputs[OUT / 'agent-process-manifest.json'])['processes'])} Prozessketten)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
