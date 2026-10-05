"""Governance fuer ScreenDefinition 1.

Floorplan, Modus und Spaltennavigation bleiben das gespeicherte Vokabular.
Abgeleitete Typen, Befehle und UX-Regeln pruefen diese Definition. Sie erzeugen
kein zweites Format.
"""

from __future__ import annotations

from typing import Any

SCREEN_SCHEMA_VERSION = 1

FLOORPLANS = frozenset({
    "worklist",
    "objectPage",
    "transaction",
    "cockpit",
    "wizard",
    "analyticalList",
})

FIELD_TYPES = frozenset({
    "text",
    "number",
    "date",
    "datetime",
    "boolean",
    "select",
    "multiselect",
    "textarea",
    "file",
    "lookup",
    "table",
    "currency",
    "percentage",
})

PRIMITIVE_BY_FIELD_TYPE = {
    "text": "TextField",
    "textarea": "TextField",
    "number": "NumberField",
    "currency": "NumberField",
    "percentage": "NumberField",
    "date": "DateField",
    "datetime": "DateTimeField",
    "select": "Select",
    "lookup": "EntityPicker",
    "multiselect": "MultiEntityPicker",
    "boolean": "Checkbox",
    "file": "FileField",
    "table": "DataTable",
}

REJECTED_KEYS = ("screenType", "listReport", "form")

REFERENCE_COMMANDS: dict[str, frozenset[str]] = {
    "logistik/tourenplanung": frozenset({
        "tour.openWorkspace",
        "tour.resolveDeliveryNote",
        "tour.create",
        "tour.openLoading",
        "tour.showHints",
        "tour.cancel",
    }),
    "transporte/fahrer": frozenset({
        "driver.create",
        "driver.openAvailable",
        "driver.openTours",
        "driver.openDocuments",
        "driver.export",
    }),
    "fuhrpark/fahrzeuge": frozenset({"vehicle.create"}),
}


def derived_screen_type(definition: dict[str, Any]) -> str | None:
    layout = definition.get("layout") or {}
    floorplan = layout.get("floorplan")
    column_navigation = layout.get("columnNavigation")
    if column_navigation in ("listDetail", "listDetailDetail") and floorplan in ("worklist", "objectPage"):
        return "MASTER_DETAIL"
    if floorplan == "worklist":
        return "WORKLIST"
    if floorplan == "objectPage":
        return "DETAIL"
    if floorplan in ("transaction", "wizard"):
        return "PROCESS"
    if floorplan == "cockpit":
        return "DASHBOARD"
    if floorplan == "analyticalList":
        return "REPORT"
    if definition.get("mode") == "list":
        return "WORKLIST"
    return None


def _fields(definition: dict[str, Any]) -> list[dict[str, Any]]:
    fields = list(definition.get("fields") or [])
    for tab in definition.get("tabs") or []:
        fields.extend(tab.get("fields") or [])
    return [field for field in fields if isinstance(field, dict)]


def _tables(definition: dict[str, Any]) -> list[dict[str, Any]]:
    tables = list(definition.get("tables") or [])
    for tab in definition.get("tabs") or []:
        tables.extend(tab.get("tables") or [])
    return [table for table in tables if isinstance(table, dict)]


def _actions(definition: dict[str, Any]) -> list[dict[str, Any]]:
    actions = [action for action in (definition.get("actions") or []) if isinstance(action, dict)]
    for table in _tables(definition):
        actions.extend(action for action in (table.get("rowActions") or []) if isinstance(action, dict))
    return actions


def _condition_errors(condition: Any, label: str) -> list[str]:
    if isinstance(condition, str):
        return [] if condition.strip() else [f"{label} enabledWhen is empty"]
    if not isinstance(condition, dict):
        return [f"{label} enabledWhen is invalid"]
    if "all" in condition:
        errors: list[str] = []
        for entry in condition.get("all") or []:
            errors.extend(_condition_errors(entry, label))
        return errors
    if "any" in condition:
        errors = []
        for entry in condition.get("any") or []:
            errors.extend(_condition_errors(entry, label))
        return errors
    if "not" in condition:
        return _condition_errors(condition.get("not"), label)
    if not str(condition.get("path") or "").strip():
        return [f"{label} enabledWhen requires a path"]
    return []


def validate_screen_definition(definition: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in REJECTED_KEYS:
        if key in definition:
            errors.append(f"{key} is not a screen definition field; use layout.floorplan")
    if definition.get("schemaVersion") != SCREEN_SCHEMA_VERSION:
        errors.append(f"schemaVersion must be {SCREEN_SCHEMA_VERSION}")
    for required in ("id", "domain", "mode", "title"):
        if not str(definition.get(required) or "").strip():
            errors.append(f"{required} is required")
    layout = definition.get("layout") or {}
    floorplan = layout.get("floorplan")
    if floorplan not in FLOORPLANS:
        errors.append(f"layout.floorplan is invalid: {floorplan}")
    if derived_screen_type(definition) is None:
        errors.append("screen type cannot be derived from floorplan and mode")

    field_keys: set[str] = set()
    for field in _fields(definition):
        key = str(field.get("key") or "").strip()
        if not key:
            errors.append("field key is required")
            continue
        if key in field_keys:
            errors.append(f"field is duplicated: {key}")
        field_keys.add(key)
        field_type = field.get("type")
        if field_type not in FIELD_TYPES:
            errors.append(f"field {key} has unknown component: {field_type}")

    data_sources = {
        source.get("key")
        for source in (definition.get("dataSources") or [])
        if isinstance(source, dict) and source.get("key")
    }
    for field in _fields(definition):
        source = field.get("dataSourceKey")
        if source and source not in data_sources:
            errors.append(f"field {field.get('key')} references unknown data source {source}")
    for table in _tables(definition):
        source = table.get("dataSourceKey")
        if source and source not in data_sources:
            errors.append(f"table {table.get('key')} references unknown data source {source}")
        column_keys: set[str] = set()
        for column in table.get("columns") or []:
            if not isinstance(column, dict):
                continue
            column_key = str(column.get("key") or "").strip()
            if column_key in column_keys:
                errors.append(f"table {table.get('key')} column is duplicated: {column_key}")
            column_keys.add(column_key)

    action_keys: set[str] = set()
    commands: list[str] = []
    for action in _actions(definition):
        key = str(action.get("key") or "").strip()
        label = f"action {key or '<unknown>'}"
        if not key:
            errors.append("action key is required")
        elif key in action_keys:
            errors.append(f"action is duplicated: {key}")
        else:
            action_keys.add(key)
        command = action.get("command")
        if command is not None:
            if not str(command).strip():
                errors.append(f"{label} command is empty")
            else:
                commands.append(str(command))
        if action.get("enabledWhen") is not None:
            errors.extend(_condition_errors(action.get("enabledWhen"), label))
        permission = action.get("permission")
        if permission is not None and not str(permission).strip():
            errors.append(f"{label} permission is empty")

    screen_id = str(definition.get("id") or "")
    expected = REFERENCE_COMMANDS.get(screen_id)
    if expected is not None:
        actual = set(commands)
        missing = sorted(expected - actual)
        unknown = sorted(actual - expected)
        if missing:
            errors.append(f"action registry missing: {', '.join(missing)}")
        if unknown:
            errors.append(f"action references unknown action registry entry: {', '.join(unknown)}")
        if len(commands) != len(actual):
            errors.append("action command is duplicated")
    return errors


def ux_lint(definition: dict[str, Any]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    screen_id = str(definition.get("id") or "")
    header_actions = [action for action in (definition.get("actions") or []) if isinstance(action, dict)]
    primaries = [action for action in header_actions if action.get("kind") == "primary"]
    if len(primaries) > 2:
        findings.append({
            "code": "UX001",
            "severity": "error",
            "message": f"{screen_id} contains {len(primaries)} primary actions.",
        })
    elif len(primaries) > 1:
        findings.append({
            "code": "UX001",
            "severity": "warning",
            "message": f"{screen_id} contains {len(primaries)} primary actions.",
        })
    elif header_actions and not primaries:
        findings.append({
            "code": "UX002",
            "severity": "warning",
            "message": f"{screen_id} has actions and no primary action.",
        })

    for field in _fields(definition):
        if field.get("required") and not str(field.get("label") or "").strip():
            findings.append({
                "code": "UX003",
                "severity": "error",
                "message": f"{screen_id} required field {field.get('key')} has no label.",
            })
        if field.get("type") == "lookup" and not field.get("minSearchChars"):
            findings.append({
                "code": "UX007",
                "severity": "warning",
                "message": f"{screen_id} EntityPicker {field.get('key')} has no search minimum.",
            })

    fields = _fields(definition)
    placement = (definition.get("layout") or {}).get("statusPlacement") or "beforeFields"
    if fields and definition.get("workflow") and placement != "afterFields":
        findings.append({
            "code": "UX004",
            "severity": "warning",
            "message": f"{screen_id} shows status before the fields it is derived from.",
        })
    if len(fields) > 8 and not definition.get("tabs"):
        findings.append({
            "code": "UX005",
            "severity": "warning",
            "message": f"{screen_id} has {len(fields)} fields and no grouping.",
        })

    for table in _tables(definition):
        columns = [column for column in (table.get("columns") or []) if isinstance(column, dict)]
        if columns and not any(column.get("filterable") for column in columns):
            findings.append({
                "code": "UX006",
                "severity": "warning",
                "message": f"{screen_id} table {table.get('key')} has no filterable column.",
            })

    for action in _actions(definition):
        if action.get("dangerLevel") in ("destructive", "critical") and not action.get("requiresConfirmation"):
            findings.append({
                "code": "UX014",
                "severity": "error",
                "message": (
                    f"{screen_id} destructive action {action.get('label') or action.get('key')} "
                    "has no confirmation policy."
                ),
            })
    return findings


def governance_errors(definition: dict[str, Any]) -> list[str]:
    return validate_screen_definition(definition) + [
        f"{finding['code']} {finding['message']}"
        for finding in ux_lint(definition)
        if finding["severity"] == "error"
    ]
