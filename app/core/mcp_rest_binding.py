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
