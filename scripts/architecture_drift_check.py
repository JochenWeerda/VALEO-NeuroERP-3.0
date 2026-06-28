#!/usr/bin/env python3
"""Architecture OS Drift-Checks — domänenzentriert.

Prüft:
  - Generatoren (OpenAPI, Inventare, C4, Index)
  - Routes/Endpoints/Services ohne Domain-Mapping (Warnung/Fehler)
  - workspace.dsl vs. container-inventory (Container ohne DSL-Erwähnung)

Verwendung:
    python scripts/architecture_drift_check.py
    python scripts/architecture_drift_check.py --strict
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = REPO_ROOT / "config" / "architecture-index.yaml"
DSL_PATH = REPO_ROOT / "docs" / "architecture" / "c4" / "workspace.dsl"


def run(cmd: list[str]) -> int:
    print(f"== {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=REPO_ROOT)
    return result.returncode


def load_yaml(path: Path) -> dict:
    try:
        import yaml
    except ImportError:
        print("FEHLER: PyYAML fehlt", file=sys.stderr)
        sys.exit(1)
    text = path.read_text(encoding="utf-8")
    # strip comment header lines
    lines = [ln for ln in text.splitlines() if not ln.strip().startswith("#")]
    return yaml.safe_load("\n".join(lines)) or {}


def check_unmapped_domains(index: dict, strict: bool) -> list[str]:
    """Fehler wenn unmapped Eintraege existieren (strict) oder nur melden."""
    errors: list[str] = []
    unmapped = index.get("unmapped", {})
    for key, label in (
        ("frontend_routes", "Frontend-Routen"),
        ("backend_services", "Backend-Services"),
        ("backend_endpoints", "Backend-Endpoints"),
    ):
        items = unmapped.get(key, [])
        if not items:
            continue
        msg = f"{len(items)} {label} ohne Domain-Mapping"
        if strict:
            sample = ", ".join(items[:3])
            errors.append(f"{msg} (z. B. {sample})")
        else:
            print(f"INFO: {msg}")
    return errors


def check_dsl_containers(index: dict) -> list[str]:
    errors: list[str] = []
    if not DSL_PATH.exists():
        return [f"DSL fehlt: {DSL_PATH}"]

    dsl_text = DSL_PATH.read_text(encoding="utf-8")
    containers = index.get("containers", [])
    domain_containers: set[str] = set()
    for domain in index.get("domains", {}).values():
        domain_containers.update(domain.get("containers", []))

    # Key infra containers expected in DSL by name
    for name in ["backend", "frontend-web", "postgres", "redis", "nats"]:
        if name not in dsl_text:
            errors.append(f"Container '{name}' nicht in workspace.dsl referenziert")

    missing_from_index = [c for c in containers if c.startswith("crm-") and c not in domain_containers]
    if missing_from_index:
        print(f"INFO: CRM-Container in Inventar, Domain-Mapping via Prefix: {len(missing_from_index)}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true", help="Generator-Checks + vollstaendiges Domain-Mapping")
    args = parser.parse_args()

    checks = [
        ["python", "scripts/render_c4_views.py", "--check"],
        [
            "python",
            "scripts/generate_architecture_index.py",
            "--check",
            *(["--require-complete"] if args.strict else []),
        ],
        ["python", "scripts/generate_container_inventory.py", "--check"],
    ]

    rc = 0
    for cmd in checks:
        if run(cmd) != 0:
            rc = 1

    if not INDEX_PATH.exists():
        print(f"FEHLER: {INDEX_PATH} fehlt", file=sys.stderr)
        return 1

    index = load_yaml(INDEX_PATH)
    errors = check_unmapped_domains(index, strict=args.strict)
    errors.extend(check_dsl_containers(index))

    stats = index.get("mapping_stats", {})
    if stats and args.strict:
        print(
            f"Mapping: routes {stats.get('frontend_routes_mapped')}/{stats.get('frontend_routes_total')}, "
            f"services {stats.get('backend_services_mapped')}/{stats.get('backend_services_total')}, "
            f"endpoints {stats.get('backend_endpoints_mapped')}/{stats.get('backend_endpoints_total')}"
        )

    for err in errors:
        print(f"FEHLER: {err}", file=sys.stderr)
        rc = 1

    if rc == 0:
        print("Architecture drift check: OK")
    else:
        print("Architecture drift check: FEHLGESCHLAGEN", file=sys.stderr)
    return rc


if __name__ == "__main__":
    sys.exit(main())
