"""Planning and incident-center helpers for the admin control center."""

from __future__ import annotations

import json
import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.integrations.services.superglue_live_readiness import build_superglue_live_readiness
from app.integrations.services.superglue_monitoring import build_superglue_admin_overview
from app.integrations.services.superglue_quarantine import (
    build_quarantine_summary,
    resolve_quarantine_entry,
    retry_quarantine_entry,
)

from .agent_ops import get_agent_ops_service
from .agent_ops_persistence import append_agent_ops_history_entry


def _utcnow() -> str:
    return datetime.now(UTC).isoformat()


def _plan_path() -> Path:
    return _resolve_runtime_path(settings.AGENT_OPS_PLAN_PATH)


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _resolve_runtime_path(configured_path: str) -> Path:
    path = Path(configured_path).expanduser().resolve()
    cwd = Path.cwd().resolve()
    temp_root = Path(tempfile.gettempdir()).resolve()
    is_workspace_path = path == cwd or cwd in path.parents
    is_pytest_temp_path = "PYTEST_CURRENT_TEST" in os.environ and (path == temp_root or temp_root in path.parents)
    if not is_workspace_path and not is_pytest_temp_path:
        raise ValueError(f"Runtime path must stay inside the working directory: {configured_path}")
    return path


def _read_plan_state() -> dict[str, Any]:
    path = _plan_path()
    if not path.exists():
        return {"schema_version": 1, "updated_at": None, "tenants": {}}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"schema_version": 1, "updated_at": None, "tenants": {}}
    if not isinstance(payload, dict):
        return {"schema_version": 1, "updated_at": None, "tenants": {}}
    payload.setdefault("schema_version", 1)
    payload.setdefault("updated_at", None)
    payload.setdefault("tenants", {})
    return payload


def _write_plan_state(payload: dict[str, Any]) -> None:
    path = _plan_path()
    _ensure_parent(path)
    path.write_text(  # NOSONAR - path is resolved and constrained by _resolve_runtime_path.
        json.dumps(payload, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def _tenant_plan_state(payload: dict[str, Any], tenant_id: str) -> dict[str, Any]:
    return payload.setdefault("tenants", {}).setdefault(tenant_id, {"items": []})


def build_control_center_planning(tenant_id: str = "system") -> dict[str, Any]:
    ops = get_agent_ops_service()
    overview = ops.build_overview(tenant_id)
    wizard = build_superglue_live_readiness(tenant_id)
    payload = _read_plan_state()
    tenant_state = _tenant_plan_state(payload, tenant_id)

    suggested_items = [
        {
            "plan_id": f"heartbeat:{heartbeat.capability_key}",
            "kind": "agent_heartbeat",
            "title": heartbeat.capability_key,
            "owner": heartbeat.owner_role,
            "cadence": heartbeat.cadence,
            "status": "active" if heartbeat.enabled else "paused",
            "next_hint": heartbeat.next_run_hint,
        }
        for heartbeat in overview.heartbeats
    ]
    suggested_items.extend(
        {
            "plan_id": f"superglue:{connector['connector_key']}",
            "kind": "superglue_connector",
            "title": connector["display_name"],
            "owner": "superglue-ops",
            "cadence": "onboarding",
            "status": "blocked" if not connector["ready"] else "ready",
            "next_hint": ", ".join(connector["blockers"]) or "ready",
        }
        for connector in wizard["connectors"]
    )

    return {
        "tenant_id": tenant_id,
        "storage_path": str(_plan_path()),
        "calendar_window": "14d",
        "suggested_items": suggested_items,
        "planned_items": list(tenant_state.get("items", [])),
        "summary": {
            "heartbeat_count": len(overview.heartbeats),
            "planned_item_count": len(tenant_state.get("items", [])),
            "blocked_connector_count": wizard["blocked_connector_count"],
        },
        "schema_version": 1,
    }


def upsert_control_center_plan_item(
    tenant_id: str,
    *,
    plan_id: str,
    title: str,
    kind: str,
    owner: str,
    scheduled_for: str,
    status: str,
    notes: str | None = None,
) -> dict[str, Any]:
    payload = _read_plan_state()
    tenant_state = _tenant_plan_state(payload, tenant_id)
    items = tenant_state.setdefault("items", [])
    updated_at = _utcnow()
    item = {
        "plan_id": plan_id,
        "title": title,
        "kind": kind,
        "owner": owner,
        "scheduled_for": scheduled_for,
        "status": status,
        "notes": notes,
        "updated_at": updated_at,
    }
    existing_index = next((index for index, current in enumerate(items) if current.get("plan_id") == plan_id), None)
    if existing_index is None:
        items.append(item)
    else:
        items[existing_index] = item
    payload["updated_at"] = updated_at
    _write_plan_state(payload)
    append_agent_ops_history_entry(tenant_id, {"event_type": "plan_upserted", "plan_id": plan_id, "status": status})
    return item


def build_control_center_incidents(tenant_id: str = "system") -> dict[str, Any]:
    ops = get_agent_ops_service()
    control_center = ops.build_control_center(tenant_id)
    readiness = build_superglue_live_readiness(tenant_id)
    quarantine = build_quarantine_summary()
    admin_overview = build_superglue_admin_overview(tenant_id)

    incidents: list[dict[str, Any]] = []
    for ticket in control_center.tickets:
        if ticket.is_stale or ticket.requires_review or ticket.blocker_reasons:
            incidents.append(
                {
                    "incident_id": f"agent:{ticket.ticket_id}",
                    "source": "agent_ops",
                    "severity": "high" if ticket.is_stale or ticket.blocker_reasons else "medium",
                    "title": ticket.work_item_title or ticket.ticket_id,
                    "status": ticket.status,
                    "owner": ticket.owner_role,
                    "escalation_target": ticket.escalation_role,
                    "recommended_action": "escalate" if ticket.is_stale else "approve",
                    "detail": {
                        "ticket_id": ticket.ticket_id,
                        "blockers": ticket.blocker_reasons,
                        "requires_review": ticket.requires_review,
                        "is_stale": ticket.is_stale,
                    },
                }
            )
    for connector in readiness["connectors"]:
        if not connector["ready"]:
            incidents.append(
                {
                    "incident_id": f"superglue:blocker:{connector['connector_key']}",
                    "source": "superglue_readiness",
                    "severity": "high" if "missing_credentials" in connector["blockers"] else "medium",
                    "title": connector["display_name"],
                    "status": "blocked",
                    "owner": "superglue-ops",
                    "escalation_target": "tenant_operations_lead",
                    "recommended_action": "configure_connector",
                    "detail": connector,
                }
            )
    for entry in quarantine.get("open_entries", []):
        incidents.append(
            {
                "incident_id": f"superglue:quarantine:{entry['entry_id']}",
                "source": "superglue_quarantine",
                "severity": "high",
                "title": entry["tool_id"],
                "status": entry["status"],
                "owner": "superglue-ops",
                "escalation_target": "tenant_operations_lead",
                "recommended_action": "resolve_quarantine",
                "detail": entry,
            }
        )

    return {
        "tenant_id": tenant_id,
        "incident_count": len(incidents),
        "open_quarantine_count": quarantine["open_count"],
        "blocked_connector_count": readiness["blocked_connector_count"],
        "stale_ticket_count": control_center.dashboard.stale_work_count,
        "review_ticket_count": control_center.dashboard.review_queue_count,
        "journal_error_count": admin_overview["journal"]["error_count"],
        "incidents": incidents,
        "schema_version": 1,
    }


def apply_control_center_incident_action(
    tenant_id: str,
    incident_id: str,
    *,
    action: str,
    requested_by: str,
    note: str | None = None,
) -> dict[str, Any]:
    if incident_id.startswith("agent:"):
        ticket_id = incident_id.split(":", 1)[1]
        intervention = get_agent_ops_service().apply_intervention(
            tenant_id,
            ticket_id,
            action=action,
            requested_by=requested_by,
            note=note,
        )
        return {"incident_id": incident_id, "result": intervention.model_dump(mode="json"), "schema_version": 1}
    if incident_id.startswith("superglue:quarantine:"):
        entry_id = incident_id.rsplit(":", 1)[1]
        if action == "resolve":
            result = resolve_quarantine_entry(entry_id=entry_id, resolved_by=requested_by, note=note)
        elif action == "retry":
            result = retry_quarantine_entry(entry_id=entry_id, retried_by=requested_by, note=note, dead_letter=False)
        elif action == "dead_letter":
            result = retry_quarantine_entry(entry_id=entry_id, retried_by=requested_by, note=note, dead_letter=True)
        else:
            raise ValueError(f"Unsupported quarantine incident action '{action}'")
        return {"incident_id": incident_id, "result": result, "schema_version": 1}
    raise ValueError(f"Unsupported incident id '{incident_id}'")
