#!/usr/bin/env python3
"""Generiert Container-Inventar aus docker-compose-Dateien fuer C4-Drift-Check.

Ausgabe:
  - docs/entwickler/container-inventory.md

Quellen:
  - docker-compose.yml (Development)
  - docker-compose.production.yml (Production / Observability)

Verwendung:
    python scripts/generate_container_inventory.py
    python scripts/generate_container_inventory.py --check
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = REPO_ROOT / "docs" / "entwickler" / "container-inventory.md"

COMPOSE_SOURCES: tuple[tuple[str, Path], ...] = (
    ("Development", REPO_ROOT / "docker-compose.yml"),
    ("Production", REPO_ROOT / "docker-compose.production.yml"),
)

# Services documented in C4 (dev + prod); used for drift hint column
C4_DOCUMENTED = frozenset(
    {
        # Dev stack
        "frontend-web",
        "bff-web",
        "dev-sse",
        "backend",
        "ki-usability",
        "inventory-service",
        "dms-adapter",
        "rations-optimization",
        "ai",
        "postgres",
        "paperless-db",
        "redis",
        "paperless-redis",
        "nats",
        "keycloak",
        "paperless",
        "crm-core",
        "crm-sales",
        "crm-service",
        "crm-workflow",
        "crm-analytics",
        "crm-communication",
        "crm-multichannel",
        "crm-security",
        "crm-ai",
        "pgadmin",
        "redis-commander",
        # Production stack
        "frontend",
        "valeo-app",
        "postgres-keycloak",
        "prometheus",
        "grafana",
        "loki",
    }
)

DEV_GROUPS: dict[str, list[str]] = {
    "Presentation": ["frontend-web"],
    "Edge / BFF": ["bff-web", "dev-sse"],
    "Core API": ["backend"],
    "Domain — CRM": [
        "crm-core",
        "crm-sales",
        "crm-service",
        "crm-workflow",
        "crm-analytics",
        "crm-communication",
        "crm-ai",
        "crm-multichannel",
        "crm-security",
    ],
    "Domain — Sonstige": ["inventory-service", "rations-optimization", "ki-usability", "ai"],
    "Integration / DMS": ["dms-adapter", "paperless", "paperless-db", "paperless-redis"],
    "Data / Event": ["postgres", "redis", "nats"],
    "Identity": ["keycloak"],
    "Dev Tools": ["pgadmin", "redis-commander"],
}

PROD_GROUPS: dict[str, list[str]] = {
    "Presentation": ["frontend"],
    "Core API": ["valeo-app"],
    "Domain — Lager": ["inventory-service"],
    "Data / Event": ["postgres", "redis", "nats"],
    "Identity": ["keycloak", "postgres-keycloak"],
    "Observability": ["prometheus", "grafana", "loki"],
}


def parse_compose_services(path: Path) -> list[str]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    in_services = False
    services: list[str] = []
    for line in text.splitlines():
        if re.match(r"^services:\s*$", line):
            in_services = True
            continue
        if in_services:
            if re.match(r"^[a-zA-Z]", line) and not line.startswith(" "):
                break
            match = re.match(r"^  ([a-zA-Z0-9][a-zA-Z0-9_-]*):\s*$", line)
            if match:
                services.append(match.group(1))
    return services


def service_group(name: str, groups: dict[str, list[str]]) -> str:
    for group, members in groups.items():
        if name in members:
            return group
    return "Sonstige"


def render_section(
    label: str,
    compose_path: Path,
    services: list[str],
    groups: dict[str, list[str]],
) -> list[str]:
    rel = compose_path.relative_to(REPO_ROOT).as_posix()
    lines = [
        f"## {label} (`{rel}`)",
        "",
        f"**{len(services)}** Services",
        "",
    ]
    if not services:
        lines.append("_Keine Services geparst._")
        lines.append("")
        return lines

    by_group: dict[str, list[str]] = {}
    for name in services:
        by_group.setdefault(service_group(name, groups), []).append(name)

    order = list(groups.keys()) + ["Sonstige"]
    for group in order:
        items = by_group.get(group)
        if not items:
            continue
        lines.append(f"### {group}")
        lines.append("")
        lines.append("| Service | In C4 dokumentiert |")
        lines.append("|---|---|")
        for name in sorted(items):
            doc = "ja" if name in C4_DOCUMENTED else "prüfen"
            lines.append(f"| `{name}` | {doc} |")
        lines.append("")

    return lines


def render(all_services: dict[str, tuple[Path, list[str], dict[str, list[str]]]], today: str) -> str:
    total = sum(len(svc) for _, svc, _ in all_services.values())
    lines = [
        "---",
        "title: Container-Inventar",
        "type: reference",
        "audience: [entwickler, betrieb]",
        "owner: Cursor",
        "status: aktiv",
        f"last_reviewed: {today}",
        "version: 3.1.0",
        "description: Docker-Compose-Services (Dev + Production) — Basis fuer C4 Container Drift-Check.",
        "---",
        "",
        "# Container-Inventar",
        "",
        "> Automatisch generiert via `python scripts/generate_container_inventory.py`. **Nicht manuell bearbeiten.**",
        "",
        "Architektur-Sicht: [C4 Container](../architecture/views/c4-02-containers.md).",
        "",
        f"**Stand:** {today} — **{total}** Services (alle Compose-Dateien)",
        "",
    ]

    drift_all: set[str] = set()
    for label, (path, services, groups) in all_services.items():
        lines.extend(render_section(label, path, services, groups))
        drift_all.update(s for s in services if s not in C4_DOCUMENTED)

    if drift_all:
        lines.extend(
            [
                "## Drift-Hinweis",
                "",
                "Folgende Compose-Services fehlen in `C4_DOCUMENTED` "
                "(Generator) — ggf. [c4-02-containers.md](../architecture/views/c4-02-containers.md) ergänzen:",
                "",
            ]
        )
        for name in sorted(drift_all):
            lines.append(f"- `{name}`")
        lines.append("")

    lines.extend(
        [
            "## Regenerieren",
            "",
            "```bash",
            "python scripts/generate_container_inventory.py",
            "python scripts/generate_container_inventory.py --check",
            "```",
            "",
            "CI: `.github/workflows/docs.yml` und `scripts/check_all_doc_generators.sh --check`.",
            "",
        ]
    )
    return "\n".join(lines)


def normalize_for_check(content: str) -> str:
    lines = [ln for ln in content.splitlines() if not ln.startswith("last_reviewed:")]
    return "\n".join(lines)


def collect_services() -> dict[str, tuple[Path, list[str], dict[str, list[str]]]]:
    result: dict[str, tuple[Path, list[str], dict[str, list[str]]]] = {}
    for label, path in COMPOSE_SOURCES:
        groups = PROD_GROUPS if label == "Production" else DEV_GROUPS
        services = parse_compose_services(path)
        if not services and path.exists() is False:
            continue
        result[label] = (path, services, groups)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate container inventory markdown")
    parser.add_argument("--check", action="store_true", help="Exit 1 if output would change")
    args = parser.parse_args()

    today = date.today().isoformat()
    all_services = collect_services()
    if not all_services or not any(svc for _, svc, _ in all_services.values()):
        print("ERROR: no services parsed from compose files", file=sys.stderr)
        return 1

    new_content = render(all_services, today)

    if args.check:
        if not OUTPUT.exists():
            print(f"DRIFT: missing {OUTPUT.relative_to(REPO_ROOT)}", file=sys.stderr)
            return 1
        existing = normalize_for_check(OUTPUT.read_text(encoding="utf-8"))
        expected = normalize_for_check(new_content)
        if existing != expected:
            print(f"DRIFT: {OUTPUT.relative_to(REPO_ROOT)} out of date — run generator", file=sys.stderr)
            return 1
        print("OK: container inventory up to date")
        return 0

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(new_content, encoding="utf-8")
    total = sum(len(svc) for _, svc, _ in all_services.values())
    print(f"Wrote {OUTPUT.relative_to(REPO_ROOT)} ({total} services across {len(all_services)} compose files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
