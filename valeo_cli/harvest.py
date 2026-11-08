"""Ernte-Steuerungsadapter (``harvest.control.v1``) — Regel fuer Regel wie die Maske.

Quelle: ``packages/frontend-web/src/components/mask-builder/runtime/harvest-control-command-adapter.ts`` und
``features/screen-studio/HarvestControls.tsx``. Die Maske waehlt eine Regelfassung aus der Regelliste und laedt den
Kontrollstand der Annahme; die CLI tut dasselbe ausdruecklich (``--regel``, ``--id``). Weder Feldwerte noch
Sichtbarkeit ersetzen eine Genehmigung: Hashes binden an den gepruefte Stand, der Server prueft erneut.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote

BASE = "/api/v1/agrar/harvest-acceptance"
CONTROL = f"{BASE}/settlement-controls"
PATHS = {
    "approve_calculation": f"{CONTROL}/acceptances/{{acceptance_id}}/approve-calculation",
    "approve_rule": f"{CONTROL}/rules/{{version_id}}/approve",
    "attest": f"{CONTROL}/acceptances/{{acceptance_id}}/attest-measurement",
    "bind_rule": f"{CONTROL}/acceptances/{{acceptance_id}}/bind-rule",
    "calculate": f"{BASE}/{{acceptance_id}}/calculate",
    "create_rule": f"{CONTROL}/rules",
    "release": f"{BASE}/{{acceptance_id}}/release?release_status=final&create_stock_movement=true&create_credit_note=true",
    "revoke_rule": f"{CONTROL}/rules/{{version_id}}/revoke",
}
RULE_COMMANDS = {"approve_rule", "revoke_rule"}
TERMS = {"customer_id": "Kunde / Lieferant", "article_id": "Artikel", "valid_from": "Vertraglich gueltig ab",
         "valid_until": "Vertraglich gueltig bis", "source_reference": "Vertragsgrundlage / Fundstelle",
         "measurement_method": "Untersuchungsmethode", "measurement_method_version": "Methodenfassung",
         "impurities_free_pct": "Vereinbarter abzugsfreier Besatz (%)"}


def _record(value: Any) -> dict:
    return value if isinstance(value, dict) else {}


def _required(value: Any, label: str) -> str:
    if value is None or not str(value).strip():
        raise ValueError(f"{label} fehlt. Bitte Auswahl oder Eingabe ergaenzen.")
    return str(value)


def _expiry(value: Any) -> str:
    text = _required(value, "Genehmigungsfrist")
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Genehmigungsfrist ist ungueltig.") from exc
    if parsed.tzinfo is None:
        parsed = parsed.astimezone()  # wie new Date(): ohne Zone gilt die lokale Zeit
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def command(action: dict) -> str:
    binding = action.get("commandBinding") or {}
    if binding.get("adapter") != "harvest.control.v1" or binding.get("command") not in PATHS:
        raise ValueError("Unbekannter Ernte-Commandvertrag.")
    return binding["command"]


def needs_rule(action: dict) -> bool:
    return command(action) in RULE_COMMANDS | {"bind_rule"}


def needs_acceptance(action: dict) -> bool:
    return command(action) not in RULE_COMMANDS | {"create_rule"}


def prepare(action: dict, *, selected_rule: dict | None, context: dict | None, entity_id: str | None,
            payload: dict, mode: str, audit_reason: str | None, idempotency_key: str, is_agent: bool) -> tuple[str, dict]:
    cmd = command(action)
    if mode != "execute" or is_agent:
        raise ValueError("Dieser Schreibweg ist nur fuer die menschliche Bedienung freigeschaltet.")
    if action.get("commandEndpoint") != PATHS[cmd] or action.get("method") != "POST":
        raise ValueError("Endpunkt widerspricht dem Ernte-Commandvertrag.")
    if action.get("requiresConfirmation") and payload.get("confirm_execution") != "confirm":
        raise ValueError("Ausfuehrung wurde nicht bestaetigt.")
    selected = _record(selected_rule)
    definition = _record(selected.get("definition"))
    ctx = _record(context)
    state = _record(ctx.get("state"))
    acceptance = _record(state.get("acceptance"))
    body: dict[str, Any] = {"idempotency_key": idempotency_key}
    url = PATHS[cmd]
    if cmd == "create_rule":
        name = _required(payload.get("rule_id"), "Regelbezeichnung")
        body["rule_id"] = name
        body["expected_version"] = definition.get("rule_version") if definition.get("rule_id") == name else 0
        terms = {key: _required(payload.get(key), label) for key, label in TERMS.items()}
        quality = payload.get("quality_limit_pct")
        terms.update(contract_id=payload.get("contract_id") or None, quality_limit_pct=None if quality in ("", None) else quality)
        body["terms"] = terms
    elif cmd in RULE_COMMANDS:
        url = url.replace("{version_id}", quote(_required(selected.get("id"), "Ausgewaehlte Regelversion"), safe=""))
        body["expected_hash"] = _required(selected.get("content_hash"), "Regelpruefung")
        body["reason"] = _required(audit_reason if audit_reason is not None else payload.get("reason"), "Pruefvermerk")
        if cmd == "approve_rule":
            body["expires_at"] = _expiry(payload.get("expires_at"))
    else:
        acceptance_id = _required(entity_id, "Annahme")
        if acceptance.get("id") != acceptance_id or payload.get("acceptance_id") != acceptance_id:
            raise ValueError("Annahme wurde geaendert. Bitte Annahme und Nachweise neu laden.")
        url = url.replace("{acceptance_id}", quote(acceptance_id, safe=""))
        if cmd in ("bind_rule", "attest", "calculate"):
            body["expected_context_hash"] = _required(ctx.get("context_hash"), "Geladener Eingabestand")
        if cmd == "bind_rule":
            body["rule_version_id"] = _required(selected.get("id"), "Ausgewaehlte Regelversion")
        if cmd == "attest":
            body["protocol_id"] = _required(_record(state.get("protocol")).get("id"), "Messprotokoll der Annahme")
            body["expected_protocol_hash"] = _required(ctx.get("protocol_hash"), "Messprotokollstand")
            body["measurement_method"] = _required(payload.get("measurement_method"), "Untersuchungsmethode")
            body["measurement_method_version"] = _required(payload.get("measurement_method_version"), "Methodenfassung")
            body["source_reference"] = _required(payload.get("measurement_source"), "Messbericht / Nachweisquelle")
        if cmd in ("approve_calculation", "release"):
            body["expected_calculation_hash"] = _required(ctx.get("calculation_hash"), "Gepruefte Berechnungsfassung")
        if cmd == "approve_calculation":
            body["reason"] = _required(audit_reason if audit_reason is not None else payload.get("reason"), "Pruefvermerk")
            body["expires_at"] = _expiry(payload.get("expires_at"))
            body["acknowledge_quality_exception"] = payload.get("acknowledge_quality_exception") is True
    return url, body


def result(response: Any) -> dict:
    """Wie ``harvestControlResult``: ohne Nachweiskennung kein Erfolg."""
    data = _record(response)
    if not (data.get("id") or data.get("control_event_id") or data.get("acceptance_number")):
        return {"success": False, "error": "Nachweisantwort ist unvollstaendig."}
    return {"success": True, "summary": "Vorgang mit unveraenderlichem Nachweis gespeichert.", "data": data}


def find_rule(rows: Any, version_id: str) -> dict:
    items = rows.get("items", rows) if isinstance(rows, dict) else rows
    for row in items if isinstance(items, list) else []:
        if (isinstance(row, dict) and row.get("id") == version_id and isinstance(row.get("definition"), dict)
                and isinstance(row.get("content_hash"), str)):
            return row
    raise ValueError(f"Regelfassung {version_id!r} steht nicht in der Regelliste.")
