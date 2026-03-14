"""
Wave 6 — Agrar-P0-Gap-Report

Prueft den Umsetzungsstand der Agrar-P0-Anforderungen:
- Schlagkartei: FLIK-ID, GeoJSON-Export
- Duengebilanz: DueV-Compliance-Check
- PSM-Spritztagebuch: Pflichtfelder, GoBD-Finalisierung

Gibt aus:
- vorhandene und fehlende Pflichtfelder/-endpoints
- Empfehlung fuer Wave-6-Paket-A-Arbeitsauftraege
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT = REPO_ROOT / "docs" / "architecture" / "process-kernel" / "wave-6" / "package-a" / "agrar-p0-gap-report.md"

# Pruefpunkte: (Kategorie, Beschreibung, Suchbegriff, Dateien)
CHECKS: list[tuple[str, str, str, list[str]]] = [
    # Schlagkartei
    ("Schlagkartei", "FeldbuchSchlag.flik_id", "flik_id", [
        "app/infrastructure/models/agrar_models.py",
    ]),
    ("Schlagkartei", "FeldbuchSchlag.geometry_wkt", "geometry_wkt", [
        "app/infrastructure/models/agrar_models.py",
    ]),
    ("Schlagkartei", "Feldblockfinder-Endpoint /find-by-flik", "find-by-flik", [
        "app/api/v1/endpoints/agrar_feldbuch.py",
    ]),
    ("Schlagkartei", "GeoJSON-Export-Endpoint", "geojson", [
        "app/api/v1/endpoints/agrar_feldbuch.py",
    ]),
    # Duengebilanz
    ("Duengung", "NaehrstoffInput-Modell", "NaehrstoffInput", [
        "app/core/duenge_bilanz.py",
    ]),
    ("Duengung", "DuengeBilanzPeriode.compliance_check()", "compliance_check", [
        "app/core/duenge_bilanz.py",
    ]),
    ("Duengung", "N-Saldo-Grenzwert 50 kg/ha", "50", [
        "app/core/duenge_bilanz.py",
    ]),
    ("Duengung", "Bilanz-Endpoint /api/v1/agrar/duengung/bilanz", "duengung/bilanz", [
        "app/api/v1/endpoints/agrar_duengung.py",
        "app/api/v1/api.py",
    ]),
    # PSM-Spritztagebuch
    ("PSM", "PsmAnwendungProtokoll.sachkunde_nr", "sachkunde_nr", [
        "app/infrastructure/models/agrar_models.py",
        "app/api/v1/endpoints/agrar_psm.py",
    ]),
    ("PSM", "PsmAnwendungProtokoll.wasser_schutzgebiet", "wasser_schutzgebiet", [
        "app/infrastructure/models/agrar_models.py",
        "app/api/v1/endpoints/agrar_psm.py",
    ]),
    ("PSM", "PSM-Finalisierung /finalize → GoBD-Beleg", "finalize", [
        "app/api/v1/endpoints/agrar_psm.py",
    ]),
    ("PSM", "PSM-Export CSV/PDF", "spritztagebuch/export", [
        "app/api/v1/endpoints/agrar_psm.py",
    ]),
]


def check(term: str, files: list[str]) -> bool:
    for rel in files:
        path = REPO_ROOT / rel
        if path.exists() and term in path.read_text(encoding="utf-8", errors="ignore"):
            return True
    return False


def main() -> None:
    results: list[dict] = []
    for category, desc, term, files in CHECKS:
        found = check(term, files)
        results.append({"category": category, "desc": desc, "status": "vorhanden" if found else "FEHLT"})

    gaps = [r for r in results if r["status"] == "FEHLT"]
    by_cat: dict[str, list[dict]] = {}
    for r in results:
        by_cat.setdefault(r["category"], []).append(r)

    lines = [
        "# Agrar-P0-Gap-Report",
        "",
        "Generiert durch `scripts/process_kernel/build_agrar_p0_gap_report.py`",
        "",
    ]

    for cat, items in by_cat.items():
        lines += [f"## {cat}", "", "| Pruefpunkt | Status |", "|-----------|--------|"]
        for it in items:
            icon = "✅" if it["status"] == "vorhanden" else "❌"
            lines.append(f"| {it['desc']} | {icon} {it['status']} |")
        lines.append("")

    done = len(results) - len(gaps)
    lines += [
        "## Zusammenfassung",
        "",
        f"- Gesamt: {len(results)} Pruefpunkte",
        f"- Erfuellt: {done}",
        f"- Offen: {len(gaps)}",
        f"- P0-Abdeckung: {done * 100 // len(results)}%",
        "",
    ]

    if gaps:
        lines += ["## Offene Wave-6-AP-Aufgaben", ""]
        for g in gaps:
            lines.append(f"- [{g['category']}] {g['desc']}")
    else:
        lines.append("## Ergebnis: Agrar-P0 vollstaendig abgedeckt ✅")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report geschrieben: {OUTPUT}")
    print(f"P0-Abdeckung: {done}/{len(results)} ({done * 100 // len(results)}%)")
    for g in gaps:
        desc = g["desc"].replace("\u2192", "->")
        print(f"  FEHLT: [{g['category']}] {desc}")


if __name__ == "__main__":
    main()
