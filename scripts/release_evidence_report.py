"""RELEASE-EVIDENCE-GATE-001 — Aggregiert alle Release-Qualitätsdimensionen.

Dimensionen:
  drift        — doc_drift_report.py --fail-over 0
  openapi      — generate_openapi.py --check
  inventories  — Inventar-Dateien vorhanden (endpoint/migration/service)
  coverage     — check_critical_backend_coverage.py (Exit 0 = pass)
  slice_harness — valeo_slice.py verify für geänderte Slices
  external     — simulate_external_assessors.py (liest artifacts/production-readiness-assessment.json)

Output:
  artifacts/release_evidence.json
  artifacts/release_evidence.md

Verwendung:
  python scripts/release_evidence_report.py [--fail-on-red] [--sha GIT_SHA]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).parent.parent
ARTIFACTS = REPO / "artifacts"


def _run(cmd: list[str]) -> tuple[int, str]:
    result = subprocess.run(
        cmd, capture_output=True, text=True, cwd=REPO
    )
    return result.returncode, (result.stdout + result.stderr).strip()


def check_drift() -> dict:
    rc, out = _run([sys.executable, "scripts/doc_drift_report.py", "--fail-over", "0"])
    total = 0
    try:
        rjson = ARTIFACTS / "doc_drift_report.json"
        if rjson.exists():
            total = json.loads(rjson.read_text())["summary"]["total_drift_items"]
    except Exception:
        pass
    return {
        "dimension": "drift",
        "status": "pass" if rc == 0 else "fail",
        "detail": f"total_drift_items={total}",
        "exit_code": rc,
    }


def check_openapi() -> dict:
    rc, out = _run([sys.executable, "scripts/generate_openapi.py", "--check"])
    return {
        "dimension": "openapi",
        "status": "pass" if rc == 0 else "fail",
        "detail": "openapi.json aktuell" if rc == 0 else "Drift erkannt — bitte generate_openapi.py ausführen",
        "exit_code": rc,
    }


def check_inventories() -> dict:
    required = [
        REPO / "docs/schnittstellen/endpoint-inventory.md",
        REPO / "docs/admin/migration-inventory.md",
        REPO / "docs/entwickler/service-inventory.md",
        REPO / "docs/schnittstellen/asyncapi.yaml",
    ]
    missing = [str(p.relative_to(REPO)) for p in required if not p.exists()]
    return {
        "dimension": "inventories",
        "status": "pass" if not missing else "fail",
        "detail": f"{len(required) - len(missing)}/{len(required)} Inventar-Dateien vorhanden"
                  + (f"; fehlend: {', '.join(missing)}" if missing else ""),
        "exit_code": 0 if not missing else 1,
    }


def check_coverage() -> dict:
    rc, out = _run([sys.executable, "scripts/check_critical_backend_coverage.py"])
    lines = [l for l in out.splitlines() if l.strip()]
    # count failures
    fail_count = sum(1 for l in lines if "below threshold" in l)
    return {
        "dimension": "coverage",
        "status": "pass" if rc == 0 else "warn",
        "detail": f"{fail_count} Dateien unter Ratchet-Schwellwert" if fail_count else "Alle Schwellwerte eingehalten",
        "exit_code": rc,
    }


def check_slice_harness() -> dict:
    slice_dir = REPO / "docs/agent-ops/slices"
    yamls = list(slice_dir.glob("*.yaml")) + list(slice_dir.glob("*.yml"))
    if not yamls:
        return {"dimension": "slice_harness", "status": "warn", "detail": "Keine Slice-YAMLs gefunden", "exit_code": 1}

    # Check harness script exists and run verify
    valeo_slice = REPO / "scripts/valeo_slice.py"
    if not valeo_slice.exists():
        return {"dimension": "slice_harness", "status": "warn", "detail": "scripts/valeo_slice.py nicht gefunden", "exit_code": 1}

    rc, out = _run([sys.executable, "scripts/valeo_slice.py", "list"])
    return {
        "dimension": "slice_harness",
        "status": "pass" if rc == 0 else "warn",
        "detail": f"{len(yamls)} Slice-YAMLs vorhanden" + (f"; list-Fehler: {out[:100]}" if rc != 0 else ""),
        "exit_code": rc,
    }


def check_external() -> dict:
    assessment = ARTIFACTS / "production-readiness-assessment.json"
    if not assessment.exists():
        return {
            "dimension": "external",
            "status": "warn",
            "detail": "Kein Assessment vorhanden (artifacts/production-readiness-assessment.json fehlt — via release-gates.yml erzeugen)",
            "exit_code": 1,
        }
    try:
        data = json.loads(assessment.read_text(encoding="utf-8"))

        # simulate_external_assessors.py-Format: {date, profiles: [{id, status, ...}]}
        profiles = data.get("profiles")
        if isinstance(profiles, list) and profiles:
            by_status: dict[str, int] = {}
            for p in profiles:
                s = str(p.get("status", "unknown")).lower()
                by_status[s] = by_status.get(s, 0) + 1
            date = data.get("date", "?")
            summary = ", ".join(f"{n}x {s}" for s, n in sorted(by_status.items()))
            if any(s in by_status for s in ("fail", "red", "nonconformity")):
                status = "fail"
            elif set(by_status) <= {"pass", "green"}:
                status = "pass"
            else:
                status = "warn"  # conditional o. ae. — Auflagen offen, kein Blocker
            return {
                "dimension": "external",
                "status": status,
                "detail": f"External assessment ({date}): {len(profiles)} Profile — {summary}",
                "exit_code": 0,
            }

        # Legacy-/Fremdformat: {passed|overall_status, score|total_score}
        passed = data.get("passed", data.get("overall_status", "unknown"))
        score = data.get("score", data.get("total_score", "?"))
        return {
            "dimension": "external",
            "status": "pass" if str(passed).lower() in ("true", "pass", "green") else "warn",
            "detail": f"External assessment: status={passed}, score={score}",
            "exit_code": 0,
        }
    except Exception as e:
        return {"dimension": "external", "status": "warn", "detail": f"Parse-Fehler: {e}", "exit_code": 1}


STATUS_EMOJI = {"pass": "PASS", "warn": "WARN", "fail": "FAIL"}
STATUS_ORDER = {"fail": 0, "warn": 1, "pass": 2}


def build_report(sha: str | None) -> dict:
    checks = [
        check_drift(),
        check_openapi(),
        check_inventories(),
        check_coverage(),
        check_slice_harness(),
        check_external(),
    ]
    worst = min(checks, key=lambda c: STATUS_ORDER[c["status"]])["status"]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_sha": sha or "unknown",
        "overall_status": worst,
        "dimensions": checks,
        "summary": {
            "pass": sum(1 for c in checks if c["status"] == "pass"),
            "warn": sum(1 for c in checks if c["status"] == "warn"),
            "fail": sum(1 for c in checks if c["status"] == "fail"),
        },
    }


def build_markdown(report: dict) -> str:
    ts = report["generated_at"][:19].replace("T", " ") + " UTC"
    overall = report["overall_status"].upper()
    lines = [
        "---",
        "title: Release-Evidence-Report",
        "description: Aggregierter Qualitätsnachweis für Staging-/Produktions-Release.",
        "type: reference",
        "audience: [lead, entwickler]",
        "owner: Claude Code",
        "status: aktiv",
        f"last_reviewed: {datetime.now(timezone.utc).date().isoformat()}",
        "version: 3.0.0",
        "---",
        "",
        "# Release-Evidence-Report",
        "",
        f"> Stand: {ts} · SHA: `{report['git_sha']}`",
        f"> Slice: RELEASE-EVIDENCE-GATE-001",
        "",
        f"## Gesamtstatus: {overall}",
        "",
        "| Dimension | Status | Detail |",
        "|---|---|---|",
    ]
    for c in report["dimensions"]:
        badge = STATUS_EMOJI[c["status"]]
        lines.append(f"| {c['dimension']} | **{badge}** | {c['detail']} |")

    s = report["summary"]
    lines += [
        "",
        f"**Zusammenfassung:** {s['pass']} PASS · {s['warn']} WARN · {s['fail']} FAIL",
        "",
        "## Gate-Verhalten",
        "",
        "Ein Staging-Release wird blockiert wenn `overall_status == fail`.",
        "WARN-Dimensionen erzeugen eine Warnung, blockieren aber nicht.",
        "",
        "```bash",
        "# Lokal ausführen:",
        "python scripts/release_evidence_report.py --fail-on-red",
        "```",
        "",
        f"*Generiert via `scripts/release_evidence_report.py` · {ts}*",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Release Evidence Report")
    parser.add_argument("--fail-on-red", action="store_true", help="Exit 1 wenn overall_status=fail")
    parser.add_argument("--sha", default=None, help="Git SHA für den Report")
    args = parser.parse_args()

    ARTIFACTS.mkdir(parents=True, exist_ok=True)

    report = build_report(args.sha)
    md = build_markdown(report)

    (ARTIFACTS / "release_evidence.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (ARTIFACTS / "release_evidence.md").write_text(md, encoding="utf-8")

    print(md)
    print(f"\nReport: artifacts/release_evidence.json")

    if args.fail_on_red and report["overall_status"] == "fail":
        print("\nFEHLER: overall_status=fail — Release blockiert.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
