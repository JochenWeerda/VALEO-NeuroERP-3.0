"""Masken im Screen Studio erzeugen — ``python -m valeo_cli studio <befehl>``.

Die CLI bedient dieselbe Studio-API wie die Studio-App (``/api/v1/studio``). Sie erfindet keinen eigenen Weg:
Vorschlag, Pruefung, Entwurf, Uebernahme vorhandener Masken, Vier-Augen-Pruefung, Simulation, Freigabe und
Rueckzug bleiben Entscheidungen des Servers mit seinen Rechten (Gestalten: Belegschreibrecht; Freigeben und
Zurueckziehen: menschliche Administration), seiner Revisionspruefung und seiner Historie.

Schutz vor verlorenen Aenderungen: Aendern und Freigeben verlangen die Revision, die man gesehen hat
(``--revision``). Pruefung, Simulation und Rueckzug nehmen ohne Angabe die aktuelle Revision und nennen sie.
Jeder schreibende Aufruf traegt einen Wiederholungsschluessel; ``--idempotenz`` wiederholt einen Aufruf.
"""
from __future__ import annotations

import json
import re
import uuid
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlencode

STUDIO = "/api/v1/studio"


def _key(args) -> str:
    return args.idempotenz or str(uuid.uuid4())


def _read_definition(path: str, stdin) -> dict[str, Any]:
    text = stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except ValueError as exc:
        raise ValueError(f"{path} ist kein gueltiges JSON: {exc}") from exc
    if isinstance(data, dict) and isinstance(data.get("definition"), dict):
        data = data["definition"]  # Ausgabe von "studio zeigen" oder "studio vorschlag" direkt weiterverwenden.
    if not isinstance(data, dict):
        raise ValueError("Die Definition muss ein JSON-Objekt sein.")
    return data


def _with_id(definition: dict[str, Any], screen_id: str | None) -> dict[str, Any]:
    """Eigene Kennung setzen; ob sie zulaessig ist ('tenant/<slug>', frei), entscheidet der Server."""
    if not screen_id:
        return definition
    renamed = {**definition, "id": screen_id}
    adapter = definition.get("adapter")
    # Die Adapterbindung zeigt auf die eigene Kennung und wandert mit; eine fremde Bindung bleibt unangetastet.
    if isinstance(adapter, dict) and adapter.get("sourceId") == definition.get("id"):
        renamed["adapter"] = {**adapter, "sourceId": screen_id}
    return renamed


def _write(path: str | None, data: dict, out: Callable[[str], None]) -> None:
    text = json.dumps(data, ensure_ascii=False, indent=2)
    if path:
        Path(path).write_text(text + "\n", encoding="utf-8")
        out(f"Definition geschrieben: {path}")
    else:
        out(text)


def _report_lines(report: dict, out: Callable[[str], None]) -> bool:
    violations = report.get("violations") or []
    all_errors = (report.get("readiness") or {}).get("errors") or []
    # Wie der Server (_report): "non_temporary" sperrt einen Studio-Entwurf nicht, er ist nur noch nicht nativ.
    errors = [e for e in all_errors if "non_temporary" not in str(e)]
    warnings = [*(f"{e} (nicht blockierend)" for e in all_errors if "non_temporary" in str(e)),
                *((report.get("readiness") or {}).get("warnings") or [])]
    ready = report.get("definitionReady")
    out(f"Definition {'bereit' if ready else 'nicht bereit'}" +
        (f" — {len(violations)} Verstoesse" if violations else "") + (f", {len(errors)} Fehler" if errors else ""))
    for item in violations:
        out(f"  Verstoss: {item if isinstance(item, str) else json.dumps(item, ensure_ascii=False)}")
    for item in errors:
        out(f"  Fehler: {item}")
    for item in warnings[:10]:
        out(f"  Hinweis: {item}")
    return bool(ready) and not violations


def _summary(record: dict) -> str:
    return (f"{record.get('id')}  {record.get('status')}  Revision {record.get('revision')}  "
            f"Maske {record.get('screen_id') or (record.get('definition') or {}).get('id')}")


def _current_revision(call, draft_id: str) -> str:
    return call("GET", f"{STUDIO}/drafts/{draft_id}")["revision"]


def _parse_columns(specs: list[str]) -> list[tuple[str, str]]:
    columns = []
    for spec in specs:
        key, _, label = spec.partition("=")
        if not key.strip():
            raise ValueError(f"--spalte erwartet feld oder feld=Bezeichnung, nicht {spec!r}")
        columns.append((key.strip(), (label or key).strip()))
    return columns


def compose(catalog: dict[str, Any], *, screen_id: str, title: str, domain: str, source_key: str,
            columns: list[tuple[str, str]], action_keys: list[str], density: str = "compact") -> dict[str, Any]:
    """Arbeitsliste ausschliesslich aus dem Server-Katalog — dieselbe Form wie der Studio-Vorschlag.

    Keine freie Adresse und keine eigene Aktion: Quelle und Aktionen muessen im Katalog stehen, Gefahrenstufe und
    Agentensperre kommen unveraendert aus ihm. Spalten sind nur lesbar; was gilt, entscheidet die Servervalidierung.
    """
    sources = {ds["key"]: ds for ds in catalog.get("dataSources") or []}
    actions = {a["key"]: a for a in catalog.get("actions") or []}
    if source_key not in sources:
        raise ValueError(f"Datenquelle {source_key!r} steht nicht im Studio-Katalog ({', '.join(sorted(sources))}).")
    unknown = [key for key in action_keys if key not in actions]
    if unknown:
        raise ValueError(f"Aktion {', '.join(unknown)} steht nicht im Studio-Katalog ({', '.join(sorted(actions))}).")
    if not columns:
        raise ValueError("Mindestens eine --spalte angeben.")
    source = sources[source_key]
    chosen = [actions[key] for key in action_keys]
    screen_actions = [{"key": a["key"], "label": a.get("label", a["key"]), "dangerLevel": a["dangerLevel"],
                       "commandEndpoint": a.get("commandEndpoint"), "forbiddenForAgents": a.get("forbiddenForAgents", False),
                       "requiresConfirmation": a["dangerLevel"] != "safe", "permission": "studio.draft.execute"}
                      for a in chosen]
    slug = screen_id.split("/", 1)[-1]
    return {
        "schemaVersion": 1, "id": screen_id, "domain": domain, "mode": "list", "title": title, "subtitle": title,
        "adapter": {"type": "native", "sourceId": screen_id, "temporary": True},
        "dataSources": [{"key": source["key"], "endpoint": source["endpoint"], "pageSize": 50}],
        "layout": {"floorplan": "worklist", "columnNavigation": "listDetail", "density": density,
                   "contextRail": "none", "tableProfile": "financial" if domain == "finance" else "standard"},
        "tables": [{"key": "list", "label": title, "dataSourceKey": source["key"], "serverPagination": True,
                    "pageSize": 25, "virtualized": True, "rowHeight": 44,
                    "columns": [{"key": key, "label": label, "sortable": True, "filterable": True} for key, label in columns]}],
        "actions": screen_actions,
        "noWorkflowReason": "Studio-Worklist priorisiert Auswahl; Statuswechsel bleiben auf der ObjectPage.",
        "agentContract": {
            "screenId": screen_id, "domain": domain, "schemaVersion": 1, "contractVersion": 1,
            "businessPurpose": title, "primaryEntity": slug,
            "readableFields": [key for key, _ in columns], "editableFields": [], "sensitiveFields": [],
            "availableActions": [{"key": a["key"], "label": a["label"], "dangerLevel": a["dangerLevel"],
                                  "requiresHumanApproval": a["forbiddenForAgents"],
                                  "requiresConfirmation": a["requiresConfirmation"], "permission": a["permission"]}
                                 for a in screen_actions],
            "validationRules": [], "workflowRules": [], "auditRequirements": [],
            "recommendedAgentTasks": [f"{title} filtern und auswerten"], "forbiddenAgentTasks": [],
            "testSelectors": {"screenRoot": f"[data-testid='screen-{screen_id}']",
                              "submitButton": "[data-testid='form-submit-btn']",
                              "workflowPanel": "[data-testid='workflow-panel']"},
            "examplePrompts": [title],
        },
    }


def _all_sources(call, query: str = "") -> list[dict[str, str]]:
    """Read all pages; an incomplete or changing inventory is never a migration plan."""
    rows = []
    seen = set()
    total = None
    while total is None or len(rows) < total:
        page = call("GET", f"{STUDIO}/native-sources?" + urlencode({"q": query, "skip": len(rows), "limit": 100}))
        count = page.get("total")
        items = page.get("items")
        if type(count) is not int or count < 0 or not isinstance(items, list):
            raise ValueError("Ungueltiges Quelleninventar.")
        if total is not None and count != total:
            raise ValueError("Quelleninventar waehrend der Planung geaendert; erneut planen.")
        total = count
        if len(rows) + len(items) > total or (not items and len(rows) < total):
            raise ValueError("Unvollstaendiges Quelleninventar.")
        for row in items:
            if not isinstance(row, dict):
                raise ValueError("Ungueltige Maskenquelle.")
            source_id, stamp = row.get("screen_id"), row.get("source_hash")
            if (not isinstance(source_id, str) or not source_id or len(source_id) > 200
                    or not isinstance(stamp, str) or not re.fullmatch(r"[0-9a-f]{64}", stamp)
                    or source_id in seen):
                raise ValueError("Ungueltige oder doppelte Maskenquelle.")
            seen.add(source_id)
            rows.append({"screen_id": source_id, "source_hash": stamp, "title": str(row.get("title") or source_id)})
    return sorted(rows, key=lambda row: row["screen_id"])


def _bulk_import(args, call, out) -> int:
    if args.protokoll and Path(args.protokoll).resolve() == Path(args.datei).resolve():
        raise ValueError("Protokoll darf den Migrationsplan nicht ueberschreiben.")
    plan = json.loads(Path(args.datei).read_text(encoding="utf-8"))
    if not isinstance(plan, dict) or plan.get("schemaVersion") != 1:
        raise ValueError("Unbekanntes Migrationsplanformat.")
    try:
        batch = uuid.UUID(plan["batch_id"])
    except (KeyError, ValueError, TypeError, AttributeError) as exc:
        raise ValueError("Migrationsplan braucht eine gueltige batch_id.") from exc
    query, sources = plan.get("query"), plan.get("sources")
    if not isinstance(query, str) or len(query) > 100 or not isinstance(sources, list):
        raise ValueError("Ungueltiger Migrationsplan.")
    # Compare complete source snapshots before the first write. Server repeats the hash check per import.
    current = _all_sources(call, query)
    expected = [{"screen_id": row["screen_id"], "source_hash": row["source_hash"]} for row in current]
    if sources != expected:
        raise ValueError("Quellenbestand oder Quellhash seit Planung geaendert; keine Uebernahme ausgefuehrt.")
    results = []
    for source in sources:
        key = str(uuid.uuid5(batch, source["screen_id"] + ":" + source["source_hash"]))
        record = call("POST", f"{STUDIO}/native-imports", {"screen_id": source["screen_id"],
                       "expected_source_hash": source["source_hash"], "idempotency_key": key})
        results.append({"source_id": source["screen_id"], "draft_id": record["id"],
                        "revision": record["revision"], "status": record["status"]})
        if args.protokoll:
            # Replays return the original record; the server, not this local journal, owns progress.
            _write(args.protokoll, {"batch_id": str(batch), "results": results}, lambda _: None)
        out("Ausgangsfassung uebernommen: " + _summary(record))
    out(f"{len(results)} Ausgangsfassungen versioniert; Aktivierung und Freigabe unveraendert.")
    return 0


def run(args, call, out, stdin) -> int:
    """``call(method, path, body=None)`` liefert JSON oder wirft (Anmeldung, 404, Serverfehler)."""
    cmd = args.studio_befehl
    if cmd == "katalog":
        catalog = call("GET", f"{STUDIO}/catalog")
        rights = catalog.get("permissions") or {}
        out(f"Katalog {catalog.get('version')}: {len(catalog.get('dataSources') or [])} Datenquellen, "
            f"{len(catalog.get('actions') or [])} Kommandoaktionen; gestalten "
            f"{'ja' if rights.get('canDesign') else 'nein'}, freigeben {'ja' if rights.get('canPublish') else 'nein'}")
        if args.json:
            out(json.dumps(catalog, ensure_ascii=False, indent=2))
        return 0
    if cmd == "quellen":
        rows = _all_sources(call, args.suche or "")
        for row in rows:
            out(f"  {row['screen_id']:<48} {row['title']}")
        out(f"{len(rows)} vorhandene Masken uebernehmbar.")
        return 0
    if cmd == "entitaet-uebernehmen":
        if not re.fullmatch(r'studio_[a-z][a-z0-9_]{0,27}',args.name):
            raise ValueError("Ungueltige Studio-Entitaetskennung.")
        registered=call("GET",f"{STUDIO}/entity-definitions/{args.name}")
        record=call("POST",f"{STUDIO}/drafts",{
            "definition":registered["definition"],"idempotency_key":_key(args)})
        _write(args.ausgabe,record,out)
        return 0
    if cmd in {"entitaet-generieren", "entitaet-erweitern"}:
        endpoint = "entity-extension-bundle" if cmd == "entitaet-erweitern" else "entity-bundle"
        report = call("POST", f"{STUDIO}/{endpoint}", _read_definition(args.datei, stdin))
        _write(args.ausgabe, report, out)
        return 0
    if cmd == "plan-speichern":
        changes = json.loads(Path(args.schema).read_text(encoding="utf-8")) if args.schema else []
        if not isinstance(changes, list):
            raise ValueError("Schemaauftrag muss eine Liste sein.")
        report = call("POST", f"{STUDIO}/drafts/{str(uuid.UUID(args.entwurf))}/migration-plan", {
            "expected_revision": args.revision, "idempotency_key": _key(args), "schema_changes": changes})
        _write(args.ausgabe, report, out)
        return 0
    if cmd == "migrationsentwurf":
        body = json.loads(Path(args.datei).read_text(encoding="utf-8"))
        if not isinstance(body, dict):
            raise ValueError("Migrationsauftrag muss ein JSON-Objekt sein.")
        report = call("POST", f"{STUDIO}/migration-plan", body)
        _write(args.ausgabe, report, out)
        return 0
    if cmd == "migrationsplan":
        target = Path(args.ausgabe)
        if target.exists():
            raise ValueError("Migrationsplan existiert bereits; fuer Wiederaufnahme denselben Plan verwenden.")
        rows = _all_sources(call, args.suche or "")
        plan = {"schemaVersion": 1, "batch_id": str(uuid.uuid4()), "query": args.suche or "",
                "sources": [{"screen_id": row["screen_id"], "source_hash": row["source_hash"]} for row in rows]}
        try:
            with target.open("x", encoding="utf-8") as handle:
                handle.write(json.dumps(plan, ensure_ascii=False, indent=2) + "\n")
        except FileExistsError as exc:
            raise ValueError("Migrationsplan wurde zwischenzeitlich angelegt; vorhandenen Plan verwenden.") from exc
        out(f"Definition geschrieben: {target}")
        out(f"{len(rows)} Quellen geplant; noch keine Maske importiert oder aktiviert.")
        return 0
    if cmd == "stapel-uebernehmen":
        return _bulk_import(args, call, out)
    if cmd == "uebernehmen":
        rows = call("GET", f"{STUDIO}/native-sources?" + urlencode({"q": args.maske, "limit": 100})).get("items", [])
        source = next((row for row in rows if row["screen_id"] == args.maske), None)
        if source is None:
            raise ValueError(f"Keine uebernehmbare Maske {args.maske!r}.")
        record = call("POST", f"{STUDIO}/native-imports", {
            "screen_id": args.maske, "expected_source_hash": source["source_hash"], "idempotency_key": _key(args)})
        out("Uebernommen: " + _summary(record))
        return 0
    if cmd == "vorschlag":
        report = call("POST", f"{STUDIO}/propose", {"intent": args.absicht})
        if args.maske:
            report = call("POST", f"{STUDIO}/validate", {"definition": _with_id(report["definition"], args.maske)})
        ready = _report_lines(report, out)
        if args.speichern:
            if not ready and report.get("violations"):
                out("Nicht gespeichert: Der Vorschlag hat Verstoesse.")
                return 1
            record = call("POST", f"{STUDIO}/drafts", {"definition": report["definition"], "idempotency_key": _key(args)})
            out("Entwurf angelegt: " + _summary(record))
        if args.ausgabe or not args.speichern:
            _write(args.ausgabe, report["definition"], out)
        return 0
    if cmd == "neu":
        definition = compose(call("GET", f"{STUDIO}/catalog"), screen_id=args.maske, title=args.titel,
                             domain=args.domaene, source_key=args.quelle, columns=_parse_columns(args.spalte),
                             action_keys=args.aktion, density=args.dichte)
        report = call("POST", f"{STUDIO}/validate", {"definition": definition})
        ready = _report_lines(report, out)
        if args.ausgabe:
            _write(args.ausgabe, report["definition"], out)
        if not args.speichern:
            return 0 if ready else 1
        if report.get("violations"):
            out("Nicht gespeichert: Die Definition hat Verstoesse.")
            return 1
        record = call("POST", f"{STUDIO}/drafts", {"definition": report["definition"], "idempotency_key": _key(args)})
        out("Entwurf angelegt: " + _summary(record))
        return 0
    if cmd == "pruefen":
        report = call("POST", f"{STUDIO}/validate", {"definition": _read_definition(args.datei, stdin)})
        return 0 if _report_lines(report, out) else 1
    if cmd == "entwuerfe":
        for record in call("GET", f"{STUDIO}/drafts").get("drafts", []):
            out("  " + _summary(record))
        return 0
    if cmd == "zeigen":
        record = call("GET", f"{STUDIO}/drafts/{args.entwurf}")
        out(_summary(record))
        if args.ausgabe:
            _write(args.ausgabe, record["definition"], out)
        return 0
    if cmd == "speichern":
        definition = _with_id(_read_definition(args.datei, stdin), args.maske)
        if args.entwurf:
            if not args.revision:
                raise ValueError("Aendern braucht die gesehene Revision (--revision, siehe 'studio zeigen').")
            record = call("PUT", f"{STUDIO}/drafts/{args.entwurf}", {
                "definition": definition, "expected_revision": args.revision, "idempotency_key": _key(args)})
        else:
            record = call("POST", f"{STUDIO}/drafts", {"definition": definition, "idempotency_key": _key(args)})
        out("Gespeichert: " + _summary(record))
        _report_lines(record, out)
        return 0
    if cmd == "historie":
        rows = call("GET", f"{STUDIO}/drafts/{args.entwurf}/history-view?limit=100")
        for row in rows.get("items", []):
            sim = f"  Simulation {row['simulation_result']}" if row.get("simulation_result") else ""
            out(f"  {row['recorded_at']}  {row['action']:<14} {row['actor']:<38} {row['revision'][:12]}"
                f"{'  aktiv' if row.get('active') else ''}{sim}")
        return 0
    transitions = {"pruefung": "submit-review", "simulieren": "simulate", "freigeben": "publish", "zurueckziehen": "retire"}
    if cmd in transitions:
        if cmd == "freigeben" and not args.revision:
            raise ValueError("Freigeben braucht die gepruefte Revision (--revision): freigegeben wird nur, was man gesehen hat.")
        revision = args.revision or _current_revision(call, args.entwurf)
        record = call("POST", f"{STUDIO}/drafts/{args.entwurf}/{transitions[cmd]}",
                      {"expected_revision": revision, "idempotency_key": _key(args)})
        if cmd == "simulieren":
            sim = record.get("simulation") or {}
            out(f"Simulation {'bestanden' if sim.get('passed') else 'nicht bestanden'} (Profil {sim.get('profile')})"
                + (f": {', '.join(sim.get('failed_checks') or [])}" if sim.get("failed_checks") else "")
                + (f" — {sim['error']}" if sim.get("error") else ""))
            return 0 if sim.get("passed") else 1
        out(f"{cmd.capitalize()}: " + _summary(record) + (f"  Route {record['route']}" if record.get("route") else ""))
        return 0
    raise ValueError(f"Unbekannter Studio-Befehl {cmd!r}")


def add_parser(sub) -> None:
    studio = sub.add_parser("studio", help="Masken im Screen Studio erzeugen, pruefen und freigeben")
    s = studio.add_subparsers(dest="studio_befehl", required=True)

    def with_key(p):
        p.add_argument("--idempotenz", metavar="SCHLUESSEL", help="Wiederholung mit demselben Schluessel")
        return p

    k = s.add_parser("katalog", help="Datenquellen, Kommandoaktionen und eigene Studio-Rechte")
    k.add_argument("--json", action="store_true")
    q = s.add_parser("quellen", help="Vorhandene Masken, die als Ausgangsfassung uebernehmbar sind")
    q.add_argument("suche", nargs="?")
    registered = with_key(s.add_parser("entitaet-uebernehmen", help="Registrierte Stammdatenmaske ohne Paketbearbeitung als Studio-Entwurf speichern"))
    registered.add_argument("name", help="Registrierte Studio-Entitaetskennung")
    registered.add_argument("--ausgabe", metavar="DATEI")
    extension = s.add_parser("entitaet-erweitern", help="Registrierte Studio-Stammdaten additiv erweitern (nur Paket)")
    extension.add_argument("datei", help="JSON mit name, expected_contract_hash und nullable columns")
    extension.add_argument("--ausgabe", metavar="DATEI")
    entity = s.add_parser("entitaet-generieren", help="Schema, Commands und Maske aus einem Stammdatenvertrag generieren")
    entity.add_argument("datei")
    entity.add_argument("--ausgabe")
    saved = with_key(s.add_parser("plan-speichern", help="Migrationsplan an gespeicherte Entwurfsrevision binden"))
    saved.add_argument("entwurf")
    saved.add_argument("--revision", required=True)
    saved.add_argument("--schema", metavar="DATEI", help="Optionale Liste additiver Schemaaenderungen")
    saved.add_argument("--ausgabe", metavar="DATEI")
    proposal = s.add_parser("migrationsentwurf", help="Funktionen verdrahten und versionierte Schemaartefakte planen")
    proposal.add_argument("datei", help="JSON mit definition und optional schema_changes")
    proposal.add_argument("--ausgabe", metavar="DATEI", help="Servergeprueften Plan samt Alembic-Quelltext speichern")
    mp = s.add_parser("migrationsplan", help="Alle registrierten Quellen hashgebunden fuer Stapeluebernahme planen")
    mp.add_argument("--suche", default="", help="Quellen nach Kennung/Bezeichnung einschraenken")
    mp.add_argument("--ausgabe", required=True, metavar="DATEI")
    bulk = s.add_parser("stapel-uebernehmen", help="Geplante Quellen als Studio-Ausgangsfassungen versionieren")
    bulk.add_argument("datei", help="Unveraenderter Migrationsplan; fuer Wiederaufnahme erneut verwenden")
    bulk.add_argument("--protokoll", metavar="DATEI", help="Fortschritt ohne Zugangsdaten protokollieren")
    u = with_key(s.add_parser("uebernehmen", help="Vorhandene Maske als versionierten Studio-Entwurf uebernehmen"))
    u.add_argument("maske")
    v = with_key(s.add_parser("vorschlag", help="Maskenvorschlag aus einer fachlichen Absicht"))
    v.add_argument("absicht")
    v.add_argument("--speichern", action="store_true", help="Vorschlag sofort als Entwurf anlegen")
    v.add_argument("--maske", metavar="tenant/KENNUNG", help="Eigene Maskenkennung statt der vorgeschlagenen")
    v.add_argument("--ausgabe", metavar="DATEI", help="Definition in Datei schreiben")
    n = with_key(s.add_parser("neu", help="Arbeitsliste gezielt aus Katalogquelle, Spalten und Katalogaktionen"))
    n.add_argument("--maske", required=True, metavar="tenant/KENNUNG")
    n.add_argument("--titel", required=True)
    n.add_argument("--domaene", required=True, help="Fachdomaene, z. B. agrar, einkauf, finance, crm")
    n.add_argument("--quelle", required=True, help="Datenquelle aus 'studio katalog --json'")
    n.add_argument("--spalte", action="append", default=[], metavar="FELD[=Bezeichnung]")
    n.add_argument("--aktion", action="append", default=[], metavar="KATALOGAKTION")
    n.add_argument("--dichte", choices=("comfortable", "compact", "expertDense"), default="compact")
    n.add_argument("--speichern", action="store_true", help="Als Entwurf anlegen, wenn ohne Verstoss")
    n.add_argument("--ausgabe", metavar="DATEI")
    p = s.add_parser("pruefen", help="Definition gegen Katalog und Gates pruefen, ohne zu speichern")
    p.add_argument("datei", help="JSON-Datei oder - fuer stdin")
    s.add_parser("entwuerfe", help="Studio-Entwuerfe des Mandanten")
    z = s.add_parser("zeigen", help="Entwurf mit Revision; optional Definition in Datei")
    z.add_argument("entwurf")
    z.add_argument("--ausgabe", metavar="DATEI")
    w = with_key(s.add_parser("speichern", help="Definition als neuen Entwurf anlegen oder Entwurf aendern"))
    w.add_argument("datei", help="JSON-Datei oder - fuer stdin")
    w.add_argument("--entwurf", help="Bestehenden Entwurf aendern")
    w.add_argument("--maske", metavar="tenant/KENNUNG", help="Maskenkennung in der Definition setzen")
    w.add_argument("--revision", help="Gesehene Revision (Pflicht beim Aendern)")
    h = s.add_parser("historie", help="Unveraenderliche Revisionshistorie")
    h.add_argument("entwurf")
    for name, text in (("pruefung", "Zur Vier-Augen-Pruefung geben"), ("simulieren", "Prozesskette pruefen"),
                       ("freigeben", "Freigeben (menschliche Administration)"),
                       ("zurueckziehen", "Freigegebene Maske zurueckziehen")):
        t = with_key(s.add_parser(name, help=text))
        t.add_argument("entwurf")
        t.add_argument("--revision", help="Gesehene Revision" + (" (Pflicht)" if name == "freigeben" else ""))
