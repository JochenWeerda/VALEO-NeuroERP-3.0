#!/usr/bin/env python
"""Rendert die MCP-Tool-Referenz aus der Tool-Registry.

Single Source of Truth ist ``config/mcp_erp_tools.yaml``. Dieses Skript erzeugt
daraus die durchsuchbare Markdown-Referenz ``docs/schnittstellen/mcp-tools.md``.

Verwendung:
    python scripts/generate_mcp_tool_reference.py
    python scripts/generate_mcp_tool_reference.py --check   # Drift-Pruefung
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY = REPO_ROOT / "config" / "mcp_erp_tools.yaml"
OUTPUT = REPO_ROOT / "docs" / "schnittstellen" / "mcp-tools.md"

RISK_BADGE = {"low": "niedrig", "medium": "mittel", "high": "hoch"}


def _yesno(value: object) -> str:
    return "ja" if value else "nein"


def _schema_block(title: str, schema: object) -> list[str]:
    if not schema:
        return []
    rendered = json.dumps(schema, ensure_ascii=False, indent=2)
    return [f"**{title}:**", "", "```json", rendered, "```", ""]


def render(registry: dict) -> str:
    tools = registry.get("tools", [])
    domains: dict[str, list[dict]] = {}
    for tool in tools:
        domains.setdefault(tool.get("domain", "sonstige"), []).append(tool)

    lines: list[str] = []
    lines.append("---")
    lines.append("title: MCP-Tool-Referenz")
    lines.append("type: reference")
    lines.append("audience: [ki-agent, integrator, entwickler]")
    lines.append("owner: Cursor")
    lines.append("status: aktiv")
    lines.append("last_reviewed: 2026-06-25")
    lines.append("version: 3.0.0")
    lines.append("---")
    lines.append("")
    lines.append("# MCP-Tool-Referenz")
    lines.append("")
    lines.append(
        "> Automatisch generiert aus `config/mcp_erp_tools.yaml` via "
        "`python scripts/generate_mcp_tool_reference.py`. **Nicht manuell bearbeiten.**"
    )
    lines.append("")
    lines.append(
        f"Registry `{registry.get('registry_id', 'MCP-ERP-TOOLS')}` "
        f"(Schema {registry.get('schema_version', 'n/a')}) — "
        f"{len(tools)} Tools in {len(domains)} Domaenen."
    )
    lines.append("")

    lines.append("## Uebersicht")
    lines.append("")
    lines.append("| Tool | Domaene | Scope | Idempotent | Risiko | Human-Approval |")
    lines.append("|---|---|---|---|---|---|")
    for tool in sorted(tools, key=lambda t: t.get("tool_id", "")):
        risk = RISK_BADGE.get(tool.get("risk_class", ""), tool.get("risk_class", "?"))
        lines.append(
            f"| `{tool.get('tool_id')}` | {tool.get('domain')} | `{tool.get('scope')}` | "
            f"{_yesno(tool.get('idempotent'))} | {risk} | "
            f"{_yesno(tool.get('human_approval_required'))} |"
        )
    lines.append("")

    for domain in sorted(domains):
        lines.append(f"## Domaene: {domain}")
        lines.append("")
        for tool in sorted(domains[domain], key=lambda t: t.get("tool_id", "")):
            risk = RISK_BADGE.get(tool.get("risk_class", ""), tool.get("risk_class", "?"))
            lines.append(f"### `{tool.get('tool_id')}` — {tool.get('name', '')}")
            lines.append("")
            lines.append(tool.get("description", ""))
            lines.append("")
            lines.append(f"- **Scope:** `{tool.get('scope')}`")
            lines.append(f"- **Idempotent:** {_yesno(tool.get('idempotent'))}")
            lines.append(f"- **Risikoklasse:** {risk}")
            lines.append(f"- **Audit:** {tool.get('audit', 'n/a')}")
            lines.append(
                f"- **Human-Approval erforderlich:** {_yesno(tool.get('human_approval_required'))}"
            )
            if tool.get("endpoint"):
                lines.append(f"- **Endpoint:** `{tool.get('endpoint')}`")
            lines.append("")
            lines.extend(_schema_block("Eingabe-Schema", tool.get("input_schema")))
            lines.extend(_schema_block("Ausgabe-Schema", tool.get("output_schema")))

    return "\n".join(lines).rstrip("\n") + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="MCP-Tool-Referenz generieren")
    parser.add_argument("--check", action="store_true", help="Drift-Pruefung (Exit 1 bei Abweichung).")
    args = parser.parse_args()

    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    content = render(registry)

    if args.check:
        if not OUTPUT.exists():
            print(f"FEHLT: {OUTPUT} existiert nicht.", file=sys.stderr)
            return 1
        if OUTPUT.read_text(encoding="utf-8") != content:
            print(
                f"DRIFT: {OUTPUT} ist nicht aktuell. Bitte "
                "'python scripts/generate_mcp_tool_reference.py' ausfuehren.",
                file=sys.stderr,
            )
            return 1
        print(f"OK: {OUTPUT} ist aktuell ({len(registry.get('tools', []))} Tools).")
        return 0

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(content, encoding="utf-8")
    print(f"Geschrieben: {OUTPUT} ({len(registry.get('tools', []))} Tools).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
