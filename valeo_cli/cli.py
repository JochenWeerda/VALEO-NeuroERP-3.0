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
import sys
import time
from typing import Any, Callable

import httpx

from valeo_cli import auth, studio, support

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
    method, path, body = support.build_request(
        action, screen_id=args.maske, entity_id=args.id, payload=payload, mode=args.modus,
        audit_reason=args.grund, idempotency_key=args.idempotenz)
    result = _request(http, token, method, path, body)
    if args.json:
        out(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        success = result.get("success") if isinstance(result, dict) else None
        out(("OK" if success is not False else "ABGELEHNT") + (f": {result.get('summary') or result.get('error') or ''}"
                                                              if isinstance(result, dict) else ""))
    return 1 if isinstance(result, dict) and result.get("success") is False else 0


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
    http = http or httpx.Client(timeout=30.0)
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
