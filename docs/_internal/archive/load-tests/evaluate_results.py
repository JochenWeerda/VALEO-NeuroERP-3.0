"""
evaluate_results.py — Wertet Locust-CSV-Ergebnisse gegen ErntepeakSLAContract aus.

Liest die von Locust generierten CSV-Dateien und gibt ein klares PASS/FAIL aus.

Verwendung:
    python load-tests/evaluate_results.py load-tests/results/erntepeak_stats.csv
"""

import csv
import sys
from pathlib import Path

# SLA-Schwellwerte (gespiegelt aus ErntepeakSLAContract)
MAX_ERROR_RATE_PCT   = 1.0      # < 1%
MAX_P95_GLOBAL_MS    = 2000.0   # < 2s
MAX_P95_DASHBOARD_MS = 250.0    # < 250ms (Gap 033)

DASHBOARD_ENDPOINTS = {
    "/controlling/dashboards",
    "/controlling/kpis",
    "/controlling/timeseries",
}


def load_stats(csv_path: str) -> list[dict]:
    rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def evaluate(csv_path: str) -> bool:
    rows = load_stats(csv_path)

    # Aggregated row
    aggregated = next((r for r in rows if r.get("Name") == "Aggregated"), None)
    if not aggregated:
        print("[ERROR] Keine aggregierte Zeile in CSV gefunden.")
        return False

    total_requests = int(aggregated.get("Request Count", 0))
    total_failures = int(aggregated.get("Failure Count", 0))
    p95_global     = float(aggregated.get("95%", 0))
    error_rate     = (total_failures / total_requests * 100) if total_requests > 0 else 0.0

    print()
    print("="*60)
    print("VALEO ERNTEPEAK — SLA-AUSWERTUNG (Gap 037)")
    print("="*60)
    print(f"  CSV-Datei       : {csv_path}")
    print(f"  Requests gesamt : {total_requests:>8,}")
    print(f"  Fehler gesamt   : {total_failures:>8,}")
    print(f"  Error Rate      : {error_rate:>7.2f}%   Ziel: < {MAX_ERROR_RATE_PCT}%")
    print(f"  p95 global      : {p95_global:>7.0f}ms  Ziel: < {MAX_P95_GLOBAL_MS:.0f}ms")
    print()

    # Dashboard-Endpoints
    dashboard_p95_max = 0.0
    for row in rows:
        name = row.get("Name", "")
        if any(ep in name for ep in DASHBOARD_ENDPOINTS):
            p95 = float(row.get("95%", 0))
            dashboard_p95_max = max(dashboard_p95_max, p95)
            status = "OK " if p95 <= MAX_P95_DASHBOARD_MS else "FAIL"
            print(f"  [{status}] {name:<40} p95={p95:.0f}ms (Ziel <{MAX_P95_DASHBOARD_MS:.0f}ms)")

    print()

    # Bewertung
    failures = []
    if error_rate > MAX_ERROR_RATE_PCT:
        failures.append(f"Error Rate {error_rate:.2f}% > {MAX_ERROR_RATE_PCT}%")
    if p95_global > MAX_P95_GLOBAL_MS:
        failures.append(f"p95 global {p95_global:.0f}ms > {MAX_P95_GLOBAL_MS:.0f}ms")
    if dashboard_p95_max > MAX_P95_DASHBOARD_MS:
        failures.append(f"Dashboard p95 {dashboard_p95_max:.0f}ms > {MAX_P95_DASHBOARD_MS:.0f}ms (Gap 033)")

    if failures:
        print("  [FAIL] SLA-Verletzungen:")
        for f in failures:
            print(f"    - {f}")
        print()
        print("  Gap 037 NICHT erfuellt.")
    else:
        print("  [PASS] Alle SLA-Ziele eingehalten.")
        print()
        print("  Gap 037 erfuellt: 500 gleichzeitige User stabil.")

    print("="*60 + "\n")
    return len(failures) == 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Verwendung: python {sys.argv[0]} <stats_csv>")
        print(f"Beispiel:   python {sys.argv[0]} load-tests/results/erntepeak_stats.csv")
        sys.exit(1)

    csv_path = sys.argv[1]
    if not Path(csv_path).exists():
        print(f"[ERROR] Datei nicht gefunden: {csv_path}")
        sys.exit(1)

    passed = evaluate(csv_path)
    sys.exit(0 if passed else 1)
