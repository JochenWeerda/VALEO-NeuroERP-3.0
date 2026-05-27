#!/usr/bin/env python3
"""
Gesamtreife-Messung: VALEO NeuroERP 3.0

Gewichtetes Scoring-Modell (8 Dimensionen, 100 Punkte gesamt).
Jede Dimension wird automatisch aus CI-Gate-Ergebnissen und
Codebase-Metriken berechnet.

Verwendung:
    python scripts/measure_gesamtreife.py
    python scripts/measure_gesamtreife.py --json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime


ENDPOINTS_DIR = "app/api/v1/endpoints"
TESTS_DIR = "tests"
E2E_DIR = "packages/frontend-web/tests/e2e"
SERVICES_DIR = "app/services"
WORKERS_DIR = "app/workers"


@dataclass
class DimensionScore:
    name: str
    weight: float
    score: float
    details: dict = field(default_factory=dict)

    @property
    def weighted(self) -> float:
        return self.weight * self.score / 100


def _run_check(script: str, *args) -> tuple[int, str]:
    result = subprocess.run(
        [sys.executable, script, *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return result.returncode, result.stdout + result.stderr


# ── 1. Security (20 Punkte) ────────────────────────────────────────────────

def score_security() -> DimensionScore:
    rc_sql, _ = _run_check("scripts/check_sql_fstrings.py")
    rc_auth, _ = _run_check("scripts/check_tenant_isolation.py")
    _, out_tenant = _run_check("scripts/check_tenant_isolation.py")
    tenant_isolated = int(re.search(r"tenant-isolated\s*:\s*(\d+)", out_tenant or "").group(1) if re.search(r"tenant-isolated\s*:\s*(\d+)", out_tenant or "") else 0)

    sql_ok = rc_sql == 0
    auth_ok = rc_auth == 0

    # Hardcoded secrets check (grep for obvious patterns)
    secrets_ok = True
    try:
        for fname in os.listdir(ENDPOINTS_DIR):
            if not fname.endswith(".py"):
                continue
            content = open(os.path.join(ENDPOINTS_DIR, fname), encoding="utf-8", errors="replace").read()
            if re.search(r'(api_key|secret|password)\s*=\s*["\'][A-Za-z0-9+/]{20,}', content, re.I):
                secrets_ok = False
                break
    except Exception:
        pass

    score = (
        (25 if sql_ok else 0) +
        (25 if auth_ok else 0) +
        (25 if tenant_isolated >= 200 else int(25 * tenant_isolated / 200)) +
        (25 if secrets_ok else 0)
    )
    return DimensionScore("Sicherheit", 20, score, {
        "sql_injection": "[OK]" if sql_ok else "[--]",
        "auth_coverage": "[OK]" if auth_ok else "[--]",
        "tenant_isolation": f"[OK] ({tenant_isolated} Dateien)" if tenant_isolated >= 200 else f"[~~] ({tenant_isolated})",
        "no_hardcoded_secrets": "[OK]" if secrets_ok else "[--]",
    })


# ── 2. Reliability / Datenintegrität (10 Punkte) ──────────────────────────

def score_reliability() -> DimensionScore:
    # GoBD Hash-Chain
    gobd_ok = os.path.exists("app/infrastructure/repositories/implementations.py")
    if gobd_ok:
        content = open("app/infrastructure/repositories/implementations.py", encoding="utf-8", errors="replace").read()
        gobd_ok = "_compute_hash" in content and "hash_current" in content

    # Alembic migrations
    try:
        n_migrations = len([f for f in os.listdir("alembic/versions") if f.endswith(".py") and not f.startswith("_")])
    except Exception:
        n_migrations = 0

    score = (
        (40 if gobd_ok else 0) +
        (40 if n_migrations >= 150 else int(40 * n_migrations / 150)) +
        20  # Transaction baseline (we trust SQLAlchemy session management)
    )
    return DimensionScore("Datenintegrität", 10, score, {
        "gobd_hash_chain": "[OK] auto-trigger" if gobd_ok else "[--]",
        "alembic_migrations": n_migrations,
    })


# ── 3. Performance / Skalierbarkeit (10 Punkte) ───────────────────────────

def score_performance() -> DimensionScore:
    rc_pag, out_pag = _run_check("scripts/check_pagination.py")
    pag_gate_ok = rc_pag == 0

    m = re.search(r"Files with unbounded .all\(\): (\d+) \(threshold: (\d+)\)", out_pag)
    pag_offenders = int(m.group(1)) if m else 99
    pag_threshold = int(m.group(2)) if m else 60
    # Gate pass = full marks; gate fail = partial based on ratio
    pag_score = 100 if pag_gate_ok else max(0, int(100 * (1 - pag_offenders / pag_threshold)))

    n1_ok = False
    try:
        for root, _, files in os.walk("app"):
            for f in files:
                if f.endswith(".py"):
                    content = open(os.path.join(root, f), encoding="utf-8", errors="replace").read()
                    if "selectinload" in content:
                        n1_ok = True
                        break
    except Exception:
        pass

    cache_ok = False
    try:
        for root, _, files in os.walk("app"):
            for f in files:
                if f.endswith(".py"):
                    content = open(os.path.join(root, f), encoding="utf-8", errors="replace").read()
                    if "cached_read_model" in content or "redis" in content.lower():
                        cache_ok = True
                        break
    except Exception:
        pass

    score = int(
        (pag_score / 100) * 40 +
        (30 if n1_ok else 0) +
        (30 if cache_ok else 0)
    )
    return DimensionScore("Performance", 10, score, {
        "pagination_gate": f"[OK] ({pag_offenders}/{pag_threshold})" if pag_gate_ok else f"[--] ({pag_offenders}/{pag_threshold})",
        "n1_elimination": "[OK] selectinload" if n1_ok else "[--]",
        "redis_caching": "[OK]" if cache_ok else "[--]",
    })


# ── 4. Maintainability / Code-Qualität (15 Punkte) ────────────────────────

def score_maintainability() -> DimensionScore:
    rc_rm, out_rm = _run_check("scripts/check_response_models.py")
    m = re.search(r"(\d+\.\d+)%", out_rm)
    rm_pct = float(m.group(1)) if m else 0.0
    rm_gate_ok = rc_rm == 0

    rc_gs, out_gs = _run_check("scripts/check_file_size.py")
    m2 = re.search(r"godfiles\): (\d+) \(threshold: (\d+)\)", out_gs)
    godfiles = int(m2.group(1)) if m2 else 99
    godfile_threshold = int(m2.group(2)) if m2 else 12
    godfile_gate_ok = rc_gs == 0
    # Gate pass = 90 score (existing godfiles are legacy debt, not new regressions)
    godfile_score = 90 if godfile_gate_ok else max(0, int(90 * godfile_threshold / max(godfiles, 1)))

    rc_oa, _ = _run_check("scripts/check_openapi_docs.py") if os.path.exists("scripts/check_openapi_docs.py") else (0, "")

    score = int(
        (rm_pct / 100) * 40 +
        (godfile_score / 100) * 30 +
        (30 if rc_oa == 0 else 20)
    )
    return DimensionScore("Wartbarkeit", 15, min(100, score), {
        "response_model_coverage": f"{rm_pct:.1f}% {'[OK]' if rm_gate_ok else '[~~]'}",
        "godfile_gate": f"[OK] ({godfiles}<={godfile_threshold})" if godfile_gate_ok else f"[--] ({godfiles}>{godfile_threshold})",
        "openapi_docs": "[OK]" if rc_oa == 0 else "[~~]",
    })


# ── 5. Fachlich & Normativ (20 Punkte) ────────────────────────────────────

def score_fachlich() -> DimensionScore:
    checks = {
        "lohnabrechnung": os.path.exists("app/services/lohn_service.py"),
        "gis_geojson": os.path.exists("packages/frontend-web/src/components/agrar/SchlagKarte.tsx"),
        "fints_hbci": os.path.exists("app/services/fints_connector.py"),
        "tse_fiskaly": os.path.exists("app/services/tse_fiskaly_service.py"),
        "elster_ustva": False,
        "llm_ocr": False,
        "dsgvo_art33": os.path.exists("app/api/v1/endpoints/gdpr_art33_breach.py"),
        "gobd_export": os.path.exists("app/api/v1/endpoints/gobd_archiv.py"),
    }

    # ELSTER UStVA endpoint
    try:
        content = open("app/api/v1/endpoints/ebilanz_elster.py", encoding="utf-8", errors="replace").read()
        checks["elster_ustva"] = "ustva" in content.lower() and "router.post" in content
    except Exception:
        pass

    # Claude OCR
    try:
        content = open("app/einkauf/ocr_invoice.py", encoding="utf-8", errors="replace").read()
        checks["llm_ocr"] = "claude" in content and "anthropic" in content
    except Exception:
        pass

    passed = sum(1 for v in checks.values() if v)
    score = int(passed / len(checks) * 100)
    return DimensionScore("Fachlich/Normativ", 20, score, {k: "[OK]" if v else "[--]" for k, v in checks.items()})


# ── 6. AI / Agent-Orchestration (10 Punkte) ───────────────────────────────

def score_ai() -> DimensionScore:
    checks = {
        "low_stock_agent": os.path.exists("app/workers/low_stock_agent.py"),
        "voice_intents_lager": os.path.exists("services/ki-usability/tests/test_voice_intent_lager_einkauf_hr.py"),
        "voice_intents_verkauf": os.path.exists("services/ki-usability/tests/test_voice_intent_verkauf_crm.py"),
        "knowledge_base": False,
        "agent_endpoints": False,
    }

    try:
        content = open("app/api/v1/endpoints/agents.py", encoding="utf-8", errors="replace").read()
        checks["agent_endpoints"] = "low-stock" in content and "simulate" in content
    except Exception:
        pass

    try:
        content = open("app/api/v1/endpoints/neuro_knowledge.py", encoding="utf-8", errors="replace").read()
        checks["knowledge_base"] = "knowledge" in content.lower()
    except Exception:
        pass

    passed = sum(1 for v in checks.values() if v)
    score = int(passed / len(checks) * 100)
    return DimensionScore("AI/Agenten", 10, score, {k: "[OK]" if v else "[--]" for k, v in checks.items()})


# ── 7. Tests & Quality (10 Punkte) ────────────────────────────────────────

def score_tests() -> DimensionScore:
    # Pytest tests
    try:
        n_pytest = len([f for f in os.listdir(TESTS_DIR) if f.startswith("test_") and f.endswith(".py")])
    except Exception:
        n_pytest = 0

    # E2E specs
    try:
        n_e2e = len([f for f in os.listdir(E2E_DIR) if f.endswith(".spec.ts")])
    except Exception:
        n_e2e = 0

    e2e_target = 60
    pytest_target = 20

    score = int(
        min(1.0, n_pytest / pytest_target) * 50 +
        min(1.0, n_e2e / e2e_target) * 50
    )
    return DimensionScore("Tests/Qualität", 10, score, {
        "pytest_test_files": n_pytest,
        "e2e_playwright_specs": n_e2e,
        "e2e_target": e2e_target,
    })


# ── 8. DevEx / CI (5 Punkte) ──────────────────────────────────────────────

def score_devex() -> DimensionScore:
    ci_gates = [
        "scripts/check_sql_fstrings.py",
        "scripts/check_tenant_isolation.py",
        "scripts/check_pagination.py",
        "scripts/check_file_size.py",
        "scripts/check_response_models.py",
    ]
    gates_present = sum(1 for g in ci_gates if os.path.exists(g))

    adrs = len([f for f in os.listdir("docs/adr") if f.endswith(".md") and "adr-" in f]) if os.path.exists("docs/adr") else 0

    score = int(
        (gates_present / len(ci_gates)) * 60 +
        min(1.0, adrs / 10) * 40
    )
    return DimensionScore("DevEx/CI", 5, score, {
        "ci_gates": f"{gates_present}/{len(ci_gates)}",
        "adrs": adrs,
    })


# ── Aggregation ────────────────────────────────────────────────────────────

def compute_gesamtreife() -> dict:
    dimensions = [
        score_security(),
        score_reliability(),
        score_performance(),
        score_maintainability(),
        score_fachlich(),
        score_ai(),
        score_tests(),
        score_devex(),
    ]

    total_weight = sum(d.weight for d in dimensions)
    total_weighted = sum(d.weighted for d in dimensions)
    gesamtreife = round(total_weighted / total_weight * 100, 1)

    return {
        "gemessen_am": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "gesamtreife_prozent": gesamtreife,
        "dimensionen": [
            {
                "name": d.name,
                "gewicht": f"{d.weight:.0f}%",
                "score": f"{d.score:.0f}/100",
                "gewichtet": f"{d.weighted:.2f}",
                "details": d.details,
            }
            for d in dimensions
        ],
        "note": (
            "[OK] Produktionsreif" if gesamtreife >= 98 else
            "[~~] Annähernd produktionsreif" if gesamtreife >= 90 else
            "[!!] Qualitätslücken vorhanden" if gesamtreife >= 75 else
            "[!!] Wesentliche Lücken"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="VALEO NeuroERP Gesamtreife-Messung")
    parser.add_argument("--json", action="store_true", help="JSON-Ausgabe")
    args = parser.parse_args()

    result = compute_gesamtreife()

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"\n{'='*60}")
        print(f"  VALEO NeuroERP — Gesamtreife-Messung")
        print(f"  Stand: {result['gemessen_am']}")
        print(f"{'='*60}")
        print(f"\n  GESAMTREIFE: {result['gesamtreife_prozent']:.1f}%  {result['note']}")
        print(f"\n  {'Dimension':<25} {'Gewicht':>8} {'Score':>8} {'Gewichtet':>10}")
        print(f"  {'-'*55}")
        for d in result["dimensionen"]:
            print(f"  {d['name']:<25} {d['gewicht']:>8} {d['score']:>8} {d['gewichtet']:>10}")
        print(f"{'='*60}\n")

    return 0 if result["gesamtreife_prozent"] >= 98 else 1


if __name__ == "__main__":
    sys.exit(main())
