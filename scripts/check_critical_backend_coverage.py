from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COVERAGE_XML = PROJECT_ROOT / "coverage.xml"

CRITICAL_THRESHOLDS: dict[str, float] = {
    "middleware/tenant_enforcement.py": 0.90,
    "services/secrets_vault.py": 0.49,
    "domains/shared/events.py": 0.65,
    "services/integration_bootstrap.py": 0.90,
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
