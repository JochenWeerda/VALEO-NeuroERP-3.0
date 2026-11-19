#!/usr/bin/env python3
"""Lineage des Tabellenkatalogs ohne Datenbank neu rechnen (samt gleichnamiger Tabellen ueber Schemata).

Der Katalog (``docs/admin/table-catalog.json|md``) fuehrt je Tabelle, welcher Code sie liest und schreibt
(``read_by``/``written_by``/``screens``). Wer SQL mit Tabellennamen in eine andere Datei verschiebt oder entfernt,
macht "Check physical table catalog" im Quality Gate rot - ohne jede Schemaaenderung. Dieses Skript laesst das
Schema wie committet und erntet nur die Lineage neu aus dem Code.

    python scripts/tabellenkatalog_lineage.py --check   # Abweichung -> Exit 1
    python scripts/tabellenkatalog_lineage.py           # neu schreiben
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(os.environ.get("VOR_PUSH_REPO") or Path(__file__).resolve().parents[1]).resolve()
sys.path.insert(0, str(REPO_ROOT))

from scripts import generate_table_catalog as katalog  # noqa: E402
from scripts.table_lineage import attach_lineage, collect_lineage  # noqa: E402


def neu_berechnet() -> tuple[str, str, str, str]:
    alt_json = katalog.JSON_OUTPUT.read_text(encoding="utf-8")
    alt_md = katalog.MD_OUTPUT.read_text(encoding="utf-8")
    payload = json.loads(alt_json)
    tabellen = set()
    for schema, body in payload["schemas"].items():
        for name, tabelle in body.get("tables", {}).items():
            tabellen.add((schema, name))
            for schluessel in ("read_by", "written_by", "screens"):
                tabelle.pop(schluessel, None)
    payload.pop("lineage_failures", None)
    lineage, fehler = collect_lineage(catalog_tables=tabellen)
    attach_lineage(payload, lineage)
    # Auch die Liste gleichnamiger Tabellen aus den Schemata neu rechnen: Nach dem Entfernen einer Tabelle blieb sie
    # sonst stehen (19.11.2026, S5: delivery_notes in domain_erp und domain_sales).
    payload["same_name_across_schemas"] = katalog._same_name_across_schemas(payload)
    if fehler:
        payload["lineage_failures"] = fehler
    heute = re.search(r"^last_reviewed: (\S+)", alt_md, re.M).group(1)
    return alt_json, alt_md, katalog.render_json(payload), katalog.render_markdown(payload, today=heute)


def main() -> int:
    alt_json, alt_md, neu_json, neu_md = neu_berechnet()
    if neu_json == alt_json and neu_md == alt_md:
        print("OK: Lineage des Tabellenkatalogs aktuell.")
        return 0
    if "--check" in sys.argv:
        print("DRIFT: Lineage des Tabellenkatalogs veraltet. 'python scripts/tabellenkatalog_lineage.py' ausfuehren.")
        return 1
    katalog.JSON_OUTPUT.write_text(neu_json, encoding="utf-8", newline="\n")
    katalog.MD_OUTPUT.write_text(neu_md, encoding="utf-8", newline="\n")
    print("Geschrieben: Lineage des Tabellenkatalogs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
