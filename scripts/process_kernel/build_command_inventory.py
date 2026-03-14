from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT = REPO_ROOT / "docs" / "architecture" / "process-kernel" / "wave-1" / "package-a" / "PKP-01-command-inventory.md"

BACKEND_FILES = [
    Path("app/api/v1/endpoints/agrar_contracts.py"),
    Path("app/api/v1/endpoints/agrar_settlements.py"),
    Path("app/api/v1/endpoints/harvest_acceptance.py"),
    Path("app/api/v1/endpoints/quality_protocols.py"),
]

FRONTEND_FILES = [
    Path("packages/frontend-web/src/pages/annahme/abrechnung.tsx"),
    Path("packages/frontend-web/src/pages/annahme/qualitaets-check.tsx"),
    Path("packages/frontend-web/src/pages/annahme/lkw-registrierung.tsx"),
    Path("packages/frontend-web/src/pages/workflow/workflow-sandbox.tsx"),
    Path("packages/frontend-web/src/pages/policy-manager.tsx"),
]

ROUTE_RE = re.compile(r"@router\.(get|post|patch|put|delete)\(\"([^\"]+)\"")
FUNC_RE = re.compile(r"async def ([a-zA-Z0-9_]+)\(")


def extract_backend_entries(relative_path: Path) -> list[dict[str, str]]:
    path = REPO_ROOT / relative_path
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    entries: list[dict[str, str]] = []
    current_route: tuple[str, str] | None = None
    for index, line in enumerate(lines, start=1):
        route_match = ROUTE_RE.search(line)
        if route_match:
            current_route = (route_match.group(1).upper(), route_match.group(2))
            continue
        func_match = FUNC_RE.search(line)
        if func_match and current_route:
            method, route = current_route
            entries.append(
                {
                    "method": method,
                    "route": route,
                    "function": func_match.group(1),
                    "path": str(relative_path).replace("\\", "/"),
                    "line": str(index),
                    "command": infer_command(func_match.group(1), route, method),
                }
            )
            current_route = None
    return entries


def extract_frontend_entries(relative_path: Path) -> list[dict[str, str]]:
    path = REPO_ROOT / relative_path
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    entries: list[dict[str, str]] = []
    for match in re.finditer(r"(?:apiClient|api)\.(get|post|patch|put|delete)<*[^>]*>*\(\s*'([^']+)'", text):
        method = match.group(1).upper()
        route = match.group(2)
        line = text[: match.start()].count("\n") + 1
        entries.append(
            {
                "method": method,
                "route": route,
                "function": "ui-call",
                "path": str(relative_path).replace("\\", "/"),
                "line": str(line),
                "command": infer_command(relative_path.stem, route, method),
            }
        )
    return entries


def infer_command(function_name: str, route: str, method: str) -> str:
    normalized = f"{function_name} {route}".lower()
    if "alloc" in normalized:
        return "contract.allocate"
    if "contract" in normalized and method == "POST":
        return "contract.create"
    if "contract" in normalized and method in {"PATCH", "PUT"}:
        return "contract.update"
    if "quality" in normalized or "protocol" in normalized:
        return "quality.record"
    if "preview" in normalized:
        return "settlement.preview"
    if "post-fibu" in normalized or "posted" in normalized:
        return "settlement.post"
    if "settlement" in normalized and method == "POST":
        return "settlement.create"
    if "workflow-sandbox" in normalized:
        return "workflow.simulate"
    if "lkw-registrierung" in normalized:
        return "acceptance.register"
    if "annahme" in normalized or "harvest" in normalized:
        return "acceptance.capture"
    if "policy" in normalized:
        return "policy.evaluate"
    return "candidate.review"


def render_markdown(backend_entries: list[dict[str, str]], frontend_entries: list[dict[str, str]]) -> str:
    lines = [
        "# PKP-01 Command-Inventur",
        "",
        "## Zweck",
        "- Inventur der bestehenden Kernprozesspfade für `Kontrakt -> Annahme -> Qualität -> Settlement`",
        "- Basis für `A3` Ziel-Command-Katalog",
        "",
        "## Status",
        "- erstellt durch reproduzierbare Code-Inventur",
        "- Quelle: `scripts/process_kernel/build_command_inventory.py`",
        "",
        "## Vorläufige Ziel-Commands",
        "- `contract.create`",
        "- `contract.update`",
        "- `contract.allocate`",
        "- `acceptance.register`",
        "- `acceptance.capture`",
        "- `quality.record`",
        "- `settlement.preview`",
        "- `settlement.create`",
        "- `settlement.post`",
        "- `workflow.simulate`",
        "- `policy.evaluate`",
        "",
        "## Backend-Inventur",
        "",
        "| Methode | Route | Funktion | Ziel-Command | Quelle |",
        "|------|------|------|------|------|",
    ]
    for entry in backend_entries:
        lines.append(
            f"| `{entry['method']}` | `{entry['route']}` | `{entry['function']}` | `{entry['command']}` | `{entry['path']}:{entry['line']}` |"
        )
    lines.extend(
        [
            "",
            "## Frontend-Inventur",
            "",
            "| Methode | API-Pfad | Ziel-Command | Quelle |",
            "|------|------|------|------|",
        ]
    )
    for entry in frontend_entries:
        lines.append(
            f"| `{entry['method']}` | `{entry['route']}` | `{entry['command']}` | `{entry['path']}:{entry['line']}` |"
        )
    lines.extend(
        [
            "",
            "## Vorläufiges Mapping bestehender Pfade -> Ziel-Command",
            "",
            "| Bereich | Bestehender Pfad | Ziel-Command | Hinweis |",
            "|------|------|------|------|",
        ]
    )
    seen: set[tuple[str, str]] = set()
    for entry in backend_entries + frontend_entries:
        key = (entry["route"], entry["command"])
        if key in seen:
            continue
        seen.add(key)
        scope = "backend" if entry in backend_entries else "frontend"
        lines.append(f"| `{scope}` | `{entry['route']}` | `{entry['command']}` | vorläufige Heuristik, fachlich prüfen |")
    lines.extend(
        [
            "",
            "## Offene Punkte",
            "- `candidate.review`-Einträge fachlich auf echte Commands konsolidieren",
            "- UI-CRUD-Pfade gegen explizite Command-Semantik prüfen",
            "- fehlende Reklamationspfade im nächsten Schritt ergänzen",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    backend_entries: list[dict[str, str]] = []
    frontend_entries: list[dict[str, str]] = []
    for file_path in BACKEND_FILES:
        backend_entries.extend(extract_backend_entries(file_path))
    for file_path in FRONTEND_FILES:
        frontend_entries.extend(extract_frontend_entries(file_path))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(render_markdown(backend_entries, frontend_entries), encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
