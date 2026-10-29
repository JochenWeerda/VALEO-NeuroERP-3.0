#!/usr/bin/env python3
"""Welche Klasse-A-Tabellen RLS bekommen und welche warten (RLS-Plan P5).

Eingabe: ``docs/admin/rls-inventory.json`` (Klassen, RLS-Status) und der Quelltext unter
``app/``, ``modules/``, ``services/``. Ausgabe: ``docs/admin/rls-rollout.json`` mit

    ready    Klasse A, noch ohne RLS, kein Grund dagegen gefunden
    pending  Tabelle -> Gruende, warum sie (noch) wartet

Die Gruende sind bewusst vorsichtig (dateiweit, nicht anweisungsgenau): ein falscher Treffer
laesst eine Tabelle warten, ein uebersehener liesse Daten still verschwinden.

    dienst            Modell eines Dienstes unter services/* (eigene Engine ohne app.tenant_id, P6)
    mandant_ermitteln Code ermittelt den Mandanten aus der Tabelle (SELECT tenant_id FROM …)
    standardmandant   Datei mit Zugriff nutzt DEFAULT_TENANT_ID oder 'default' als Mandant
    mandant_null      Datei mit Zugriff fragt tenant_id IS NULL ab
    uebergreifend     mandantenuebergreifende Arbeit ohne Systemverbindung (system_session, P6)
    identitaet        Schluessel/Token/Sitzung: Nachschlagen vor der Mandantenbindung

    python scripts/rls_rollout.py            # schreiben
    python scripts/rls_rollout.py --check    # Abweichung -> Exit 1
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
INVENTORY = REPO_ROOT / "docs" / "admin" / "rls-inventory.json"
OUTPUT = REPO_ROOT / "docs" / "admin" / "rls-rollout.json"
CODE_ROOTS = ("app", "modules", "services")
SKIP_PARTS = {"tests", "test", "node_modules", "__pycache__", "alembic"}

DEFAULT_TENANT = re.compile(r"\bDEFAULT_TENANT_ID\b|tenant_id\s*(?:=|==|IN\s*\()\s*['\"]default['\"]|['\"]default['\"]\s*\)")
TENANT_NULL = re.compile(r"tenant_id\s+IS\s+NULL", re.I)
CROSS_TENANT = re.compile(r"\bcross_tenant_(?:scope|job)\(")
# Cross-tenant code that connects as valeo_system (BYPASSRLS) is not blocked by RLS (P6).
SYSTEM_CONNECTION = re.compile(r"\bsystem_session\(|\bcross_tenant_job\(")
IDENTITY_NAME = re.compile(r"(?:token|api_key|session|credential|secret)", re.I)
TABLENAME = re.compile(r"__tablename__\s*=\s*['\"]([a-z_0-9]+)['\"]")


def _code_files():
    for root in CODE_ROOTS:
        for path in sorted((REPO_ROOT / root).rglob("*.py")):
            rel = path.relative_to(REPO_ROOT).as_posix()
            if SKIP_PARTS & set(rel.split("/")):
                continue
            yield rel, path.read_text(encoding="utf-8", errors="replace")


def _model_tables(text: str) -> set[str]:
    """ORM table names declared in a file, schema-qualified where the file names one."""
    names = set()
    schemas = set(re.findall(r"['\"]schema['\"]\s*:\s*['\"]([a-z_]+)['\"]|schema\s*=\s*['\"]([a-z_]+)['\"]", text))
    flat = {a or b for a, b in schemas} or {"public"}
    for name in TABLENAME.findall(text):
        for schema in flat:
            names.add(f"{schema}.{name}")
    return names


CLASS_TABLE = re.compile(
    r"^class\s+([A-Z][A-Za-z0-9_]*)\s*\([^)]*\):\s*\n(?:[^\n]*\n){0,6}?\s+__tablename__\s*=\s*['\"]([a-z_0-9]+)['\"]",
    re.M,
)


def _model_classes(files) -> dict[str, set[str]]:
    """ORM class name -> qualified tables (schema from the declaring file)."""
    classes: dict[str, set[str]] = {}
    for rel, text in files:
        if "__tablename__" not in text:
            continue
        schemas = {a or b for a, b in re.findall(
            r"['\"]schema['\"]\s*:\s*['\"]([a-z_]+)['\"]|schema\s*=\s*['\"]([a-z_]+)['\"]", text)} or {"public"}
        for cls, name in CLASS_TABLE.findall(text):
            classes.setdefault(cls, set()).update(f"{s}.{name}" for s in schemas)
    return classes


def analyse(inventory: dict) -> dict:
    tables = [t["table"] for t in inventory["tables"] if t["class"] == "A" and not t["rls"]]
    files = list(_code_files())
    service_tables = set()
    for rel, text in files:
        if rel.startswith("services/"):
            service_tables |= {n.split(".", 1)[1] for n in _model_tables(text)}

    refs: dict[str, list[tuple[str, str]]] = {t: [] for t in tables}
    patterns = {}
    for t in tables:
        schema, name = t.split(".")
        if schema == "public":
            patterns[t] = re.compile(
                rf"(?:\bpublic\.{name}\b|(?:FROM|JOIN|INTO|UPDATE)\s+\"?{name}\b|__tablename__\s*=\s*['\"]{name}['\"])", re.I)
        else:
            patterns[t] = re.compile(rf"\b{schema}\.\"?{name}\b")
    classes = _model_classes(files)
    table_set = set(tables)
    class_refs = {cls: re.compile(rf"\b{cls}\b") for cls, qualified in classes.items() if qualified & table_set}
    for rel, text in files:
        models = _model_tables(text)
        via_class = set()
        for cls, rx in class_refs.items():
            if rx.search(text):
                via_class |= classes[cls] & table_set
        for t in tables:
            if t in models or t in via_class or patterns[t].search(text):
                refs[t].append((rel, text))

    ready, pending = [], {}
    for t in tables:
        schema, name = t.split(".")
        reasons = set()
        if schema == "public" and name in service_tables:
            reasons.add("dienst")
        if IDENTITY_NAME.search(name):
            reasons.add("identitaet")
        lookup = re.compile(rf"SELECT\s+(?:DISTINCT\s+)?tenant_id\s+FROM\s+(?:{schema}\.)?\"?{name}\b", re.I)
        for rel, text in refs[t]:
            if rel.startswith("services/"):
                reasons.add("dienst")
            if lookup.search(text):
                reasons.add("mandant_ermitteln")
            if DEFAULT_TENANT.search(text):
                reasons.add("standardmandant")
            if TENANT_NULL.search(text):
                reasons.add("mandant_null")
            if CROSS_TENANT.search(text) and not SYSTEM_CONNECTION.search(text):
                reasons.add("uebergreifend")
        if reasons:
            pending[t] = sorted(reasons)
        else:
            ready.append(t)
    return {
        "_note": "Generiert von scripts/rls_rollout.py aus docs/admin/rls-inventory.json; nicht von Hand aendern.",
        "summary": {"ready": len(ready), "pending": len(pending),
                    "reasons": {r: sum(r in v for v in pending.values()) for r in
                                ("dienst", "mandant_ermitteln", "standardmandant", "mandant_null", "uebergreifend", "identitaet")}},
        "ready": sorted(ready),
        "pending": dict(sorted(pending.items())),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = analyse(json.loads(INVENTORY.read_text(encoding="utf-8")))
    text = json.dumps(result, ensure_ascii=False, indent=1) + "\n"
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != text:
            print(f"DRIFT: {OUTPUT.relative_to(REPO_ROOT)} nicht aktuell. 'python scripts/rls_rollout.py' ausfuehren.")
            return 1
        print(f"OK: {OUTPUT.relative_to(REPO_ROOT)} aktuell.")
        return 0
    OUTPUT.write_text(text, encoding="utf-8")
    print(f"Geschrieben: {OUTPUT.relative_to(REPO_ROOT)} {result['summary']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
