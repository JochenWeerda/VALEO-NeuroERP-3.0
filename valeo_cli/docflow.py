"""DocFlow-Command-Adapter (``docflow.v1``) der Belegfamilie — Zeile fuer Zeile wie die Maske.

Quelle: ``packages/frontend-web/src/components/mask-builder/runtime/docflow-command-adapter.ts`` und
``governance/condition-engine.ts``. Reine Transportanpassung, keine Fachlogik und keine Rechtevergabe: Ob eine
Aktion im Belegzustand erlaubt ist, sagt der Server in den Belegdaten (``aktionen[].erlaubt``); Rechte, Mandant,
Versionen und Wiederholungen prueft er beim Aufruf noch einmal.
"""
from __future__ import annotations

from typing import Any
from urllib.parse import quote

PATHS = {"update": "", "release": "/release", "post": "/post", "reverse": "/reverse", "convert": "/convert",
         "approval_request": "/approvals", "approval_decide": "/approvals/{approval_id}/decision"}
FIELDS = {"update": {"currency", "document_date", "source_ref", "items"}, "release": set(), "post": {"posting_date"},
          "reverse": {"reason"}, "convert": {"quantities_by_source_item_id"}, "approval_request": {"reason"},
          "approval_decide": {"note"}}


def _read_path(root: dict, path: str) -> Any:
    if path in root:
        return root[path]
    current: Any = root
    for segment in path.split("."):
        if not isinstance(current, dict) or segment not in current:
            return None
        current = current[segment]
    return current


def _present(value: Any) -> bool:
    return value is not None and value != "" and value is not False


def evaluate(condition: Any, root: dict) -> bool:
    """Wie ``evaluateCondition``: Zeichenkette = Feld vorhanden; all/any/not; path mit exists/equals/notEquals."""
    if isinstance(condition, str):
        return _present(_read_path(root, condition))
    if "all" in condition:
        return all(evaluate(c, root) for c in condition["all"])
    if "any" in condition:
        return any(evaluate(c, root) for c in condition["any"])
    if "not" in condition:
        return not evaluate(condition["not"], root)
    value = _read_path(root, condition["path"])
    if condition.get("exists") is True and not _present(value):
        return False
    if condition.get("exists") is False and _present(value):
        return False
    if "equals" in condition and value != condition["equals"]:
        return False
    if "notEquals" in condition and value == condition["notEquals"]:
        return False
    if condition.get("exists") is None and "equals" not in condition and "notEquals" not in condition:
        return _present(value)
    return True


def action_enabled(action: dict, root: dict | None) -> bool:
    if action.get("disabled"):
        return False
    if not action.get("enabledWhen"):
        return True
    return bool(root) and evaluate(action["enabledWhen"], root)


def _server_action(action: dict, data: dict) -> dict | None:
    key = action["commandBinding"].get("stateAction") or action["key"]
    available = data.get("aktionen") if isinstance(data.get("aktionen"), list) else []
    return next((candidate for candidate in available if isinstance(candidate, dict) and candidate.get("key") == key), None)


def prepare(action: dict, *, entity_id: str | None, data: dict, payload: dict, mode: str, audit_reason: str | None,
            idempotency_key: str, expected_version: int | None, is_agent: bool) -> tuple[str, str, dict]:
    binding = action.get("commandBinding") or {}
    command = binding.get("command")
    if binding.get("adapter") != "docflow.v1" or command not in PATHS:
        raise ValueError("DocFlow-Command-Adapter fehlt oder ist unbekannt.")
    if is_agent:
        raise ValueError("Schreibende DocFlow-Agentenaktionen sind nicht freigeschaltet.")
    if not entity_id:
        raise ValueError("Belegbindung fehlt oder widerspricht dem Aufruf.")
    expected_endpoint = f"/api/v1/docflow/{{entity_id}}{PATHS[command]}"
    method = "PUT" if command == "update" else "POST"
    if action.get("commandEndpoint") != expected_endpoint or (action.get("method") or "POST") != method:
        raise ValueError("DocFlow-Endpoint widerspricht dem versionierten Kommando.")
    server_action = _server_action(action, data)
    if not action_enabled(action, data) or not server_action or server_action.get("erlaubt") is not True:
        raise ValueError("Diese Aktion ist im aktuellen Belegzustand gesperrt.")
    if mode != "execute" and (command != "convert" or not binding.get("preview") or mode != "dryRun"):
        raise ValueError("Dieses DocFlow-Kommando bietet keine schreibfreie Vorschau.")
    version = expected_version if expected_version is not None else data.get("version")
    if not isinstance(version, int) or isinstance(version, bool) or version < 1:
        raise ValueError("Belegversion fehlt.")
    if data.get("version") != version:
        raise ValueError("Belegversion hat sich geaendert. Bitte erneut pruefen.")
    if set(payload) - FIELDS[command]:
        raise ValueError("Unzulaessige Eingaben fuer das DocFlow-Kommando: " + ", ".join(sorted(set(payload) - FIELDS[command])))
    body: dict[str, Any] = dict(payload)
    url = expected_endpoint.replace("{entity_id}", quote(entity_id, safe=""))
    defaults = binding.get("defaults") or {}
    if command == "approval_request":
        if defaults.get("action") not in ("post", "reverse"):
            raise ValueError("Freigabeaktion fehlt.")
        body["action"] = defaults["action"]
    elif command == "approval_decide":
        approval_id = server_action.get("approval_id")
        if (not isinstance(approval_id, str) or not approval_id or not isinstance(defaults.get("granted"), bool)
                or defaults.get("action") not in ("post", "reverse")):
            raise ValueError("Konkrete Freigabebindung fehlt.")
        url = url.replace("{approval_id}", quote(approval_id, safe=""))
        body["granted"] = defaults["granted"]
    else:
        if not 8 <= len(idempotency_key) <= 120:
            raise ValueError("Idempotenzschluessel fehlt oder ist ungueltig.")
        body["expected_version"] = version
        body["idempotency_key"] = idempotency_key
        if command == "convert":
            target = defaults.get("target_doc_type")
            if not isinstance(target, str) or not target:
                raise ValueError("Folgebelegart fehlt.")
            body["target_doc_type"] = target
            body["dry_run"] = mode == "dryRun"
        if command == "reverse":
            reason = audit_reason if audit_reason is not None else payload.get("reason")
            if not isinstance(reason, str) or len(reason.strip()) < 3 or len(reason) > 300:
                raise ValueError("Stornogrund fehlt oder ist ungueltig (--grund, 3 bis 300 Zeichen).")
            body["reason"] = reason.strip()
    return method, url, body


def result(action: dict, *, entity_id: str, data: dict, mode: str, response: Any,
           expected_version: int | None) -> dict:
    """Wie ``docflowCommandResult``: Eine Antwort ausserhalb des Vertrags ist kein Erfolg."""
    binding = action.get("commandBinding") or {}
    command = binding.get("command")
    body = response if isinstance(response, dict) else {}
    if command == "update":
        version = expected_version if expected_version is not None else data.get("version")
        if (body.get("id") != entity_id or body.get("status") != "draft" or not isinstance(version, int)
                or body.get("version") != version + 1 or not isinstance(body.get("items"), list)):
            return {"success": False, "error": "Bearbeitungsantwort entspricht nicht dem Belegvertrag."}
        return {"success": True, "summary": f"Belegentwurf gespeichert (Version {body['version']}).",
                "affectedIds": [str(body["id"])]}
    if command in ("approval_request", "approval_decide"):
        defaults = binding.get("defaults") or {}
        allowed = ["requested", "granted"] if command == "approval_request" else ["granted" if defaults.get("granted") else "denied"]
        approval_id = (_server_action(action, data) or {}).get("approval_id")
        if (not isinstance(body.get("id"), str) or body.get("status") not in allowed or body.get("action") != defaults.get("action")
                or command == "approval_decide" and body.get("id") != approval_id):
            return {"success": False, "error": "Freigabeantwort entspricht nicht dem Aufrufvertrag."}
        return {"success": True, "summary": "Freigabe angefragt." if command == "approval_request"
                else "Freigabe erteilt." if defaults.get("granted") else "Freigabe abgelehnt."}
    expected_status = "dry_run" if mode == "dryRun" else "ok"
    if body.get("command") != command or body.get("status") != expected_status or body.get("source_doc_id") != entity_id:
        return {"success": False, "error": "DocFlow-Antwort entspricht nicht dem Aufrufvertrag."}
    ids = [body.get(k) for k in ("source_doc_id", "target_doc_id", "posting_id") if isinstance(body.get(k), str) and body.get(k)]
    summary = ("Folgebeleg-Vorschau ohne Speicherung: Positionen "
               f"{(body.get('payload') or {}).get('item_count', '')}" if mode == "dryRun" else "Belegaktion abgeschlossen.")
    return {"success": True, "summary": summary, "affectedIds": ids}


def entity_endpoint(definition: dict, entity_id: str) -> str:
    source = next((ds for ds in definition.get("dataSources") or [] if ds.get("key") == "entity"), None)
    if not source or "{entity_id}" not in source.get("endpoint", ""):
        raise ValueError("Die Maske hat keine Belegquelle fuer den Belegzustand.")
    return source["endpoint"].replace("{entity_id}", quote(entity_id, safe=""))
