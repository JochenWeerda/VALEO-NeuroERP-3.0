"""MCP-ERP-TOOLS-001 — Rollenbasierter ERP-Tool-Katalog fuer Agent-Zugriff."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

_REGISTRY_PATH = Path(__file__).resolve().parents[2] / "config" / "mcp_erp_tools.yaml"

_RISK_CLASSES = {"low", "medium", "high", "critical"}
_AUDIT_TYPES = {"read", "write", "none"}
_DATA_CLASSIFICATION_LEVELS = {
    "PUBLIC",
    "EU_ONLY",
    "LOCAL_ONLY",
    "SYNTHETIC_ALLOWED",
    "NEVER",
}


class McpToolValidationError(ValueError):
    """Raised when a tool entry is malformed."""


def _load_registry() -> dict[str, Any]:
    if not _REGISTRY_PATH.exists():
        raise FileNotFoundError(f"MCP tool registry not found: {_REGISTRY_PATH}")
    with _REGISTRY_PATH.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _validate_tool(tool: dict[str, Any]) -> None:
    required = {"tool_id", "domain", "name", "scope", "idempotent", "risk_class", "audit"}
    missing = required - tool.keys()
    if missing:
        raise McpToolValidationError(f"Tool {tool.get('tool_id', '?')} missing fields: {missing}")
    if tool["risk_class"] not in _RISK_CLASSES:
        raise McpToolValidationError(
            f"Tool {tool['tool_id']}: invalid risk_class '{tool['risk_class']}'"
        )
    if tool["audit"] not in _AUDIT_TYPES:
        raise McpToolValidationError(
            f"Tool {tool['tool_id']}: invalid audit type '{tool['audit']}'"
        )
    dc = tool.get("data_classification")
    if not dc:
        raise McpToolValidationError(
            f"Tool {tool['tool_id']}: missing data_classification"
        )
    if dc not in _DATA_CLASSIFICATION_LEVELS:
        raise McpToolValidationError(
            f"Tool {tool['tool_id']}: invalid data_classification '{dc}'"
        )


class McpToolRegistryService:
    """Reads and validates the MCP tool registry YAML."""

    def __init__(self, registry_path: Path | None = None) -> None:
        self._path = registry_path or _REGISTRY_PATH
        self._cache: dict[str, Any] | None = None

    def _registry(self) -> dict[str, Any]:
        if self._cache is None:
            self._cache = _load_registry() if self._path == _REGISTRY_PATH else self._load_custom()
        return self._cache

    def _load_custom(self) -> dict[str, Any]:
        with self._path.open("r", encoding="utf-8") as fh:
            return yaml.safe_load(fh)

    def list_tools(
        self,
        domain: str | None = None,
        scope: str | None = None,
        risk_class: str | None = None,
    ) -> list[dict[str, Any]]:
        tools: list[dict[str, Any]] = self._registry().get("tools", [])
        if domain:
            tools = [t for t in tools if t.get("domain") == domain]
        if scope:
            tools = [t for t in tools if t.get("scope") == scope]
        if risk_class:
            tools = [t for t in tools if t.get("risk_class") == risk_class]
        return tools

    def get_tool(self, tool_id: str) -> dict[str, Any]:
        for tool in self._registry().get("tools", []):
            if tool.get("tool_id") == tool_id:
                return tool
        raise KeyError(f"Tool not found: {tool_id}")

    def validate_all(self) -> list[str]:
        errors: list[str] = []
        for tool in self._registry().get("tools", []):
            try:
                _validate_tool(tool)
            except McpToolValidationError as exc:
                errors.append(str(exc))
        return errors

    def summary(self) -> dict[str, Any]:
        tools = self._registry().get("tools", [])
        domains: dict[str, int] = {}
        risk_counts: dict[str, int] = {}
        human_approval_required = 0
        for tool in tools:
            domains[tool.get("domain", "unknown")] = domains.get(tool.get("domain", "unknown"), 0) + 1
            rc = tool.get("risk_class", "unknown")
            risk_counts[rc] = risk_counts.get(rc, 0) + 1
            if tool.get("human_approval_required"):
                human_approval_required += 1
        return {
            "registry_id": self._registry().get("registry_id"),
            "total_tools": len(tools),
            "by_domain": domains,
            "by_risk_class": risk_counts,
            "human_approval_required": human_approval_required,
            "validation_errors": self.validate_all(),
        }


mcp_tool_registry_service = McpToolRegistryService()
