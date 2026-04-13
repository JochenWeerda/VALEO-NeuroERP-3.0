from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COVERAGE_XML = PROJECT_ROOT / "coverage.xml"

CRITICAL_THRESHOLDS: dict[str, float] = {
    # Infra / Governance
    "middleware/tenant_enforcement.py": 0.90,
    "services/secrets_vault.py": 0.49,
    "domains/shared/events.py": 0.65,
    "services/integration_bootstrap.py": 0.90,
    # Finance / FIBU Core (COV-FIN-002)
    "api/v1/endpoints/finance_actions.py": 0.90,
    "api/v1/endpoints/finance_followup.py": 0.70,
    "api/v1/endpoints/fibu_connectors.py": 0.80,
    "api/v1/endpoints/dunning.py": 0.50,
    "api/v1/endpoints/payment_runs.py": 0.30,
    "api/v1/endpoints/exchange_rates.py": 0.50,
    "api/v1/endpoints/booking_templates.py": 0.40,
    "api/v1/endpoints/chart_of_accounts.py": 0.50,
    "api/v1/endpoints/finance_read_models.py": 0.60,
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
