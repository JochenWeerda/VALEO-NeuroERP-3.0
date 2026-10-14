"""Validate Process-Kernel read bindings against a real OpenAPI document."""
from __future__ import annotations

from typing import Any
from app.core.mcp_tool_contracts import MCPToolContract


def _schema(spec: dict[str, Any], value: dict[str, Any]) -> dict[str, Any]:
    seen: set[str] = set()
    while "$ref" in value:
        ref = value["$ref"]
        if not ref.startswith("#/components/schemas/") or ref in seen:
            raise ValueError("Unsupported or cyclic schema reference")
        seen.add(ref)
        value = spec["components"]["schemas"][ref.rsplit("/", 1)[1]]
    variants = value.get("anyOf", [])
    nonnull = [item for item in variants if item.get("type") != "null"]
    if len(nonnull) == 1:
        return _schema(spec, nonnull[0])
    return value


def check_read_binding(spec: dict[str, Any], contract: MCPToolContract) -> list[str]:
    """Reject silent GET parameter loss; POST transformations need separate proof."""
    method, path = (contract.api_endpoint or "").split(" ", 1)
    if method not in {"GET", "HEAD"}:
        return []
    item = spec.get("paths", {}).get(path, {})
    operation = item.get(method.lower())
    prefix = contract.tool_name
    if not operation:
        return [f"{prefix}: missing REST operation {method} {path}"]
    errors: list[str] = []
    if not operation.get("operationId"):
        errors.append(f"{prefix}: missing REST operationId")
    parameters = {p["name"]: p for p in item.get("parameters", []) + operation.get("parameters", [])
                  if p.get("in") in {"query", "path"}}
    declared = {p.name: p for p in contract.parameter}
    if len(declared) != len(contract.parameter):
        errors.append(f"{prefix}: duplicate tool parameter")
    for name, parameter in parameters.items():
        if parameter.get("required") and (name not in declared or not declared[name].pflicht):
            errors.append(f"{prefix}: missing required REST parameter {name}")
    for name, parameter in declared.items():
        target = parameters.get(name)
        if target is None:
            errors.append(f"{prefix}: unknown REST parameter {name}")
            continue
        schema = _schema(spec, target.get("schema", {}))
        if schema.get("type") != parameter.typ.value:
            errors.append(f"{prefix}: incompatible type for {name}")
        if "enum" in schema and (not parameter.enum_werte or not set(parameter.enum_werte).issubset(schema["enum"])):
            errors.append(f"{prefix}: incompatible enum for {name}")
        for bound in ("minimum", "maximum"):
            required = schema.get(bound)
            actual = getattr(parameter, bound)
            if required is not None and (actual is None or
                    (bound == "minimum" and actual < required) or
                    (bound == "maximum" and actual > required)):
                errors.append(f"{prefix}: weaker {bound} for {name}")
    return errors


def _expanded_schema(document: dict[str, Any], value: Any, seen: frozenset[str] = frozenset()) -> Any:
    if isinstance(value, list):
        return [_expanded_schema(document, item, seen) for item in value]
    if not isinstance(value, dict):
        return value
    if "$ref" in value:
        ref = value["$ref"]
        if not ref.startswith("#/"):
            raise ValueError("External schema reference is not allowed")
        if ref in seen:
            return {"$ref": ref.rsplit("/", 1)[-1]}
        target: Any = document
        for part in ref[2:].split("/"):
            target = target[part.replace("~1", "/").replace("~0", "~")]
        return _expanded_schema(document, target, seen | {ref})
    result = {}
    for key, item in value.items():
        if key in {"$defs", "title"}:
            continue
        if key in {"properties", "patternProperties"}:
            result[key] = {name: _expanded_schema(document, schema, seen)
                           for name, schema in item.items()}
        else:
            result[key] = _expanded_schema(document, item, seen)
    return result


def check_request_binding(spec: dict[str, Any], contract: MCPToolContract) -> list[str]:
    """Compare an explicitly canonical MCP request schema to real REST JSON input."""
    if contract.input_schema is None:
        return []
    method, path = (contract.api_endpoint or "").split(" ", 1)
    operation = spec.get("paths", {}).get(path, {}).get(method.lower(), {})
    body = operation.get("requestBody", {}).get("content", {}).get("application/json", {}).get("schema")
    if body is None:
        return [f"{contract.tool_name}: missing REST JSON request schema"]
    expected = _expanded_schema(contract.input_schema, contract.input_schema)
    actual = _expanded_schema(spec, body)
    if expected != actual:
        return [f"{contract.tool_name}: MCP/REST request schema drift"]
    return []
