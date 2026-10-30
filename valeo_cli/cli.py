"""Kommandozeile: ``python -m valeo_cli <befehl>``.

    anmelden                      Device-Anmeldung im Browser
    abmelden                      Sitzung beim Provider beenden
    status                        Wer bin ich, welcher Mandant, wie lange noch
    aktionen <maske>              Aktionen einer Maske und ob die CLI sie ausfuehren kann
    zeigen <maske> <aktion>       Vertrag einer Aktion (Felder, Bestaetigung, Begruendung)
    ausfuehren <maske> <aktion>   Aktion ueber denselben Kommandoweg wie die Maske
    studio <befehl>               Masken im Screen Studio erzeugen, pruefen, freigeben (siehe valeo_cli.studio)

Exit-Codes: 0 erfolgreich, 1 fachlich abgelehnt (auch 409) oder nicht ausfuehrbar, 2 Bedienfehler, 3 Anmeldung oder Berechtigung,
4 Server oder Netz.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import uuid
from urllib.parse import quote, urlencode
from typing import Any, Callable

import httpx

from valeo_cli import auth, docflow, harvest, studio, support

DEFAULT_API = "http://localhost:8000"


class UsageError(RuntimeError):
    pass


class ServerError(RuntimeError):
    pass


class Forbidden(RuntimeError):
    """403: angemeldet, aber nicht berechtigt (Rolle, Mandant, Vier-Augen-Prinzip)."""


class Conflict(RuntimeError):
    """409: Der Server lehnt fachlich ab (veraltete Revision, schon vorhanden, falscher Zustand)."""


def _api_base() -> str:
    return os.environ.get("VALEO_API_URL", DEFAULT_API).rstrip("/")


def _detail(response: httpx.Response) -> str:
    try:
        body = response.json()
    except ValueError:
        return response.text[:300]
    detail = body.get("detail", body) if isinstance(body, dict) else body
    return detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)[:600]


def _request(http: httpx.Client, token: str, method: str, path: str, body: dict | None = None) -> Any:
    response = http.request(method, _api_base() + path, json=body,
                            headers={"Authorization": f"Bearer {token}", "Accept": "application/json"})
    if response.status_code == 401:
        raise auth.AuthError(f"Anmeldung ungueltig oder abgelaufen: {_detail(response)}")
    if response.status_code == 403:
        raise Forbidden(_detail(response))
    if response.status_code == 409:
        raise Conflict(_detail(response))
    if response.status_code == 404:
        raise UsageError(f"Nicht gefunden: {_detail(response)}")
    if response.status_code >= 400:
        raise ServerError(f"{response.status_code}: {_detail(response)}")
    return response.json() if response.content else {}


def _definition(http: httpx.Client, token: str, screen_id: str) -> dict:
    return _request(http, token, "GET", f"/api/v1/masks/{screen_id}/screen-definition")


def _action(definition: dict, key: str) -> dict:
    for action in support.iter_actions(definition):
        if action["key"] == key:
            return action
    raise UsageError(f"Maske {definition.get('id')} hat keine Aktion {key!r}.")


def _is_agent(token: str) -> bool:
    """Fail closed: Nur ein Token mit ``identity_type=human`` gilt als Mensch."""
    return auth.claims(token).get("identity_type") != "human"


def _parse_fields(pairs: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for pair in pairs:
        key, sep, value = pair.partition("=")
        if not sep or not key:
            raise UsageError(f"--feld erwartet name=wert, nicht {pair!r}")
        out[key] = value
    return out


def _read_data(source: str | None, stdin) -> dict:
    if not source:
        return {}
    text = stdin.read() if source == "-" else open(source, encoding="utf-8").read()
    try:
        data = json.loads(text)
    except ValueError as exc:
        raise UsageError(f"--daten ist kein gueltiges JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise UsageError("--daten muss ein JSON-Objekt sein.")
    return data


def cmd_aktionen(args, http, token, out) -> int:
    definition = _definition(http, token, args.maske)
    out(f"{definition.get('title', args.maske)} ({definition.get('id', args.maske)})")
    for action in support.iter_actions(definition):
        checked = support.support(action)
        flags = [flag for flag, on in (("Bestaetigung", support.needs_confirmation(action)),
                                       ("Begruendung", action.get("auditReasonRequired")),
                                       ("nur Mensch", action.get("forbiddenForAgents") or action.get("humanApprovalRequired")))
                 if on]
        state = "CLI" if checked.supported else f"-  ({support.reason_text(checked.reason)})"
        out(f"  {action['key']:<32} {action.get('label', ''):<34} {state}" + (f"  [{', '.join(flags)}]" if flags else ""))
    return 0


def cmd_zeigen(args, http, token, out) -> int:
    action = _action(_definition(http, token, args.maske), args.aktion)
    checked = support.support(action)
    out(json.dumps({
        "aktion": action["key"], "bezeichnung": action.get("label"),
        "cli": checked.supported, "grund": None if checked.supported else support.reason_text(checked.reason),
        "methode": action.get("method", "POST"), "endpunkt": action.get("commandEndpoint"),
        "braucht_id": support.requires_entity(action), "recht": action.get("permission"),
        "gefahr": action.get("dangerLevel", "safe"), "bestaetigung": support.needs_confirmation(action),
        "begruendung_pflicht": bool(action.get("auditReasonRequired")),
        "nur_mensch": bool(action.get("forbiddenForAgents") or action.get("humanApprovalRequired")),
        "felder": [{k: f.get(k) for k in ("key", "label", "type", "required", "options", "helpText") if k in f}
                   for f in action.get("inputFields") or []],
    }, ensure_ascii=False, indent=2))
    return 0


def cmd_ausfuehren(args, http, token, out, ask: Callable[[str], str], stdin) -> int:
    action = _action(_definition(http, token, args.maske), args.aktion)
    checked = support.support(action)
    if not checked.supported:
        out(f"Nicht per CLI ausfuehrbar: {support.reason_text(checked.reason)}")
        return 1
    blocked = support.policy_block(action, is_agent=_is_agent(token))
    if blocked:
        out(blocked)
        return 1
    payload = {**_read_data(args.daten, stdin), **support.coerce_fields(action, _parse_fields(args.feld))}
    if args.modus == "execute":
        missing = support.missing_required(action, payload)
        if missing:
            raise UsageError("Pflichtfelder fehlen: " + ", ".join(missing))
        if action.get("auditReasonRequired") and not (args.grund or "").strip():
            raise UsageError("Diese Aktion verlangt eine Begruendung (--grund).")
        if support.needs_confirmation(action) and not args.ja:
            answer = ask(f"{action.get('label', action['key'])} wirklich ausfuehren? [ja/nein] ")
            if answer.strip().lower() not in {"ja", "j", "yes", "y"}:
                out("Abgebrochen; nichts ausgefuehrt.")
                return 1
            args.ja = True  # bestaetigt; der Ernte-Adapter verlangt die Bestaetigung als confirm_execution
    if (action.get("commandBinding") or {}).get("adapter") == "harvest.control.v1":
        return _run_harvest(action, args, http, token, out, payload)
    if action.get("commandBinding"):
        # Belegfamilie: Zustand und Version aus derselben Belegquelle wie die Maske, dann der versionierte Adapter.
        if not args.id:
            raise UsageError("Diese Aktion braucht eine Belegkennung (--id).")
        definition = _definition(http, token, args.maske)
        data = _request(http, token, "GET", docflow.entity_endpoint(definition, args.id))
        key = args.idempotenz or str(uuid.uuid4())
        try:
            method, path, body = docflow.prepare(
                action, entity_id=args.id, data=data, payload=payload, mode=args.modus, audit_reason=args.grund,
                idempotency_key=key, expected_version=args.version, is_agent=_is_agent(token))
        except ValueError as exc:
            # Belegzustand, Version oder Bindung passen nicht: fachlich abgelehnt, nichts gesendet.
            out(f"Abgelehnt: {exc}")
            return 1
        response = (_send_retryable(http, token, method, path, body, key, out) if "idempotency_key" in body
                    else _request(http, token, method, path, body))
        result = docflow.result(action, entity_id=args.id, data=data, mode=args.modus, response=response,
                                expected_version=args.version)
        if "idempotency_key" in body:
            result["idempotenz"] = key
    else:
        generated = bool(re.fullmatch(r'/api/v1/studio/entities/studio_[a-z0-9_]+/(?:\{entity_id\}/)?actions/(?:create|update|delete)', action.get('commandEndpoint', '')))
        if action.get('requiresExpectedVersion') or (generated and action['commandEndpoint'].endswith(('/update', '/delete'))):
            version = args.version if args.version is not None else payload.get('expected_version')
            if type(version) is not int or version < 1:
                raise UsageError('Diese Aktion braucht die gelesene Version (--version).')
            if 'expected_version' in payload and payload['expected_version'] != version:
                raise UsageError('Widerspruechliche Versionsangaben.')
            payload = {**payload, 'expected_version': version}
        key = args.idempotenz or (str(uuid.uuid4()) if generated or action.get('requiresIdempotencyKey') else None)
        method, path, body = support.build_request(
            action, screen_id=args.maske, entity_id=args.id, payload=payload, mode=args.modus,
            audit_reason=args.grund, idempotency_key=key)
        result = (_send_retryable(http, token, method, path, body, key, out) if key
                  else _request(http, token, method, path, body))
        if generated and not args.idempotenz and isinstance(result, dict):
            result = {**result, 'idempotenz': key}
    if args.json:
        out(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        success = result.get("success") if isinstance(result, dict) else None
        out(("OK" if success is not False else "ABGELEHNT") + (f": {result.get('summary') or result.get('error') or ''}"
                                                              if isinstance(result, dict) else ""))
    return 1 if isinstance(result, dict) and result.get("success") is False else 0


def _send_retryable(http, token, method, path, body, key, out):
    """Unsicherer Ausgang (Netz oder 5xx nach dem Absenden): Schluessel nennen, damit die Wiederholung derselbe
    Auftrag bleibt - wie die Maske, die nach einem unsicheren Ergebnis denselben Schluessel wiederverwendet."""
    try:
        return _request(http, token, method, path, body)
    except (ServerError, httpx.HTTPError):
        out(f"Ausgang unsicher. Wiederholen mit: --idempotenz {key}")
        raise


def _run_harvest(action, args, http, token, out, payload) -> int:
    """Ernte-Steuerung: Regelfassung (--regel) und Kontrollstand der Annahme (--id) wie in der Maske laden."""
    allowed = _request(http, token, "GET", f"{harvest.CONTROL}/permissions").get("allowed_actions", [])
    if action["key"] not in allowed:
        out("Verweigert: Fuer diese Aktion fehlt die Berechtigung.")
        return 3
    selected = None
    if harvest.needs_rule(action):
        if not args.regel:
            raise UsageError("Diese Aktion braucht eine Regelfassung (--regel <Versionskennung>).")
        page = 1
        while selected is None:
            rows = _request(http, token, "GET", f"{harvest.CONTROL}/rules?limit=100&page={page}")
            items = rows.get("items", rows) if isinstance(rows, dict) else rows
            try:
                selected = harvest.find_rule(items, args.regel)
            except ValueError:
                if not items or len(items) < 100:
                    raise
                page += 1
    context = None
    if harvest.needs_acceptance(action):
        if not args.id:
            raise UsageError("Diese Aktion braucht eine Annahme (--id).")
        context = _request(http, token, "GET", f"{harvest.CONTROL}/acceptances/{quote(args.id, safe='')}/context")
        payload = {**payload, "acceptance_id": args.id}
    if args.ja:
        payload = {**payload, "confirm_execution": "confirm"}
    try:
        url, body = harvest.prepare(action, selected_rule=selected, context=context, entity_id=args.id, payload=payload,
                                    mode=args.modus, audit_reason=args.grund,
                                    idempotency_key=args.idempotenz or str(uuid.uuid4()), is_agent=_is_agent(token))
    except ValueError as exc:
        out(f"Abgelehnt: {exc}")
        return 1
    result = harvest.result(_send_retryable(http, token, "POST", url, body, body["idempotency_key"], out))
    result["idempotenz"] = body["idempotency_key"]
    out(json.dumps(result, ensure_ascii=False, indent=2) if args.json else
        ("OK" if result["success"] else "ABGELEHNT") + f": {result.get('summary') or result.get('error')}")
    return 0 if result["success"] else 1


def cmd_status(args, http, settings, out) -> int:
    token = auth.access_token(http, settings)
    c = auth.claims(token)
    remaining = int(c.get("exp", 0) - time.time())
    out(json.dumps({"benutzer": c.get("preferred_username") or c.get("sub"),
                    "mandant": c.get("tenant_id") or c.get("mandanten_id"),
                    "identitaet": c.get("identity_type") or "unbekannt (gilt als Agent)",
                    "client": c.get("azp"), "token_gueltig_s": max(remaining, 0),
                    "quelle": "VALEO_ACCESS_TOKEN" if os.environ.get("VALEO_ACCESS_TOKEN") else "Sitzung"},
                   ensure_ascii=False, indent=2))
    return 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="python -m valeo_cli", description="Maskenaktionen der VALEO NeuroERP.")
    sub = p.add_subparsers(dest="befehl", required=True)
    login = sub.add_parser("anmelden", help="Device-Anmeldung im Browser")
    login.add_argument("--kein-browser", action="store_true", help="Browser nicht automatisch oeffnen")
    sub.add_parser("abmelden", help="Sitzung beenden")
    sub.add_parser("status", help="Angemeldete Identitaet anzeigen")
    d = sub.add_parser("daten", help="Deklarierte Maskendaten mit denselben Fachrechten lesen")
    d.add_argument("maske")
    d.add_argument("quelle", help="Datenquellenschluessel aus der ScreenDefinition")
    d.add_argument("--id", help="Objektkennung fuer eine Detailquelle")
    d.add_argument("--seite", type=int, default=1)
    d.add_argument("--limit", type=int, default=50)
    d.add_argument("--suche")
    d.add_argument("--tabelle")
    d.add_argument("--vollstaendig", action="store_true", help="Vollstaendiger begrenzter Tabellenbestand")
    d.add_argument("--preset", action="append", default=[], metavar="FILTER=WERT", help="Registrierten Listenfilter auswaehlen")
    d.add_argument("--sortieren")
    d.add_argument("--richtung", choices=["asc", "desc"], default="asc")
    d.add_argument("--filter", dest="tabellenfilter", metavar="DATEI|-", help="Filterplan als JSON-Objekt")
    a = sub.add_parser("aktionen", help="Aktionen einer Maske")
    a.add_argument("maske")
    z = sub.add_parser("zeigen", help="Vertrag einer Aktion")
    z.add_argument("maske")
    z.add_argument("aktion")
    x = sub.add_parser("ausfuehren", help="Aktion ausfuehren")
    x.add_argument("maske")
    x.add_argument("aktion")
    x.add_argument("--id", help="Objektkennung fuer {entity_id}")
    x.add_argument("--feld", action="append", default=[], metavar="NAME=WERT")
    x.add_argument("--daten", metavar="DATEI|-", help="Eingabe als JSON-Objekt")
    x.add_argument("--modus", choices=support.MODES, default="execute")
    x.add_argument("--grund", help="Begruendung fuer den Nachweis")
    x.add_argument("--ja", action="store_true", help="Bestaetigung ohne Rueckfrage")
    x.add_argument("--idempotenz", metavar="SCHLUESSEL", help="Wiederholung mit demselben Schluessel")
    x.add_argument("--regel", metavar="VERSIONSKENNUNG", help="Regelfassung (Ernte-Steuerung)")
    x.add_argument("--version", type=int, help="Gesehene Belegversion (Belege); sonst die aktuelle")
    x.add_argument("--json", action="store_true", help="Antwort vollstaendig als JSON")
    studio.add_parser(sub)
    return p


def main(argv: list[str] | None = None, *, http: httpx.Client | None = None, out: Callable[[str], None] = print,
         ask: Callable[[str], str] | None = None, stdin=None) -> int:
    args = parser().parse_args(argv)
    settings = auth.Settings.from_env()
    stdin = stdin or sys.stdin
    if ask is None:
        def ask(prompt: str) -> str:
            # Ohne Antwort gilt die Rueckfrage als abgelehnt (Pipes, und Git Bash meldet trotz EOF ein Terminal).
            try:
                return input(prompt) if stdin.isatty() else ""
            except EOFError:
                return ""
    own = http is None
    # Docker Desktop can accept ::1 connections without forwarding their responses.
    # Bind only the local HTTP transport to IPv4; preserve issuer URLs and remote TLS/proxy policy.
    http = http or httpx.Client(timeout=30.0, mounts={
        "http://localhost": httpx.HTTPTransport(local_address="0.0.0.0"),
    })
    try:
        if args.befehl == "anmelden":
            session = auth.login(http, settings, announce=out, open_browser=not args.kein_browser)
            who = auth.claims(session["access_token"])
            out(f"Angemeldet als {who.get('preferred_username') or who.get('sub')}.")
            return 0
        if args.befehl == "abmelden":
            out("Abgemeldet." if auth.logout(http, settings) else "Es bestand keine Sitzung.")
            return 0
        if args.befehl == "status":
            return cmd_status(args, http, settings, out)
        token = auth.access_token(http, settings)
        if args.befehl == "daten":
            if not 1 <= args.seite <= 1000000 or not 1 <= args.limit <= 100:
                raise UsageError("Seite muss 1..1000000 und Limit 1..100 sein.")
            params = {"page": args.seite, "limit": args.limit}
            if args.vollstaendig:
                params["complete"] = "true"
            if args.preset:
                selections = {}
                for option in args.preset:
                    key, separator, value = option.partition("=")
                    if not separator or not key or not value or key in selections or len(selections) >= 8:
                        raise UsageError("Listenfilter als eindeutiges FILTER=WERT angeben.")
                    selections[key] = value
                params["preset_filters"] = json.dumps(selections, ensure_ascii=False)

            if args.id is not None:
                params["entity_id"] = args.id
            if args.suche is not None:
                params["q"] = args.suche
            if args.tabelle is not None:
                params["table_key"] = args.tabelle
            if args.sortieren is not None:
                params.update(sort=args.sortieren, sort_dir=args.richtung)
            if args.tabellenfilter is not None:
                params["filter_plan"] = json.dumps(_read_data(args.tabellenfilter, stdin), ensure_ascii=False)
            path = f"/api/v1/masks/{quote(args.maske, safe='')}/data/{quote(args.quelle, safe='')}?" + urlencode(params)
            out(json.dumps(_request(http, token, "GET", path), ensure_ascii=False, indent=2))
            return 0
        if args.befehl == "studio":
            return studio.run(args, lambda method, path, body=None: _request(http, token, method, path, body), out, stdin)
        if args.befehl == "aktionen":
            return cmd_aktionen(args, http, token, out)
        if args.befehl == "zeigen":
            return cmd_zeigen(args, http, token, out)
        return cmd_ausfuehren(args, http, token, out, ask, stdin)
    except Conflict as exc:
        out(f"Abgelehnt: {exc}")
        return 1
    except (UsageError, ValueError) as exc:
        out(f"Fehler: {exc}")
        return 2
    except Forbidden as exc:
        out(f"Verweigert: {exc}")
        return 3
    except auth.AuthError as exc:
        out(f"Anmeldung: {exc}")
        return 3
    except (ServerError, httpx.HTTPError) as exc:
        out(f"Server: {exc}")
        return 4
    finally:
        if own:
            http.close()
