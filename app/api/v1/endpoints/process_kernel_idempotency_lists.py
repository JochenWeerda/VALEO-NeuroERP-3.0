"""Idempotenz-Listen und Overview-Parity der Process-Kernel-API (Godfile-Auslagerung)."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from app.core.tenant import get_tenant_id
from app.core.action_idempotency import build_idempotency_overview
from app.api.v1.endpoints.process_kernel_api import ProcessKernelOut

router = APIRouter(prefix="/process", tags=["process-kernel", "parity"])


@router.get("/actions/idempotency/overview", response_model=ProcessKernelOut, summary="Idempotency overview abrufen")
def get_idempotency_overview(tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    """Liefert einen Monitoring-Ueberblick ueber den Idempotenz-Layer inkl. flacher KPIs."""
    overview = build_idempotency_overview(tenant_id)
    lookup_paths = [
        "/api/v1/process/actions/execute",
        "/api/v1/process/actions/idempotency/{tenant_id}/{idempotency_key}",
        "/api/v1/process/actions/{execution_id}",
    ]
    catalog = overview.get("catalog") if isinstance(overview.get("catalog"), dict) else {}
    store = overview.get("store") if isinstance(overview.get("store"), dict) else {}
    flat = {
        "confidence_score": overview.get("confidence_score"),
        "recommended_action": overview.get("recommended_action"),
        "total_commands": catalog.get("total_commands"),
        "idempotent_commands": catalog.get("idempotent_commands"),
        "human_confirmation_commands": catalog.get("human_confirmation_commands"),
        "agent_ready_commands": catalog.get("agent_ready_commands"),
        "idempotent_coverage_pct": catalog.get("idempotent_coverage_pct"),
        "total_records": store.get("total_records"),
        "tenant_count": store.get("tenant_count"),
        "execution_count": store.get("execution_count"),
        "command_count": store.get("command_count"),
        "aggregate_count": store.get("aggregate_count"),
    }
    return {**overview, **flat, "lookup_paths": lookup_paths}


@router.get("/actions/idempotency/commands", summary="Idempotente Commands auflisten")
def list_idempotency_commands(tenant_id: str = Depends(get_tenant_id)) -> list[dict[str, str]]:
    """Flache Command-Liste fuer Studio-Cockpit-Tabelle (wie Legacy-Chips)."""
    overview = build_idempotency_overview(tenant_id)
    store = overview.get("store") if isinstance(overview.get("store"), dict) else {}
    commands = store.get("commands") if isinstance(store.get("commands"), list) else []
    return [{"id": name, "name": name} for name in commands if isinstance(name, str)]


@router.get("/actions/idempotency/aggregates", summary="Idempotente Aggregate auflisten")
def list_idempotency_aggregates(tenant_id: str = Depends(get_tenant_id)) -> list[dict[str, str]]:
    """Flache Aggregate-Liste fuer Studio-Cockpit-Tabelle (wie Legacy-Chips)."""
    overview = build_idempotency_overview(tenant_id)
    store = overview.get("store") if isinstance(overview.get("store"), dict) else {}
    aggregates = store.get("aggregates") if isinstance(store.get("aggregates"), list) else []
    return [{"id": name, "name": name} for name in aggregates if isinstance(name, str)]


@router.get("/actions/idempotency/lookup-paths", summary="Idempotenz-Lookup-Pfade")
def list_idempotency_lookup_paths(tenant_id: str = Depends(get_tenant_id)) -> list[dict[str, str]]:
    """Lookup-Pfade aus dem Overview als Liste (Human/CI/MCP)."""
    _ = tenant_id
    paths = [
        "/api/v1/process/actions/execute",
        "/api/v1/process/actions/idempotency/{tenant_id}/{idempotency_key}",
        "/api/v1/process/actions/{execution_id}",
    ]
    return [{"id": path, "path": path} for path in paths]
