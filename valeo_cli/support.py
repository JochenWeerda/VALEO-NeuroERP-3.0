"""Was die CLI ausfuehren darf und wie der Aufruf aussieht — gespiegelt aus der Maskenlaufzeit.

Quelle der Regeln ist ``packages/frontend-web/src/components/mask-builder/runtime/useActionRuntime.ts`` und
``ActionRuntime.ts``. Diese Datei hat keine Abhaengigkeit zum Server: Sie laeuft auf dem Rechner der Anwenderin
und im Generator ``scripts/generate_cli_mask_commands.py``, der daraus das CLI-Register fuer die Ratsche baut.
So kann das Register nicht mehr versprechen, als die CLI tatsaechlich tut.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

MODES = ("execute", "dryRun", "validate", "propose")

#: Command-Adapter, die die CLI wie die Maske nachbaut (``valeo_cli.docflow``, ``valeo_cli.harvest``).
SUPPORTED_ADAPTERS = {"docflow.v1", "harvest.control.v1"}

#: Pfadparameter, die der generische Weg der Maske selbst einsetzt (useActionRuntime). Alle anderen gehoeren
#: einem Command-Adapter (DocFlow-Freigabe, Ernte-Regelversion) und sind hier nicht nachgebaut.
GENERIC_PATH_PARAMETERS = {"{entity_id}", "{screen_id}"}

_PLACEHOLDER = re.compile(r"\{[^}]+\}")
_DOCFLOW = re.compile(r"^/api/v1/docflow(?:/|$)")
_IDENTITY_BUDGET = re.compile(r"^/api/v1/identity/budgets/actions/(root|allocate)$")
_ROW_COMMANDS = {
    "/api/v1/training/onboarding/runs/{entity_id}/actions/loeschen": "expected_revision",
    "/api/v1/training/qualifications/{entity_id}/actions/loeschen": "expected_revision",
    "/api/v1/training/assignments/{entity_id}/actions/loeschen": "expected_revision",
    "/api/v1/logistik/versand/profile/{entity_id}/actions/deactivate": "expected_active",
}


def row_command(action: dict[str, Any]) -> str | None:
    return _ROW_COMMANDS.get(action.get("commandEndpoint"))


@dataclass(frozen=True)
class Support:
    supported: bool
    reason: str | None = None


def support(action: dict[str, Any]) -> Support:
    """Kann die CLI diese Aktion so ausfuehren wie die Maske? Sonst: warum nicht."""
    if "readView" in action:
        view = action["readView"]
        endpoint = view.get("endpoint") if isinstance(view, dict) else None
        safe = (isinstance(endpoint, str) and re.fullmatch(r"/api/v1/(?:[A-Za-z0-9_-]+|\{[A-Za-z_][A-Za-z0-9_]*\})(?:/(?:[A-Za-z0-9_-]+|\{[A-Za-z_][A-Za-z0-9_]*\}))*/?", endpoint)
                and len(re.findall(r"\{([^{}]+)\}", endpoint)) <= 1
                and action.get("localEffect") == "view" and action.get("method", "GET") == "GET"
                and not any(key in action for key in ("commandEndpoint", "inputFlow", "download", "commandBinding", "command"))
                and not any(re.search(r"(?:^|_)(tenant|mandant|actor|user|agent)(?:_|$)", key, re.I)
                            for key in re.findall(r"\{([^{}]+)\}", endpoint)))
        return Support(bool(safe), None if safe else "leseansicht_ungueltig")
    flow = action.get("inputFlow")
    if flow:
        # Eingabefluss der Maske: Ein Mensch sendet die Formularfelder an denselben Fachweg (nur ``execute``).
        endpoint = flow.get("submitEndpoint") if isinstance(flow, dict) else None
        if not endpoint:
            return Support(False, "eingabe_in_maske")
        unknown = set(_PLACEHOLDER.findall(endpoint)) - GENERIC_PATH_PARAMETERS
        if unknown:
            return Support(False, "pfadparameter:" + ",".join(sorted(unknown)))
        return Support(True)
    endpoint = action.get("commandEndpoint")
    if not endpoint:
        return Support(False, "kein_endpunkt")
    binding = action.get("commandBinding")
    if binding:
        adapter = binding.get("adapter", "unbekannt") if isinstance(binding, dict) else "unbekannt"
        return Support(True) if adapter in SUPPORTED_ADAPTERS else Support(False, f"adapter:{adapter}")
    if _DOCFLOW.match(endpoint):
        return Support(False, "docflow_ohne_adapter")
    unknown = set(_PLACEHOLDER.findall(endpoint)) - GENERIC_PATH_PARAMETERS
    if unknown:
        return Support(False, "pfadparameter:" + ",".join(sorted(unknown)))
    return Support(True)


REASON_TEXT = {
    "eingabe_in_maske": "Diese Aktion erfordert die Eingabe und Bestaetigung in der Maske (kein Sendeweg deklariert).",
    "leseansicht_ungueltig": "Die deklarierte Leseansicht ist nicht gültig.",
    "kein_endpunkt": "Die Aktion hat keinen Kommando-Endpunkt; die Maske verdrahtet sie selbst.",
    "docflow_ohne_adapter": "DocFlow-Aktionen brauchen den versionierten Command-Adapter.",
}


def reason_text(reason: str | None) -> str:
    if reason and reason.startswith("adapter:"):
        return f"Der Command-Adapter '{reason.split(':', 1)[1]}' ist in der CLI noch nicht umgesetzt."
    if reason and reason.startswith("pfadparameter:"):
        return f"Pfadparameter {reason.split(':', 1)[1]} setzt nur ein Command-Adapter ein."
    return REASON_TEXT.get(reason or "", reason or "")


def input_flow_endpoint(action: dict[str, Any]) -> str | None:
    flow = action.get("inputFlow")
    return flow.get("submitEndpoint") if isinstance(flow, dict) else None


def requires_entity(action: dict[str, Any]) -> bool:
    view = action.get("readView")
    if isinstance(view, dict):
        return bool(_PLACEHOLDER.search(view.get("endpoint", "")))
    return "{entity_id}" in (action.get("commandEndpoint") or input_flow_endpoint(action) or "")


def identity_budget_input(endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Wie ``identity-budget-command-adapter.ts``: nur die Felder des strengen Kontingent-Kommandos."""
    match = _IDENTITY_BUDGET.match(endpoint)
    if not match:
        return payload
    fields = ["tokens", "max_children"] + ([] if match.group(1) == "root" else ["parent", "owner", "kind", "request_id"])
    return {key: payload[key] for key in fields if key in payload}


def build_request(action: dict[str, Any], *, screen_id: str, entity_id: str | None, payload: dict[str, Any],
                  mode: str, audit_reason: str | None, idempotency_key: str | None) -> tuple[str, str, dict[str, Any]]:
    """Methode, Pfad und Koerper — derselbe Umschlag wie im generischen Zweig von useActionRuntime."""
    if mode not in MODES:
        raise ValueError(f"Unbekannter Modus {mode!r}; erlaubt: {', '.join(MODES)}")
    checked = support(action)
    if not checked.supported:
        raise ValueError(reason_text(checked.reason))
    if action.get("commandBinding"):
        raise ValueError("Adapteraktionen baut valeo_cli.docflow, nicht der generische Weg.")
    flow_endpoint = input_flow_endpoint(action)
    if flow_endpoint:
        # Das Formular der Maske sendet seine Felder ohne Aktionsumschlag; einen Trockenlauf gibt es dort nicht.
        if mode != "execute":
            raise ValueError("Eingabefluesse kennen keinen Trockenlauf; nur ausfuehren (--modus execute).")
        if requires_entity(action) and not entity_id:
            raise ValueError("Diese Aktion braucht eine Objektkennung (--id).")
        path = flow_endpoint.replace("{entity_id}", quote(entity_id or "", safe="")).replace("{screen_id}", screen_id)
        body = dict(payload)
        if audit_reason and "reason" not in body:
            body["reason"] = audit_reason
        return (action["inputFlow"].get("method") or "POST").upper(), path, body
    endpoint = action["commandEndpoint"]
    if requires_entity(action) and not entity_id:
        raise ValueError("Diese Aktion braucht eine Objektkennung (--id).")
    path = endpoint.replace("{entity_id}", quote(entity_id or "", safe="")).replace("{screen_id}", screen_id)
    row_field = row_command(action)
    if row_field:
        if mode != "execute":
            raise ValueError("Dieser Zeilenbefehl unterstuetzt keinen Trockenlauf.")
        if not idempotency_key or not idempotency_key.strip():
            raise ValueError("Wiederholungsschluessel erforderlich.")
        if set(payload) != {row_field}:
            raise ValueError(f"Genau {row_field} als gelesenen Stand angeben.")
        value = payload[row_field]
        if row_field == "expected_active":
            if value is not True:
                raise ValueError("Der gelesene Profilstand muss aktiv sein.")
            if not audit_reason or not audit_reason.strip():
                raise ValueError("Diese Aktion verlangt eine Begruendung (--grund).")
        else:
            if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
                raise ValueError("Gelesene Revision als 64 kleingeschriebene Hexzeichen erforderlich.")
            if audit_reason:
                raise ValueError("Dieser Zeilenbefehl akzeptiert keine Begruendung.")
        body = {row_field: value, "_idempotencyKey": idempotency_key}
        if row_field == "expected_active":
            body["_auditReason"] = audit_reason
        return "POST", path, body
    body: dict[str, Any] = dict(identity_budget_input(endpoint, payload))
    if mode != "execute":
        body["_mode"] = mode
    if audit_reason:
        body["_auditReason"] = audit_reason
    if idempotency_key:
        body["_idempotencyKey"] = idempotency_key
    return (action.get("method") or "POST").upper(), path, body


def policy_block(action: dict[str, Any], *, is_agent: bool) -> str | None:
    """Wie ``checkActionPolicy``: Agentensperre und menschliche Freigabe. Rechte prueft der Server."""
    if is_agent and action.get("forbiddenForAgents"):
        return f"Aktion \"{action['key']}\" ist fuer Agent-Aufrufe gesperrt."
    if is_agent and action.get("humanApprovalRequired"):
        return f"Aktion \"{action['key']}\" erfordert menschliche Genehmigung."
    if is_agent and action.get("inputFlow"):
        return f"Aktion \"{action['key']}\" ist ein Eingabefluss der Maske und Menschen vorbehalten."
    return None


def needs_confirmation(action: dict[str, Any]) -> bool:
    return bool(action.get("requiresConfirmation")) or action.get("dangerLevel") in {"high", "critical"}


def iter_actions(definition: dict[str, Any]):
    """Alle Aktionen einer ScreenDefinition, je Schluessel einmal (Kopf, Register, Tabellenzeilen)."""
    seen: set[str] = set()
    stack: list[Any] = [definition]
    while stack:
        node = stack.pop(0)
        if isinstance(node, dict):
            for key in ("actions", "rowActions", "availableActions"):
                for action in node.get(key) or []:
                    if isinstance(action, dict) and action.get("key") and action["key"] not in seen:
                        seen.add(action["key"])
                        yield action
            stack.extend(value for key, value in node.items() if key not in ("actions", "rowActions", "availableActions"))
        elif isinstance(node, list):
            stack.extend(node)


def coerce_fields(action: dict[str, Any], raw: dict[str, str]) -> dict[str, Any]:
    """``feld=wert`` aus der Kommandozeile in die deklarierten Feldtypen; Pflicht und Auswahl pruefen."""
    fields = {f["key"]: f for f in action.get("inputFields") or [] if isinstance(f, dict) and f.get("key")}
    out: dict[str, Any] = {}
    for key, value in raw.items():
        field = fields.get(key, {})
        kind = field.get("type")
        if kind in {"number", "currency", "percentage"}:
            try:
                out[key] = int(value) if re.fullmatch(r"-?\d+", value) else float(value)
            except ValueError as exc:
                raise ValueError(f"Feld {key}: Zahl erwartet, nicht {value!r}") from exc
        elif kind == "stringList":
            try:
                values=json.loads(value)
                if not isinstance(values,list) or len(values)>100 or any(not isinstance(item,str) or len(item)>200 for item in values):
                    raise ValueError("bounded text list required")
            except (ValueError,TypeError) as error:
                raise ValueError(f"Feld {key}: JSON-Textliste mit maximal 100 Eintraegen erwartet") from error
            out[key]=values
        elif kind in {"boolean", "checkbox"}:
            if value.lower() not in {"true", "false", "ja", "nein", "1", "0"}:
                raise ValueError(f"Feld {key}: ja/nein erwartet, nicht {value!r}")
            out[key] = value.lower() in {"true", "ja", "1"}
        else:
            out[key] = value
        options = [o.get("value") for o in field.get("options") or [] if isinstance(o, dict)]
        if options and out[key] not in options:
            raise ValueError(f"Feld {key}: erlaubt sind {', '.join(map(str, options))}")
    return out


def missing_required(action: dict[str, Any], payload: dict[str, Any]) -> list[str]:
    return [f["key"] for f in action.get("inputFields") or []
            if isinstance(f, dict) and f.get("required") and payload.get(f["key"]) in (None, "")]


def creation_request(definition: dict[str, Any], payload: dict[str, Any], *, idempotency_key: str | None,
                     is_agent: bool = False) -> tuple[str, dict[str, Any]]:
    """Anlage ueber den ``creation``-Block der ScreenDefinition — wie ``UniversalNativeCreatePage``.

    Es zaehlen nur die nicht schreibgeschuetzten Anlagefelder; Vorgaben der Maske gelten, leere Werte fallen weg.
    Belegfamilien (``docflow.create.v1``) legt ``ausfuehren`` ueber ihren Adapter an, nicht diese Anlage.
    Agenten duerfen anlegen (Entwicklungsphase, Nutzerentscheidung 08.11.2026, wie ``mask.action.execute``); Rechte,
    Mandant und Validierung prueft der Server. Eine fachliche Sperre der Anlage (``forbiddenForAgents``) gilt weiter.
    """
    creation = definition.get("creation")
    if not isinstance(creation, dict) or not isinstance(creation.get("endpoint"), str):
        raise ValueError("Fuer diese Maske ist keine Neuanlage freigegeben.")
    if is_agent and creation.get("forbiddenForAgents"):
        raise PermissionError("Diese Anlage ist Menschen vorbehalten (forbiddenForAgents).")
    if creation.get("adapter"):
        raise ValueError(f"Anlage ueber Adapter {creation['adapter']} nicht per CLI.")
    endpoint = creation["endpoint"]
    if not re.fullmatch(r"/api/v1(?:/[A-Za-z0-9_-]+)+/?", endpoint):
        raise ValueError("Ungueltiger Anlageweg.")
    fields = [f for f in creation.get("fields") or [] if isinstance(f, dict) and f.get("key")]
    if not fields:
        fields = [f for f in [*(definition.get("fields") or []),
                              *(f for tab in definition.get("tabs") or [] for f in tab.get("fields") or [])]
                  if isinstance(f, dict) and f.get("key")]
    allowed = {f["key"] for f in fields if not f.get("readOnly")}
    unknown = sorted(set(payload) - allowed)
    if unknown:
        raise ValueError("Unbekannte Anlagefelder: " + ", ".join(unknown))
    body = {key: value for key, value in {**(creation.get("defaults") or {}), **payload}.items()
            if key in allowed and value is not None and value != ""}
    missing = [f["key"] for f in fields if f.get("required") and not f.get("readOnly") and body.get(f["key"]) in (None, "")]
    if missing:
        raise ValueError("Pflichtfelder fehlen: " + ", ".join(missing))
    if creation.get("requiresIdempotencyKey"):
        if not idempotency_key:
            raise ValueError("Diese Anlage braucht einen Wiederholungsschluessel.")
        body["idempotency_key"] = idempotency_key
    return endpoint, body
