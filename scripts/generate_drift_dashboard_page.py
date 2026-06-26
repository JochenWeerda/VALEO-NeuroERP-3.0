"""DOC-DRIFT-DASHBOARD-002 — Erzeugt docs/entwickler/drift-dashboard.md aus doc_drift_report.json.

Verwendung:
    python scripts/generate_drift_dashboard_page.py [--report PATH]

Liest artifacts/doc_drift_report.json (erzeugt von scripts/doc_drift_report.py).
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).parent.parent
DEFAULT_REPORT = REPO / "artifacts" / "doc_drift_report.json"
OUTPUT = REPO / "docs" / "entwickler" / "drift-dashboard.md"


def status_badge(count: int) -> str:
    if count == 0:
        return "gruen"
    if count <= 5:
        return "gelb"
    return "rot"


def load_report(report_path: Path) -> dict:
    if not report_path.exists():
        print(f"Report nicht gefunden: {report_path}", file=sys.stderr)
        print("Bitte zuerst ausführen: python scripts/doc_drift_report.py", file=sys.stderr)
        sys.exit(1)
    return json.loads(report_path.read_text(encoding="utf-8"))


def format_timestamp(iso: str) -> str:
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return iso


def build_page(report: dict) -> str:
    summary = report.get("summary", {})
    issues = report.get("issues", [])
    generated_at = format_timestamp(report.get("generated_at", "unbekannt"))
    total = summary.get("total_drift_items", 0)
    badge = status_badge(total)

    lines = [
        "---",
        "title: Doku-Code-Drift-Dashboard",
        "description: Aktueller Status des Doku-Code-Drift-Reports (DOC-DRIFT-GATE-002).",
        "type: reference",
        "audience: [entwickler, lead]",
        "owner: Claude Code",
        "status: aktiv",
        f"last_reviewed: {datetime.now(timezone.utc).date().isoformat()}",
        "version: 3.0.0",
        "---",
        "",
        "# Doku-Code-Drift-Dashboard",
        "",
        "> Generiert via `scripts/generate_drift_dashboard_page.py`",
        "> Quelle: `artifacts/doc_drift_report.json` · `scripts/doc_drift_report.py`",
        "",
        "## Status",
        "",
        f"| Metrik | Wert |",
        "|---|---|",
        f"| Gesamter Drift | **{total}** |",
        f"| Status | **{badge.upper()}** |",
        f"| Stand | {generated_at} |",
        f"| Gate | `--fail-over 0` (DOC-DRIFT-GATE-002) |",
        "",
    ]

    # Dimension breakdown
    dim_map = [
        ("endpoint_no_doc",       "Endpoints ohne Doku"),
        ("migration_no_runbook",  "Migrationen ohne Runbook"),
        ("service_no_doc",        "Services ohne Doku"),
        ("page_no_route_or_nav",  "Frontend-Seiten ohne Route/Nav"),
    ]
    lines += [
        "## Dimensionen",
        "",
        "| Dimension | Anzahl | Status |",
        "|---|---|---|",
    ]
    for key, label in dim_map:
        count = summary.get(key, 0)
        dim_badge = status_badge(count)
        lines.append(f"| {label} | {count} | {dim_badge.upper()} |")
    lines.append("")

    # Issues list
    if issues:
        lines += [
            "## Offene Punkte",
            "",
            "| Typ | Datei/Stem |",
            "|---|---|",
        ]
        for issue in issues[:50]:
            typ = issue.get("type", "?")
            item = issue.get("file", issue.get("stem", "?"))
            lines.append(f"| `{typ}` | `{item}` |")
        if len(issues) > 50:
            lines.append(f"| … | +{len(issues) - 50} weitere (siehe report JSON) |")
        lines.append("")
    else:
        lines += [
            "## Offene Punkte",
            "",
            "Kein Drift erkannt — Gate ist grün.",
            "",
        ]

    lines += [
        "## Gate-Verhalten",
        "",
        "Der Drift-Gate-Step in `quality-gate.yml` bricht den Build wenn `total_drift_items > 0`:",
        "",
        "```bash",
        "python scripts/doc_drift_report.py --fail-over 0",
        "```",
        "",
        "Bei neuem Drift sofort beheben:",
        "",
        "1. Endpoint/Migration/Service/Seite in bestehendem Inventar-Dokument ergänzen",
        "2. Oder Generator neu ausführen (z. B. `python scripts/generate_code_inventories.py`)",
        "3. Committen — Gate wird grün",
        "",
        "## Verlauf",
        "",
        "> Historische Drift-Reports werden als CI-Artefakte unter `.github/workflows/doc-drift-report.yml`",
        "> für 90 Tage aufbewahrt (retention-days: 90).",
        "",
        f"*Stand: {generated_at} · {total} Drift-Items · Slice: DOC-DRIFT-DASHBOARD-002*",
    ]

    return "\n".join(lines) + "\n"


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Drift-Dashboard-Seite generieren")
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    args = parser.parse_args()

    report = load_report(Path(args.report))
    page = build_page(report)
    OUTPUT.write_text(page, encoding="utf-8")
    total = report.get("summary", {}).get("total_drift_items", "?")
    print(f"Geschrieben: {OUTPUT} (total_drift_items={total})")


if __name__ == "__main__":
    main()
