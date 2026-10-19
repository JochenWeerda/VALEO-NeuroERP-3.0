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
        rows = call("GET", f"{STUDIO}/native-sources?" + urlencode({"q": args.suche or "", "limit": 100}))
        for row in rows.get("items", []):
            out(f"  {row['screen_id']:<48} {row['title']}")
        out(f"{rows.get('total', 0)} vorhandene Masken uebernehmbar.")
        return 0
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
    u = with_key(s.add_parser("uebernehmen", help="Vorhandene Maske als versionierten Studio-Entwurf uebernehmen"))
    u.add_argument("maske")
    v = with_key(s.add_parser("vorschlag", help="Maskenvorschlag aus einer fachlichen Absicht"))
    v.add_argument("absicht")
    v.add_argument("--speichern", action="store_true", help="Vorschlag sofort als Entwurf anlegen")
    v.add_argument("--maske", metavar="tenant/KENNUNG", help="Eigene Maskenkennung statt der vorgeschlagenen")
    v.add_argument("--ausgabe", metavar="DATEI", help="Definition in Datei schreiben")
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
