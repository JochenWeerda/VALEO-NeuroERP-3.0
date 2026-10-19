"""Was die CLI ausfuehren darf und wie der Aufruf aussieht — gespiegelt aus der Maskenlaufzeit.

Quelle der Regeln ist ``packages/frontend-web/src/components/mask-builder/runtime/useActionRuntime.ts`` und
``ActionRuntime.ts``. Diese Datei hat keine Abhaengigkeit zum Server: Sie laeuft auf dem Rechner der Anwenderin
und im Generator ``scripts/generate_cli_mask_commands.py``, der daraus das CLI-Register fuer die Ratsche baut.
So kann das Register nicht mehr versprechen, als die CLI tatsaechlich tut.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

MODES = ("execute", "dryRun", "validate", "propose")

#: Command-Adapter, die die CLI wie die Maske nachbaut (``valeo_cli.docflow``).
SUPPORTED_ADAPTERS = {"docflow.v1"}

#: Pfadparameter, die der generische Weg der Maske selbst einsetzt (useActionRuntime). Alle anderen gehoeren
#: einem Command-Adapter (DocFlow-Freigabe, Ernte-Regelversion) und sind hier nicht nachgebaut.
GENERIC_PATH_PARAMETERS = {"{entity_id}", "{screen_id}"}

_PLACEHOLDER = re.compile(r"\{[^}]+\}")
_DOCFLOW = re.compile(r"^/api/v1/docflow(?:/|$)")
_IDENTITY_BUDGET = re.compile(r"^/api/v1/identity/budgets/actions/(root|allocate)$")


@dataclass(frozen=True)
class Support:
    supported: bool
    reason: str | None = None


def support(action: dict[str, Any]) -> Support:
    """Kann die CLI diese Aktion so ausfuehren wie die Maske? Sonst: warum nicht."""
    if action.get("inputFlow"):
        return Support(False, "eingabe_in_maske")
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
    "eingabe_in_maske": "Diese Aktion erfordert die Eingabe und Bestaetigung in der Maske.",
    "kein_endpunkt": "Die Aktion hat keinen Kommando-Endpunkt; die Maske verdrahtet sie selbst.",
    "docflow_ohne_adapter": "DocFlow-Aktionen brauchen den versionierten Command-Adapter.",
}


def reason_text(reason: str | None) -> str:
    if reason and reason.startswith("adapter:"):
        return f"Der Command-Adapter '{reason.split(':', 1)[1]}' ist in der CLI noch nicht umgesetzt."
    if reason and reason.startswith("pfadparameter:"):
        return f"Pfadparameter {reason.split(':', 1)[1]} setzt nur ein Command-Adapter ein."
    return REASON_TEXT.get(reason or "", reason or "")


def requires_entity(action: dict[str, Any]) -> bool:
    return "{entity_id}" in (action.get("commandEndpoint") or "")


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
    endpoint = action["commandEndpoint"]
    if requires_entity(action) and not entity_id:
        raise ValueError("Diese Aktion braucht eine Objektkennung (--id).")
    path = endpoint.replace("{entity_id}", quote(entity_id or "", safe="")).replace("{screen_id}", screen_id)
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
