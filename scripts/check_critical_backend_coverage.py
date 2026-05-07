from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COVERAGE_XML = PROJECT_ROOT / "coverage.xml"

CRITICAL_THRESHOLDS: dict[str, float] = {
    # ── Infra / Governance ────────────────────────────────────────────────────
    "middleware/tenant_enforcement.py": 0.97,       # 100.0% measured  (COV-RATCHET-004: +7pp)
    "services/secrets_vault.py": 0.49,              #  50.4% measured — knapper Puffer
    "domains/shared/events.py": 0.66,               #  68.4% measured  (COV-RATCHET-004: +1pp)
    "services/integration_bootstrap.py": 0.92,      #  94.6% measured

    # ── Finance / FIBU Core (COV-FIN-002/003) ────────────────────────────────
    "api/v1/endpoints/finance_actions.py": 0.88,    #  91.0% measured  (COV-RATCHET-004: -2pp Puffer)
    "api/v1/endpoints/finance_followup.py": 0.71,   #  73.4% measured  (COV-RATCHET-004: +1pp)
    "api/v1/endpoints/fibu_connectors.py": 0.78,    #  81.0% measured  (COV-RATCHET-004: -2pp Puffer)
    "api/v1/endpoints/dunning.py": 0.85,            #  87.5% measured  (COV-RATCHET-004: +5pp)
    "api/v1/endpoints/payment_runs.py": 0.84,       #  86.7% measured  (COV-RATCHET-004: +4pp)
    "api/v1/endpoints/exchange_rates.py": 0.77,     #  79.6% measured  (COV-RATCHET-004: +2pp)
    "api/v1/endpoints/booking_templates.py": 0.62,  #  63.6% measured  (COV-RATCHET-004: +2pp)
    "api/v1/endpoints/chart_of_accounts.py": 0.63,  #  65.2% measured  (COV-RATCHET-004: +3pp)
    "api/v1/endpoints/finance_read_models.py": 0.87, #  89.5% measured  (COV-RATCHET-004: +2pp)
    # Finance ergänzend (neu)
    "api/v1/endpoints/journal_entries.py": 0.19,    #  19.8% measured — Buchungsjournal
    "api/v1/endpoints/open_items.py": 0.39,         #  40.8% measured — Offene Posten  (+7pp)
    "api/v1/endpoints/financial_reports.py": 0.25,  #  26.5% measured — Abschlussberichte (+5pp)

    # ── Inventory / Warehouse (COV-INV-001/002) ───────────────────────────────
    "api/v1/endpoints/waage.py": 0.88,              #  91.1% measured  (COV-RATCHET-004: +3pp)
    "api/v1/endpoints/warehouses.py": 0.95,         #  97.1% measured
    "api/v1/endpoints/warehouse_transfers.py": 0.65, #  67.8% measured  (COV-RATCHET-004: +5pp)
    "api/v1/endpoints/inventory_counts.py": 0.57,   #  59.9% measured  (+7pp)
    "api/v1/endpoints/inventory_operations.py": 0.54, #  55.7% measured  (+4pp)

    # ── Landhandel-Kern (COV-RATCHET-004 angehoben) ───────────────────────────
    "api/v1/endpoints/kontrakte.py": 0.27,          #  28.5% measured  (+5pp)
    "api/v1/endpoints/harvest_acceptance.py": 0.24, #  25.3% measured  (+4pp)
    "api/v1/endpoints/articles.py": 0.23,           #  23.7% measured  (+5pp)
    "api/v1/endpoints/sales_orders.py": 0.38,       #  39.8% measured  (+6pp)
    "api/v1/endpoints/ap_invoices.py": 0.42,        #  43.6% measured  (+7pp)

    # ── Agrar-Differenziator ──────────────────────────────────────────────────
    "api/v1/endpoints/agrar_p0.py": 0.72,           #  75.0% measured  (COV-RATCHET-004: +2pp)
    "api/v1/endpoints/agrar_contracts.py": 0.51,    #  53.5% measured  (+6pp)
    "api/v1/endpoints/silo.py": 0.31,               #  32.6% measured  (+6pp)

    # ── Security / Compliance ─────────────────────────────────────────────────
    "api/v1/endpoints/audit.py": 0.38,              #  39.8% measured  (+6pp)
    "api/v1/endpoints/gdpr.py": 0.28,               #  29.8% measured  (+6pp)
    "api/v1/endpoints/security_monitoring.py": 0.69, #  71.4% measured  (+4pp)

    # ── Neue Pfade (COV-RATCHET-004 / DOMAIN-PARITY-COV-001) ─────────────────
    "api/v1/endpoints/strecke.py": 0.18,            #  ~22% estimated — Streckenhandel
}


def _normalise(filename: str) -> str:
    return filename.replace("\\", "/").lstrip("./")


def main() -> None:
    if not COVERAGE_XML.exists():
        raise SystemExit("coverage.xml not found. Run pytest with coverage reporting first.")

    tree = ET.parse(COVERAGE_XML)
    root = tree.getroot()

    measured: dict[str, float] = {}
    for cls in root.findall(".//class"):
        filename = _normalise(cls.attrib.get("filename", ""))
        line_rate = float(cls.attrib.get("line-rate", "0"))
        measured[filename] = line_rate

    failures: list[str] = []
    for filename, threshold in CRITICAL_THRESHOLDS.items():
        actual = measured.get(filename)
        if actual is None:
            failures.append(f"{filename}: not present in coverage.xml")
            continue
        if actual < threshold:
            failures.append(
                f"{filename}: {actual:.1%} below threshold {threshold:.1%}"
            )

    if failures:
        raise SystemExit("Critical backend coverage below ratchet:\n- " + "\n- ".join(failures))

    print("Critical backend coverage OK.")


if __name__ == "__main__":
    main()
