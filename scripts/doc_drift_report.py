#!/usr/bin/env python3
"""AI-DOC-DRIFT-DASHBOARD-001 — Doku-Code-Drift-Report.

Prueft:
1. API-Endpoint-Module ohne Erwaehnung in docs/
2. Alembic-Migrationen ohne Erwaehnung in docs/
3. Services ohne Erwaehnung in docs/
4. Frontend-Seiten ohne Route (route-inventory) und ohne Nav-Treffer (Heuristik)

Ausgabe: JSON-Report in artifacts/doc_drift_report.json + Markdown-Summary auf stdout.
CI: .github/workflows/doc-drift-report.yml (informativ, nicht blockierend).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = REPO_ROOT / "artifacts"
DOCS_DIR = REPO_ROOT / "docs"
ALEMBIC_DIR = REPO_ROOT / "alembic" / "versions"
ENDPOINTS_DIR = REPO_ROOT / "app" / "api" / "v1" / "endpoints"
SERVICES_DIR = REPO_ROOT / "app" / "services"
PAGES_DIR = REPO_ROOT / "packages" / "frontend-web" / "src" / "pages"
NAV_DOMAINS_DIR = REPO_ROOT / "packages" / "frontend-web" / "src" / "app" / "navigation" / "domains"
ROUTE_INVENTORY = (
    REPO_ROOT / "packages" / "frontend-web" / "src" / "app" / "routing" / "route-inventory.gen.json"
)

SKIP_ENDPOINTS = frozenset({"__init__", "health", "deps"})
SKIP_PAGE_NAMES = frozenset({"not-found", "error", "layout"})


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def _all_docs_text() -> str:
    texts = []
    for p in DOCS_DIR.rglob("*.md"):
        texts.append(p.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(texts)


def _nav_text() -> str:
    parts = []
    if NAV_DOMAINS_DIR.exists():
        for nav_file in sorted(NAV_DOMAINS_DIR.glob("*.tsx")):
            parts.append(_read(nav_file))
    return "\n".join(parts)


def _route_inventory() -> tuple[set[str], set[str]]:
    if not ROUTE_INVENTORY.exists():
        return set(), set()
    data = json.loads(ROUTE_INVENTORY.read_text(encoding="utf-8"))
    modules: set[str] = set()
    paths: set[str] = set()
    for route in data.get("routes", []):
        module = route.get("module")
        path = route.get("path")
        if module:
            modules.add(module)
        if path is not None:
            paths.add(str(path))
    return modules, paths


def page_to_module(page: Path) -> str:
    rel = page.relative_to(PAGES_DIR).with_suffix("").as_posix()
    return f"@/pages/{rel}"


def check_endpoints_without_docs(docs_text: str) -> list[dict]:
    issues = []
    if not ENDPOINTS_DIR.exists():
        return issues
    for f in sorted(ENDPOINTS_DIR.glob("*.py")):
        stem = f.stem
        if stem in SKIP_ENDPOINTS:
            continue
        if stem not in docs_text:
            issues.append({"type": "endpoint_no_doc", "file": str(f.relative_to(REPO_ROOT)), "stem": stem})
    return issues


def check_migrations_without_runbook(docs_text: str) -> list[dict]:
    issues = []
    if not ALEMBIC_DIR.exists():
        return issues
    for f in sorted(ALEMBIC_DIR.glob("*.py")):
        stem = f.stem
        if stem in ("__init__", "env"):
            continue
        if stem not in docs_text:
            issues.append({"type": "migration_no_runbook", "file": str(f.relative_to(REPO_ROOT)), "stem": stem})
    return issues


def check_services_without_docs(docs_text: str) -> list[dict]:
    issues = []
    if not SERVICES_DIR.exists():
        return issues
    for f in sorted(SERVICES_DIR.glob("*.py")):
        stem = f.stem
        if stem.startswith("__"):
            continue
        if stem not in docs_text:
            issues.append({"type": "service_no_doc", "file": str(f.relative_to(REPO_ROOT)), "stem": stem})
    return issues


def check_pages_without_route_or_nav(
    nav_text: str,
    route_modules: set[str],
    route_paths: set[str],
) -> list[dict]:
    issues = []
    if not PAGES_DIR.exists():
        return issues
    for f in sorted(PAGES_DIR.rglob("*.tsx")):
        name = f.stem
        if name.startswith("_") or name in SKIP_PAGE_NAMES:
            continue
        module = page_to_module(f)
        if module in route_modules:
            continue
        rel = str(f.relative_to(PAGES_DIR)).replace("\\", "/").removesuffix(".tsx")
        path_hint = rel.replace("/index", "") if rel.endswith("/index") else rel
        if path_hint in route_paths or path_hint in nav_text or name in nav_text:
            continue
        issues.append(
            {
                "type": "page_no_route_or_nav",
                "file": str(f.relative_to(REPO_ROOT)),
                "path_hint": path_hint,
                "module": module,
            }
        )
    return issues


def build_report() -> dict:
    docs_text = _all_docs_text()
    nav_text = _nav_text()
    route_modules, route_paths = _route_inventory()

    endpoint_issues = check_endpoints_without_docs(docs_text)
    migration_issues = check_migrations_without_runbook(docs_text)
    service_issues = check_services_without_docs(docs_text)
    page_issues = check_pages_without_route_or_nav(nav_text, route_modules, route_paths)

    all_issues = endpoint_issues + migration_issues + service_issues + page_issues

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(REPO_ROOT),
        "summary": {
            "total_drift_items": len(all_issues),
            "endpoint_no_doc": len(endpoint_issues),
            "migration_no_runbook": len(migration_issues),
            "service_no_doc": len(service_issues),
            "page_no_route_or_nav": len(page_issues),
        },
        "issues": all_issues,
    }


def print_markdown_summary(report: dict) -> None:
    s = report["summary"]
    print(f"# Doku-Code-Drift-Report — {report['generated_at'][:10]}")
    print()
    print("| Kategorie | Anzahl |")
    print("|---|---|")
    print(f"| Endpoints ohne Doku | {s['endpoint_no_doc']} |")
    print(f"| Migrationen ohne Runbook | {s['migration_no_runbook']} |")
    print(f"| Services ohne Doku | {s['service_no_doc']} |")
    print(f"| Frontend-Seiten ohne Route/Nav | {s['page_no_route_or_nav']} |")
    print(f"| **Gesamt** | **{s['total_drift_items']}** |")
    print()
    if s["total_drift_items"] == 0:
        print("Kein Drift erkannt.")
    else:
        print("## Details (Auszug)")
        for issue in report["issues"][:30]:
            print(f"- [{issue['type']}] {issue.get('file', issue.get('stem', '?'))}")
        if len(report["issues"]) > 30:
            print(f"  … und {len(report['issues']) - 30} weitere.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Doku-Code-Drift-Report")
    parser.add_argument(
        "--fail-over",
        type=int,
        default=None,
        help="Exit 1 wenn total_drift_items diesen Wert uebersteigt (optional, CI-Hard-Gate).",
    )
    args = parser.parse_args()

    report = build_report()

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    out = ARTIFACTS_DIR / "doc_drift_report.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print_markdown_summary(report)
    print(f"\nReport gespeichert: {out}")

    if args.fail_over is not None and report["summary"]["total_drift_items"] > args.fail_over:
        print(
            f"\nFEHLER: Drift {report['summary']['total_drift_items']} > Schwellwert {args.fail_over}.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
