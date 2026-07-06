"""Read-only Quellen für generate_agent_handbuch.py (keine Markdown-Ausgabe)."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[1]

# Workflow-Dateinamen-Präfix → process_key (Flow Spine)
WORKFLOW_PREFIX_TO_PROCESS: dict[str, str] = {
    "otc-": "order-to-cash",
    "p2p-": "procure-to-pay",
    "inv-": "inventory-to-settlement",
    "cts-": "contract-to-settlement",
    "vk-": "harvest-to-settlement",
    "rek-": "complaint-to-resolution",
    "crm-001": "order-to-cash",
    "fin-": "finance-to-close",
    "com-": "compliance-to-report",
    "svc-": "service-to-customer",
    "hts-": "harvest-to-settlement",
}

# mask_id → Flow-Spine process_keys
MASK_TO_PROCESSES: dict[str, list[str]] = {
    "crm/customer-360": ["order-to-cash", "service-to-customer"],
    "sales/sales-order": ["order-to-cash"],
    "sales/delivery-note": ["order-to-cash"],
    "einkauf/supplier": ["procure-to-pay"],
    "einkauf/purchase-order": ["procure-to-pay"],
    "finance/ap-invoice": ["procure-to-pay"],
    "finance/ar-open-item": ["order-to-cash"],
    "finance/payment-run": ["procure-to-pay", "order-to-cash", "finance-to-close"],
    "lager/article-stock": ["inventory-to-settlement"],
    "lager/stock-movement": ["inventory-to-settlement"],
    "agrar/harvest-settlement": ["harvest-to-settlement", "contract-to-settlement"],
    "agrar/kontrakte": ["contract-to-settlement", "harvest-to-settlement"],
    "crm/opportunity": ["order-to-cash"],
    "qualitaet/reklamation": ["complaint-to-resolution"],
}

PROCESS_API_BASE = "/api/v1/process/flow-spines"


def _ensure_repo_on_path() -> None:
    root = str(REPO)
    if root not in sys.path:
        sys.path.insert(0, root)


def load_flow_spine_catalog() -> list[dict[str, str]]:
    _ensure_repo_on_path()
    from app.core.flow_spine_registry import CATALOG

    return list(CATALOG)


def load_flow_spine_workspaces() -> dict[str, dict[str, Any]]:
    _ensure_repo_on_path()
    from app.core.flow_spine_registry import WORKSPACES

    return WORKSPACES


def load_screen_definitions() -> dict[str, dict[str, Any]]:
    _ensure_repo_on_path()
    from app.core.screen_definitions import _SCREEN_DEFINITIONS

    out: dict[str, dict[str, Any]] = {}
    for mask_id, builder in _SCREEN_DEFINITIONS.items():
        if callable(builder):
            out[mask_id] = builder()
        else:
            out[mask_id] = builder
    return out


def load_mcp_tools() -> list[dict[str, Any]]:
    path = REPO / "config" / "mcp_erp_tools.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return list(data.get("tools") or [])


def load_events() -> list[dict[str, Any]]:
    events_file = REPO / "events_raw.json"
    if not events_file.is_file():
        subprocess.run(
            [sys.executable, str(REPO / "scripts" / "extract_events.py")],
            cwd=REPO,
            check=True,
            capture_output=True,
        )
    return json.loads(events_file.read_text(encoding="utf-8"))


def load_routes() -> list[dict[str, str]]:
    path = REPO / "packages" / "frontend-web" / "src" / "app" / "routing" / "route-inventory.gen.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return list(data.get("routes") or [])


def load_workflow_specs() -> dict[str, list[dict[str, str]]]:
    """process_key → [{file, title, lane}]"""
    workflows_dir = REPO / "docs" / "workflows"
    by_process: dict[str, list[dict[str, str]]] = {}
    for path in sorted(workflows_dir.glob("*.md")):
        name = path.name
        if name.startswith("sec-") or name.startswith("int-sg-") or "kernel" in name:
            continue
        text = path.read_text(encoding="utf-8")[:800]
        process_key = None
        for prefix, key in WORKFLOW_PREFIX_TO_PROCESS.items():
            if name.startswith(prefix):
                process_key = key
                break
        if not process_key:
            m = re.search(r"process[_-]?key[`'\"]*\s*[:=]\s*[`'\"]?([a-z0-9-]+)", text, re.I)
            if m:
                process_key = m.group(1)
        if not process_key:
            for key in (
                "order-to-cash",
                "procure-to-pay",
                "inventory-to-settlement",
                "harvest-to-settlement",
                "contract-to-settlement",
                "complaint-to-resolution",
                "service-to-customer",
                "finance-to-close",
                "compliance-to-report",
            ):
                if key in text.lower() or key.replace("-", " ") in text.lower():
                    process_key = key
                    break
        if not process_key:
            continue
        title_m = re.search(r"^#\s+(.+)$", text, re.M)
        lane_m = re.search(r"\*\*Lane:\*\*\s*(.+)$", text, re.M)
        by_process.setdefault(process_key, []).append(
            {
                "file": f"workflows/{name}",
                "title": (title_m.group(1).strip() if title_m else name),
                "lane": (lane_m.group(1).strip() if lane_m else ""),
            }
        )
    return by_process


_SENSITIVE = re.compile(r"passw|token|secret|iban|bic|konto_nr|credit_card", re.I)


def derive_agent_contract(defn: dict[str, Any]) -> dict[str, Any]:
    """Spiegelt app/api/v1/endpoints/mask_screen_definition._generate_agent_contract."""

    def collect_fields(d: dict[str, Any]) -> list[dict[str, Any]]:
        fields: list[dict[str, Any]] = list(d.get("fields") or [])
        for tab in d.get("tabs") or []:
            fields.extend(tab.get("fields") or [])
        return fields

    all_fields = collect_fields(defn)
    readable = [f["key"] for f in all_fields if f.get("key")]
    editable = [f["key"] for f in all_fields if f.get("key") and not f.get("readOnly")]
    sensitive = [
        f["key"]
        for f in all_fields
        if f.get("key")
        and (_SENSITIVE.search(f.get("key", "")) or _SENSITIVE.search(f.get("label", "")))
    ]
    explicit = defn.get("agentContract") or {}
    if explicit.get("sensitiveFields"):
        sensitive = list(dict.fromkeys([*sensitive, *explicit["sensitiveFields"]]))

    actions_out = []
    for a in defn.get("actions") or []:
        actions_out.append(
            {
                "key": a.get("key"),
                "label": a.get("label", a.get("key")),
                "dangerLevel": a.get("dangerLevel", "safe"),
                "humanApprovalRequired": bool(a.get("humanApprovalRequired")),
                "requiresConfirmation": bool(a.get("requiresConfirmation")),
                "permission": a.get("permission"),
                "commandEndpoint": a.get("commandEndpoint"),
                "method": a.get("method", "POST" if a.get("commandEndpoint") else None),
                "stubReason": a.get("stubReason"),
            }
        )

    return {
        "screenId": defn.get("id", ""),
        "domain": defn.get("domain"),
        "businessPurpose": explicit.get(
            "businessPurpose",
            f"{defn.get('title', '')} — {defn.get('domain', '')}",
        ),
        "readableFields": explicit.get("readableFields", readable),
        "editableFields": explicit.get("editableFields", editable),
        "sensitiveFields": sensitive,
        "availableActions": actions_out,
        "examplePrompts": explicit.get("examplePrompts") or [],
        "summaryEndpoint": defn.get("summaryEndpoint"),
        "dataSources": [
            {"key": ds.get("key"), "endpoint": ds.get("endpoint")}
            for ds in (defn.get("dataSources") or [])
        ],
    }


def mask_rollout_route(mask_id: str) -> str:
    return f"/mask-rollout/{mask_id.replace('/', '__')}/:entityId"


def risk_summary(actions: list[dict[str, Any]]) -> str:
    levels = {a.get("dangerLevel", "safe") for a in actions}
    if "high" in levels:
        return "high"
    if "moderate" in levels:
        return "medium"
    return "low"


def mcp_tools_for_domain(domain: str | None, tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not domain:
        return []
    return [t for t in tools if t.get("domain") == domain]


def events_for_domain(domain: str | None, events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not domain:
        return []
    dom = domain.lower()
    return [e for e in events if (e.get("domain") or "").lower() == dom or dom in (e.get("id") or "")]
