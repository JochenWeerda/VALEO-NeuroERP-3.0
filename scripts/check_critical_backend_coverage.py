from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COVERAGE_XML = PROJECT_ROOT / "coverage.xml"

CRITICAL_THRESHOLDS: dict[str, float] = {
    # ── Infra / Governance ────────────────────────────────────────────────────
    "middleware/tenant_enforcement.py": 0.90,       # 100.0% measured
    "services/secrets_vault.py": 0.49,              #  50.4% measured — knapper Puffer
    "domains/shared/events.py": 0.65,               #  68.4% measured
    "services/integration_bootstrap.py": 0.92,      #  94.6% measured

    # ── Finance / FIBU Core (COV-FIN-002) ────────────────────────────────────
    "api/v1/endpoints/finance_actions.py": 0.90,    #  91.0% measured
    "api/v1/endpoints/finance_followup.py": 0.70,   #  73.4% measured
    "api/v1/endpoints/fibu_connectors.py": 0.80,    #  81.0% measured
    "api/v1/endpoints/dunning.py": 0.80,            #  87.5% measured
    "api/v1/endpoints/payment_runs.py": 0.80,       #  86.7% measured
    "api/v1/endpoints/exchange_rates.py": 0.75,     #  79.6% measured
    "api/v1/endpoints/booking_templates.py": 0.60,  #  63.6% measured
    "api/v1/endpoints/chart_of_accounts.py": 0.60,  #  65.2% measured
    "api/v1/endpoints/finance_read_models.py": 0.85, #  89.5% measured
    # Finance ergänzend (neu)
    "api/v1/endpoints/journal_entries.py": 0.15,    #  19.8% measured — Buchungsjournal
    "api/v1/endpoints/open_items.py": 0.32,         #  40.8% measured — Offene Posten
    "api/v1/endpoints/financial_reports.py": 0.20,  #  26.5% measured — Abschlussberichte

    # ── Inventory / Warehouse (COV-INV-001) ──────────────────────────────────
    "api/v1/endpoints/waage.py": 0.85,              #  91.1% measured
    "api/v1/endpoints/warehouses.py": 0.95,         #  97.1% measured
    "api/v1/endpoints/warehouse_transfers.py": 0.60, #  67.8% measured
    "api/v1/endpoints/inventory_counts.py": 0.50,   #  59.9% measured
    "api/v1/endpoints/inventory_operations.py": 0.50, #  55.7% measured

    # ── Landhandel-Kern (neu) ─────────────────────────────────────────────────
    "api/v1/endpoints/kontrakte.py": 0.22,          #  28.5% measured — Vertragsabwicklung
    "api/v1/endpoints/harvest_acceptance.py": 0.20, #  25.3% measured — Warenannahme
    "api/v1/endpoints/articles.py": 0.18,           #  23.7% measured — Artikelstamm
    "api/v1/endpoints/sales_orders.py": 0.32,       #  39.8% measured — Verkaufsaufträge
    "api/v1/endpoints/ap_invoices.py": 0.35,        #  43.6% measured — Kreditorenrechnungen

    # ── Agrar-Differenziator (neu) ────────────────────────────────────────────
    "api/v1/endpoints/agrar_p0.py": 0.70,           #  75.0% measured — DüV / PSM / FLIK
    "api/v1/endpoints/agrar_contracts.py": 0.45,    #  53.5% measured — Agrarverträge
    "api/v1/endpoints/silo.py": 0.25,               #  32.6% measured — Siloverwaltung

    # ── Security / Compliance (neu) ───────────────────────────────────────────
    "api/v1/endpoints/audit.py": 0.32,              #  39.8% measured — Audit-Log
    "api/v1/endpoints/gdpr.py": 0.22,               #  29.8% measured — DSGVO
    "api/v1/endpoints/security_monitoring.py": 0.65, #  71.4% measured — Security
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
