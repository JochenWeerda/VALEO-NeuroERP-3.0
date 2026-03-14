"""
Wave 5 — E2E-Prozessketten-Report

Prueft die Vollstaendigkeit der Referenzkette:
  KonContract → HarvestAcceptance → QualityProtocol → AgrarSettlement → APInvoice → JournalEntry

Gibt aus:
- welche Endpoint-Paare die Referenz setzen
- welche Luecken noch nicht implementiert sind
- Empfehlung fuer Wave-5-AP2
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT = REPO_ROOT / "docs" / "architecture" / "process-kernel" / "wave-5" / "package-a" / "e2e-chain-report.md"

# Erwartete Referenzfelder je Aggregattyp → Elternaggregat
EXPECTED_REFS: list[tuple[str, str, str]] = [
    ("HarvestAcceptance", "contract_id", "KonContract"),
    ("QualityProtocol", "acceptance_id", "HarvestAcceptance"),
    ("AgrarSettlement", "protocol_id", "QualityProtocol"),
    ("AgrarSettlement", "contract_id", "KonContract"),
    ("APInvoice", "settlement_id", "AgrarSettlement"),
    ("JournalEntry", "invoice_id", "APInvoice"),
]

# Backend-Dateien, in denen die Referenzfelder geprueft werden
BACKEND_FILES = [
    "app/api/v1/endpoints/harvest_acceptance.py",
    "app/api/v1/endpoints/quality_protocols.py",
    "app/api/v1/endpoints/agrar_settlements.py",
    "app/api/v1/endpoints/ap_invoices.py",
    "app/infrastructure/models/agrar_models.py",
    "app/infrastructure/models/finance_models.py",
    "app/core/agrar_process_references.py",
]


def check_ref(field: str, files: list[str]) -> bool:
    for rel in files:
        path = REPO_ROOT / rel
        if path.exists() and field in path.read_text(encoding="utf-8", errors="ignore"):
            return True
    return False


def main() -> None:
    rows: list[dict] = []
    for aggregate, field, parent in EXPECTED_REFS:
        found = check_ref(field, BACKEND_FILES)
        rows.append({
            "aggregate": aggregate,
            "field": field,
            "parent": parent,
            "status": "vorhanden" if found else "FEHLT",
        })

    gaps = [r for r in rows if r["status"] == "FEHLT"]

    lines = [
        "# E2E-Prozessketten-Report",
        "",
        "Generiert durch `scripts/process_kernel/build_e2e_chain_report.py`",
        "",
        "## Referenzkette",
        "",
        "| Aggregat | Referenzfeld | Elternaggregat | Status |",
        "|----------|-------------|----------------|--------|",
    ]
    for r in rows:
        icon = "✅" if r["status"] == "vorhanden" else "❌"
        lines.append(f"| `{r['aggregate']}` | `{r['field']}` | `{r['parent']}` | {icon} {r['status']} |")

    lines += [
        "",
        f"## Zusammenfassung",
        "",
        f"- Gesamt: {len(rows)} Referenzen",
        f"- Vorhanden: {len(rows) - len(gaps)}",
        f"- Fehlend: {len(gaps)}",
        "",
    ]

    if gaps:
        lines += [
            "## Luecken (Wave-5-AP2 Aufgaben)",
            "",
        ]
        for g in gaps:
            lines.append(f"- `{g['aggregate']}.{g['field']}` → Referenz auf `{g['parent']}` einziehen")
    else:
        lines.append("## Ergebnis: Kette vollstaendig ✅")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report geschrieben: {OUTPUT}")
    print(f"Luecken: {len(gaps)}/{len(rows)}")
    for g in gaps:
        print(f"  FEHLT: {g['aggregate']}.{g['field']} → {g['parent']}")


if __name__ == "__main__":
    main()
