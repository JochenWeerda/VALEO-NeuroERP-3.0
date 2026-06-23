#!/usr/bin/env python3
"""AI-DOC-DRIFT-DASHBOARD-001 — Doku-Code-Drift-Report.

Prueft:
1. Neue API-Routen (app/api/v1/endpoints/*.py) ohne Eintrag in open-gaps-and-known-issues.md
2. Neue Alembic-Migrationen ohne Runbook-Erwaehnung in docs/
3. Neue Services (app/services/*.py) ohne Erwahnung in docs/
4. Frontend-Seiten (src/pages/**/*.tsx) ohne Nav-Eintrag (Heuristik)

Ausgabe: JSON-Report in artifacts/doc_drift_report.json + Markdown-Summary auf stdout.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = REPO_ROOT / "artifacts"
DOCS_DIR = REPO_ROOT / "docs"
OPEN_GAPS_FILE = REPO_ROOT / "docs" / "project-context" / "open-gaps-and-known-issues.md"
ALEMBIC_DIR = REPO_ROOT / "alembic" / "versions"
ENDPOINTS_DIR = REPO_ROOT / "app" / "api" / "v1" / "endpoints"
SERVICES_DIR = REPO_ROOT / "app" / "services"
PAGES_DIR = REPO_ROOT / "packages" / "frontend-web" / "src" / "pages"
NAV_OPS = REPO_ROOT / "packages" / "frontend-web" / "src" / "app" / "navigation" / "domains" / "operations.tsx"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def _all_docs_text() -> str:
    texts = []
    for p in DOCS_DIR.rglob("*.md"):
        texts.append(p.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(texts)


def check_endpoints_without_docs(docs_text: str) -> list[dict]:
    issues = []
    if not ENDPOINTS_DIR.exists():
        return issues
    for f in sorted(ENDPOINTS_DIR.glob("*.py")):
        stem = f.stem
        if stem in ("__init__", "health", "deps"):
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


def check_pages_without_nav(nav_text: str) -> list[dict]:
    issues = []
    if not PAGES_DIR.exists():
        return issues
    for f in sorted(PAGES_DIR.rglob("*.tsx")):
        name = f.stem
        if name.startswith("_") or name in ("index", "not-found", "error"):
            continue
        rel = str(f.relative_to(PAGES_DIR)).replace("\\", "/")
        path_hint = rel.removesuffix(".tsx").replace("/", "/")
        if path_hint not in nav_text and name not in nav_text:
            issues.append({"type": "page_no_nav", "file": str(f.relative_to(REPO_ROOT)), "path_hint": path_hint})
    return issues


def build_report() -> dict:
    docs_text = _all_docs_text()
    nav_text = _read(NAV_OPS)

    endpoint_issues = check_endpoints_without_docs(docs_text)
    migration_issues = check_migrations_without_runbook(docs_text)
    service_issues = check_services_without_docs(docs_text)
    page_issues = check_pages_without_nav(nav_text)

    all_issues = endpoint_issues + migration_issues + service_issues + page_issues

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(REPO_ROOT),
        "summary": {
            "total_drift_items": len(all_issues),
            "endpoint_no_doc": len(endpoint_issues),
            "migration_no_runbook": len(migration_issues),
            "service_no_doc": len(service_issues),
            "page_no_nav": len(page_issues),
        },
        "issues": all_issues,
    }


def print_markdown_summary(report: dict) -> None:
    s = report["summary"]
    print(f"# Doku-Code-Drift-Report — {report['generated_at'][:10]}")
    print()
    print(f"| Kategorie | Anzahl |")
    print(f"|---|---|")
    print(f"| Endpoints ohne Doku | {s['endpoint_no_doc']} |")
    print(f"| Migrationen ohne Runbook | {s['migration_no_runbook']} |")
    print(f"| Services ohne Doku | {s['service_no_doc']} |")
    print(f"| Frontend-Seiten ohne Nav | {s['page_no_nav']} |")
    print(f"| **Gesamt** | **{s['total_drift_items']}** |")
    print()
    if s["total_drift_items"] == 0:
        print("✓ Kein Drift erkannt.")
    else:
        print("## Details")
        for issue in report["issues"][:30]:
            print(f"- [{issue['type']}] {issue.get('file', issue.get('stem', '?'))}")
        if len(report["issues"]) > 30:
            print(f"  … und {len(report['issues']) - 30} weitere.")


def main() -> int:
    report = build_report()

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    out = ARTIFACTS_DIR / "doc_drift_report.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print_markdown_summary(report)
    print(f"\nReport gespeichert: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
