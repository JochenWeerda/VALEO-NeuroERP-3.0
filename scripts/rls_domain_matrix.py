#!/usr/bin/env python3
"""Entscheidungsmatrix fuer die noch nicht abgesicherten Mandantentabellen (RLS-Domains).

Eingabe:
    docs/admin/rls-inventory.json      Klassen A/B/C/D, RLS-Status (P0)
    docs/admin/rls-rollout.json        Gruende der zurueckgestellten Klasse-A-Tabellen (P5)
    docs/admin/rls-domain-data.json    Datenbefund der gewachsenen Datenbank (``--data``)
    Quelltext unter app/, modules/, services/

Ausgabe:
    docs/admin/rls-domain-matrix.json  je Tabelle: Domain, Ursache, fuehrendes Modell,
                                       lesende/schreibende Verbraucher, Identitaetsquelle,
                                       Worker, Fundstellen, Bereinigung, Policy-Vorschlag
    docs/admin/rls-domain-matrix.md    dieselbe Matrix je Domain zum Lesen

Ursachen (eine Tabelle kann mehrere haben, ``ursache`` ist die fuehrende):

    dienst            Modell/Zugriff eines Dienstes unter services/* - Mandant nicht tokengebunden
    position          Klasse C: keine tenant_id, Mandant haengt am Elternbeleg
    referenzdaten     Code liest NULL- oder 'system'-Zeilen als gemeinsame Daten
    mandant_nullbar   Klasse B oder Code fragt tenant_id IS NULL ab
    standardmandant   Code faellt auf DEFAULT_TENANT_ID/'default' zurueck
    identitaet        Schluessel/Token: Nachschlagen vor der Mandantenbindung

Alle Code-Befunde sind dateiweit und heuristisch (wie rls_rollout.py): sie zeigen, wo
nachzusehen ist, nicht dass dort ein Fehler liegt. Die Fundstellen (Datei:Zeile) sind
die Arbeitsliste der Fachkorrektur.

    python scripts/rls_domain_matrix.py            # Matrix aus Inventar + Datenbefund schreiben
    python scripts/rls_domain_matrix.py --check    # Abweichung -> Exit 1
    python scripts/rls_domain_matrix.py --data     # Datenbefund lesend aus LIVE_DATABASE_URL
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import rls_rollout  # noqa: E402

REPO_ROOT = rls_rollout.REPO_ROOT
INVENTORY = rls_rollout.INVENTORY
ROLLOUT = rls_rollout.OUTPUT
DATA = REPO_ROOT / "docs" / "admin" / "rls-domain-data.json"
OUTPUT = REPO_ROOT / "docs" / "admin" / "rls-domain-matrix.json"
MARKDOWN = REPO_ROOT / "docs" / "admin" / "rls-domain-matrix.md"

PUBLIC_DOMAINS = {
    "crm": "crm", "opportunities": "crm", "einkauf": "einkauf", "zahlungslauf": "einkauf",
    "inventory": "inventory", "finance": "finance", "agent": "ki", "mcp": "ki",
    "number": "shared", "outbox": "shared",
}
WORKER_PATH = re.compile(r"(?:^|/)(?:workers?|jobs?|tasks?|scheduler[a-z_]*|celery[a-z_]*)(?:/|\.py$|_)")
WRITE_SQL = r"(?:INSERT\s+INTO|UPDATE|DELETE\s+FROM)\s+{target}\b"
ORM_WRITE = re.compile(r"\.(?:add|add_all|delete|merge|bulk_save_objects|bulk_insert_mappings)\(|\binsert\(|\bupdate\(|\bdelete\(")
DEFAULT_LINE = re.compile(r"\bDEFAULT_TENANT_ID\b|tenant_id[\"']?\s*(?:=|==|,|:)\s*(?:str\s*=\s*)?[\"']default[\"']|[\"']default[\"']\s*\)")
NULL_LINE = re.compile(r"tenant_id\s+IS\s+NULL|tenant_id\.is_\(None\)|tenant_id\s*==\s*None", re.I)
SHARED_LINE = re.compile(
    r"tenant_id\s+IS\s+NULL\s+OR|OR\s+[a-z_.]*tenant_id\s+IS\s+NULL|or_\([^)]*tenant_id\.is_\(None\)"
    r"|tenant_id\s+IN\s*\([^)]*['\"]system['\"]|tenant_id\s*(?:=|==)\s*['\"]system['\"]", re.I)
IDENTITY = {
    "token": re.compile(r"from app\.core\.tenant import|get_verified_tenant_id|get_current_tenant_id|current_tenant_or_none|tenant_scope\("),
    "kopfzeile": re.compile(r"from app\.core\.dependencies import[^\n]*get_tenant_id|Header\([^)]*[Tt]enant"),
    "nutzlast": re.compile(r"(?:payload|body|data|request_data|item)(?:\.|\[\s*['\"]|\.get\(\s*['\"])tenant_id"),
    "standardmandant": re.compile(r"\bDEFAULT_TENANT_ID\b|[\"']default[\"']\s*\)|tenant_id[^\n]{0,20}[\"']default[\"']"),
}
URSACHEN = ("dienst", "position", "referenzdaten", "mandant_nullbar", "standardmandant", "identitaet")


def domain_of(table: str) -> str:
    schema, name = table.split(".", 1)
    if schema == "public":
        return PUBLIC_DOMAINS.get(name.split("_", 1)[0], "public")
    return schema.removeprefix("domain_")


def scope_tables(inventory: dict) -> list[dict]:
    """Tables with a tenant but without RLS: class A/B without RLS, class C."""
    return [t for t in inventory["tables"] if t["class"] in ("A", "B", "C") and not t["rls"]]


def _patterns(table: str, classes: dict[str, set[str]]):
    schema, name = table.split(".")
    if schema == "public":
        target = rf"(?:public\.)?\"?{name}"
        direct = re.compile(rf"(?:\bpublic\.{name}\b|(?:FROM|JOIN|INTO|UPDATE)\s+\"?{name}\b)", re.I)
    else:
        target = rf"{schema}\.\"?{name}"
        direct = re.compile(rf"\b{schema}\.\"?{name}\b")
    owned = [cls for cls, tables in classes.items() if table in tables]
    by_class = re.compile(rf"\b(?:{'|'.join(map(re.escape, owned))})\b") if owned else None
    return direct, re.compile(WRITE_SQL.format(target=target), re.I), by_class, [name, *owned]


def _lines(text: str, rx: re.Pattern) -> list[int]:
    return [i for i, line in enumerate(text.splitlines(), 1) if rx.search(line)]


def analyse(inventory: dict, rollout: dict, data: dict, files=None) -> dict:
    files = list(files if files is not None else rls_rollout._code_files())
    classes = rls_rollout._model_classes(files)
    service_models = set()
    for rel, text in files:
        if rel.startswith("services/"):
            service_models |= rls_rollout._model_tables(text)
    service_names = {t.split(".", 1)[1] for t in service_models}
    model_files: dict[str, list[str]] = defaultdict(list)
    for rel, text in files:
        for table in rls_rollout._model_tables(text):
            model_files[table].append(rel)

    rows = []
    for entry in scope_tables(inventory):
        table = entry["table"]
        schema, name = table.split(".")
        direct, write_sql, by_class, needles = _patterns(table, classes)
        models = sorted(model_files.get(table, []))
        leser, schreiber, worker, identitaet = [], [], [], Counter()
        default_hits, null_hits, shared_hits = [], [], []
        for rel, text in files:
            if rel not in models and not any(n in text for n in needles):
                continue
            hit_class = bool(by_class and by_class.search(text))
            if not (rel in models or hit_class or direct.search(text)):
                continue
            leser.append(rel)
            if write_sql.search(text) or (hit_class and ORM_WRITE.search(text)):
                schreiber.append(rel)
            if WORKER_PATH.search(rel):
                worker.append(rel)
            for source, rx in IDENTITY.items():
                if rx.search(text):
                    identitaet[source] += 1
            if rel.startswith("services/"):
                identitaet["dienst"] += 1
            default_hits += [f"{rel}:{n}" for n in _lines(text, DEFAULT_LINE)]
            null_hits += [f"{rel}:{n}" for n in _lines(text, NULL_LINE)]
            shared_hits += [f"{rel}:{n}" for n in _lines(text, SHARED_LINE)]

        gruende = set(rollout["pending"].get(table, []))
        if entry["class"] == "B":
            gruende.add("mandant_nullbar")
        if entry["class"] == "C":
            gruende.add("position")
        if "mandant_null" in gruende:
            gruende.discard("mandant_null")
            gruende.add("mandant_nullbar")
        if table in service_models or (schema == "public" and name in service_names) or any(
                r.startswith("services/") for r in leser):
            gruende.add("dienst")
        if shared_hits:
            gruende.add("referenzdaten")
        if default_hits:
            gruende.add("standardmandant")
        befund = data.get("tables", {}).get(table)
        if befund and (befund.get("null") or 0) > 0:
            gruende.add("mandant_nullbar")
        ursache = next((u for u in URSACHEN if u in gruende), "standardmandant")
        rows.append({
            "table": table,
            "domain": domain_of(table),
            "class": entry["class"],
            "tenant_type": entry.get("tenant_type"),
            "eltern": entry.get("tenant_parents", []),
            "ursache": ursache,
            "gruende": [u for u in URSACHEN if u in gruende],
            "modell": models,
            "leser": sorted(set(leser) - set(schreiber)),
            "schreiber": sorted(set(schreiber)),
            "worker": sorted(set(worker)),
            "identitaet": dict(sorted(identitaet.items())),
            "standardmandant_stellen": default_hits,
            "null_stellen": null_hits,
            "gemeinsam_stellen": shared_hits,
            "daten": befund,
            "bereinigung": bereinigung(entry, befund),
            "policy": policy(ursache, entry, befund),
        })
    rows.sort(key=lambda r: (r["domain"], r["table"]))
    by_domain: dict[str, Counter] = defaultdict(Counter)
    for r in rows:
        by_domain[r["domain"]][r["ursache"]] += 1
    return {
        "_note": "Generiert von scripts/rls_domain_matrix.py; nicht von Hand aendern.",
        "datenstand": data.get("stand"),
        "summary": {
            "tabellen": len(rows),
            "nach_klasse": dict(sorted(Counter(r["class"] for r in rows).items())),
            "nach_ursache": {u: sum(r["ursache"] == u for r in rows) for u in URSACHEN},
            "nach_domain": {d: dict(sorted(c.items())) for d, c in sorted(by_domain.items())},
        },
        "tables": rows,
    }


def bereinigung(entry: dict, befund: dict | None) -> list[str]:
    steps = []
    if entry["class"] == "C":
        steps.append("tenant_id aus dem Elternbeleg nachziehen, NOT NULL, Verbund-FK (eltern_id, tenant_id)")
    if befund is None:
        return steps + (["Datenbefund fehlt (Tabelle nicht in der gewachsenen Datenbank)"] if entry["class"] != "C" else [])
    if befund.get("null"):
        steps.append(f"{befund['null']} Zeilen ohne Mandant: Herkunft klaeren (blockiert die Migration)")
    if befund.get("default"):
        steps.append(f"{befund['default']} Zeilen mit 'default': Herkunft klaeren (blockiert die Migration)")
    if befund.get("system"):
        steps.append(f"{befund['system']} 'system'-Zeilen: gemeinsame Referenzdaten begruenden oder zuordnen")
    if befund.get("verwaist"):
        steps.append(f"{befund['verwaist']} Zeilen ohne Elternbeleg: klaeren (blockiert die Migration)")
    return steps


def policy(ursache: str, entry: dict, befund: dict | None) -> str:
    if ursache == "dienst":
        return "keine, bis der Dienst tokengebundene Identitaet hat (rls-dienste-identitaet-vorschlag.md)"
    if ursache == "identitaet":
        return "keine Mandanten-Policy: Nachschlagen vor der Mandantenbindung, Zugriff ueber valeo_system"
    shared = bool(befund and befund.get("system")) or ursache == "referenzdaten"
    read = "eigener Mandant + 'system' lesen (Begruendung je Tabellenfamilie)" if shared else "eigener Mandant"
    base = f"getrennt: SELECT {read}; INSERT/UPDATE/DELETE nur eigener Mandant"
    if entry["class"] == "C":
        return f"{base}; tenant_id aus {', '.join(entry.get('tenant_parents', []))}"
    return base


# --- Datenbefund (gewachsene Datenbank, nur lesend) ---------------------------------------

DATA_SQL = """
SELECT count(*) AS zeilen,
       count(*) FILTER (WHERE {col} IS NULL) AS "null",
       count(*) FILTER (WHERE {col}::text = 'default') AS "default",
       count(*) FILTER (WHERE {col}::text = 'system') AS "system",
       count(DISTINCT {col}) AS mandanten
  FROM {table}
"""
FK_SQL = """
SELECT a.attname, cf.oid::regclass::text, af.attname
  FROM pg_constraint k
  JOIN pg_class c ON c.oid = k.conrelid
  JOIN pg_class cf ON cf.oid = k.confrelid
  JOIN pg_attribute a ON a.attrelid = k.conrelid AND a.attnum = k.conkey[1]
  JOIN pg_attribute af ON af.attrelid = k.confrelid AND af.attnum = k.confkey[1]
 WHERE k.contype = 'f' AND k.conrelid = to_regclass(:t) AND cardinality(k.conkey) = 1
"""


def collect_data(url: str, inventory: dict) -> dict:
    import sqlalchemy as sa
    from datetime import date

    engine = sa.create_engine(url)
    result = {}
    with engine.connect() as conn:
        conn.execute(sa.text("SET TRANSACTION READ ONLY"))
        for entry in scope_tables(inventory):
            table = entry["table"]
            if conn.execute(sa.text("SELECT to_regclass(:t)"), {"t": table}).scalar() is None:
                continue
            has_tenant = conn.execute(sa.text(
                "SELECT 1 FROM information_schema.columns WHERE table_schema=:s AND table_name=:n "
                "AND column_name='tenant_id'"), dict(zip(("s", "n"), table.split(".")))).scalar()
            if has_tenant:
                row = conn.execute(sa.text(DATA_SQL.format(col="tenant_id", table=table))).mappings().one()
                result[table] = dict(row)
                continue
            # Klasse C: Zeilen und Zeilen ohne erreichbaren Elternbeleg.
            fks = [r for r in conn.execute(sa.text(FK_SQL), {"t": table}).all()
                   if r[1] in entry.get("tenant_parents", [])]
            info = {"zeilen": conn.execute(sa.text(f"SELECT count(*) FROM {table}")).scalar()}
            for col, parent, pcol in sorted(fks):
                info.setdefault("eltern_fk", []).append(f"{col} -> {parent}.{pcol}")
                info["verwaist"] = info.get("verwaist", 0) + conn.execute(sa.text(
                    f"SELECT count(*) FROM {table} x WHERE x.{col} IS NOT NULL AND NOT EXISTS "
                    f"(SELECT 1 FROM {parent} p WHERE p.{pcol} = x.{col})")).scalar()
            if fks:
                # Zeilen, die an keinem Elternbeleg haengen: ihr Mandant ist nicht ableitbar.
                info["ohne_eltern"] = conn.execute(sa.text(
                    f"SELECT count(*) FROM {table} WHERE "
                    + " AND ".join(f"{col} IS NULL" for col, _, _ in fks))).scalar()
            result[table] = info
        conn.rollback()
    engine.dispose()
    return {"_note": "Lesender Befund der gewachsenen Datenbank (scripts/rls_domain_matrix.py --data).",
            "stand": date.today().isoformat(), "tables": dict(sorted(result.items()))}


# --- Ausgabe ------------------------------------------------------------------------------

def _short(items: list[str], limit: int = 4) -> str:
    if not items:
        return "–"
    shown = ", ".join(f"`{i}`" for i in items[:limit])
    return shown + (f" (+{len(items) - limit})" if len(items) > limit else "")


def _daten(befund: dict | None) -> str:
    if not befund:
        return "–"
    if "mandanten" in befund:
        parts = [f"{befund['zeilen']} Z.", f"{befund['mandanten']} Mand."]
        parts += [f"{befund[k]} {k}" for k in ("null", "default", "system") if befund.get(k)]
        return ", ".join(parts)
    parts = [f"{befund['zeilen']} Z."]
    parts += [f"{befund[k]} {k}" for k in ("verwaist", "ohne_eltern") if befund.get(k)]
    return ", ".join(parts)


def render_markdown(matrix: dict) -> str:
    out = [
        "---", "title: RLS-Domain-Matrix (generiert)", "type: reference", "audience: [agent, entwickler]",
        "owner: Claude Code", "status: aktiv", "description: Generierte Entscheidungsmatrix der noch nicht "
        "abgesicherten Mandantentabellen je Domain.", "---", "",
        "# RLS-Domain-Matrix (generiert)", "",
        "Generiert von `scripts/rls_domain_matrix.py`; nicht von Hand aendern. Entscheidungen und "
        "Reihenfolge: `docs/architecture/rls-domaenen-entscheidungsmatrix.md`.", "",
        f"Datenstand gewachsene Datenbank: {matrix['datenstand'] or 'kein Befund'}. "
        f"Tabellen: {matrix['summary']['tabellen']}.", "",
        "| Domain | " + " | ".join(URSACHEN) + " |", "|---|" + "---|" * len(URSACHEN),
    ]
    for domain, counts in matrix["summary"]["nach_domain"].items():
        out.append(f"| {domain} | " + " | ".join(str(counts.get(u, "")) for u in URSACHEN) + " |")
    by_domain: dict[str, list[dict]] = defaultdict(list)
    for row in matrix["tables"]:
        by_domain[row["domain"]].append(row)
    for domain, rows in by_domain.items():
        out += ["", f"## {domain}", "",
                "| Tabelle | Kl. | Ursache | Modell | Schreiber | Leser | Worker | Identitaet | Daten | Bereinigung | Policy |",
                "|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in rows:
            ident = ", ".join(f"{k} {v}" for k, v in r["identitaet"].items()) or "–"
            out.append(
                f"| `{r['table']}` | {r['class']} | {', '.join(r['gruende'])} | {_short(r['modell'], 2)} | "
                f"{_short(r['schreiber'])} | {len(r['leser'])} | {_short(r['worker'], 2)} | {ident} | "
                f"{_daten(r['daten'])} | {'; '.join(r['bereinigung']) or '–'} | {r['policy']} |")
    return "\n".join(out) + "\n"


def _render_all() -> tuple[str, str]:
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    rollout = json.loads(ROLLOUT.read_text(encoding="utf-8"))
    data = json.loads(DATA.read_text(encoding="utf-8")) if DATA.exists() else {}
    matrix = analyse(inventory, rollout, data)
    return json.dumps(matrix, ensure_ascii=False, indent=1) + "\n", render_markdown(matrix)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--data", action="store_true", help="Datenbefund aus LIVE_DATABASE_URL lesen")
    args = parser.parse_args()
    if args.data:
        url = os.environ.get("LIVE_DATABASE_URL")
        if not url:
            print("LIVE_DATABASE_URL nicht gesetzt (gewachsene Datenbank, nur lesend).")
            return 2
        inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
        DATA.write_text(json.dumps(collect_data(url, inventory), ensure_ascii=False, indent=1) + "\n",
                        encoding="utf-8")
        print(f"Geschrieben: {DATA.relative_to(REPO_ROOT)}")
    text, markdown = _render_all()
    if args.check:
        stale = [p for p, want in ((OUTPUT, text), (MARKDOWN, markdown))
                 if not p.exists() or p.read_text(encoding="utf-8") != want]
        if stale:
            print("DRIFT: " + ", ".join(str(p.relative_to(REPO_ROOT)) for p in stale)
                  + " nicht aktuell. 'python scripts/rls_domain_matrix.py' ausfuehren.")
            return 1
        print("OK: RLS-Domain-Matrix aktuell.")
        return 0
    OUTPUT.write_text(text, encoding="utf-8")
    MARKDOWN.write_text(markdown, encoding="utf-8")
    summary = json.loads(text)["summary"]
    print(f"Geschrieben: {OUTPUT.relative_to(REPO_ROOT)} {summary['nach_klasse']} {summary['nach_ursache']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
